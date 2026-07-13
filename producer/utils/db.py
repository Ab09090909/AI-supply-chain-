"""
Producer Database Module (Supabase Integration)
Drop-in replacement for SQLite version, works with existing dashboard view.py
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from supabase import create_client, Client
from supabase.exceptions import APIError

# -----------------------------------------------------------------------------
# Supabase Configuration (Use environment variables for security!)
# -----------------------------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "your-service-role-key")

# -----------------------------------------------------------------------------
# ProducerDB Class: Supabase-backed data operations
# -----------------------------------------------------------------------------
class ProducerDB:
    def __init__(self):
        """Initialize Supabase client and seed sample data if tables are empty"""
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        self._seed_sample_data_if_empty()

    def _seed_sample_data_if_empty(self):
        """Add test data to empty tables for dashboard demonstration"""
        try:
            # Check if orders table is empty
            orders_count = self.supabase.table("orders").select("id", count="exact").execute()
            if orders_count.count > 0:
                return  # Skip seeding if data exists

            now = datetime.now().isoformat()
            # Seed sample orders
            sample_orders = [
                {"order_number": "ORD-001", "buyer_name": "Acme Corp", "items": [{"name": "Organic Wheat (50lb)"}], "total": 2450.00, "status": "Shipped", "created_at": (datetime.now() - timedelta(days=2)).isoformat(), "updated_at": now},
                {"order_number": "ORD-002", "buyer_name": "Global Foods Inc", "items": [{"name": "PremiumRice (25lb)"}, {"name": "Quinoa (10lb)"}], "total": 1890.50, "status": "Processing", "created_at": (datetime.now() - timedelta(days=1)).isoformat(), "updated_at": now},
                {"order_number": "ORD-003", "buyer_name": "Local Bakery", "items": [{"name": "Almond Flour (10lb)"}], "total": 320.75, "status": "Pending", "created_at": datetime.now().isoformat(), "updated_at": now},
                {"order_number": "ORD-004", "buyer_name": "Restaurant Group", "items": [{"name": "Olive Oil (5gal)"}, {"name": "Balsamic Vinegar (1gal)"}], "total": 1245.00, "status": "Delivered", "created_at": (datetime.now() - timedelta(days=5)).isoformat(), "updated_at": now},
                {"order_number": "ORD-005", "buyer_name": "Grocery Chain", "items": [{"name": "Pasta (20lb)"}, {"name": "Tomato Sauce (case)"}], "total": 678.25, "status": "Pending", "created_at": (datetime.now() - timedelta(hours=4)).isoformat(), "updated_at": now},
            ]
            self.supabase.table("orders").insert(sample_orders).execute()

            # Seed sample projects
            sample_projects = [
                {"name": "Summer Marketing Campaign", "description": "Q3 social media video series", "start_date": (datetime.now() - timedelta(days=5)).isoformat(), "end_date": (datetime.now() + timedelta(days=10)).isoformat(), "progress": 45, "status": "on_track"},
                {"name": "Client X Feature Film", "description": "Documentary production for client X", "start_date": (datetime.now() - timedelta(days=12)).isoformat(), "end_date": (datetime.now() + timedelta(days=8)).isoformat(), "progress": 62, "status": "at_risk"},
                {"name": "Product Launch Video", "description": "New product line launch content", "start_date": (datetime.now() + timedelta(days=2)).isoformat(), "end_date": (datetime.now() + timedelta(days=20)).isoformat(), "progress": 10, "status": "pending"},
                {"name": "Holiday Ad Campaign", "description": "Year-end holiday promotional content", "start_date": (datetime.now() - timedelta(days=1)).isoformat(), "end_date": (datetime.now() + timedelta(days=25)).isoformat(), "progress": 15, "status": "on_track"},
            ]
            self.supabase.table("projects").insert(sample_projects).execute()

            # Seed sample team
            sample_team = [
                {"name": "Alex Johnson", "role": "Director", "utilization": 95, "availability": "Limited", "email": "alex@company.com"},
                {"name": "Sam Carter", "role": "Senior Editor", "utilization": 72, "availability": "Available", "email": "sam@company.com"},
                {"name": "Jordan Lee", "role": "Producer", "utilization": 88, "availability": "Limited", "email": "jordan@company.com"},
                {"name": "Taylor Smith", "role": "Production Coordinator", "utilization": 65, "availability": "Available", "email": "taylor@company.com"},
                {"name": "Morgan Reyes", "role": "Post-Production Lead", "utilization": 92, "availability": "Limited", "email": "morgan@company.com"},
            ]
            self.supabase.table("team").insert(sample_team).execute()

            # Seed sample budget data
            sample_budget = [
                {"category": "Talent", "planned": 120000, "actual": 118000, "project_id": 1},
                {"category": "Equipment", "planned": 85000, "actual": 92000, "project_id": 1},
                {"category": "Locations", "planned": 45000, "actual": 42000, "project_id": 2},
                {"category": "Post-Production", "planned": 70000, "actual": 81000, "project_id": 1},
                {"category": "Marketing", "planned": 30000, "actual": 28000, "project_id": 3},
            ]
            self.supabase.table("budget").insert(sample_budget).execute()

            # Seed sample approvals
            sample_approvals = [
                {"id": "APR-001", "type": "Expense", "amount": 2400.00, "item": None, "requestor": "Line Producer A", "status": "pending", "due_date": (datetime.now() + timedelta(days=1)).isoformat()},
                {"id": "APR-002", "type": "Deliverable", "amount": None, "item": "Feature Cut v3", "requestor": "Post-Production Lead", "status": "pending", "due_date": (datetime.now() + timedelta(days=2)).isoformat()},
                {"id": "APR-003", "type": "Contract", "amount": None, "item": "Location Services Inc", "requestor": "Production Coordinator", "status": "pending", "due_date": (datetime.now() + timedelta(days=3)).isoformat()},
            ]
            self.supabase.table("approvals").insert(sample_approvals).execute()

            # Seed sample risks
            sample_risks = [
                {"title": "Location permit expires in 3 days", "severity": "high", "project": "Summer Campaign Shoot", "status": "open"},
                {"title": "Budget overrun risk: Post-production 15% over estimate", "severity": "medium", "project": "Client X Feature Film", "status": "open"},
                {"title": "2 team members OOO next week", "severity": "low", "project": "All Active Projects", "status": "open"},
            ]
            self.supabase.table("risks").insert(sample_risks).execute()

            # Seed sample audit logs
            sample_logs = [
                {"timestamp": datetime.now().isoformat(), "user": "Alex Johnson", "action": "Updated", "item": "Order #ORD-001", "details": "Changed status from Processing to Shipped"},
                {"timestamp": datetime.now().isoformat(), "user": "Sam Carter", "action": "Approved", "item": "Expense Request #EXP-123", "details": "Approved $2,400 for equipment rental"},
                {"timestamp": datetime.now().isoformat(), "user": "Jordan Lee", "action": "Created", "item": "Project: Summer Campaign", "details": "Added new production milestone: Final Cut Review"},
                {"timestamp": (datetime.now() - timedelta(hours=1)).isoformat(), "user": "Admin", "action": "Modified", "item": "Budget: Client X Feature", "details": "Increased post-production budget by 10%"},
                {"timestamp": (datetime.now() - timedelta(hours=3)).isoformat(), "user": "Taylor Smith", "action": "Created", "item": "Order #ORD-003", "details": "New order from Local Bakery"},
            ]
            self.supabase.table("audit_logs").insert(sample_logs).execute()

            # Seed sample products
            sample_products = [
                {"name": "Organic Wheat (50lb)", "sku": "WHT-50LB", "quantity": 120, "reorder_level": 20, "price": 49.00, "category": "Grains"},
                {"name": "Premium Rice (25lb)", "sku": "RCE-25LB", "quantity": 85, "reorder_level": 15, "price": 32.50, "category": "Grains"},
                {"name": "Almond Flour (10lb)", "sku": "ALM-10LB", "quantity": 12, "reorder_level": 10, "price": 24.99, "category": "Baking"},
                {"name": "Olive Oil (5gal)", "sku": "OLV-5GAL", "quantity": 8, "reorder_level": 5, "price": 89.95, "category": "Oils"},
                {"name": "Pasta (20lb)", "sku": "PST-20LB", "quantity": 45, "reorder_level": 15, "price": 18.75, "category": "Grains"},
            ]
            self.supabase.table("products").insert(sample_products).execute()

            print("Sample data seeded to Supabase successfully")
        except APIError as e:
            print(f"Error seeding sample data: {str(e)}")

    # -------------------------------------------------------------------------
    # Core Dashboard Methods (100% compatible with existing view.py)
    # -------------------------------------------------------------------------
    def get_orders(self, status: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Fetch orders with optional filters for status and date range"""
        try:
            query = self.supabase.table("orders").select("*")
            
            if status:
                query = query.eq("status", status)
            if start_date:
                query = query.gte("created_at", start_date)
            if end_date:
                query = query.lte("created_at", end_date)
            
            response = query.order("created_at", desc=True).execute()
            return response.data
        except APIError as e:
            print(f"Error fetching orders: {str(e)}")
            return []

    def get_projects(self, status: Optional[str] = None) -> List[Dict]:
        """Fetch all production projects with optional status filter"""
        try:
            query = self.supabase.table("projects").select("*")
            if status:
                query = query.eq("status", status)
            
            response = query.order("start_date", asc=True).execute()
            return response.data
        except APIError as e:
            print(f"Error fetching projects: {str(e)}")
            return []

    def get_team(self) -> List[Dict]:
        """Fetch all team members with utilization and availability"""
        try:
            response = self.supabase.table("team").select("*").order("name", asc=True).execute()
            return response.data
        except APIError as e:
            print(f"Error fetching team: {str(e)}")
            return []

    def get_budget_data(self, project_id: Optional[int] = None) -> Dict:
        """Fetch budget planned vs actual data, optionally filtered by project"""
        try:
            query = self.supabase.table("budget").select("category, planned, actual")
            if project_id:
                query = query.eq("project_id", project_id)
            
            response = query.execute()
            rows = response.data
            
            return {
                "categories": [row["category"] for row in rows],
                "planned": [float(row["planned"]) for row in rows],
                "actual": [float(row["actual"]) for row in rows]
            }
        except APIError as e:
            print(f"Error fetching budget data: {str(e)}")
            return {"categories": [], "planned": [], "actual": []}

    def get_approvals(self, status: str = "pending") -> List[Dict]:
        """Fetch approval requests filtered by status (default: pending)"""
        try:
            response = self.supabase.table("approvals").select("*").eq("status", status).order("due_date", asc=True).execute()
            return response.data
        except APIError as e:
            print(f"Error fetching approvals: {str(e)}")
            return []

    def get_risks(self, severity: Optional[str] = None, status: str = "open") -> List[Dict]:
        """Fetch active project risks, optionally filtered by severity"""
        try:
            query = self.supabase.table("risks").select("*").eq("status", status)
            if severity:
                query = query.eq("severity", severity)
            
            response = query.execute()
            return response.data
        except APIError as e:
            print(f"Error fetching risks: {str(e)}")
            return []

    def get_audit_logs(self, limit: int = 50, user: Optional[str] = None) -> List[Dict]:
        """Fetch recent audit logs, optionally filtered by user"""
        try:
            query = self.supabase.table("audit_logs").select("*")
            if user:
                query = query.eq("user", user)
            
            response = query.order("timestamp", desc=True).limit(limit).execute()
            return response.data
        except APIError as e:
            print(f"Error fetching audit logs: {str(e)}")
            return []

    def get_products_below_reorder(self) -> List[Dict]:
        """Fetch products with stock below reorder level for restock alerts"""
        try:
            response = self.supabase.table("products").select("*").lte("quantity", "reorder_level").order("quantity", asc=True).execute()
            return response.data
        except APIError as e:
            print(f"Error fetching restock alerts: {str(e)}")
            return []

    # -------------------------------------------------------------------------
    # Data Modification Methods (with automatic audit logging)
    # -------------------------------------------------------------------------
    def update_order_status(self, order_id: int, new_status: str, user: str = "System") -> bool:
        """Update order status and log change to audit trail"""
        try:
            now = datetime.now().isoformat()
            # Get order number for audit log
            order = self.supabase.table("orders").select("order_number").eq("id", order_id).execute().data[0]
            if not order:
                return False

            # Update order
            self.supabase.table("orders").update({
                "status": new_status,
                "updated_at": now
            }).eq("id", order_id).execute()

            # Log change
            self.log_audit(
                user=user,
                action="Updated",
                item=f"Order #{order['order_number']}",
                details=f"Changed status to {new_status}"
            )
            return True
        except APIError as e:
            print(f"Error updating order status: {str(e)}")
            return False

    def update_approval_status(self, approval_id: str, new_status: str, user: str = "System") -> bool:
        """Update approval status and log change to audit trail"""
        try:
            # Get approval details for audit log
            approval = self.supabase.table("approvals").select("type, item, requestor").eq("id", approval_id).execute().data[0]
            if not approval:
                return False
            approval_desc = approval["item"] or approval["requestor"] or approval["type"]

            # Update approval
            self.supabase.table("approvals").update({
                "status": new_status
            }).eq("id", approval_id).execute()

            # Log change
            self.log_audit(
                user=user,
                action=new_status.capitalize(),
                item=f"Approval #{approval_id}: {approval['type']}",
                details=f"{new_status.capitalize()} {approval_desc}"
            )
            return True
        except APIError as e:
            print(f"Error updating approval status: {str(e)}")
            return False

    def add_order(self, order_number: str, buyer_name: str, items: List[Dict], total: float, user: str = "System") -> bool:
        """Add a new order and log to audit trail"""
        try:
            now = datetime.now().isoformat()
            self.supabase.table("orders").insert({
                "order_number": order_number,
                "buyer_name": buyer_name,
                "items": items,
                "total": total,
                "status": "Pending",
                "created_at": now,
                "updated_at": now
            }).execute()

            self.log_audit(
                user=user,
                action="Created",
                item=f"Order #{order_number}",
                details=f"New order for {buyer_name}, total: ${total:.2f}"
            )
            return True
        except APIError as e:
            print(f"Error adding order: {str(e)}")
            return False

    def add_project(self, name: str, description: str, start_date: str, end_date: str, user: str = "System") -> bool:
        """Add a new production project and log to audit trail"""
        try:
            now = datetime.now().isoformat()
            self.supabase.table("projects").insert({
                "name": name,
                "description": description,
                "start_date": start_date,
                "end_date": end_date,
                "status": "pending",
                "created_at": now
            }).execute()

            self.log_audit(
                user=user,
                action="Created",
                item=f"Project: {name}",
                details=f"New project created, timeline: {start_date} to {end_date}"
            )
            return True
        except APIError as e:
            print(f"Error adding project: {str(e)}")
            return False

    def log_audit(self, user: str, action: str, item: str, details: str):
        """Log a change to the Supabase audit trail (called automatically for all data modifications)"""
        try:
            now = datetime.now().isoformat()
            self.supabase.table("audit_logs").insert({
                "timestamp": now,
                "user": user,
                "action": action,
                "item": item,
                "details": details,
                "created_at": now
            }).execute()
        except APIError as e:
            print(f"Error logging audit: {str(e)}")

# -----------------------------------------------------------------------------
# Global DB Instance (drop-in replacement for old SQLite version)
# -----------------------------------------------------------------------------
db = ProducerDB()
