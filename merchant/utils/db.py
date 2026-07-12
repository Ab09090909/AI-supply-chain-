"""
Merchant Database Access Layer
"""
import json
from typing import List, Dict, Optional

try:
    from database.connection import db
except ImportError:
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
    db = MockDB()

class MerchantDB:
    """Merchant-specific database operations"""
    
    def __init__(self):
        self.merchant_id = 2  # Current merchant ID
    
    def get_available_products(self, category: str = None) -> List[Dict]:
        """Get products available for purchase"""
        if category:
            query = """
                SELECT p.*, u.name as producer_name
                FROM products p
                JOIN users u ON p.producer_id = u.id
                WHERE p.stock > 0 AND p.is_active = 1 AND p.category = ?
                ORDER BY p.price ASC
            """
            params = (category,)
        else:
            query = """
                SELECT p.*, u.name as producer_name
                FROM products p
                JOIN users u ON p.producer_id = u.id
                WHERE p.stock > 0 AND p.is_active = 1
                ORDER BY p.price ASC
            """
            params = ()
        
        results = db.execute_query(query, params, fetch=True)
        return results or []
    
    def get_suppliers(self) -> List[Dict]:
        """Get list of suppliers (producers)"""
        query = """
            SELECT u.id, u.name, u.location, u.is_verified,
                   COUNT(p.id) as product_count,
                   AVG(p.price) as avg_price
            FROM users u
            JOIN products p ON u.id = p.producer_id
            WHERE u.role = 'producer' AND u.is_active = 1
            GROUP BY u.id
            ORDER BY u.name
        """
        return db.execute_query(query, fetch=True) or []
    
    def get_supplier_performance(self, supplier_id: int) -> Dict:
        """Get performance metrics for a supplier"""
        # Order fulfillment rate
        query = """
            SELECT 
                COUNT(*) as total_orders,
                SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered_orders,
                AVG(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as fulfillment_rate
            FROM orders
            WHERE seller_id = ? AND seller_role = 'producer'
        """
        result = db.execute_query(query, (supplier_id,), fetch=True)
        
        if result:
            perf = result[0]
            return {
                "total_orders": perf['total_orders'],
                "delivered": perf['delivered_orders'],
                "fulfillment_rate": round(perf['fulfillment_rate'] * 100, 1) if perf['fulfillment_rate'] else 0
            }
        return {"total_orders": 0, "delivered": 0, "fulfillment_rate": 0}
    
    def place_order(self, order_data: Dict) -> Optional[int]:
        """Place new order"""
        query = """
            INSERT INTO orders 
            (order_number, buyer_id, buyer_role, seller_id, seller_role,
             items, subtotal, tax, shipping, total, status, payment_status,
             shipping_address, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            order_data['order_number'],
            self.merchant_id,
            'merchant',
            order_data['seller_id'],
            'producer',
            json.dumps(order_data['items']),
            order_data['subtotal'],
            order_data.get('tax', 0),
            order_data.get('shipping', 0),
            order_data['total'],
            'pending',
            'pending',
            json.dumps(order_data.get('shipping_address', {})),
            order_data.get('notes', '')
        )
        return db.execute_query(query, params)
    
    def get_order_history(self, status: str = None) -> List[Dict]:
        """Get merchant's order history"""
        if status:
            query = """
                SELECT o.*, u.name as producer_name
                FROM orders o
                JOIN users u ON o.seller_id = u.id
                WHERE o.buyer_id = ? AND o.buyer_role = 'merchant' AND o.status = ?
                ORDER BY o.created_at DESC
            """
            params = (self.merchant_id, status)
        else:
            query = """
                SELECT o.*, u.name as producer_name
                FROM orders o
                JOIN users u ON o.seller_id = u.id
                WHERE o.buyer_id = ? AND o.buyer_role = 'merchant'
                ORDER BY o.created_at DESC
            """
            params = (self.merchant_id,)
        
        results = db.execute_query(query, params, fetch=True)
        
        for order in results or []:
            if order.get('items'):
                order['items'] = json.loads(order['items'])
        
        return results or []
    
    def add_to_favorites(self, product_id: int) -> bool:
        """Add product to favorites"""
        query = "INSERT OR IGNORE INTO favorites (user_id, product_id) VALUES (?, ?)"
        result = db.execute_query(query, (self.merchant_id, product_id))
        return result is not None
    
    def get_cart_items(self) -> List[Dict]:
        """Get shopping cart items"""
        query = """
            SELECT c.*, p.name, p.price, p.unit, p.stock, u.name as producer_name
            FROM cart_items c
            JOIN products p ON c.product_id = p.id
            JOIN users u ON p.producer_id = u.id
            WHERE c.user_id = ?
        """
        return db.execute_query(query, (self.merchant_id,), fetch=True) or []
    
    def add_to_cart(self, product_id: int, quantity: int = 1) -> bool:
        """Add item to cart"""
        query = """
            INSERT OR REPLACE INTO cart_items (user_id, product_id, quantity, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """
        result = db.execute_query(query, (self.merchant_id, product_id, quantity))
        return result is not None

# Global instance
merchant_db = MerchantDB()
