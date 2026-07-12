"""
Producer Helper Functions
"""
from datetime import datetime, timedelta
import random
import json

def generate_order_number(prefix: str = "PO") -> str:
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{timestamp}"

def format_currency(amount: float, currency: str = "$") -> str:
    """Format amount as currency string"""
    return f"{currency}{amount:,.2f}"

def format_date(date_str: str) -> str:
    """Format date string for display"""
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%b %d, %Y")
    except:
        return date_str

def get_time_ago(date_str: str) -> str:
    """Get human-readable time ago"""
    if not date_str:
        return "Unknown"
    
    try:
        dt = datetime.fromisoformat(date_str)
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    except:
        return date_str

def get_stock_status(stock: int, min_stock: int) -> tuple[str, str]:
    """Get stock status and emoji"""
    if stock == 0:
        return "Critical", "🔴"
    elif stock <= min_stock * 1.2:
        return "Low", "🟡"
    else:
        return "Good", "🟢"

def get_status_badge(status: str) -> str:
    """Get HTML badge for order status"""
    badges = {
        'pending': '<span class="badge badge-warning">Pending</span>',
        'confirmed': '<span class="badge badge-info">Confirmed</span>',
        'processing': '<span class="badge badge-info">Processing</span>',
        'shipped': '<span class="badge badge-info">Shipped</span>',
        'delivered': '<span class="badge badge-success">Delivered</span>',
        'cancelled': '<span class="badge badge-danger">Cancelled</span>',
        'flagged': '<span class="badge badge-danger">Flagged</span>',
        'refunded': '<span class="badge badge-secondary">Refunded</span>',
    }
    return badges.get(status.lower(), f'<span class="badge">{status}</span>')

def generate_mock_time_series(days: int = 30, base: float = 100, variance: float = 20):
    """Generate mock time series data for charts"""
    from datetime import datetime, timedelta
    dates = [datetime.now() - timedelta(days=x) for x in range(days, 0, -1)]
    values = [base + (x * 0.5) + random.uniform(-variance, variance) for x in range(days)]
    return dates, values

def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
