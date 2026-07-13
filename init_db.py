"""
Database Schema & Seed Data
Complete schema for the AI Supply Chain Platform
"""
import sqlite3
import hashlib
import os

DB_NAME = "supply_chain.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # ---- Users ----
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('producer','merchant','customer','admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ---- Products ----
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL DEFAULT 0,
            current_stock INTEGER NOT NULL DEFAULT 0,
            min_stock INTEGER NOT NULL DEFAULT 0,
            description TEXT,
            producer_id INTEGER NOT NULL,
            status TEXT DEFAULT 'active' CHECK(status IN ('active','inactive','draft')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producer_id) REFERENCES users(id)
        )
    ''')

    # ---- Orders ----
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producer_id INTEGER NOT NULL,
            merchant_id INTEGER,
            product_id INTEGER,
            quantity INTEGER NOT NULL DEFAULT 1,
            total_amount REAL NOT NULL DEFAULT 0,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending','confirmed','processing','shipped','delivered','cancelled')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producer_id) REFERENCES users(id),
            FOREIGN KEY (merchant_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # ---- Agreements (B2B) ----
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agreements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producer_id INTEGER NOT NULL,
            merchant_id INTEGER,
            terms TEXT,
            status TEXT DEFAULT 'pending' CHECK(status IN ('active','pending','expired','cancelled')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producer_id) REFERENCES users(id),
            FOREIGN KEY (merchant_id) REFERENCES users(id)
        )
    ''')

    # ---- Fraud Logs ----
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fraud_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producer_id INTEGER,
            order_id INTEGER,
            risk_score REAL NOT NULL DEFAULT 0 CHECK(risk_score >= 0 AND risk_score <= 1),
            fraud_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producer_id) REFERENCES users(id),
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    ''')

    # ---- Favorites ----
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # ---- AI Predictions ----
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producer_id INTEGER,
            product_id INTEGER,
            prediction_type TEXT,
            predicted_value REAL,
            confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producer_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # ---- Notifications ----
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT,
            type TEXT DEFAULT 'info' CHECK(type IN ('info','warning','error','success')),
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ---- Seed demo users ----
    demo_users = [
        ("producer@demo.com", "producer"),
        ("merchant@demo.com", "merchant"),
        ("customer@demo.com", "customer"),
        ("admin@demo.com", "admin")
    ]

    for email, role in demo_users:
        pwd_hash = hashlib.sha256("password".encode()).hexdigest()
        try:
            cursor.execute(
                "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
                (email, pwd_hash, role)
            )
        except sqlite3.IntegrityError:
            pass  # Already exists

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()
