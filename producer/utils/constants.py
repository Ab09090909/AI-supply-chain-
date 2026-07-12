"""
Producer-specific constants
NO shared imports allowed
"""
import os

# Producer info
PRODUCER_NAME = "Green Valley Farms"
PRODUCER_ID = 1
PRODUCER_EMAIL = "producer@demo.com"

# Navigation tabs
TABS = {
    "dashboard": "📊 Dashboard",
    "inventory": "📦 Inventory",
    "marketplace": "🤝 Merchant Matching",
    "ai_insights": "💡 AI Insights",
    "settings": "⚙️ Settings"
}

# Color scheme
COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17becf"
}

# Thresholds
REORDER_THRESHOLD = 1.2  # 120% of min stock
FRAUD_THRESHOLD = 0.7
