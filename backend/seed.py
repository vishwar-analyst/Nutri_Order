import sqlite3

from werkzeug.security import generate_password_hash

from database import get_db_connection
from tamil_food_catalog import TRADITIONAL_DISHES, catalog_record


# Nutrition is illustrative per-serving data and is deliberately marked estimated.
# Restaurant owners should replace it with verified recipes/lab measurements.
FOODS = [
    ("Chettinad Chicken Biryani", 240, 560, 4.9, "Biryani", 0, "Aromatic seeraga samba rice layered with peppery Chettinad chicken masala.", "/images/chettinad-chicken-biryani.jpg", "Seeraga samba rice, chicken, onion, tomato, yogurt, ginger, garlic, Chettinad spices", "non-vegetarian", "Lunch", 29, 62, 18, "estimated"),
    ("Ghee Roast Dosa", 110, 390, 4.8, "Breakfast", 1, "A crisp, lacy dosa roasted in ghee and served with sambar and coconut chutney.", "/images/ghee-roast-dosa.png", "Rice, urad dal, fenugreek, ghee; served with sambar and coconut chutney", "vegetarian", "Breakfast", 8, 54, 15, "estimated"),
    ("Traditional Banana Leaf Meals", 190, 640, 4.8, "Traditional Meals", 1, "A comforting spread of rice, seasonal poriyal, kootu, sambar, rasam and curd.", "/images/banana-leaf-meals.jpg", "Rice, seasonal vegetables, lentils, tamarind, yogurt, spices", "vegetarian", "Lunch", 16, 98, 17, "estimated"),
    ("Parotta with Salna", 130, 520, 4.7, "Dinner", 1, "Flaky layered parotta served with a fragrant, slow-cooked vegetable salna.", "/images/parotta-with-salna.jpg", "Wheat flour, oil; salna with onion, tomato, coconut, spices", "vegetarian", "Dinner", 10, 70, 19, "estimated"),
    ("Chicken 65", 180, 430, 4.7, "Snacks", 0, "A fiery Tamil favourite: crisp chicken bites tossed with curry leaves and chillies.", "/images/chicken-65.jpg", "Chicken, yogurt, rice flour, ginger, garlic, chilli, curry leaves", "non-vegetarian", "Snacks", 31, 22, 23, "estimated"),
    ("Ven Pongal", 90, 330, 4.6, "Breakfast", 1, "Soft rice and moong dal pongal finished with pepper, cumin and ghee.", "/images/ven-pongal.jpg", "Rice, moong dal, pepper, cumin, ginger, ghee, cashew", "vegetarian", "Breakfast", 10, 47, 11, "estimated"),
    ("Vegetable Biryani", 170, 420, 4.6, "Biryani", 1, "Fragrant basmati rice with seasonal vegetables and warm whole spices.", "/images/vegetable-biryani.jpg", "Basmati rice, seasonal vegetables, yogurt, mint, spices", "vegetarian", "Lunch", 11, 67, 12, "estimated"),
    ("Idli with Sambar", 75, 280, 4.6, "Breakfast", 1, "Steamed soft idlis paired with lentil-rich sambar and fresh coconut chutney.", "/images/idli-with-sambar.jpg", "Rice, urad dal; sambar with lentils, vegetables and tamarind; coconut chutney", "vegetarian", "Breakfast", 9, 52, 5, "estimated"),
    ("Chettinad Chicken Curry", 220, 390, 4.8, "Non-Vegetarian", 0, "Slow-simmered chicken in a bold, freshly ground Chettinad spice and coconut gravy.", "/images/chettinad-chicken-curry.jpg", "Chicken, onion, tomato, coconut, pepper, fennel, Chettinad spices", "non-vegetarian", "Dinner", 32, 14, 24, "estimated"),
    ("Madurai Fish Curry", 210, 340, 4.7, "Non-Vegetarian", 0, "Tangy tamarind fish curry with chilli, fenugreek and fragrant curry leaves.", "/images/madurai-fish-curry.jpg", "Fish, tamarind, tomato, chilli, fenugreek, curry leaves", "non-vegetarian", "Lunch", 28, 12, 17, "estimated"),
    ("Mutton Chukka", 260, 460, 4.8, "Non-Vegetarian", 0, "Tender mutton cooked down with black pepper, shallots and curry leaves.", "/images/mutton-chukka.jpg", "Mutton, shallots, pepper, ginger, garlic, curry leaves, spices", "non-vegetarian", "Dinner", 34, 9, 29, "estimated"),
    ("Sambar Rice", 95, 360, 4.5, "Traditional Meals", 1, "Homestyle rice and lentils simmered with vegetables, tamarind and sambar spice.", "/images/sambar-rice.jpg", "Rice, toor dal, vegetables, tamarind, sambar spice", "vegetarian", "Lunch", 12, 68, 8, "estimated"),
    ("Curd Rice", 80, 290, 4.5, "Traditional Meals", 1, "Cooling curd rice tempered with mustard, ginger and curry leaves.", "/images/curd-rice.jpg", "Rice, yogurt, mustard, ginger, curry leaves", "vegetarian", "Lunch", 9, 44, 8, "estimated"),
    ("South Indian Filter Coffee", 45, 110, 4.8, "Beverages", 1, "Strong decoction and frothy milk, traditionally poured and served hot.", "/images/south-indian-filter-coffee.jpg", "Coffee, milk, sugar (optional)", "vegetarian", "Beverages", 4, 12, 4, "estimated"),
    ("Kuzhi Paniyaram", 85, 250, 4.5, "Snacks", 1, "Golden, crisp-edged paniyaram made from a gently fermented rice and lentil batter.", "/images/kuzhi-paniyaram.jpg", "Rice, urad dal, onion, green chilli, curry leaves", "vegetarian", "Snacks", 7, 42, 7, "estimated"),
    ("Sweet Kesari", 70, 310, 4.4, "Desserts", 1, "A golden semolina sweet with cardamom, ghee and toasted cashews.", "/images/sweet-kesari.jpg", "Semolina, sugar, ghee, cardamom, cashew", "vegetarian", "Desserts", 5, 48, 12, "estimated"),
]


def seed_data():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """INSERT INTO users (username, password, password_hash, role, email, full_name)
               VALUES (?, '', ?, ?, ?, ?)""",
            ("customer", generate_password_hash("1234"), "customer", "customer@nutriorder.local", "Demo Customer"),
        )
    except sqlite3.IntegrityError:
        cursor.execute(
            "UPDATE users SET email = COALESCE(NULLIF(email, ''), ?), "
            "full_name = COALESCE(NULLIF(full_name, ''), ?) WHERE username = ?",
            ("customer@nutriorder.local", "Demo Customer", "customer"),
        )

    try:
        cursor.execute(
            """INSERT INTO users (username, password, password_hash, role, email, full_name)
               VALUES (?, '', ?, ?, ?, ?)""",
                ("bakery", generate_password_hash("1234"), "bakery", "owner@nutriorder.local", "Restaurant Owner"),
        )
    except sqlite3.IntegrityError:
        cursor.execute(
            "UPDATE users SET email = COALESCE(NULLIF(email, ''), ?), "
            "full_name = COALESCE(NULLIF(full_name, ''), ?) WHERE username = ?",
            ("owner@nutriorder.local", "Restaurant Owner", "bakery"),
        )

    # Upgrade legacy prototype plaintext passwords immediately during startup.
    legacy_users = cursor.execute(
        "SELECT id, password FROM users WHERE password_hash IS NULL OR password_hash = ''"
    ).fetchall()
    for user in legacy_users:
        if user["password"]:
            cursor.execute(
                "UPDATE users SET password_hash = ?, password = '' WHERE id = ?",
                (generate_password_hash(user["password"]), user["id"]),
            )

    # Remove old demo-only bakery inventory. Existing order_items retain name/price snapshots.
    cursor.execute(
        "DELETE FROM foods WHERE name IN (?, ?, ?, ?, ?, ?, ?, ?)",
        ("Veg Puff", "Egg Puff", "Cream Bun", "Fruit Cake", "Fresh Fruit Juice", "Chocolate Cake", "Vegetable Sandwich", "Fresh Fruit Bowl"),
    )

    insert_sql = """INSERT INTO foods
        (name, price, calories, rating, category, healthy, description, image_url,
         ingredients, food_type, meal_type, protein, carbs, fat, nutrition_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    for food in FOODS:
        cursor.execute("SELECT id FROM foods WHERE name = ?", (food[0],))
        existing = cursor.fetchone()
        if existing:
            cursor.execute(
                """UPDATE foods SET price=?, calories=?, rating=?, category=?, healthy=?,
                   description=?, image_url=?, ingredients=?, food_type=?, meal_type=?,
                   protein=?, carbs=?, fat=?, nutrition_status=? WHERE id=?""",
                (*food[1:], existing["id"]),
            )
        else:
            cursor.execute(insert_sql, food)

        # These curated records are the Tamil Nadu restaurant's own demo menu.
        # Do not populate stock, allergen, serving-size, or missing nutrient claims.
        cursor.execute(
            "UPDATE foods SET cuisine = COALESCE(cuisine, 'Tamil Nadu'), restaurant_name = COALESCE(restaurant_name, 'NutriOrder AI'), catalog_status = COALESCE(catalog_status, 'active_seed_menu') WHERE name = ?",
            (food[0],),
        )

    # Add informational catalog entries with NULL price/nutrition and no
    # dish-photo claim. They remain non-orderable until the restaurant confirms
    # its actual recipe, offer price, image and availability.
    for entry in TRADITIONAL_DISHES:
        record = catalog_record(entry)
        existing = cursor.execute(
            "SELECT id, food_slug FROM foods WHERE lower(name) = lower(?) OR food_slug = ? LIMIT 1",
            (record["name"], record["food_slug"]),
        ).fetchone()
        if existing:
            cursor.execute(
                """UPDATE foods SET food_slug=COALESCE(food_slug, ?), tamil_name=COALESCE(tamil_name, ?),
                   restaurant_name=COALESCE(restaurant_name, 'NutriOrder AI'), cuisine=COALESCE(cuisine, 'Tamil Nadu'),
                   preparation_method=COALESCE(preparation_method, ?), catalog_status=COALESCE(catalog_status, 'active_seed_menu')
                   WHERE id=?""",
                (record["food_slug"], record["tamil_name"], record["cooking_method"], existing["id"]),
            )
            continue

        cursor.execute(
            """INSERT INTO foods
               (name, price, calories, rating, category, healthy, description, image_url,
                ingredients, food_type, meal_type, protein, carbs, fat, nutrition_status,
                fiber, sodium, serving_size, allergens, cooking_method, cuisine,
                availability_status, dietary_verified, allergens_verified, food_slug,
                tamil_name, preparation_method, nutrition_source, nutrition_confidence,
                restaurant_name, catalog_status)
               VALUES (?, NULL, NULL, NULL, ?, 0, ?, NULL, ?, ?, ?, NULL, NULL, NULL, 'unavailable',
                       NULL, NULL, NULL, NULL, ?, 'Tamil Nadu', 'pending_confirmation', 0, 0,
                       ?, ?, ?, NULL, NULL, 'NutriOrder AI', 'reference_pending_restaurant_confirmation')""",
            (
                record["name"], record["category"], record["description"], record["ingredients"],
                record["food_type"], record["meal_type"], record["cooking_method"], record["food_slug"],
                record["tamil_name"], record["cooking_method"],
            ),
        )

    connection.commit()
    connection.close()
    print("Tamil Nadu restaurant sample menu added successfully!")


if __name__ == "__main__":
    seed_data()