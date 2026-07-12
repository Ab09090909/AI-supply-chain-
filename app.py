"""
AI Supply Chain Platform - Login & Producer Portal with Hamburger Menu
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
    initial_sidebar_state="collapsed"  # Collapse default sidebar
)

# Hide default sidebar completely
st.markdown("""
<style>
/* Hide the default sidebar */
section[data-testid="stSidebar"] {
    display: none !important;
}

/* Hide collapse button */
button[kind="header"] {
    display: none !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============ HAMBURGER MENU STYLES ============

st.markdown("""
<style>
/* Hamburger button */
.hamburger-btn {
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 9999;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.75rem 1rem;
    font-size: 1.5rem;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
}

.hamburger-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}

/* Navigation overlay */
.nav-overlay {
    position: fixed;
    top: 0;
    left: -320px;
    width: 320px;
    height: 100vh;
    background: white;
    box-shadow: 4px 0 20px rgba(0,0,0,0.15);
    z-index: 9998;
    transition: left 0.3s ease;
    overflow-y: auto;
    padding: 2rem 1.5rem;
}

.nav-overlay.open {
    left: 0;
}

/* Close button */
.close-btn {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: none;
    border: none;
    font-size: 2rem;
    cursor: pointer;
    color: #666;
}

/* Profile section */
.profile-section {
    text-align: center;
    padding: 2rem 0;
    border-bottom: 1px solid #e0e0e0;
    margin-bottom: 1.5rem;
}

.profile-avatar {
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
    margin: 0 auto 1rem auto;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* Navigation items */
.nav-item {
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: #333;
    font-size: 1rem;
    text-decoration: none;
}

.nav-item:hover {
    background: #e3f2fd;
    color: #1976d2;
}

.nav-item.active {
    background: #e3f2fd;
    color: #1976d2;
    font-weight: 600;
}

/* Stats section */
.stats-section {
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e0e0e0;
}

/* Main content padding */
.main-content {
    padding: 2rem;
    padding-top: 5rem;
}

/* Overlay backdrop */
.backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.3);
    z-index: 9997;
    display: none;
}

.backdrop.show {
    display: block;
}
</style>
""", unsafe_allow_html=True)

# ============ DATABASE FUNCTIONS ============

def get_db_connection():
    db_path = Path(__file__).parent / "data" / "supply_chain.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_inventory_from_db():
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
        
        for order in results:
            if order.get('items'):
                order['items'] = json.loads(order['items'])
        
        return results
    except Exception as e:
        print(f"DB Error: {e}")
        return []

# ============ HAMBURGER MENU COMPONENTS ============

def render_hamburger_button():
    """Render the hamburger menu button"""
    st.markdown("""
    <button class="hamburger-btn" onclick="toggleMenu()">☰</button>
    """, unsafe_allow_html=True)

def render_nav_overlay():
    """Render the navigation overlay"""
    # Get current page from session state
    current_page = st.session_state.get('current_page', 'Dashboard')
    
    st.markdown(f"""
    <div class="nav-overlay" id="navOverlay">
        <button class="close-btn" onclick="toggleMenu()">×</button>
        
        <!-- Profile Section -->
        <div class="profile-section">
            <div class="profile-avatar">👨‍🌾</div>
            <h2>Green Valley Farms</h2>
            <p style="color: #666;">Producer Portal</p>
        </div>
        
        <!-- Navigation -->
        <div style="margin-bottom: 2rem;">
            <h3 style="font-size: 0.85rem; text-transform: uppercase; color: #666; margin-bottom: 1rem;">Navigation</h3>
            <a href="#" class="nav-item {'active' if current_page == 'Dashboard' else ''}" onclick="navigateTo('Dashboard')">📊 Dashboard</a>
            <a href="#" class="nav-item {'active' if current_page == 'Inventory' else ''}" onclick="navigateTo('Inventory')">📦 Inventory</a>
            <a href="#" class="nav-item {'active' if current_page == 'Orders' else ''}" onclick="navigateTo('Orders')">📋 Orders</a>
            <a href="#" class="nav-item {'active' if current_page == 'Marketplace' else ''}" onclick="navigateTo('Marketplace')">🤝 Marketplace</a>
            <a href="#" class="nav-item {'active' if current_page == 'Settings' else ''}" onclick="navigateTo('Settings')">⚙️ Settings</a>
        </div>
        
        <!-- Quick Stats -->
        <div class="stats-section">
            <h3 style="font-size: 0.85rem; text-transform: uppercase; color: #666; margin-bottom: 1rem;">Quick Stats</h3>
            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                <div>
                    <p style="font-size: 0.85rem; color: #666;">Active Orders</p>
                    <p style="font-size: 1.5rem; font-weight: 700; color: #667eea;">24</p>
                    <p style="font-size: 0.8rem; color: #28a745;">↑ +3 today</p>
                </div>
                <div>
                    <p style="font-size: 0.85rem; color: #666;">Revenue</p>
                    <p style="font-size: 1.5rem; font-weight: 700; color: #667eea;">$45.2K</p>
                    <p style="font-size: 0.8rem; color: #28a745;">↑ +5.3%</p>
                </div>
            </div>
        </div>
        
        <!-- AI Assistant Toggle -->
        <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e0e0e0;">
            <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                <input type="checkbox" id="aiToggle" onchange="toggleAI()"> 
                <span>🤖 AI Assistant</span>
            </label>
        </div>
        
        <!-- Logout -->
        <div style="margin-top: 2rem;">
            <button onclick="logout()" style="width: 100%; padding: 0.75rem; background: #dc3545; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem;">🚪 Logout</button>
        </div>
    </div>
    
    <!-- Backdrop -->
    <div class="backdrop" id="backdrop" onclick="toggleMenu()"></div>
    
    <script>
        function toggleMenu() {{
            const overlay = document.getElementById('navOverlay');
            const backdrop = document.getElementById('backdrop');
            overlay.classList.toggle('open');
            backdrop.classList.toggle('show');
        }}
        
        function navigateTo(page) {{
            // Set session state via Streamlit
            window.parent.postMessage({{type: 'streamlit:navigate', page: page}}, '*');
            toggleMenu();
        }}
        
        function toggleAI() {{
            const aiToggle = document.getElementById('aiToggle');
            window.parent.postMessage({{type: 'streamlit:setState', key: 'show_ai', value: aiToggle.checked}}, '*');
        }}
        
        function logout() {{
            window.parent.postMessage({{type: 'streamlit:logout'}}, '*');
        }}
    </script>
    """, unsafe_allow_html=True)

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
    """Producer portal with hamburger menu"""
    
    # Render hamburger button (fixed position)
    render_hamburger_button()
    
    # Render navigation overlay (hidden by default)
    render_nav_overlay()
    
    # Handle navigation from hamburger menu
    if 'navigate_to' in st.session_state:
        page = st.session_state.navigate_to
        del st.session_state.navigate_to
    else:
        page = st.session_state.get('current_page', 'Dashboard')
    
    # Main content with padding for hamburger button
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    if page == "Dashboard":
        st.session_state.current_page = 'Dashboard'
        show_dashboard()
    elif page == "Inventory":
        st.session_state.current_page = 'Inventory'
        show_inventory()
    elif page == "Orders":
        st.session_state.current_page = 'Orders'
        show_orders()
    elif page == "Marketplace":
        st.session_state.current_page = 'Marketplace'
        show_marketplace()
    elif page == "Settings":
        st.session_state.current_page = 'Settings'
        show_settings()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Assistant
    if st.session_state.get("show_ai", False):
        with st.expander("🤖 AI Assistant", expanded=True):
            st.write("Ask me anything about your supply chain...")
            user_input = st.text_input("Your question:", key="ai_input")
            if user_input:
                st.write(f"**AI:** I received '{user_input}'. This is a demo response.")

def show_dashboard():
    """Producer Dashboard"""
    st.title("📊 Producer Dashboard")
    st.caption("Welcome back! Here's your supply chain overview.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        orders = get_orders_from_db()
        st.metric("Active Orders", str(len(orders)), "+3 today")
    with col2:
        inventory = get_inventory_from_db()
        st.metric("Inventory Items", str(len(inventory)))
    with col3:
        st.metric("Avg Price", "$4.85", "+2.1%")
    with col4:
        st.metric("Risk Score", "12%", "-3%", delta_color="inverse")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Yield Performance (30 Days)")
        dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
        values = [100 + x * 0.5 + (x % 5) * 2 for x in range(30)]
        df = pd.DataFrame({"Date": dates, "Yield (tons)": values})
        st.plotly_chart(px.line(df, x="Date", y="Yield (tons)", template="plotly_white"), use_container_width=True)
    
    with col2:
        st.subheader("🎯 Quality Index")
        quality_data = pd.DataFrame({"Metric": ["Purity", "Moisture", "Protein", "Appearance"], "Score": [98, 95, 96, 97]})
        st.plotly_chart(px.bar(quality_data, x="Score", y="Metric", orientation="h", color="Score", template="plotly_white"), use_container_width=True)
    
    st.subheader("📋 Recent Orders")
    if orders:
        for order in orders[:3]:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.write(f"**{order.get('order_number', '#N/A')}**")
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
    """Producer Inventory"""
    st.title("📦 Inventory Management")
    st.caption("Track stock levels and manage products")
    
    inventory = get_inventory_from_db()
    
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
    
    if inventory:
        df_data = []
        for item in inventory:
            stock = item.get('stock', 0)
            min_stock = item.get('reorder_point', 0)
            status = "🔴 Critical" if stock == 0 else "🟡 Low" if stock <= min_stock * 1.2 else "🟢 Good"
            
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
        
        st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)
    else:
        st.warning("No inventory items found")

def show_orders():
    """Producer Orders & Agreements"""
    st.title("📋 Orders & Agreements")
    st.caption("Manage incoming orders and contracts")
    
    orders = get_orders_from_db()
    
    tab1, tab2 = st.tabs(["📥 Received Orders", "📄 Agreement Preview"])
    
    with tab1:
        st.subheader("Incoming Order Requests")
        
        if orders:
            for order in orders:
                with st.container():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.write(f"**{order.get('order_number', '#N/A')}**")
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
                        else:
                            st.warning("Pending")
                    
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
    render_hamburger_button()
    render_nav_overlay_merchant()
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("Merchant Portal")
    st.write("Merchant content coming soon...")
    st.markdown('</div>', unsafe_allow_html=True)

def customer_portal():
    render_hamburger_button()
    render_nav_overlay_customer()
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("Customer Store")
    st.write("Customer content coming soon...")
    st.markdown('</div>', unsafe_allow_html=True)

def admin_portal():
    render_hamburger_button()
    render_nav_overlay_admin()
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("Admin Console")
    st.write("Admin content coming soon...")
    st.markdown('</div>', unsafe_allow_html=True)

def render_nav_overlay_merchant():
    st.markdown("""
    <div class="nav-overlay" id="navOverlayMerchant">
        <button class="close-btn" onclick="toggleMenu()">×</button>
        <div class="profile-section">
            <div class="profile-avatar" style="background: linear-gradient(135deg, #764ba2, #667eea);">🛒</div>
            <h2>Metro Retail Inc</h2>
            <p style="color: #666;">Merchant Portal</p>
        </div>
        <div style="margin-bottom: 2rem;">
            <h3 style="font-size: 0.85rem; text-transform: uppercase; color: #666; margin-bottom: 1rem;">Navigation</h3>
            <a href="#" class="nav-item">📈 Dashboard</a>
            <a href="#" class="nav-item">🛍️ Marketplace</a>
            <a href="#" class="nav-item">📦 Orders</a>
            <a href="#" class="nav-item">🛡️ Fraud Check</a>
            <a href="#" class="nav-item">⚙️ Settings</a>
        </div>
        <div class="stats-section">
            <h3 style="font-size: 0.85rem; text-transform: uppercase; color: #666; margin-bottom: 1rem;">Quick Stats</h3>
            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                <div>
                    <p style="font-size: 0.85rem; color: #666;">Active Orders</p>
                    <p style="font-size: 1.5rem; font-weight: 700; color: #764ba2;">12</p>
                </div>
                <div>
                    <p style="font-size: 0.85rem; color: #666;">Suppliers</p>
                    <p style="font-size: 1.5rem; font-weight: 700; color: #764ba2;">12</p>
                </div>
            </div>
        </div>
        <div style="margin-top: 2rem;">
            <button onclick="logout()" style="width: 100%; padding: 0.75rem; background: #dc3545; color: white; border: none; border-radius: 8px; cursor: pointer;">🚪 Logout</button>
        </div>
    </div>
    <div class="backdrop" id="backdropMerchant" onclick="toggleMenu()"></div>
    """, unsafe_allow_html=True)

def render_nav_overlay_customer():
    st.markdown("""
    <div class="nav-overlay" id="navOverlayCustomer">
        <button class="close-btn" onclick="toggleMenu()">×</button>
        <div class="profile-section">
            <div class="profile-avatar" style="background: linear-gradient(135deg, #28a745, #20c997);">🛍️</div>
            <h2>John Consumer</h2>
            <p style="color: #666;">Customer Store</p>
        </div>
        <div style="margin-bottom: 2rem;">
            <h3 style="font-size: 0.85rem; text-transform: uppercase; color: #666; margin-bottom: 1rem;">Navigation</h3>
            <a href="#" class="nav-item">🏠 Home</a>
            <a href="#" class="nav-item">🛍️ Marketplace</a>
            <a href="#" class="nav-item">💡 Recommendations</a>
            <a href="#" class="nav-item">💝 Favorites</a>
        </div>
        <div class="stats-section">
            <h3 style="font-size: 0.85rem; text-transform: uppercase; color: #666; margin-bottom: 1rem;">Quick Stats</h3>
            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                <div>
                    <p style="font-size: 0.85rem; color: #666;">Cart Items</p>
                    <p style="font-size: 1.5rem; font-weight: 700; color: #28a745;">3</p>
                </div>
                <div>
                    <p style="font-size: 0.85rem; color: #666;">Favorites</p>
                    <p style="font-size: 1.5rem; font-weight: 700; color: #28a745;">12</p>
                </div>
            </div>
        </div>
        <div style="margin-top: 2rem;">
            <button onclick="logout()" style="width: 100%; padding: 0.75rem; background: #dc3545; color: white; border: none; border-radius: 8px; cursor: pointer;">🚪 Logout</button>
        </div>
    </div>
    <div class="backdrop" id="backdropCustomer" onclick="toggleMenu()"></div>
    """, unsafe_allow_html=True)

def render_nav_overlay_admin():
    st.markdown("""
    <div class="nav-overlay" id="navOverlayAdmin">
        <button class="close-btn" onclick="toggleMenu()">×</button>
        <div class="profile-section">
            <div class="profile-avatar" style="background: linear-gradient(135deg, #dc3545, #c82333);">⚙️</div>
            <h2>System Admin</h2>
            <p style="color: #666;">Admin Console</p>
        </div>
        <div style="margin-bottom: 2rem;">
            <h3 style="font-size: 0.85rem; text-transform: uppercase; color: #666; margin-bottom: 1rem;">Navigation</h3>
            <a href="#" class="nav-item">📊 Dashboard</a>
            <a href="#" class="nav-item">👥 Users</a>
            <a href="#" class="nav-item">🏷️ Products</a>
            <a href="#" class="nav-item">🚨 Fraud Monitor</a>
            <a href="#" class="nav-item">🤖 ML Performance</a>
            <a href="#" class="nav-item">📄 Reports</a>
        </div>
        <div class="stats-section">
            <h3 style="font-size: 0.85rem; text-transform: uppercase; color: #666; margin-bottom: 1rem;">System Status</h3>
            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                <div>
                    <p style="font-size: 0.85rem; color: #666;">Health</p>
                    <p style="font-size: 1.5rem; font-weight: 700; color: #28a745;">98.5%</p>
                </div>
                <div>
                    <p style="font-size: 0.85rem; color: #666;">Users</p>
                    <p style="font-size: 1.5rem; font-weight: 700; color: #dc3545;">89</p>
                </div>
            </div>
        </div>
        <div style="margin-top: 2rem;">
            <button onclick="logout()" style="width: 100%; padding: 0.75rem; background: #dc3545; color: white; border: none; border-radius: 8px; cursor: pointer;">🚪 Logout</button>
        </div>
    </div>
    <div class="backdrop" id="backdropAdmin" onclick="toggleMenu()"></div>
    """, unsafe_allow_html=True)

# ============ MAIN ============

def main():
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "role" not in st.session_state:
        st.session_state.role = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
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
