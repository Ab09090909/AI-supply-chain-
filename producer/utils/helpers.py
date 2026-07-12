"""
Producer-specific helper functions
"""
from datetime import datetime, timedelta
import random

def generate_order_number(prefix: str = "PO") -> str:
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{timestamp}"

def get_status_color(status: str) -> str:
    """Get color for order status"""
    status_colors = {
        "delivered": "#28a745",
        "completed": "#28a745",
        "in transit": "#17becf",
        "processing": "#ffc107",
        "pending": "#ffc107",
        "flagged": "#dc3545",
        "cancelled": "#dc3545"
    }
    return status_colors.get(status.lower(), "#666666")

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"

def get_stock_status(stock: int, min_stock: int) -> tuple:
    """Get stock status and emoji"""
    if stock == 0:
        return "Critical", "🔴"
    elif stock <= min_stock * 1.2:
        return "Low", "🟡"
    else:
        return "Good", "🟢"

def generate_mock_chart_data(days: int = 30, base: float = 100, variance: float = 20):
    """Generate mock time series data"""
    dates = [datetime.now() - timedelta(days=x) for x in range(days, 0, -1)]
    values = [base + (x * 0.5) + random.uniform(-variance, variance) for x in range(days)]
    return dates, values
