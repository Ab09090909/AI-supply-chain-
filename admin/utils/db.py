"""
Admin Database Access Layer
"""
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta

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

class AdminDB:
    """Admin-specific database operations"""
    
    def get_system_stats(self) -> Dict:
        """Get system-wide statistics"""
        stats = {}
        
        # User counts
        query = "SELECT role, COUNT(*) as count FROM users WHERE is_active = 1 GROUP BY role"
        results = db.execute_query(query, fetch=True)
        if results:
            for row in results:
                stats[row['role']] = row['count']
        
        # Order stats
        query = "SELECT COUNT(*) as total, SUM(total) as revenue FROM orders"
        result = db.execute_query(query, fetch=True)
        if result:
            stats['total_orders'] = result[0]['total']
            stats['total_revenue'] = result[0]['revenue'] or 0
        
        # Fraud alerts
        query = "SELECT COUNT(*) as count FROM fraud_logs WHERE status = 'pending'"
        result = db.execute_query(query, fetch=True)
        if result:
            stats['fraud_alerts'] = result[0]['count']
        
        # System health
        stats['system_health'] = 98.5
        stats['uptime'] = '99.98%'
        
        return stats
    
    def get_all_users(self, role: str = None, limit: int = 100) -> List[Dict]:
        """Get all users with optional role filter"""
        if role:
            query = """
                SELECT id, email, name, role, is_active, is_verified, created_at, last_login
                FROM users
                WHERE role = ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            params = (role, limit)
        else:
            query = """
                SELECT id, email, name, role, is_active, is_verified, created_at, last_login
                FROM users
                ORDER BY created_at DESC
                LIMIT ?
            """
            params = (limit,)
        
        return db.execute_query(query, params, fetch=True) or []
    
    def get_user_details(self, user_id: int) -> Optional[Dict]:
        """Get detailed user information"""
        query = "SELECT * FROM users WHERE id = ?"
        results = db.execute_query(query, (user_id,), fetch=True)
        return results[0] if results else None
    
    def toggle_user_status(self, user_id: int, is_active: bool) -> bool:
        """Activate/deactivate user"""
        query = "UPDATE users SET is_active = ? WHERE id = ?"
        result = db.execute_query(query, (1 if is_active else 0, user_id))
        return result is not None
    
    def get_fraud_alerts(self, status: str = None) -> List[Dict]:
        """Get fraud detection alerts"""
        if status:
            query = """
                SELECT f.*, u.name as user_name, u.email as user_email
                FROM fraud_logs f
                JOIN users u ON f.user_id = u.id
                WHERE f.status = ?
                ORDER BY f.created_at DESC
            """
            params = (status,)
        else:
            query = """
                SELECT f.*, u.name as user_name, u.email as user_email
                FROM fraud_logs f
                JOIN users u ON f.user_id = u.id
                ORDER BY f.created_at DESC
            """
            params = ()
        
        results = db.execute_query(query, params, fetch=True)
        
        for alert in results or []:
            if alert.get('transaction_data'):
                alert['transaction_data'] = json.loads(alert['transaction_data'])
            if alert.get('risk_factors'):
                alert['risk_factors'] = json.loads(alert['risk_factors'])
        
        return results or []
    
    def review_fraud_alert(self, alert_id: int, admin_id: int, status: str) -> bool:
        """Review fraud alert"""
        query = """
            UPDATE fraud_logs 
            SET status = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        result = db.execute_query(query, (status, admin_id, alert_id))
        return result is not None
    
    def get_ml_model_performance(self) -> List[Dict]:
        """Get ML model performance metrics"""
        query = """
            SELECT prediction_type, 
                   AVG(confidence) as avg_confidence,
                   COUNT(*) as prediction_count,
                   MAX(created_at) as last_used
            FROM ai_predictions
            GROUP BY prediction_type
            ORDER BY last_used DESC
        """
        results = db.execute_query(query, fetch=True)
        return results or []
    
    def get_all_products(self, category: str = None, limit: int = 100) -> List[Dict]:
        """Get all products in system"""
        if category:
            query = """
                SELECT p.*, u.name as producer_name
                FROM products p
                JOIN users u ON p.producer_id = u.id
                WHERE p.category = ?
                ORDER BY p.created_at DESC
                LIMIT ?
            """
            params = (category, limit)
        else:
            query = """
                SELECT p.*, u.name as producer_name
                FROM products p
                JOIN users u ON p.producer_id = u.id
                ORDER BY p.created_at DESC
                LIMIT ?
            """
            params = (limit,)
        
        return db.execute_query(query, params, fetch=True) or []
    
    def get_all_orders(self, status: str = None, days: int = 30) -> List[Dict]:
        """Get all orders in system"""
        date_filter = datetime.now() - timedelta(days=days)
        
        if status:
            query = """
                SELECT o.*, 
                       u1.name as buyer_name, u2.name as seller_name
                FROM orders o
                JOIN users u1 ON o.buyer_id = u1.id
                JOIN users u2 ON o.seller_id = u2.id
                WHERE o.status = ? AND o.created_at >= ?
                ORDER BY o.created_at DESC
            """
            params = (status, date_filter.isoformat())
        else:
            query = """
                SELECT o.*, 
                       u1.name as buyer_name, u2.name as seller_name
                FROM orders o
                JOIN users u1 ON o.buyer_id = u1.id
                JOIN users u2 ON o.seller_id = u2.id
                WHERE o.created_at >= ?
                ORDER BY o.created_at DESC
            """
            params = (date_filter.isoformat(),)
        
        results = db.execute_query(query, params, fetch=True)
        
        for order in results or []:
            if order.get('items'):
                order['items'] = json.loads(order['items'])
        
        return results or []
    
    def get_system_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent system logs"""
        query = """
            SELECT a.*, u.name as user_name
            FROM audit_logs a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.created_at DESC
            LIMIT ?
        """
        return db.execute_query(query, (limit,), fetch=True) or []
    
    def generate_report(self, report_type: str, parameters: Dict, generated_by: int) -> int:
        """Generate system report"""
        query = """
            INSERT INTO reports (report_type, generated_by, parameters, status)
            VALUES (?, ?, ?, 'generating')
        """
        params = (
            report_type,
            generated_by,
            json.dumps(parameters)
        )
        return db.execute_query(query, params)
    
    def get_analytics_data(self, days: int = 30) -> Dict:
        """Get analytics data for dashboard"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Revenue over time
        query = """
            SELECT DATE(created_at) as date, SUM(total) as revenue, COUNT(*) as orders
            FROM orders
            WHERE created_at BETWEEN ? AND ?
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        revenue_data = db.execute_query(query, (start_date.isoformat(), end_date.isoformat()), fetch=True) or []
        
        # Category distribution
        query = """
            SELECT p.category, COUNT(*) as count, SUM(o.total) as revenue
            FROM orders o
            JOIN products p ON JSON_EXTRACT(o.items, '$[0].sku') = p.sku
            WHERE o.created_at BETWEEN ? AND ?
            GROUP BY p.category
        """
        category_data = db.execute_query(query, (start_date.isoformat(), end_date.isoformat()), fetch=True) or []
        
        # User growth
        query = """
            SELECT DATE(created_at) as date, COUNT(*) as new_users
            FROM users
            WHERE created_at BETWEEN ? AND ?
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        user_growth = db.execute_query(query, (start_date.isoformat(), end_date.isoformat()), fetch=True) or []
        
        return {
            'revenue_data': revenue_data,
            'category_data': category_data,
            'user_growth': user_growth,
            'total_revenue': sum(d['revenue'] for d in revenue_data),
            'total_orders': sum(d['orders'] for d in revenue_data)
        }

# Global instance
admin_db = AdminDB()
