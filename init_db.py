"""
Database Initialization - Run this once
"""
import sqlite3
import os
from pathlib import Path

def init_db():
    # Create data directory
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    db_path = data_dir / "supply_chain.db"
    
    # Connect and create tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
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
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created at: {db_path}")
    return db_path

if __name__ == "__main__":
    init_db()
