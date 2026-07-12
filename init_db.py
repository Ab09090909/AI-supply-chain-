"""
Database Initialization Script
Run this ONCE to create and seed the database
"""
import sqlite3
import os
from pathlib import Path

def init_database():
    """Create SQLite database with schema and demo data"""
    
    # Create data directory
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    db_path = data_dir / "supply_chain.db"
    
    print("🚀 Initializing database...")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # ============ CREATE TABLES ============
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('producer', 'merchant', 'customer', 'admin')),
            password_hash TEXT NOT NULL,
            phone TEXT,
            location TEXT,
            avatar_url TEXT,
            is_active BOOLEAN DEFAULT 1,
            is_verified BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            metadata JSON
        )
    """)
    
    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL CHECK(category IN ('Grains', 'Dairy', 'Fruits', 'Vegetables', 'Meat', 'Bakery', 'Other')),
            price REAL NOT NULL CHECK(price >= 0),
            stock INTEGER DEFAULT 0 CHECK(stock >= 0),
            unit TEXT NOT NULL,
            reorder_point INTEGER DEFAULT 10 CHECK(reorder_point >= 0),
            reorder_quantity INTEGER DEFAULT 50,
            producer_id INTEGER NOT NULL,
            images JSON,
            specifications JSON,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producer_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            buyer_id INTEGER NOT NULL,
            buyer_role TEXT NOT NULL,
            seller_id INTEGER NOT NULL,
            seller_role TEXT NOT NULL,
            items JSON NOT NULL,
            subtotal REAL NOT NULL,
            tax REAL DEFAULT 0,
            shipping REAL DEFAULT 0,
            total REAL NOT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'flagged', 'refunded')),
            shipping_address JSON,
            payment_method TEXT,
            payment_status TEXT DEFAULT 'pending' CHECK(payment_status IN ('pending', 'paid', 'escrow', 'released', 'refunded')),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (buyer_id) REFERENCES users(id),
            FOREIGN KEY (seller_id) REFERENCES users(id)
        )
    """)
    
    # Agreements table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agreements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agreement_number TEXT UNIQUE NOT NULL,
            order_id INTEGER NOT NULL,
            producer_id INTEGER NOT NULL,
            merchant_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            terms JSON NOT NULL,
            price_per_unit REAL NOT NULL,
            quantity INTEGER NOT NULL,
            total_value REAL NOT NULL,
            delivery_date DATE NOT NULL,
            delivery_location TEXT NOT NULL,
            penalty_clause TEXT,
            advance_percentage REAL DEFAULT 30.0,
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'pending_signature', 'signed', 'active', 'completed', 'cancelled')),
            producer_signed_at TIMESTAMP,
            merchant_signed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (producer_id) REFERENCES users(id),
            FOREIGN KEY (merchant_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    # Fraud logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fraud_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_data JSON NOT NULL,
            risk_score REAL NOT NULL CHECK(risk_score >= 0 AND risk_score <= 1),
            flagged BOOLEAN DEFAULT 0,
            risk_factors JSON,
            user_id INTEGER,
            order_id INTEGER,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'reviewed', 'false_positive', 'confirmed')),
            reviewed_by INTEGER,
            reviewed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (reviewed_by) REFERENCES users(id)
        )
    """)
    
    # Favorites table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, product_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """)
    
    # Cart items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, product_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """)
    
    # AI predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_type TEXT NOT NULL,
            input_data JSON NOT NULL,
            prediction_result JSON NOT NULL,
            confidence REAL,
            model_version TEXT,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Notifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            data JSON,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    print("✅ Tables created successfully")
    
    # ============ SEED DEMO DATA ============
    
    # Demo users
    users = [
        ("producer@demo.com", "Green Valley Farms", "producer", "hash123", "+1 555-0101", "California, USA", 1),
        ("merchant@demo.com", "Metro Retail Inc", "merchant", "hash123", "+1 555-0102", "New York, USA", 1),
        ("customer@demo.com", "John Consumer", "customer", "hash123", "+1 555-0103", "Texas, USA", 1),
        ("admin@demo.com", "System Admin", "admin", "hash123", "+1 555-0100", "Remote", 1),
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO users (email, name, role, password_hash, phone, location, is_verified)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        users
    )
    
    # Demo products
    products = [
        ("AGR-001", "Organic Wheat", "Premium grade wheat", "Grains", 4.20, 450, "ton", 100, 50, 1, 1),
        ("AGR-002", "Fresh Dairy Milk", "Farm fresh whole milk", "Dairy", 3.50, 35, "gallon", 50, 100, 1, 1),
        ("AGR-003", "Premium Avocados", "Hass avocados", "Fruits", 12.00, 12, "unit", 40, 100, 1, 1),
        ("AGR-004", "Free Range Eggs", "Organic free-range eggs", "Dairy", 5.50, 200, "dozen", 80, 50, 1, 1),
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO products 
           (sku, name, description, category, price, stock, unit, reorder_point, reorder_quantity, producer_id, is_active)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        products
    )
    
    # Demo orders
    orders = [
        ("ORD-2024-001", 2, "merchant", 1, "producer", 
         '[{"sku":"AGR-001","name":"Organic Wheat","qty":10,"price":4.20}]',
         42.00, 0, 0, 42.00, "delivered", "paid",
         '{"city":"NYC"}',
         "Electronically processed"),
        
        ("ORD-2024-002", 3, "customer", 1, "producer",
         '[{"sku":"AGR-003","name":"Premium Avocados","qty":6,"price":12.00}]',
         72.00, 0, 0, 72.00, "delivered", "paid",
         '{"city":"LA"}',
         "Gift wrapping requested"),
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO orders 
           (order_number, buyer_id, buyer_role, seller_id, seller_role, items, subtotal, total, status, payment_status, shipping_address, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        orders
    )
    
    conn.commit()
    conn.close()
    
    print("✅ Demo data seeded successfully")
    print(f"   - {len(users)} users")
    print(f"   - {len(products)} products")
    print(f"   - {len(orders)} orders")
    print(f"\n📍 Database location: {db_path}")
    print("\n🎉 Setup complete! Run: streamlit run app.py")

if __name__ == "__main__":
    init_database()
