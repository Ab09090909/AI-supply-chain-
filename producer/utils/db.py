"""
Producer-specific database access
Self-contained - no external imports except standard library
"""
import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime

class ProducerDB:
    """Producer-specific database helper"""
    
    def __init__(self):
        self.db_path = "../data/supply_chain.db"
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        except Exception as e:
            print(f"DB connection error: {e}")
            self.conn = None
    
    def get_inventory(self, producer_id: int = 1) -> List[Dict]:
        """Get all inventory items for producer"""
        if not self.conn:
            return self._get_mock_inventory()
        
        try:
            cursor = self.conn.execute(
                "SELECT * FROM products WHERE producer_id = ?",
                (producer_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception:
            return self._get_mock_inventory()
    
    def get_orders(self, producer_id: int = 1, status: str = None) -> List[Dict]:
        """Get orders for producer, optionally filtered by status"""
        if not self.conn:
            return self._get_mock_orders()
        
        try:
            query = "SELECT * FROM orders WHERE user_id = ? AND role = 'producer'"
            params = [producer_id]
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC"
            
            cursor = self.conn.execute(query, params)
            orders = []
            for row in cursor.fetchall():
                order = dict(row)
                # Parse items JSON
                try:
                    order['items'] = json.loads(order['items'])
                except:
                    order['items'] = []
                orders.append(order)
            return orders
        except Exception:
            return self._get_mock_orders()
    
    def get_incoming_orders(self, producer_id: int = 1) -> List[Dict]:
        """Get pending/awaiting orders"""
        return self.get_orders(producer_id, 'pending') + self.get_orders(producer_id, 'awaiting')
    
    def create_order(self, order_data: Dict) -> bool:
        """Create new order"""
        if not self.conn:
            return False
        
        try:
            cursor = self.conn.execute(
                """INSERT INTO orders (order_number, user_id, role, items, total, status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    order_data['order_number'],
                    order_data['user_id'],
                    order_data['role'],
                    json.dumps(order_data['items']),
                    order_data['total'],
                    order_data['status']
                )
            )
            self.conn.commit()
            return cursor.lastrowid > 0
        except Exception:
            return False
    
    def update_inventory(self, sku: str, stock: int) -> bool:
        """Update product stock"""
        if not self.conn:
            return False
        
        try:
            cursor = self.conn.execute(
                "UPDATE products SET stock = ? WHERE sku = ?",
                (stock, sku)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception:
            return False
    
    def _get_mock_inventory(self) -> List[Dict]:
        """Fallback mock inventory"""
        return [
            {"sku": "AGR-001", "name": "Organic Wheat", "category": "Grains", "stock": 450, "min": 100, "price": 4.20},
            {"sku": "AGR-002", "name": "Fresh Dairy Milk", "category": "Dairy", "stock": 35, "min": 50, "price": 3.50},
            {"sku": "AGR-003", "name": "Premium Avocados", "category": "Fruits", "stock": 12, "min": 40, "price": 12.00},
            {"sku": "AGR-004", "name": "Free Range Eggs", "category": "Dairy", "stock": 200, "min": 80, "price": 5.50},
            {"sku": "AGR-005", "name": "Organic Rice", "category": "Grains", "stock": 45, "min": 60, "price": 3.80},
            {"sku": "AGR-006", "name": "Organic Carrots", "category": "Vegetables", "stock": 0, "min": 30, "price": 2.90},
        ]
    
    def _get_mock_orders(self) -> List[Dict]:
        """Fallback mock orders"""
        return [
            {"id": "#PO-001", "merchant": "Metro Retail Inc", "product": "Organic Wheat", "amount": 2400, "status": "Delivered", "date": "2024-01-15"},
            {"id": "#PO-002", "merchant": "Fresh Market Co", "product": "Fresh Dairy", "amount": 1850, "status": "In Transit", "date": "2024-01-16"},
            {"id": "#ORD-2024-0891", "merchant": "Metro Retail Inc", "product": "Organic Wheat (50 tons)", "amount": 12500, "status": "pending", "date": "2024-01-20"},
        ]
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Global instance
db = ProducerDB()
