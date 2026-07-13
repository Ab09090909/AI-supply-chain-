"""
Producer Database Module (Supabase Integration)
Production version - NO demo data seeding
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from supabase import create_client, Client
from supabase.exceptions import APIError

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "your-service-role-key")

# -----------------------------------------------------------------------------
# ProducerDB Class
# -----------------------------------------------------------------------------
class ProducerDB:
    def __init__(self):
        """Initialize Supabase client - NO seeding"""
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

    # -------------------------------------------------------------------------
    # Read Operations
    # -------------------------------------------------------------------------
    def get_orders(self, status: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Fetch orders with optional filters"""
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
        """Fetch production projects"""
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
        """Fetch team members"""
        try:
            response = self.supabase.table("team").select("*").order("name", asc=True).execute()
            return response.data
        except APIError as e:
            print(f"Error fetching team: {str(e)}")
            return []

    def get_budget_data(self, project_id: Optional[int] = None) -> Dict:
        """Fetch budget data"""
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
        """Fetch approval requests"""
        try:
            response = self.supabase.table("approvals").select("*").eq("status", status).order("due_date", asc=True).execute()
            return response.data
        except APIError as e:
            print(f"Error fetching approvals: {str(e)}")
            return []

    def get_risks(self, severity: Optional[str] = None, status: str = "open") -> List[Dict]:
        """Fetch risk items"""
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
        """Fetch audit logs"""
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
        """Fetch products needing restock"""
        try:
            response = self.supabase.table("products").select("*").lte("quantity", "reorder_level").order("quantity", asc=True).execute()
            return response.data
        except APIError as e:
            print(f"Error fetching restock alerts: {str(e)}")
            return []

    # -------------------------------------------------------------------------
    # Write Operations (with audit logging)
    # -------------------------------------------------------------------------
    def update_order_status(self, order_id: int, new_status: str, user: str = "System") -> bool:
        """Update order status"""
        try:
            now = datetime.now().isoformat()
            order = self.supabase.table("orders").select("order_number").eq("id", order_id).execute().data[0]
            if not order:
                return False
            
            self.supabase.table("orders").update({
                "status": new_status,
                "updated_at": now
            }).eq("id", order_id).execute()

            self.log_audit(user, "Updated", f"Order #{order['order_number']}", f"Changed status to {new_status}")
            return True
        except APIError as e:
            print(f"Error updating order: {str(e)}")
            return False

    def update_approval_status(self, approval_id: str, new_status: str, user: str = "System") -> bool:
        """Update approval status"""
        try:
            approval = self.supabase.table("approvals").select("type, item, requestor").eq("id", approval_id).execute().data[0]
            if not approval:
                return False
            
            approval_desc = approval["item"] or approval["requestor"] or approval["type"]
            self.supabase.table("approvals").update({"status": new_status}).eq("id", approval_id).execute()
            
            self.log_audit(user, new_status.capitalize(), f"Approval #{approval_id}: {approval['type']}", f"{new_status.capitalize()} {approval_desc}")
            return True
        except APIError as e:
            print(f"Error updating approval: {str(e)}")
            return False

    def add_order(self, order_number: str, buyer_name: str, items: List[Dict], total: float, user: str = "System") -> bool:
        """Add new order"""
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
            self.log_audit(user, "Created", f"Order #{order_number}", f"New order for {buyer_name}, total: ${total:.2f}")
            return True
        except APIError as e:
            print(f"Error adding order: {str(e)}")
            return False

    def add_project(self, name: str, description: str, start_date: str, end_date: str, user: str = "System") -> bool:
        """Add new project"""
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
            self.log_audit(user, "Created", f"Project: {name}", f"New project created, timeline: {start_date} to {end_date}")
            return True
        except APIError as e:
            print(f"Error adding project: {str(e)}")
            return False

    def log_audit(self, user: str, action: str, item: str, details: str):
        """Log audit trail entry"""
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

# Global instance
db = ProducerDB()
