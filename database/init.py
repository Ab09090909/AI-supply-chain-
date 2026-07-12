"""
Database Initialization Script
Supports both SQLite and PostgreSQL
"""
import os
from pathlib import Path

def init_database():
    """Initialize database tables"""
    if USE_POSTGRES:
        init_postgres()
    else:
        init_sqlite()

def init_sqlite():
    """Initialize SQLite database"""
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect("data/supply_chain.db")
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Read SQLite schema
    schema_path = Path(__file__).parent / "schema.sqlite.sql"
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    
    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print("✅ SQLite database initialized")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

def init_postgres():
    """Initialize PostgreSQL database"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(
            DATABASE_URL,
            cursor_factory=RealDictCursor
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Read PostgreSQL schema
        schema_path = Path(__path__).parent / "schema.sql"
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        
        try:
            cursor.execute(schema_sql)
            print("✅ PostgreSQL database initialized")
        except Exception as e:
            print(f"❌ Schema error: {e}")
    except Exception as e:
        print(f"❌ PostgreSQL connection error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def seed_demo_data():
    """Insert demo data"""
    if USE_POSTGRES:
        seed_postgres()
    else:
        seed_sqlite()

def seed_sqlite():
    """Seed SQLite database"""
    import sqlite3
    
    conn = sqlite3.connect("data/supply_chain.db")
    cursor = conn.cursor()
    
    try:
        # Users
        cursor.executemany(
            """INSERT OR IGNORE INTO users (email, name, role, password_hash, phone, location, is_verified)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                ("producer@demo.com", "Green Valley Farms", "producer", "scrypt:32768:8:1$salt$hash", "+1 555-0101", "California, USA", 1),
                ("merchant@demo.com", "Metro Retail Inc", "merchant", "scrypt:32768:8:1$salt$hash", "+1 555-0102", "New York, USA", 1),
                ("customer@demo.com", "John Consumer", "customer", "scrypt:32768:8:1$salt$hash", "+1 555-0103", "Texas, USA", 1),
                ("admin@demo.com", "System Admin", "admin", "scrypt:32768:8:1$salt$hash", "+1 555-0100", "Remote", 1),
            ]
        )
        
        # Products
        cursor.executemany(
            """INSERT OR IGNORE INTO products 
               (sku, name, description, category, price, stock, unit, reorder_point, reorder_quantity, producer_id, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                ("AGR-001", "Organic Wheat", "Premium grade wheat", "Grains", 4.20, 450, "ton", 100, 50, 1, 1),
                ("AGR-002", "Fresh Dairy Milk", "Farm fresh whole milk", "Dairy", 3.50, 35, "gallon", 50, 100, 1, 1),
                ("AGR-003", "Premium Avocados", "Hass avocados", "Fruits", 12.00, 12, "unit", 40, 100, 1, 1),
                ("AGR-004", "Free Range Eggs", "Organic free-range eggs", "Dairy", 5.50, 200, "dozen", 80, 50, 1, 1),
            ]
        )
        
        # Orders
        cursor.executemany(
            """INSERT OR IGNORE INTO orders 
               (order_number, buyer_id, buyer_role, seller_id, seller_role, items, subtotal, total, status, payment_status, shipping_address)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                ("ORD-2024-001", 2, "merchant", 1, "producer", '[{"sku":"AGR-001","qty":10,"price":4.20}]', 42.00, 42.00, "delivered", "paid", '{"city":"NYC"}'),
                ("ORD-2024-002", 3, "customer", 1, "producer", '[{"sku":"AGR-003","qty":6,"price":12.00}]', 72.00, 72.00, "delivered", "paid", '{"city":"LA"}'),
            ]
        )
        
        conn.commit()
        print("✅ SQLite demo data seeded")
    except Exception as e:
        print(f"❌ Seed error: {e}")
        conn.rollback()
    finally:
        conn.close()

def seed_postgres():
    """Seed PostgreSQL database"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Users
        cursor.executemany(
            """INSERT INTO users (email, name, role, password_hash, phone, location, is_verified)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (email) DO NOTHING""",
            [
                ("producer@demo.com", "Green Valley Farms", "producer", "scrypt:32768:8:1$salt$hash", "+1 555-0101", "California, USA", True),
                ("merchant@demo.com", "Metro Retail Inc", "merchant", "scrypt:32768:8:1$salt$hash", "+1 555-0102", "New York, USA", True),
                ("customer@demo.com", "John Consumer", "customer", "scrypt:32768:8:1$salt$hash", "+1 555-0103", "Texas, USA", True),
                ("admin@demo.com", "System Admin", "admin", "scrypt:32768:8:1$salt$hash", "+1 555-0100", "Remote", True),
            ]
        )
        
        # Products
        cursor.executemany(
            """INSERT INTO products (sku, name, description, category, price, stock, unit, reorder_point, reorder_quantity, producer_id, is_active)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (sku) DO NOTHING""",
            [
                ("AGR-001", "Organic Wheat", "Premium grade wheat", "Grains", 4.20, 450, "ton", 100, 50, 1, True),
                ("AGR-002", "Fresh Dairy Milk", "Farm fresh whole milk", "Dairy", 3.50, 35, "gallon", 50, 100, 1, True),
                ("AGR-003", "Premium Avocados", "Hass avocados", "Fruits", 12.00, 12, "unit", 40, 100, 1, True),
                ("AGR-004", "Free Range Eggs", "Organic free-range eggs", "Dairy", 5.50, 200, "dozen", 80, 50, 1, True),
            ]
        )
        
        # Orders
        cursor.executemany(
            """INSERT INTO orders (order_number, buyer_id, buyer_role, seller_id, seller_role, items, subtotal, total, status, payment_status, shipping_address)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (order_number) DO NOTHING""",
            [
                ("ORD-2024-001", 2, "merchant", 1, "producer", '[{"sku":"AGR-001","qty":10,"price":4.20}]', 42.00, 42.00, "delivered", "paid", '{"city":"NYC"}'),
                ("ORD-2024-002", 3, "customer", 1, "producer", '[{"sku":"AGR-003","qty":6,"price":12.00}]', 72.00, 72.00, "delivered", "paid", '{"city":"LA"}'),
            ]
        )
        
        print("✅ PostgreSQL demo data seeded")
    except Exception as e:
        print(f"❌ PostgreSQL seed error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
