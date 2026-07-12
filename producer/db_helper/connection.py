"""
Producer Database Helper
Database connection wrapper
"""
from producer.utils.db import db

def get_db_connection():
    """Get database connection"""
    return db

def get_inventory():
    """Get inventory items"""
    return db.get_inventory(1)

def get_orders():
    """Get all orders"""
    return db.get_orders(1)

def get_pending_orders():
    """Get pending orders"""
    return db.get_orders(1, 'pending')
