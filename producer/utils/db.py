"""
Producer Database Access Layer
"""
import json
import sqlite3
import os
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

# Get project root directory (2 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "supply_chain.db"

class MockDB:
    """Fallback when shared database is not available"""
    def __init__(self):
        # Ensure data directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.db_path = str(DB_PATH)
    
    def execute_query(self, query, params=None, fetch=False):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = [dict(row) for row in cursor.fetchall()]
            else:
                result = cursor.lastrowid
            
            conn.commit()
            conn.close()
            return result
        except Exception as e:
            print(f"MockDB error: {e}")
            return None

# Try to import shared database, fallback to MockDB
try:
    from database.connection import db as shared_db
except ImportError:
    shared_db = MockDB()

class ProducerDB:
    """Producer-specific database operations"""
    
    def __init__(self):
        self.producer_id = 1
        self.db = shared_db
    
    def _ensure_connection(self):
        """Ensure database file exists"""
        if not DB_PATH.exists():
            print(f"⚠️ Database not found at {DB_PATH}")
            print("Please run: python database/init.py")
            return False
        return True
    
    def get_inventory(self) -> List[Dict]:
        """Get all inventory items for current producer"""
        if not self._ensure_connection():
            return []
        
        query = """
            SELECT id, sku, name, description, category, price, stock, unit,
                   reorder_point, reorder_quantity, is_active, created_at
            FROM products 
            WHERE producer_id = ? AND is_active = 1
            ORDER BY category, name
        """
        results = self.db.execute_query(query, (self.producer_id,), fetch=True)
        return results if results else []
    
    def get_orders(self, status: str = None) -> List[Dict]:
        """Get orders for current producer"""
        if not self._ensure_connection():
            return []
        
        if status:
            query = """
                SELECT o.*, u.name as buyer_name, u.email as buyer_email
                FROM orders o
                JOIN users u ON o.buyer_id = u.id
                WHERE o.seller_id = ? AND o.seller_role = 'producer' AND o.status = ?
                ORDER BY o.created_at DESC
            """
            params = (self.producer_id, status)
        else:
            query = """
                SELECT o.*, u.name as buyer_name, u.email as buyer_email
                FROM orders o
                JOIN users u ON o.buyer_id = u.id
                WHERE o.seller_id = ? AND o.seller_role = 'producer'
                ORDER BY o.created_at DESC
            """
            params = (self.producer_id,)
        
        results = self.db.execute_query(query, params, fetch=True)
        
        # Parse JSON fields
        for order in results or []:
            if order.get('items'):
                try:
                    order['items'] = json.loads(order['items'])
                except:
                    order['items'] = []
            if order.get('shipping_address'):
                try:
                    order['shipping_address'] = json.loads(order['shipping_address'])
                except:
                    order['shipping_address'] = {}
        
        return results or []
    
    def get_pending_orders(self) -> List[Dict]:
        """Get pending orders requiring action"""
        return self.get_orders('pending') + self.get_orders('awaiting')
    
    def create_order(self, order_data: Dict) -> Optional[int]:
        """Create new order"""
        if not self._ensure_connection():
            return None
            
        query = """
            INSERT INTO orders 
            (order_number, buyer_id, buyer_role, seller_id, seller_role,
             items, subtotal, tax, shipping, total, status, payment_status,
             shipping_address, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            order_data['order_number'],
            order_data['buyer_id'],
            order_data['buyer_role'],
            self.producer_id,
            'producer',
            json.dumps(order_data['items']),
            order_data['subtotal'],
            order_data.get('tax', 0),
            order_data.get('shipping', 0),
            order_data['total'],
            order_data.get('status', 'pending'),
            order_data.get('payment_status', 'pending'),
            json.dumps(order_data.get('shipping_address', {})),
            order_data.get('notes', '')
        )
        return self.db.execute_query(query, params)
    
    def get_merchant_matches(self, category: str = None, radius: int = 100) -> List[Dict]:
        """Get AI-matched merchants (mock implementation)"""
        return [
            {"name": "FoodCo Distributors", "match_score": 95, "distance": 15, "rating": 4.8, "capacity": "1000 units/week"},
            {"name": "FreshChain Inc", "match_score": 87, "distance": 25, "rating": 4.6, "capacity": "800 units/week"},
            {"name": "OrganicMarket", "match_score": 82, "distance": 30, "rating": 4.5, "capacity": "600 units/week"},
        ]
    
    def update_stock(self, sku: str, new_stock: int) -> bool:
        """Update product stock"""
        if not self._ensure_connection():
            return False
            
        query = "UPDATE products SET stock = ? WHERE sku = ? AND producer_id = ?"
        result = self.db.execute_query(query, (new_stock, sku, self.producer_id))
        return result is not None

# Global instance
db = ProducerDB()
