import os
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE = Path(os.getenv("NUTRIORDER_DB", "nutriorder.db")).expanduser()
if not DATABASE.is_absolute():
    DATABASE = PROJECT_ROOT / DATABASE
DATABASE = DATABASE.resolve()


def get_db_connection():

    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE, timeout=10)

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables():

    connection = get_db_connection()

    cursor = connection.cursor()

    # USERS

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT,
            full_name TEXT,
            phone TEXT,
            password_hash TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    user_columns = {
        row["name"] for row in cursor.execute("PRAGMA table_info(users)").fetchall()
    }
    optional_user_columns = {
        "email": "TEXT",
        "full_name": "TEXT",
        "phone": "TEXT",
        "password_hash": "TEXT",
        "is_active": "INTEGER NOT NULL DEFAULT 1",
        "created_at": "TIMESTAMP",
    }
    for column, definition in optional_user_columns.items():
        if column not in user_columns:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")

    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique "
        "ON users(email COLLATE NOCASE) WHERE email IS NOT NULL AND email != ''"
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            used_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # FOODS

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL,
            calories INTEGER,
            rating REAL,
            category TEXT,
            healthy INTEGER DEFAULT 0,
            description TEXT,
            image_url TEXT,
            ingredients TEXT,
            food_type TEXT DEFAULT 'vegetarian',
            meal_type TEXT,
            protein REAL,
            carbs REAL,
            fat REAL,
            nutrition_status TEXT DEFAULT 'unavailable',
            fiber REAL,
            sodium REAL,
            serving_size TEXT,
            allergens TEXT,
            cooking_method TEXT,
            cuisine TEXT,
            availability_status TEXT,
            dietary_verified INTEGER,
            allergens_verified INTEGER,
            food_slug TEXT,
            tamil_name TEXT,
            preparation_method TEXT,
            nutrition_source TEXT,
            nutrition_confidence TEXT,
            restaurant_name TEXT,
            catalog_status TEXT,
            image_verified INTEGER
        )
    """)

    # Additive migration for existing demo databases; existing order history stays intact.
    food_columns = {
        row["name"] for row in cursor.execute("PRAGMA table_info(foods)").fetchall()
    }
    optional_food_columns = {
        "description": "TEXT",
        "image_url": "TEXT",
        "ingredients": "TEXT",
        "food_type": "TEXT DEFAULT 'vegetarian'",
        "meal_type": "TEXT",
        "protein": "REAL",
        "carbs": "REAL",
        "fat": "REAL",
        "nutrition_status": "TEXT DEFAULT 'unavailable'",
        "fiber": "REAL",
        "sodium": "REAL",
        "serving_size": "TEXT",
        "allergens": "TEXT",
        "cooking_method": "TEXT",
        "cuisine": "TEXT",
        "availability_status": "TEXT",
        "dietary_verified": "INTEGER",
        "allergens_verified": "INTEGER",
        "food_slug": "TEXT",
        "tamil_name": "TEXT",
        "preparation_method": "TEXT",
        "nutrition_source": "TEXT",
        "nutrition_confidence": "TEXT",
        "restaurant_name": "TEXT",
        "catalog_status": "TEXT",
        "image_verified": "INTEGER",
    }
    for column, definition in optional_food_columns.items():
        if column not in food_columns:
            cursor.execute(f"ALTER TABLE foods ADD COLUMN {column} {definition}")

    # Older databases declared price NOT NULL. Rebuild only that table so new
    # catalog-only dishes can truthfully carry an unknown (NULL) offer price.
    # order_items stores name/price snapshots and has no food-table foreign key.
    price_info = next(row for row in cursor.execute("PRAGMA table_info(foods)") if row["name"] == "price")
    if price_info["notnull"]:
        cursor.execute("""
            CREATE TABLE foods_nullable_price (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL,
                calories INTEGER,
                rating REAL,
                category TEXT,
                healthy INTEGER DEFAULT 0,
                description TEXT,
                image_url TEXT,
                ingredients TEXT,
                food_type TEXT DEFAULT 'vegetarian',
                meal_type TEXT,
                protein REAL,
                carbs REAL,
                fat REAL,
                nutrition_status TEXT DEFAULT 'unavailable',
                fiber REAL,
                sodium REAL,
                serving_size TEXT,
                allergens TEXT,
                cooking_method TEXT,
                cuisine TEXT,
                availability_status TEXT,
                dietary_verified INTEGER,
                allergens_verified INTEGER,
                food_slug TEXT,
                tamil_name TEXT,
                preparation_method TEXT,
                nutrition_source TEXT,
                nutrition_confidence TEXT,
                restaurant_name TEXT,
                catalog_status TEXT,
                image_verified INTEGER
            )
        """)
        columns = [row["name"] for row in cursor.execute("PRAGMA table_info(foods_nullable_price)")]
        column_sql = ", ".join(f'"{column}"' for column in columns)
        cursor.execute(f"INSERT INTO foods_nullable_price ({column_sql}) SELECT {column_sql} FROM foods")
        cursor.execute("DROP TABLE foods")
        cursor.execute("ALTER TABLE foods_nullable_price RENAME TO foods")

    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_foods_slug_unique ON foods(food_slug) WHERE food_slug IS NOT NULL AND food_slug != ''")

    # ORDERS

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE NOT NULL,
            customer_id INTEGER,
            total REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ORDER ITEMS

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            food_id INTEGER,
            food_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    """)

    connection.commit()

    connection.close()


if __name__ == "__main__":

    create_tables()

    print("Database created successfully!")