"""
Customer Database Access Layer
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

class CustomerDB:
    """Customer-specific database operations"""
    
    def __init__(self):
        self.customer_id = 3  # Current customer ID
    
    def get_favorites(self) -> List[Dict]:
        """Get customer's favorite products"""
        query = """
            SELECT f.*, p.name, p.price, p.unit, p.stock, u.name as producer_name
            FROM favorites f
            JOIN products p ON f.product_id = p.id
            JOIN users u ON p.producer_id = u.id
            WHERE f.user_id = ?
            ORDER BY f.created_at DESC
        """
        results = db.execute_query(query, (self.customer_id,), fetch=True)
        return results or []
    
    def add_favorite(self, product_id: int) -> bool:
        """Add product to favorites"""
        query = "INSERT OR IGNORE INTO favorites (user_id, product_id) VALUES (?, ?)"
        result = db.execute_query(query, (self.customer_id, product_id))
        return result is not None
    
    def remove_favorite(self, product_id: int) -> bool:
        """Remove product from favorites"""
        query = "DELETE FROM favorites WHERE user_id = ? AND product_id = ?"
        result = db.execute_query(query, (self.customer_id, product_id))
        return result is not None and result > 0
    
    def get_cart(self) -> List[Dict]:
        """Get shopping cart"""
        query = """
            SELECT c.*, p.name, p.price, p.unit, p.stock, p.sku, u.name as producer_name
            FROM cart_items c
            JOIN products p ON c.product_id = p.id
            JOIN users u ON p.producer_id = u.id
            WHERE c.user_id = ?
            ORDER BY c.created_at DESC
        """
        results = db.execute_query(query, (self.customer_id,), fetch=True)
        return results or []
    
    def add_to_cart(self, product_id: int, quantity: int = 1) -> bool:
        """Add item to cart"""
        query = """
            INSERT OR REPLACE INTO cart_items (user_id, product_id, quantity, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """
        result = db.execute_query(query, (self.customer_id, product_id, quantity))
        return result is not None
    
    def remove_from_cart(self, product_id: int) -> bool:
        """Remove item from cart"""
        query = "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?"
        result = db.execute_query(query, (self.customer_id, product_id))
        return result is not None and result > 0
    
    def get_recommendations(self) -> List[Dict]:
        """Get personalized recommendations"""
        # In production, this would use ML model
        query = """
            SELECT p.*, u.name as producer_name
            FROM products p
            JOIN users u ON p.producer_id = u.id
            WHERE p.is_active = 1 AND p.stock > 0
            ORDER BY RANDOM()
            LIMIT 6
        """
        results = db.execute_query(query, fetch=True)
        return results or []
    
    def get_purchase_history(self) -> List[Dict]:
        """Get customer's order history"""
        query = """
            SELECT o.*, u.name as producer_name
            FROM orders o
            JOIN users u ON o.seller_id = u.id
            WHERE o.buyer_id = ? AND o.buyer_role = 'customer'
            ORDER BY o.created_at DESC
        """
        results = db.execute_query(query, (self.customer_id,), fetch=True)
        
        for order in results or []:
            if order.get('items'):
                order['items'] = json.loads(order['items'])
        
        return results or []
    
    def place_order(self, cart_items: List[Dict], shipping_address: Dict) -> Optional[int]:
        """Place order from cart"""
        # Generate order number
        order_number = f"ORD-CUST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate totals
        subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
        total = subtotal  # Add tax/shipping in production
        
        # Create order
        query = """
            INSERT INTO orders 
            (order_number, buyer_id, buyer_role, seller_id, seller_role,
             items, subtotal, total, status, payment_status, shipping_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # For simplicity, use first seller (in production, multiple sellers)
        seller_id = cart_items[0].get('seller_id', 1)
        
        params = (
            order_number,
            self.customer_id,
            'customer',
            seller_id,
            'producer',
            json.dumps(cart_items),
            subtotal,
            total,
            'pending',
            'pending',
            json.dumps(shipping_address)
        )
        
        order_id = db.execute_query(query, params)
        
        if order_id:
            # Clear cart
            for item in cart_items:
                db.execute_query(
                    "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?",
                    (self.customer_id, item.get('product_id'))
                )
        
        return order_id

# Global instance
customer_db = CustomerDB()
