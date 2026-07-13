"""
Producer Helper Functions - Formatting, badges, utilities
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
    if amount is None:
        return f"{currency}0.00"
    return f"{currency}{amount:,.2f}"


def format_date(date_str: str) -> str:
    """Format date string for display"""
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%b %d, %Y")
    except Exception:
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
    except Exception:
        return date_str


def get_stock_status(current_stock: int, min_stock: int, max_stock: int) -> str:
    """Returns the stock status based on current, min, and max thresholds."""
    if current_stock <= 0:
        return "Out of Stock"
    elif current_stock < min_stock:
        return "Low Stock"
    elif current_stock > max_stock:
        return "Overstocked"
    else:
        return "In Stock"


def get_status_color(status: str) -> str:
    """Get color code for status indicator"""
    status_colors = {
        "on_track": "#10b981",
        "at_risk": "#f59e0b",
        "delayed": "#ef4444",
        "pending": "#667eea",
        "processing": "#3b82f6",
        "shipped": "#fbbf24",
        "delivered": "#10b981",
        "cancelled": "#ef4444",
        "confirmed": "#3b82f6",
        "active": "#10b981",
        "expired": "#ef4444",
        "flagged": "#f43f5e",
    }
    return status_colors.get(status.lower(), "#94a3b8")
