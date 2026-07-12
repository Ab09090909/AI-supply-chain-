"""
Producer Database Helper
Thin wrapper around shared database connection
"""
from database.connection import db

def get_inventory(producer_id: int = 1) -> list:
    """Get inventory for producer"""
    query = "SELECT * FROM products WHERE producer_id = ? AND is_active = 1"
    return db.execute_query(query, (producer_id,), fetch=True) or []

def get_orders(producer_id: int = 1) -> list:
    """Get orders for producer"""
    query = """
        SELECT o.*, u.name as buyer_name 
        FROM orders o
        JOIN users u ON o.buyer_id = u.id
        WHERE o.seller_id = ? AND o.seller_role = 'producer'
        ORDER BY o.created_at DESC
    """
    return db.execute_query(query, (producer_id,), fetch=True) or []

def get_pending_orders(producer_id: int = 1
