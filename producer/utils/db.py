"""
Producer Database Access Layer
"""
import json
from typing import List, Dict, Optional
from datetime import datetime

# Import shared database connection
try:
    from database.connection import db as shared_db
except ImportError:
    # Fallback for standalone testing
    import sqlite3
    class MockDB:
        def execute_query(self, query, params=None, fetch=False):
            conn = sqlite3.connect("data/supply_chain.db")
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
    shared_db = MockDB()

class ProducerDB:
    """Producer-specific database operations"""
    
    def __init__(self):
        self.producer_id = 1  # Current producer ID (would come from session)
        self.db = shared_db  # Use shared connection
    
    def get_inventory(self) -> List[Dict]:
        """Get all inventory items for current producer"""
        query = """
            SELECT id, sku, name, description, category, price, stock, unit,
                   reorder_point, reorder_quantity, is_active, created_at
            FROM products 
            WHERE producer_id = ? AND is_active = 1
            ORDER BY category, name
        """
        results = self.db.execute_query(query, (self.producer_id,), fetch=True)
        return results if results else []
    
    def get_inventory_by_category(self, category: str) -> List[Dict]:
        """Get inventory filtered by category"""
        query = """
            SELECT * FROM products 
            WHERE producer_id = ? AND category = ? AND is_active = 1
            ORDER BY name
        """
        return self.db.execute_query(query, (self.producer_id, category), fetch=True) or []
    
    def get_low_stock_items(self) -> List[Dict]:
        """Get items below reorder point"""
        query = """
            SELECT * FROM products 
            WHERE producer_id = ? 
            AND stock <= reorder_point 
            AND is_active = 1
            ORDER BY stock ASC
        """
        return self.db.execute_query(query, (self.producer_id,), fetch=True) or []
    
    def get_product_by_sku(self, sku: str) -> Optional[Dict]:
        """Get single product by SKU"""
        query = "SELECT * FROM products WHERE sku = ? AND producer_id = ?"
        results = self.db.execute_query(query, (sku, self.producer_id), fetch=True)
        return results[0] if results else None
    
    def add_product(self, product_data: Dict) -> bool:
        """Add new product"""
        query = """
            INSERT INTO products 
            (sku, name, description, category, price, stock, unit, 
             reorder_point, reorder_quantity, producer_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            product_data['sku'],
            product_data['name'],
            product_data.get('description', ''),
            product_data['category'],
            product_data['price'],
            product_data.get('stock', 0),
            product_data['unit'],
            product_data.get('reorder_point', 10),
            product_data.get('reorder_quantity', 50),
            self.producer_id
        )
        result = self.db.execute_query(query, params)
        return result is not None
    
    def update_stock(self, sku: str, new_stock: int) -> bool:
        """Update product stock"""
        query = "UPDATE products SET stock = ? WHERE sku = ? AND producer_id = ?"
        result = self.db.execute_query(query, (new_stock, sku, self.producer_id))
        return result is not None
    
    def get_orders(self, status: str = None) -> List[Dict]:
        """Get orders for current producer"""
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
                order['items'] = json.loads(order['items'])
            if order.get('shipping_address'):
                order['shipping_address'] = json.loads(order['shipping_address'])
        
        return results or []
    
    def get_pending_orders(self) -> List[Dict]:
        """Get pending orders requiring action"""
        return self.get_orders('pending') + self.get_orders('awaiting')
    
    def create_order(self, order_data: Dict) -> Optional[int]:
        """Create new order"""
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
        mock_matches = [
            {"name": "FoodCo Distributors", "match_score": 95, "distance": 15, "rating": 4.8, "capacity": "1000 units/week"},
            {"name": "FreshChain Inc", "match_score": 87, "distance": 25, "rating": 4.6, "capacity": "800 units/week"},
            {"name": "OrganicMarket", "match_score": 82, "distance": 30, "rating": 4.5, "capacity": "600 units/week"},
        ]
        return mock_matches
    
    def get_price_forecast(self, product_id: int, days: int = 30) -> Dict:
        """Get AI price forecast"""
        return {
            "product_id": product_id,
            "forecast_days": days,
            "current_price": 4.20,
            "predicted_prices": [4.20 + (i * 0.02) for i in range(days)],
            "confidence": 0.85,
            "recommendation": "Hold"
        }
    
    def get_demand_forecast(self, category: str, days: int = 7) -> Dict:
        """Get AI demand forecast"""
        return {
            "category": category,
            "forecast_days": days,
            "current_demand": 65,
            "predicted_demand": [65 + (i * 2) for i in range(days)],
            "confidence": 0.82,
            "alert": None
        }

# Global instance - this is what should be imported
db = ProducerDB()
