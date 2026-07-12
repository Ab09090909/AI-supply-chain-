"""
Database Initialization Script
Run this once to set up the complete database
"""
import sqlite3
import os
from pathlib import Path

def init_database(db_path: str = "data/supply_chain.db"):
    """Initialize database with schema and seed data"""
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Read and execute schema
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    
    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print(f"✅ Database schema created at: {db_path}")
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def seed_demo_data(db_path: str = "data/supply_chain.db"):
    """Insert demo data for testing"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # ============================================
        # DEMO USERS
        # ============================================
        users = [
            ("producer@demo.com", "Green Valley Farms", "producer", "scrypt:32768:8:1$salt$hash", "+1 555-0101", "California, USA", 1),
            ("merchant@demo.com", "Metro Retail Inc", "merchant", "scrypt:32768:8:1$salt$hash", "+1 555-0102", "New York, USA", 1),
            ("customer@demo.com", "John Consumer", "customer", "scrypt:32768:8:1$salt$hash", "+1 555-0103", "Texas, USA", 1),
            ("admin@demo.com", "System Admin", "admin", "scrypt:32768:8:1$salt$hash", "+1 555-0100", "Remote", 1),
            ("producer2@demo.com", "Sunrise Organic", "producer", "scrypt:32768:8:1$salt$hash", "+1 555-0104", "Oregon, USA", 1),
        ]
        
        cursor.executemany(
            """INSERT OR IGNORE INTO users (email, name, role, password_hash, phone, location, is_verified)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            users
        )
        
        # ============================================
        # DEMO PRODUCTS
        # ============================================
        products = [
            ("AGR-001", "Organic Wheat", "Premium grade wheat, protein content 12%+", "Grains", 4.20, 450, "ton", 100, 50, 1, 1),
            ("AGR-002", "Fresh Dairy Milk", "Farm fresh whole milk", "Dairy", 3.50, 35, "gallon", 50, 100, 1, 1),
            ("AGR-003", "Premium Avocados", "Hass avocados, ready to eat", "Fruits", 12.00, 12, "unit", 40, 100, 1, 1),
            ("AGR-004", "Free Range Eggs", "Organic free-range eggs", "Dairy", 5.50, 200, "dozen", 80, 50, 1, 1),
            ("AGR-005", "Organic Rice", "Basmati rice, aged 1 year", "Grains", 3.80, 45, "unit", 60, 100, 1, 1),
            ("AGR-006", "Organic Carrots", "Fresh organic carrots", "Vegetables", 2.90, 0, "unit", 30, 100, 1, 1),
            ("AGR-007", "Artisan Bread", "Sourdough loaf", "Bakery", 4.99, 50, "loaf", 20, 30, 5, 1),
            ("AGR-008", "Organic Honey", "Raw wildflower honey", "Other", 8.99, 25, "jar", 15, 50, 5, 1),
        ]
        
        cursor.executemany(
            """INSERT OR IGNORE INTO products 
               (sku, name, description, category, price, stock, unit, reorder_point, reorder_quantity, producer_id, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            products
        )
        
        # ============================================
        # DEMO ORDERS
        # ============================================
        orders = [
            ("ORD-2024-001", 2, "merchant", 1, "producer", 
             '[{"sku":"AGR-001","name":"Organic Wheat","qty":10,"price":4.20}]',
             42.00, 0, 0, 42.00, "delivered", "paid",
             '{"street":"123 Warehouse District","city":"Metro City","state":"CA","zip":"90001"}',
             "Electronically processed", "2024-01-15 10:30:00"),
            
            ("ORD-2024-002", 3, "customer", 1, "producer",
             '[{"sku":"AGR-003","name":"Premium Avocados","qty":6,"price":12.00}]',
             72.00, 0, 0, 72.00, "delivered", "paid",
             '{"street":"456 Oak Avenue","city":"Los Angeles","state":"CA","zip":"90002"}',
             "Gift wrapping requested", "2024-01-16 14:20:00"),
            
            ("ORD-2024-003", 2, "merchant", 1, "producer",
             '[{"sku":"AGR-002","name":"Fresh Dairy Milk","qty":50,"price":3.50}]',
             175.00, 0, 0, 175.00, "processing", "escrow",
             '{"street":"789 Market Street","city":"San Francisco","state":"CA","zip":"90003"}',
             "Urgent delivery", "2024-01-20 09:15:00"),
        ]
        
        cursor.executemany(
            """INSERT OR IGNORE INTO orders 
               (order_number, buyer_id, buyer_role, seller_id, seller_role, items, subtotal, tax, shipping, total, status, payment_status, shipping_address, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            orders
        )
        
        # ============================================
        # DEMO FRAUD LOGS
        # ============================================
        fraud_logs = [
            ('{"supplier":"FastFoods Inc","amount":15000,"history":true}', 0.89, 1, '["High transaction amount","Late delivery history"]', 2, NULL, "flagged", NULL, "2024-01-20"),
            ('{"supplier":"QuickSupply Co","amount":5000,"history":false}', 0.45, 0, '["Medium risk pattern"]', 2, NULL, "reviewed", 4, "2024-01-19"),
            ('{"supplier":"BulkGoods Ltd","amount":8000,"history":true}', 0.72, 1, '["Past disputes","High amount"]', 2, NULL, "confirmed", 4, "2024-01-18"),
        ]
        
        cursor.executemany(
            """INSERT OR IGNORE INTO fraud_logs 
               (transaction_data, risk_score, flagged, risk_factors, user_id, order_id, status, reviewed_by, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            fraud_logs
        )
        
        # ============================================
        # DEMO FAVORITES
        # ============================================
        favorites = [
            (3, 3),  -- John Consumer favorites Premium Avocados
            (3, 4),  -- Free Range Eggs
            (3, 8),  -- Organic Honey
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO favorites (user_id, product_id) VALUES (?, ?)",
            favorites
        )
        
        # ============================================
        # DEMO NOTIFICATIONS
        # ============================================
        notifications = [
            (1, "New Order Received", "Metro Retail Inc placed an order for Organic Wheat", "info", '{"order_id": 3}', 0),
            (2, "Order Confirmed", "Your order #ORD-2024-002 has been confirmed", "success", '{"order_id": 2}', 1),
            (1, "Low Stock Alert", "Premium Avocados stock is critically low (12 units)", "warning", '{"sku": "AGR-003"}', 0),
            (4, "Fraud Alert", "Suspicious activity detected from FastFoods Inc", "error", '{"fraud_id": 1}', 0),
        ]
        
        cursor.executemany(
            """INSERT OR IGNORE INTO notifications 
               (user_id, title, message, type, data, is_read)
               VALUES (?, ?, ?, ?, ?, ?)""",
            notifications
        )
        
        # ============================================
        # DEMO AI PREDICTIONS
        # ============================================
        predictions = [
            ("price_forecast", '{"product":"wheat","days":30}', '{"forecast":[4.20,4.25,4.30,4.28,4.35],"confidence":0.85}', 0.85, "v2.1", 1),
            ("demand_forecast", '{"category":"Dairy","days":7}', '{"forecast":[78,92,85,88,95,90,85],"confidence":0.82}', 0.82, "v2.1", 1),
            ("fraud_risk", '{"supplier":"NewSupplier","amount":5000}', '{"risk_score":0.45,"flagged":false}', 0.45, "v2.1", 2),
        ]
        
        cursor.executemany(
            """INSERT OR IGNORE INTO ai_predictions 
               (prediction_type, input_data, prediction_result, confidence, model_version, user_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            predictions
        )
        
        # ============================================
        # SYSTEM SETTINGS
        # ============================================
        settings = [
            ("app_name", "AI Supply Chain Platform", "string", "Application name"),
            ("app_version", "2.1.0", "string", "Current version"),
            ("fraud_threshold_high", "0.7", "number", "High risk threshold"),
            ("fraud_threshold_medium", "0.4", "number", "Medium risk threshold"),
            ("price_volatility_warning", "0.15", "number", "Price change warning threshold"),
            ("maintenance_mode", "false", "boolean", "Enable maintenance mode"),
            ("max_upload_size", "10", "number", "Max file upload size in MB"),
            ("session_timeout", "8", "number", "Session timeout in hours"),
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO settings (key, value, type, description) VALUES (?, ?, ?, ?)",
            settings
        )
        
        conn.commit()
        print("✅ Demo data seeded successfully")
        print(f"   - {len(users)} users")
        print(f"   - {len(products)} products")
        print(f"   - {len(orders)} orders")
        print(f"   - {len(fraud_logs)} fraud logs")
        print(f"   - {len(favorites)} favorites")
        print(f"   - {len(notifications)} notifications")
        print(f"   - {len(predictions)} AI predictions")
        print(f"   - {len(settings)} system settings")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def reset_database(db_path: str = "data/supply_chain.db"):
    """Drop all tables and recreate (WARNING: destroys all data)"""
    import os
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️ Deleted existing database: {db_path}")
    
    init_database(db_path)
    seed_demo_data(db_path)
    print("✅ Database reset complete")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        print("⚠️  WARNING: This will delete all existing data!")
        confirm = input("Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            reset_database()
    else:
        init_database()
        seed_demo_data()
