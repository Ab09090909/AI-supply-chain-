"""
Producer DB Helper - Centralized data access layer for Producer portal
Uses the thread-safe SQLite singleton from database/connection.py
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import random
import hashlib

# ---------------------------------------------------------------------------
# Connection (graceful fallback: try singleton, else direct sqlite3)
# ---------------------------------------------------------------------------
try:
    # When running from project root
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from database.connection import db as _db
    _USE_SINGLETON = True
except ImportError:
    _USE_SINGLETON = False

DB_PATH = str(Path(__file__).resolve().parent.parent.parent / "data" / "supply_chain.db")

def _get_conn() -> sqlite3.Connection:
    """Return a connection – prefer the singleton, fallback to direct."""
    if _USE_SINGLETON:
        c = _db.get_connection()
        if c:
            return c
    # Fallback
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def query(sql: str, params: tuple = None, fetch: str = "all") -> Any:
    """Execute SELECT and return rows as list[dict]."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        if fetch == "one":
            row = cur.fetchone()
            return dict(row) if row else None
        return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        print(f"[DB query error] {e}")
        return [] if fetch == "all" else None


def execute(sql: str, params: tuple = None) -> Optional[int]:
    """Execute INSERT/UPDATE/DELETE, return lastrowid."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        print(f"[DB execute error] {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return None


# ===================================================================
# PRODUCER DATA ACCESS FUNCTIONS
# ===================================================================

def get_producer_id(email: str) -> Optional[int]:
    """Get producer user id from email."""
    row = query("SELECT id FROM users WHERE email=? AND role='producer'", (email,), fetch="one")
    return row["id"] if row else None


def get_producer_profile(email: str) -> Optional[Dict]:
    """Get producer profile info."""
    return query(
        "SELECT id, email, role, created_at FROM users WHERE email=? AND role='producer'",
        (email,), fetch="one"
    )


# ---- PRODUCTS ----

def get_products(producer_id: int = None, category: str = None,
                 search: str = None, status: str = None) -> List[Dict]:
    """Get products with optional filters."""
    sql = "SELECT * FROM products WHERE 1=1"
    params = []
    if producer_id:
        sql += " AND producer_id=?"
        params.append(producer_id)
    if category:
        sql += " AND category=?"
        params.append(category)
    if search:
        sql += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if status:
        sql += " AND status=?"
        params.append(status)
    sql += " ORDER BY created_at DESC"
    return query(sql, tuple(params))


def get_product_by_id(product_id: int) -> Optional[Dict]:
    return query("SELECT * FROM products WHERE id=?", (product_id,), fetch="one")


def add_product(name: str, category: str, price: float, stock: int,
                min_stock: int, description: str = "", producer_id: int = 1,
                status: str = "active") -> Optional[int]:
    return execute(
        """INSERT INTO products
           (name, category, price, current_stock, min_stock, description, producer_id, status)
           VALUES (?,?,?,?,?,?,?,?)""",
        (name, category, price, stock, min_stock, description, producer_id, status)
    )


def update_product(product_id: int, **kwargs) -> bool:
    """Update product fields dynamically."""
    if not kwargs:
        return False
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [product_id]
    return execute(f"UPDATE products SET {sets} WHERE id=?", tuple(vals)) is not None


def delete_product(product_id: int) -> bool:
    return execute("DELETE FROM products WHERE id=?", (product_id,)) is not None


def get_product_categories() -> List[str]:
    rows = query("SELECT DISTINCT category FROM products WHERE category IS NOT NULL")
    return [r["category"] for r in rows if r["category"]]


# ---- ORDERS ----

def get_orders(producer_id: int = None, status: str = None,
               date_from: str = None, date_to: str = None) -> List[Dict]:
    sql = "SELECT * FROM orders WHERE 1=1"
    params = []
    if producer_id:
        sql += " AND producer_id=?"
        params.append(producer_id)
    if status:
        sql += " AND status=?"
        params.append(status)
    if date_from:
        sql += " AND created_at >= ?"
        params.append(date_from)
    if date_to:
        sql += " AND created_at <= ?"
        params.append(date_to)
    sql += " ORDER BY created_at DESC"
    return query(sql, tuple(params))


def get_order_by_id(order_id: int) -> Optional[Dict]:
    return query("SELECT * FROM orders WHERE id=?", (order_id,), fetch="one")


def update_order_status(order_id: int, status: str) -> bool:
    return execute("UPDATE orders SET status=? WHERE id=?", (status, order_id)) is not None


def get_order_stats(producer_id: int = None) -> Dict:
    """Aggregate order statistics."""
    base = "SELECT" if not producer_id else "SELECT"
    where = f"WHERE producer_id={producer_id}" if producer_id else ""
    
    total = query(f"SELECT COUNT(*) as cnt FROM orders {where}", fetch="one")
    pending = query(f"SELECT COUNT(*) as cnt FROM orders {where} AND status='pending'", fetch="one")
    shipped = query(f"SELECT COUNT(*) as cnt FROM orders {where} AND status='shipped'", fetch="one")
    delivered = query(f"SELECT COUNT(*) as cnt FROM orders {where} AND status='delivered'", fetch="one")
    revenue = query(f"SELECT COALESCE(SUM(total_amount),0) as rev FROM orders {where} AND status='delivered'", fetch="one")
    
    return {
        "total_orders": total["cnt"] if total else 0,
        "pending_orders": pending["cnt"] if pending else 0,
        "shipped_orders": shipped["cnt"] if shipped else 0,
        "delivered_orders": delivered["cnt"] if delivered else 0,
        "total_revenue": revenue["rev"] if revenue else 0,
    }


# ---- AGREEMENTS ----

def get_agreements(producer_id: int = None, status: str = None) -> List[Dict]:
    sql = "SELECT * FROM agreements WHERE 1=1"
    params = []
    if producer_id:
        sql += " AND producer_id=?"
        params.append(producer_id)
    if status:
        sql += " AND status=?"
        params.append(status)
    sql += " ORDER BY created_at DESC"
    return query(sql, tuple(params))


# ---- FRAUD LOGS ----

def get_fraud_logs(producer_id: int = None) -> List[Dict]:
    sql = "SELECT * FROM fraud_logs WHERE 1=1"
    params = []
    if producer_id:
        sql += " AND producer_id=?"
        params.append(producer_id)
    sql += " ORDER BY created_at DESC LIMIT 50"
    return query(sql, tuple(params))


def get_fraud_stats() -> Dict:
    total = query("SELECT COUNT(*) as cnt FROM fraud_logs", fetch="one")
    flagged = query("SELECT COUNT(*) as cnt FROM fraud_logs WHERE risk_score > 0.7", fetch="one")
    return {
        "total_flags": total["cnt"] if total else 0,
        "high_risk": flagged["cnt"] if flagged else 0,
    }


# ---- AI PREDICTIONS ----

def get_ai_predictions(producer_id: int = None) -> List[Dict]:
    sql = "SELECT * FROM ai_predictions WHERE 1=1"
    params = []
    if producer_id:
        sql += " AND producer_id=?"
        params.append(producer_id)
    sql += " ORDER BY created_at DESC LIMIT 100"
    return query(sql, tuple(params))


# ---- NOTIFICATIONS ----

def get_notifications(user_id: int) -> List[Dict]:
    return query(
        "SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 50",
        (user_id,)
    )


def mark_notification_read(notif_id: int) -> bool:
    return execute("UPDATE notifications SET is_read=1 WHERE id=?", (notif_id,)) is not None


# ---- REVENUE TIME SERIES (for charts) ----

def get_revenue_timeline(producer_id: int = None, days: int = 30) -> List[Dict]:
    """Get daily revenue for the last N days."""
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    sql = """
        SELECT DATE(created_at) as date,
               COUNT(*) as order_count,
               COALESCE(SUM(total_amount), 0) as revenue
        FROM orders
        WHERE created_at >= ? AND status = 'delivered'
    """
    params = [date_from]
    if producer_id:
        sql += " AND producer_id=?"
        params.append(producer_id)
    sql += " GROUP BY DATE(created_at) ORDER BY date"
    return query(sql, tuple(params))


def get_category_distribution(producer_id: int = None) -> List[Dict]:
    """Get revenue/product distribution by category."""
    sql = """
        SELECT category,
               COUNT(*) as product_count,
               COALESCE(SUM(price), 0) as total_value
        FROM products WHERE 1=1
    """
    params = []
    if producer_id:
        sql += " AND producer_id=?"
        params.append(producer_id)
    sql += " GROUP BY category"
    return query(sql, tuple(params))


def get_stock_summary(producer_id: int = None) -> Dict:
    """Get inventory stock level summary."""
    sql = "SELECT * FROM products WHERE 1=1"
    params = []
    if producer_id:
        sql += " AND producer_id=?"
        params.append(producer_id)
    
    products = query(sql, tuple(params))
    total_items = len(products)
    low_stock = sum(1 for p in products if p.get("current_stock", 0) < p.get("min_stock", 0))
    out_of_stock = sum(1 for p in products if p.get("current_stock", 0) == 0)
    total_value = sum(p.get("price", 0) * p.get("current_stock", 0) for p in products)
    
    return {
        "total_items": total_items,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "total_inventory_value": total_value,
        "healthy_stock": total_items - low_stock - out_of_stock,
    }


# ---- SEED DEMO DATA (if tables are empty) ----

def seed_producer_demo_data():
    """Insert demo data for the producer dashboard if tables are empty."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        
        # Check if products table has data
        cur.execute("SELECT COUNT(*) FROM products")
        if cur.fetchone()[0] > 0:
            return  # Already has data
        
        # Get producer user id
        cur.execute("SELECT id FROM users WHERE role='producer' LIMIT 1")
        row = cur.fetchone()
        producer_id = row[0] if row else 1
        
        demo_products = [
            ("Organic Wheat Grain", "Agriculture", 45.00, 1200, 200, "Premium organic wheat from sustainable farms"),
            ("Cold-Pressed Olive Oil", "Oils & Fats", 28.50, 850, 100, "Extra virgin cold-pressed olive oil"),
            ("Raw Cashew Nuts", "Nuts & Seeds", 62.00, 600, 150, "Premium grade raw cashew nuts"),
            ("Green Coffee Beans", "Beverages", 35.00, 2000, 300, "Single origin Arabica green coffee"),
            ("Organic Honey", "Sweeteners", 22.00, 450, 80, "Pure organic wildflower honey"),
            ("Basmati Rice", "Grains", 18.00, 3000, 500, "Long-grain premium Basmati rice"),
            ("Dried Turmeric", "Spices", 40.00, 300, 50, "Organic turmeric powder"),
            ("Coconut Oil", "Oils & Fats", 15.00, 1500, 200, "Virgin coconut oil for cooking"),
            ("Almond Butter", "Nut Butter", 55.00, 200, 40, "Smooth organic almond butter"),
            ("Quinoa Seeds", "Grains", 48.00, 700, 100, "Premium white quinoa seeds"),
            ("Chia Seeds", "Seeds", 32.00, 900, 120, "Organic black chia seeds"),
            ("Maple Syrup", "Sweeteners", 38.00, 350, 60, "Grade A pure maple syrup"),
        ]
        
        for name, cat, price, stock, min_stock, desc in demo_products:
            cur.execute(
                """INSERT INTO products
                   (name, category, price, current_stock, min_stock, description, producer_id, status)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (name, cat, price, stock, min_stock, desc, producer_id, "active")
            )
        
        # Seed demo orders
        statuses = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]
        now = datetime.now()
        for i in range(25):
            days_ago = random.randint(1, 60)
            order_date = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
            status = random.choice(statuses)
            amount = round(random.uniform(500, 15000), 2)
            cur.execute(
                """INSERT INTO orders
                   (producer_id, merchant_id, product_id, quantity, total_amount, status, created_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (producer_id, random.randint(2, 5), random.randint(1, 12),
                 random.randint(10, 500), amount, status, order_date)
            )
        
        # Seed demo fraud logs
        for i in range(8):
            log_date = (now - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S")
            risk = round(random.uniform(0.3, 0.95), 2)
            cur.execute(
                """INSERT INTO fraud_logs
                   (producer_id, order_id, risk_score, fraud_type, created_at)
                   VALUES (?,?,?,?,?)""",
                (producer_id, random.randint(1, 25), risk,
                 random.choice(["price_anomaly", "velocity_spike", "new_account", "geo_mismatch"]),
                 log_date)
            )
        
        # Seed demo agreements
        agreement_statuses = ["active", "pending", "expired"]
        for i in range(6):
            cur.execute(
                """INSERT INTO agreements
                   (producer_id, merchant_id, terms, status, created_at)
                   VALUES (?,?,?,?,?)""",
                (producer_id, random.randint(2, 5),
                 f"Supply agreement for bulk order #{i+1}. Terms: Net-30 payment, minimum order 100 units.",
                 random.choice(agreement_statuses),
                 (now - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d %H:%M:%S"))
            )
        
        # Seed demo notifications
        notif_types = [
            ("New order received", "Order #ORD-2024-001 has been placed for Organic Wheat Grain."),
            ("Low stock alert", "Almond Butter stock is below minimum threshold."),
            ("Fraud detection alert", "Suspicious activity detected on Order #ORD-2024-015."),
            ("Agreement signed", "Merchant Co. signed a new supply agreement."),
            ("Delivery confirmed", "Order #ORD-2024-008 has been delivered successfully."),
            ("Price prediction update", "AI model predicts 12% price increase for Coffee Beans."),
            ("Inventory restocked", "Chia Seeds inventory has been replenished."),
            ("New merchant inquiry", "FreshFoods Inc. sent a partnership request."),
        ]
        for i, (title, msg) in enumerate(notif_types):
            cur.execute(
                """INSERT INTO notifications
                   (user_id, title, message, type, is_read, created_at)
                   VALUES (?,?,?,?,?,?)""",
                (producer_id, title, msg, "info", 1 if i > 3 else 0,
                 (now - timedelta(hours=i*3)).strftime("%Y-%m-%d %H:%M:%S"))
            )
        
        conn.commit()
        print("Demo data seeded successfully!")
    except Exception as e:
        print(f"Seed error (may already exist): {e}")
        try:
            conn.rollback()
        except Exception:
            pass
