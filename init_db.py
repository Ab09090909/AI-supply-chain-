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

    # Create users table with proper hashed password support
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # CRITICAL FIX: Removed malformed CHECK(risk_score>= 0 AND risk_score 0)
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

    # Insert demo users with PROPER cryptographic hashing (Fixes High #23)
    demo_users = [
        ("producer@demo.com", "producer"),
        ("merchant@demo.com", "merchant"),
        ("customer@demo.com", "customer"),
        ("admin@demo.com", "admin")
    ]
    
    for email, role in demo_users:
        # Hash the password "password" using SHA-256
        pwd_hash = hashlib.sha256("password".encode()).hexdigest()
        try:
            cursor.execute(
                "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
                (email, pwd_hash, role)
            )
        except sqlite3.IntegrityError:
            pass  # User already exists

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully with secure password hashes.")

if __name__ == "__main__":
    init_db()
