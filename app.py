"""
AI Supply Chain Platform - Login & Producer Portal
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import json
from pathlib import Path

# Page config
st.set_page_config(
    page_title="AI Supply Chain Platform",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============ DATABASE FUNCTIONS ============

def get_db_connection():
    """Get SQLite database connection"""
    db_path = Path(__file__).parent / "data" / "supply_chain.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_inventory_from_db():
    """Get inventory from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, u.name as producer_name 
            FROM products p
            JOIN users u ON p.producer_id = u.id
            WHERE p.producer_id = 1 AND p.is_active = 1
        """)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    except Exception as e:
        print(f"DB Error: {e}")
        return []

def get_orders_from_db():
    """Get orders from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.*, u.name as buyer_name
            FROM orders o
            JOIN users u ON o.buyer_id = u.id
            WHERE o.seller_id = 1 AND o.seller_role = 'producer'
            ORDER BY o.created_at DESC
        """)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Parse JSON fields
        for order in results:
            if order.get('items'):
                order['items'] = json.loads(order['items'])
        
        return results
    except Exception as e:
        print(f"DB Error: {e}")
        return []

# ============ LOGIN PAGE ============

def login_page():
    """Simple login page"""
    st.title("🔗 AI Supply Chain Platform")
    st.markdown("### Multi-Enterprise Supply Chain Intelligence")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("---")
            
            st.subheader("Select Portal")
            role = st.radio(
                "Choose your role",
                ["Producer", "Merchant", "Customer", "Admin"],
                format_func=lambda x: {
                    "Producer": "🌾 Producer Portal",
                    "Merchant": "🛒 Merchant Portal",
                    "Customer": "🛍️ Customer Store",
                    "Admin": "⚙️ Admin Console"
                }[x],
                label_visibility="collapsed",
                index=0
            )
            
            st.markdown("---")
            
            with st.form("login_form"):
                st.text_input("Email", value="producer@demo.com", placeholder="Enter your email")
                st.text_input("Password", value="password", type="password", placeholder="Enter your password")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    submit = st.form_submit_button("Login", use_container_width=True, type="primary")
                with col_b:
                    demo = st.form_submit_button("Demo Mode", use_container_width=True)
                
                if submit or demo:
                    st.session_state.logged_in = True
                    st.session_state.role = role.lower()
                    st.rerun()

# ============ PRODUCER PORTAL ============

def producer_portal():
    """Producer portal with WORKING SIDEBAR"""
    
    # ============ ENTIRE SIDEBAR CONTEXT IS HERE ============
    with st.sidebar:
        # Profile Header
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="
                width: 80px; 
                height: 80px; 
                background: linear-gradient(135deg, #667eea, #764ba2); 
                border-radius: 50%; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                color: white; 
                font-weight: bold; 
                font-size: 32px;
                margin: 0 auto;
            ">👨‍🌾</div>
            <h2 style='margin: 1rem 0 0 0; font-size: 1.2rem;'>Green Valley Farms</h2>
            <p style='color: #666; font-size: 0.9rem; margin: 0;'>Producer Portal</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.subheader("Navigation")
        page = st.radio(
            "Go to",
            ["Dashboard", "Inventory", "Orders", "Marketplace", "Settings"],
            label_visibility="collapsed",
            key="producer_nav"
        )
        
        st.markdown("---")
        
        # Quick Stats
        st.subheader("Quick Stats")
        st.metric("Active Orders", "24", "+3 today")
        st.metric("Revenue", "$45.2K", "+5.3%")
        
        st.markdown("---")
        
        # AI Assistant toggle
        show_ai = st.checkbox("🤖 AI Assistant", value=False)
        st.session_state.show_ai = show_ai
        
        st.markdown("---")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.rerun()
    # ============ END SIDEBAR ============
    
    # Main content based on selection
    if page == "Dashboard":
        show_dashboard()
    elif page == "Inventory":
        show_inventory()
    elif page == "Orders":
        show_orders()
    elif page == "Marketplace":
        show_marketplace()
    elif page == "Settings":
        show_settings()
    
    # AI Assistant
    if st.session_state.get("show_ai", False):
        with st.expander("🤖 AI Assistant", expanded=True):
            st.write("Ask me anything about your supply chain...")
            user_input = st.text_input("Your question:", key="ai_input")
            if user_input:
                st.write(f"**AI:** I received '{user_input}'. This is a demo response.")

def show_dashboard():
    """Producer Dashboard with REAL database data"""
    st.title("📊 Producer Dashboard")
    st.caption("Welcome back! Here's your supply chain overview.")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        orders = get_orders_from_db()
        st.metric(label="Active Orders", value=str(len(orders)), delta="+3 today")
    
    with col2:
        inventory = get_inventory_from_db()
        st.metric(label="Inventory Items", value=str(len(inventory)))
    
    with col3:
        st.metric(label="Avg Price", value="$4.85", delta="+2.1%")
    
    with col4:
        st.metric(label="Risk Score", value="12%", delta="-3%", delta_color="inverse")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Yield Performance (30 Days)")
        dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
        values = [100 + x * 0.5 + (x % 5) * 2 for x in range(30)]
        
        df = pd.DataFrame({"Date": dates, "Yield (tons)": values})
        fig = px.line(df, x="Date", y="Yield (tons)", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Quality Index")
        quality_data = pd.DataFrame({
            "Metric": ["Purity", "Moisture", "Protein", "Appearance"],
            "Score": [98, 95, 96, 97]
        })
        fig = px.bar(quality_data, x="Score", y="Metric", orientation="h", 
                     color="Score", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent Orders from database
    st.subheader("📋 Recent Orders")
    
    if orders:
        for order in orders[:3]:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    order_num = order.get('order_number', f"#{order.get('id', 'N/A')}")
                    st.write(f"**{order_num}**")
                with col2:
                    st.write(order.get('buyer_name', 'Unknown'))
                with col3:
                    items = order.get('items', [])
                    item_name = items[0].get('name', 'N/A') if items else 'N/A'
                    st.write(item_name)
                with col4:
                    st.write(f"${order.get('total', 0):,.2f}")
                with col5:
                    status = order.get('status', 'Unknown')
                    if status == "delivered":
                        st.success(status)
                    elif status == "processing":
                        st.info(status)
                    else:
                        st.warning(status)
                st.markdown("---")
    else:
        st.info("No orders yet")

def show_inventory():
    """Producer Inventory with REAL database data"""
    st.title("📦 Inventory Management")
    st.caption("Track stock levels and manage products")
    
    # Get real inventory from database
    inventory = get_inventory_from_db()
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total SKUs", str(len(inventory)))
    with col2:
        total_value = sum(item.get('stock', 0) * item.get('price', 0) for item in inventory)
        st.metric("Stock Value", f"${total_value:,.2f}")
    with col3:
        low_stock = sum(1 for item in inventory if 0 < item.get('stock', 0) <= item.get('reorder_point', 0) * 1.2)
        st.metric("Low Stock", str(low_stock), delta_color="inverse")
    with col4:
        out_of_stock = sum(1 for item in inventory if item.get('stock', 0) == 0)
        st.metric("Out of Stock", str(out_of_stock), delta_color="inverse")
    
    st.markdown("---")
    
    # Inventory table
    if inventory:
        df_data = []
        for item in inventory:
            stock = item.get('stock', 0)
            min_stock = item.get('reorder_point', 0)
            
            if stock == 0:
                status = "🔴 Critical"
            elif stock <= min_stock * 1.2:
                status = "🟡 Low"
            else:
                status = "🟢 Good"
            
            df_data.append({
                "SKU": item.get('sku', ''),
                "Product": item.get('name', ''),
                "Category": item.get('category', ''),
                "Stock": f"{stock} {item.get('unit', 'units')}",
                "Min Level": min_stock,
                "Status": status,
                "Price": f"${item.get('price', 0):.2f}",
                "Value": f"${stock * item.get('price', 0):.2f}"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("No inventory items found")
    
    st.markdown("---")
    
    # Actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add Product", use_container_width=True, type="primary"):
            st.success("Add product form would open here")
    with col2:
        if st.button("📦 Generate Restock Report"):
            low_items = [item for item in inventory if item.get('stock', 0) <= item.get('reorder_point', 0) * 1.2]
            if low_items:
                st.warning(f"Restock needed for {len(low_items)} items:")
                for item in low_items:
                    st.write(f"- {item.get('name')}: Current {item.get('stock')}, Min {item.get('reorder_point')}")
            else:
                st.success("All stock levels healthy!")
    with col3:
        if st.button("📥 Export CSV"):
            st.success("Inventory exported to CSV")

def show_orders():
    """Producer Orders & Agreements"""
    st.title("📋 Orders & Agreements")
    st.caption("Manage incoming orders and contracts")
    
    # Get orders from database
    orders = get_orders_from_db()
    
    # Tabs
    tab1, tab2 = st.tabs(["📥 Received Orders", "📄 Agreement Preview"])
    
    with tab1:
        st.subheader("Incoming Order Requests")
        
        if orders:
            for order in orders:
                with st.container():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        order_num = order.get('order_number', f"#{order.get('id')}")
                        st.write(f"**{order_num}**")
                        st.caption(order.get('buyer_name', 'Unknown'))
                    with col2:
                        items = order.get('items', [])
                        item_name = items[0].get('name', 'N/A') if items else 'N/A'
                        qty = items[0].get('qty', '') if items else ''
                        st.write(f"{item_name} ({qty})")
                    with col3:
                        st.write(f"${order.get('total', 0):,.2f}")
                    with col4:
                        status = order.get('status', 'pending')
                        if status == 'delivered':
                            st.success("Delivered")
                        elif status == 'processing':
                            st.info("Processing")
                        elif status == 'pending':
                            st.warning("Pending")
                        else:
                            st.write(status)
                    
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    with btn_col1:
                        if st.button("📄 Review", key=f"agree_{order['id']}"):
                            st.session_state.show_agreement = True
                    with btn_col2:
                        if st.button("✅ Accept", key=f"accept_{order['id']}", type="primary"):
                            st.success(f"Order {order.get('order_number')} accepted!")
                    with btn_col3:
                        if st.button("⏸️ Hold", key=f"hold_{order['id']}"):
                            st.info("Order placed on hold")
                    st.markdown("---")
        else:
            st.info("No orders found")
    
    with tab2:
        st.subheader("Contract Agreement Preview")
        st.markdown("**Order:** #ORD-2024-0891")
        st.markdown("**Parties:** Green Valley Farms ↔ Metro Retail Inc")
        st.markdown("---")
        st.markdown("### Product Details")
        st.write("- **Item:** Organic Wheat, Grade A")
        st.write("- **Quantity:** 50 metric tons")
        st.write("- **Price:** $250.00/ton")
        st.write("- **Total:** $12,500.00")
        st.markdown("---")
        st.markdown("### Delivery Terms")
        st.write("- **Deadline:** February 15, 2024")
        st.write("- **Location:** 123 Warehouse District")
        st.write("- **Penalty:** 0.5% per day")
        st.markdown("---")
        st.markdown("### Payment Terms")
        st.write("- **Advance:** 30% ($3,750) on confirmation")
        st.write("- **Balance:** 70% ($8,750) on delivery")
        st.markdown("---")
        st.markdown("### AI Verification ✅")
        st.write("- Supplier verified (3 years)")
        st.write("- 48 past orders, 0 disputes")
        st.write("- Credit score: 8.5/10")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancel"):
                st.rerun()
        with col2:
            if st.button("Sign & Accept", type="primary"):
                st.success("✅ Order accepted!")

def show_marketplace():
    """Marketplace content"""
    st.title("🤝 AI Merchant Matching")
    st.caption("Find the best merchants for your products")
    
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Product Category", ["Grains", "Dairy", "Fruits", "Vegetables"])
    with col2:
        radius = st.slider("Delivery Radius (miles)", 10, 500, 100)
    
    if st.button("🔍 Find Matches", type="primary", use_container_width=True):
        with st.spinner("Analyzing 2,400 merchants..."):
            import time
            time.sleep(1.5)
            
            st.subheader("🏆 Top Matches")
            
            matches = [
                {"name": "FoodCo Distributors", "match": 95, "distance": 15, "rating": "4.8/5"},
                {"name": "FreshChain Inc", "match": 87, "distance": 25, "rating": "4.6/5"},
                {"name": "OrganicMarket", "match": 82, "distance": 30, "rating": "4.5/5"},
            ]
            
            for idx, match in enumerate(matches, 1):
                with st.container():
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        st.write(f"**{idx}. {match['name']}**")
                    with col_b:
                        st.metric("Match", f"{match['match']}%")
                    with col_c:
                        st.caption(f"📍 {match['distance']} mi")
                    with col_d:
                        st.metric("Rating", match['rating'])
                    st.markdown("---")

def show_settings():
    """Settings content"""
    st.title("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["Profile", "Notifications", "Security"])
    
    with tab1:
        st.subheader("Producer Profile")
        with st.form("profile"):
            st.text_input("Farm Name", value="Green Valley Farms")
            st.text_input("Contact Person", value="John Producer")
            st.text_input("Email", value="producer@demo.com")
            st.text_input("Phone", value="+1 555-0123")
            if st.form_submit_button("Save Changes", type="primary"):
                st.success("✅ Profile updated!")
    
    with tab2:
        st.subheader("Notifications")
        st.checkbox("Email notifications", value=True)
        st.checkbox("SMS alerts", value=True)
        st.checkbox("Daily reports", value=False)
    
    with tab3:
        st.subheader("Security")
        with st.form("password"):
            st.text_input("Current Password", type="password")
            st.text_input("New Password", type="password")
            if st.form_submit_button("Update Password"):
                st.success("✅ Password updated!")

# ============ OTHER PORTALS ============

def merchant_portal():
    with st.sidebar:
        st.title("🛒 Merchant Portal")
        page = st.radio("Navigation", ["Dashboard", "Marketplace", "Orders", "Fraud Check", "Settings"])
    st.title(f"Merchant - {page}")
    st.write(f"Merchant {page} content coming soon...")

def customer_portal():
    with st.sidebar:
        st.title("🛍️ Customer Store")
        page = st.radio("Navigation", ["Home", "Marketplace", "Recommendations", "Favorites"])
    st.title(f"Customer - {page}")
    st.write(f"Customer {page} content coming soon...")

def admin_portal():
    with st.sidebar:
        st.title("⚙️ Admin Console")
        page = st.radio("Navigation", ["Dashboard", "Users", "Products", "Fraud Monitor", "ML Performance", "Reports"])
    st.title(f"Admin - {page}")
    st.write(f"Admin {page} content coming soon...")

# ============ MAIN ============

def main():
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "role" not in st.session_state:
        st.session_state.role = None
    
    # Route based on login status
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.role == "producer":
            producer_portal()
        elif st.session_state.role == "merchant":
            merchant_portal()
        elif st.session_state.role == "customer":
            customer_portal()
        elif st.session_state.role == "admin":
            admin_portal()
        else:
            st.error("Invalid role selected")
            if st.button("Return to Login"):
                st.session_state.logged_in = False
                st.rerun()

if __name__ == "__main__":
    main()
