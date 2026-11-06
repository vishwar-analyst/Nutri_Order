import os
import secrets
import sqlite3
import uuid
from datetime import timedelta

from flask import Flask, jsonify, request, session

from flask_cors import CORS
from pathlib import Path
import sys

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent
for import_path in (str(PROJECT_ROOT), str(BACKEND_DIR)):
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from database import (
    get_db_connection,
    create_tables
)
from seed import seed_data

from rag.chatbot import answer_question
from auth_service import (
    consume_password_reset,
    create_session,
    issue_password_reset,
    normalize_email,
    password_error,
    valid_email,
    validate_customer_registration,
    verify_or_upgrade_password,
)
from nutrimatch_service import chat_reply, load_menu as load_nutrimatch_menu, recommend as build_nutrimatch_recommendations, validate_profile


app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.getenv("NUTRIORDER_SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("NUTRIORDER_COOKIE_SECURE", "false").lower() == "true",
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    MAX_CONTENT_LENGTH=64 * 1024,
)
frontend_origins = [
    origin.strip()
    for origin in os.getenv(
        "NUTRIORDER_FRONTEND_ORIGIN",
        "http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500,http://127.0.0.1:5500",
    ).split(",")
    if origin.strip()
]
CORS(
    app,
    resources={r"/api/*": {"origins": frontend_origins}},
    supports_credentials=True,
)

create_tables()
seed_data()


# =====================================
# HOME
# =====================================

@app.route("/")
def home():

    return "NutriOrder AI Backend is Running!"


# =====================================
# TEST
# =====================================

@app.route("/api/test")
def test():

    return jsonify({
        "success": True,
        "message": "API connected successfully"
    })


# =====================================
# GROUNDED NUTRIBOT CHAT
# =====================================

@app.route("/api/chat", methods=["POST"])
@app.route("/api/nutribot/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "message": "Send a JSON object."}), 400

    question = data.get("message", data.get("question", ""))
    if not isinstance(question, str) or not question.strip():
        return jsonify({"success": False, "message": "Enter a question."}), 400

    question = question.strip()
    if len(question) > 500:
        return jsonify({"success": False, "message": "Questions must be 500 characters or fewer."}), 400

    try:
        result = answer_question(question)
    except Exception as error:
        # Keep implementation details, prompts, and provider credentials out of API responses.
        app.logger.warning("NutriBot request failed (%s).", type(error).__name__)
        return jsonify({"success": False, "message": "NutriBot is temporarily unavailable."}), 503

    return jsonify({"success": True, **result})


# =====================================
# LOGIN
# =====================================

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "message": "Send a valid JSON object."}), 400

    identifier = data.get("identifier", data.get("email", ""))
    if not isinstance(identifier, str):
        identifier = ""
    identifier = identifier.strip()
    email = normalize_email(identifier)
    password = data.get("password")
    if not identifier or len(identifier) > 254 or not isinstance(password, str):
        return jsonify({"success": False, "message": "Enter your email or username and password."}), 400

    connection = get_db_connection()
    try:
        user = connection.execute(
            """SELECT * FROM users
               WHERE (email = ? COLLATE NOCASE OR username = ? COLLATE NOCASE)
                 AND is_active = 1
               LIMIT 1""",
            (email, identifier),
        ).fetchone()
        if not user or not verify_or_upgrade_password(user, password, connection):
            return jsonify({"success": False, "message": "Email/username or password is incorrect."}), 401
        safe_user = create_session(user, remember=bool(data.get("remember", False)))
        destination = {
            "customer": "/frontend/customer.html",
            "owner": "/bakery/dashboard.html",
            "admin": "/admin/dashboard.html",
        }.get(safe_user["role"], "/frontend/customer.html")
        return jsonify({"success": True, "user": safe_user, "redirect_url": destination})
    finally:
        connection.close()


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "message": "Send a valid JSON object."}), 400
    issue, profile = validate_customer_registration(data)
    if issue:
        return jsonify({"success": False, "message": issue}), 400

    connection = get_db_connection()
    try:
        existing = connection.execute(
            "SELECT id FROM users WHERE email = ? COLLATE NOCASE", (profile["email"],)
        ).fetchone()
        if existing:
            return jsonify({"success": False, "message": "An account with this email already exists. Sign in instead."}), 409

        username = f"user_{uuid.uuid4().hex[:16]}"
        from werkzeug.security import generate_password_hash

        try:
            cursor = connection.execute(
                """INSERT INTO users (username, password, password_hash, role, email, full_name, phone)
                   VALUES (?, '', ?, 'customer', ?, ?, ?)""",
                (
                    username,
                    generate_password_hash(profile["password"]),
                    profile["email"],
                    profile["full_name"],
                    profile["phone"],
                ),
            )
        except sqlite3.IntegrityError:
            connection.rollback()
            return jsonify({"success": False, "message": "An account with this email already exists. Sign in instead."}), 409
        connection.commit()
        user = connection.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
        safe_user = create_session(user)
        return jsonify({"success": True, "user": safe_user, "redirect_url": "/frontend/customer.html"}), 201
    finally:
        connection.close()


@app.route("/api/me", methods=["GET"])
def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "user": None}), 401
    connection = get_db_connection()
    try:
        user = connection.execute(
            "SELECT * FROM users WHERE id = ? AND is_active = 1", (user_id,)
        ).fetchone()
        if not user:
            session.clear()
            return jsonify({"success": False, "user": None}), 401
        role = "owner" if user["role"] == "bakery" else user["role"]
        return jsonify({
            "success": True,
            "user": {
                "id": int(user["id"]),
                "username": user["username"],
                "full_name": user["full_name"] or user["username"],
                "email": user["email"],
                "role": role,
            },
        })
    finally:
        connection.close()


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "You are signed out."})


def _session_role():
    role = session.get("role")
    return "owner" if role == "bakery" else role


def _auth_error(allowed_roles):
    if not session.get("user_id"):
        return jsonify({"success": False, "message": "Sign in to continue."}), 401
    if _session_role() not in allowed_roles:
        return jsonify({"success": False, "message": "Your account is not permitted to do this."}), 403
    return None


@app.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json(silent=True)
    email = normalize_email(data.get("email")) if isinstance(data, dict) else ""
    if not valid_email(email):
        return jsonify({"success": False, "message": "Enter a valid email address."}), 400

    connection = get_db_connection()
    try:
        try:
            issue_password_reset(email, connection)
        except Exception:
            # Do not expose whether an account exists or the mail service is configured.
            pass
        return jsonify({"success": True, "message": "If an account exists for that email, password reset instructions will be sent."})
    finally:
        connection.close()


@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "message": "Send a valid JSON object."}), 400
    token = data.get("token")
    password = data.get("password")
    issue = password_error(password)
    if issue:
        return jsonify({"success": False, "message": issue}), 400
    if not isinstance(token, str) or not token:
        return jsonify({"success": False, "message": "This reset link is invalid or expired."}), 400
    connection = get_db_connection()
    try:
        if not consume_password_reset(token, password, connection):
            return jsonify({"success": False, "message": "This reset link is invalid or expired."}), 400
        session.clear()
        return jsonify({"success": True, "message": "Password updated. You can now sign in."})
    finally:
        connection.close()


# =====================================
# GET ALL FOODS
# =====================================

def _food_payload(food):
    return {
        "id": food["id"],
        "food_id": food["food_slug"] or str(food["id"]),
        "food_slug": food["food_slug"],
        "name": food["name"],
        "food_name": food["name"],
        "tamil_name": food["tamil_name"],
        "price": food["price"],
        "calories": food["calories"],
        "rating": food["rating"],
        "category": food["category"],
        "healthy": bool(food["healthy"]),
        "description": food["description"],
        "image_url": food["image_url"],
        "image_verified": bool(food["image_verified"]),
        "ingredients": food["ingredients"],
        "food_type": food["food_type"],
        "dietary_type": food["food_type"],
        "meal_type": food["meal_type"],
        "protein": food["protein"],
        "carbs": food["carbs"],
        "fat": food["fat"],
        "fiber": food["fiber"],
        "sodium": food["sodium"],
        "nutrition_status": food["nutrition_status"],
        "nutrition_source": food["nutrition_source"],
        "nutrition_confidence": food["nutrition_confidence"],
        "serving_size": food["serving_size"],
        "allergens": food["allergens"],
        "allergens_verified": bool(food["allergens_verified"]),
        "dietary_verified": bool(food["dietary_verified"]),
        "cooking_method": food["cooking_method"],
        "preparation_method": food["preparation_method"],
        "cuisine": food["cuisine"],
        "availability_status": food["availability_status"],
        "restaurant_name": food["restaurant_name"],
        "catalog_status": food["catalog_status"],
    }

@app.route("/api/foods")
def get_foods():

    connection = get_db_connection()

    foods = connection.execute("""
        SELECT *
        FROM foods
        ORDER BY id
    """).fetchall()

    connection.close()

    return jsonify([_food_payload(food) for food in foods])


@app.route("/api/foods/categories")
def food_categories():
    connection = get_db_connection()
    try:
        rows = connection.execute(
            "SELECT DISTINCT category FROM foods WHERE category IS NOT NULL AND category != '' ORDER BY category"
        ).fetchall()
        return jsonify({"success": True, "categories": [row["category"] for row in rows]})
    finally:
        connection.close()


@app.route("/api/foods/<int:food_id>")
def get_food(food_id: int):
    connection = get_db_connection()
    try:
        food = connection.execute("SELECT * FROM foods WHERE id = ?", (food_id,)).fetchone()
        if not food:
            return jsonify({"success": False, "message": "Food item was not found."}), 404
        return jsonify({"success": True, "food": _food_payload(food)})
    finally:
        connection.close()


# =====================================
# HEALTHY FOODS
# =====================================

@app.route("/api/foods/healthy")
def healthy_foods():

    connection = get_db_connection()

    foods = connection.execute("""
        SELECT *
        FROM foods
        WHERE healthy = 1
    """).fetchall()

    connection.close()

    return jsonify([_food_payload(food) for food in foods])


# =====================================
# NUTRIMATCH PERSONALIZED DISCOVERY
# =====================================

@app.route("/api/nutrimatch/profile", methods=["POST"])
def nutrimatch_profile():
    data = request.get_json(silent=True)
    try:
        profile = validate_profile(data)
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400
    return jsonify({
        "success": True,
        "profile": profile,
        "profile_saved": False,
        "message": "Preferences are validated for this request only and are not stored.",
    })


@app.route("/api/nutrimatch/recommendations", methods=["POST"])
def nutrimatch_recommendations():
    data = request.get_json(silent=True)
    try:
        profile = validate_profile(data)
        result = build_nutrimatch_recommendations(profile)
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400
    except Exception as error:
        app.logger.warning("NutriMatch recommendation failed (%s).", type(error).__name__)
        return jsonify({"success": False, "message": "Recommendations are temporarily unavailable."}), 503
    return jsonify(result)


@app.route("/api/nutrimatch/chat", methods=["POST"])
def nutrimatch_chat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "message": "Send a JSON object."}), 400
    try:
        result = chat_reply(data.get("message"), data.get("preferences"))
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400
    except Exception as error:
        app.logger.warning("NutriMatch chat failed (%s).", type(error).__name__)
        return jsonify({"success": False, "message": "NutriMatch chat is temporarily unavailable."}), 503
    return jsonify(result)


@app.route("/api/nutrimatch/foods", methods=["GET"])
def nutrimatch_foods():
    return jsonify(load_nutrimatch_menu())


@app.route("/api/nutrimatch/foods/<int:food_id>", methods=["GET"])
def nutrimatch_food_detail(food_id: int):
    food = next((item for item in load_nutrimatch_menu() if item["id"] == food_id), None)
    if not food:
        return jsonify({"success": False, "message": "Food item was not found."}), 404
    return jsonify({"success": True, "food": food})


@app.route("/api/nutrimatch/categories", methods=["GET"])
def nutrimatch_categories():
    foods = load_nutrimatch_menu()
    return jsonify({
        "success": True,
        "categories": sorted({food["category"] for food in foods if food.get("category")}),
        "meal_types": sorted({food["meal_type"] for food in foods if food.get("meal_type")}),
        "cuisines": sorted({food["cuisine"] for food in foods if food.get("cuisine")}),
    })


@app.route("/api/nutrimatch/filters", methods=["GET"])
def nutrimatch_filters():
    from nutrimatch_service import (
        ALLERGIES, BUDGETS, CUISINES, DIETARY_TYPES, GOALS,
        HEALTH_CONSIDERATIONS, MEALS, NUTRITION_PREFERENCES, TASTES,
    )
    return jsonify({
        "success": True,
        "goals": sorted(GOALS),
        "health_considerations": sorted(HEALTH_CONSIDERATIONS),
        "dietary_preferences": sorted(DIETARY_TYPES),
        "cuisines": sorted(CUISINES),
        "allergies": sorted(ALLERGIES),
        "nutrition_preferences": sorted(NUTRITION_PREFERENCES),
        "taste_preferences": sorted(TASTES),
        "meal_preferences": sorted(MEALS),
        "budgets": sorted(BUDGETS),
    })


# =====================================
# CREATE ORDER
# =====================================

@app.route("/api/orders", methods=["POST"])
def create_order():

    auth_error = _auth_error(["customer"])
    if auth_error:
        return auth_error

    data = request.get_json()

    customer_id = data.get("customer_id")

    if customer_id != session.get("user_id"):
        return jsonify({"success": False, "message": "You can only order for your own account."}), 403

    items = data.get("items", [])

    if not isinstance(items, list) or not items:

        return jsonify({
            "success": False,
            "message": "Cart is empty"
        }), 400


    connection = get_db_connection()
    cursor = connection.cursor()
    order_lines = []
    total = 0
    try:
        for item in items:
            if not isinstance(item, dict):
                connection.close()
                return jsonify({"success": False, "message": "Each cart item must be valid."}), 400
            try:
                food_id = int(item.get("id"))
                quantity = int(item.get("quantity"))
            except (TypeError, ValueError):
                connection.close()
                return jsonify({"success": False, "message": "Each cart item needs a valid ID and quantity."}), 400
            if quantity < 1 or quantity > 50:
                connection.close()
                return jsonify({"success": False, "message": "Quantity must be between 1 and 50."}), 400
            food = connection.execute(
                "SELECT id, name, price, availability_status, catalog_status FROM foods WHERE id = ?",
                (food_id,),
            ).fetchone()
            if not food or food["price"] is None:
                connection.close()
                return jsonify({"success": False, "message": "This dish is not currently orderable; confirm its restaurant price first."}), 409
            if food["catalog_status"] == "reference_pending_restaurant_confirmation" or food["availability_status"] in {"pending_confirmation", "unavailable", "out_of_stock", "disabled"}:
                connection.close()
                return jsonify({"success": False, "message": "This dish is not currently available to order."}), 409
            line_price = float(food["price"])
            total += line_price * quantity
            order_lines.append((food["id"], food["name"], quantity, line_price))
    except Exception:
        connection.close()
        raise


    order_id = "NOAI-" + uuid.uuid4().hex[:8].upper()


    cursor.execute("""
        INSERT INTO orders
        (
            order_id,
            customer_id,
            total,
            status
        )

        VALUES (?, ?, ?, ?)
    """, (
        order_id,
        customer_id,
        total,
        "Pending"
    ))


    for food_id, food_name, quantity, line_price in order_lines:

        cursor.execute("""
            INSERT INTO order_items
            (
                order_id,
                food_id,
                food_name,
                quantity,
                price
            )

            VALUES (?, ?, ?, ?, ?)
        """, (
            order_id,
            food_id,
            food_name,
            quantity,
            line_price
        ))


    connection.commit()

    connection.close()


    return jsonify({

        "success": True,

        "order_id": order_id,

        "total": total,

        "status": "Pending"

    })


# =====================================
# CUSTOMER ORDERS
# =====================================

@app.route("/api/orders/customer/<int:customer_id>")
def customer_orders(customer_id):

    auth_error = _auth_error(["customer"])
    if auth_error:
        return auth_error
    if customer_id != session.get("user_id"):
        return jsonify({"success": False, "message": "You can only view your own orders."}), 403

    connection = get_db_connection()

    orders = connection.execute("""
        SELECT *
        FROM orders
        WHERE customer_id = ?
        ORDER BY id DESC
    """, (customer_id,)).fetchall()

    result = []

    for order in orders:

        items = connection.execute("""
            SELECT *
            FROM order_items
            WHERE order_id = ?
        """, (order["order_id"],)).fetchall()

        item_list = []

        for item in items:

            item_list.append({

                "name": item["food_name"],

                "quantity": item["quantity"],

                "price": item["price"]

            })


        result.append({

            "order_id": order["order_id"],

            "total": order["total"],

            "status": order["status"],

            "created_at": order["created_at"],

            "items": item_list

        })


    connection.close()

    return jsonify(result)


# =====================================
# ALL BAKERY ORDERS
# =====================================

@app.route("/api/bakery/orders")
def bakery_orders():

    auth_error = _auth_error(["owner", "admin"])
    if auth_error:
        return auth_error

    connection = get_db_connection()

    orders = connection.execute("""
        SELECT orders.*,
               users.full_name AS customer_name,
               users.username AS customer_username,
               users.email AS customer_email,
               users.phone AS customer_phone
        FROM orders
        LEFT JOIN users ON users.id = orders.customer_id
        ORDER BY orders.id DESC
    """).fetchall()

    result = []

    for order in orders:

        items = connection.execute("""
            SELECT *
            FROM order_items
            WHERE order_id = ?
        """, (order["order_id"],)).fetchall()

        item_list = []

        for item in items:

            item_list.append({

                "name": item["food_name"],

                "quantity": item["quantity"],

                "price": item["price"]

            })


        result.append({

            "order_id": order["order_id"],

            "customer": {
                "name": order["customer_name"] or order["customer_username"] or "Customer details unavailable",
                "email": order["customer_email"] or None,
                "phone": order["customer_phone"] or None,
            },

            "total": order["total"],

            "status": order["status"],

            "created_at": order["created_at"],

            "items": item_list

        })


    connection.close()

    return jsonify(result)


# =====================================
# UPDATE ORDER STATUS
# =====================================

@app.route(
    "/api/orders/<order_id>/status",
    methods=["PUT"]
)
def update_order_status(order_id):

    auth_error = _auth_error(["owner", "admin"])
    if auth_error:
        return auth_error

    data = request.get_json()

    status = data.get("status")

    allowed_statuses = [

        "Pending",

        "Accepted",

        "Preparing",

        "Ready",

        "Completed"

    ]

    if status not in allowed_statuses:

        return jsonify({

            "success": False,

            "message": "Invalid status"

        }), 400


    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE orders

        SET status = ?

        WHERE order_id = ?
    """, (
        status,
        order_id
    ))

    connection.commit()

    connection.close()


    return jsonify({

        "success": True,

        "message": "Order status updated"

    })


# =====================================
# RUN
# =====================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )