"""
AI Supply Chain Platform - Login & Producer Portal
"""
import streamlit as st

# Page config - MUST be first
st.set_page_config(
    page_title="AI Supply Chain Platform",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FORCE SIDEBAR OPEN - This CSS ensures sidebar is always visible
st.markdown("""
<style>
/* Force sidebar open */
section[data-testid="stSidebar"] {
    display: block !important;
    width: 280px !important;
    min-width: 280px !important;
    max-width: 280px !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    left: 0 !important;
    top: 0 !important;
    bottom: 0 !important;
    z-index: 999 !important;
}

/* Push main content to the right */
.main > div {
    margin-left: 280px !important;
    padding-left: 2rem !important;
}

/* Hide the collapse button */
button[kind="header"] {
    display: none !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def login_page():
    """Simple login page"""
    st.title("🔗 AI Supply Chain Platform")
    st.markdown("### Multi-Enterprise Supply Chain Intelligence")
    
    # Create a container for centering
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("---")
            
            # Role selection - FORCE PRODUCER FOR TESTING
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
                index=0  # DEFAULT TO PRODUCER (first option)
            )
            
            st.markdown("---")
            
            # Login form
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
            
            st.markdown("---")
            st.caption("🔒 Secure login | Demo mode available")

def producer_portal():
    """Producer portal with WORKING sidebar"""
    
    # ============ SIDEBAR ============
    with st.sidebar:
        # Profile Section
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
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
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
        st.metric("Inventory Items", "6")
        st.metric("Revenue", "$45.2K", "+5.3%")
        
        st.markdown("---")
        
        # AI Assistant toggle
        show_ai = st.checkbox("🤖 AI Assistant", value=False)
        st.session_state.show_ai = show_ai
        
        st.markdown("---")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.rerun()
    
    # ============ MAIN CONTENT ============
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
                st.write(f"**AI Response:** I received '{user_input}'. This is a demo response.")

def show_dashboard():
    """Producer Dashboard"""
    st.title("📊 Producer Dashboard")
    st.caption("Welcome back! Here's your supply chain overview.")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Active Orders", value="24", delta="+3 today")
    
    with col2:
        st.metric(label="Inventory Turn", value="4.2x", delta="+0.3")
    
    with col3:
        st.metric(label="Avg Price", value="$4.85", delta="+2.1%")
    
    with col4:
        st.metric(label="Risk Score", value="12%", delta="-3%", delta_color="inverse")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Yield Performance (30 Days)")
        import pandas as pd
        import plotly.express as px
        from datetime import datetime, timedelta
        
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
    
    # Recent Orders
    st.subheader("📋 Recent Orders")
    
    orders_data = [
        {"Order ID": "#PO-001", "Merchant": "Metro Retail Inc", "Product": "Organic Wheat", "Amount": "$2,400", "Status": "Delivered"},
        {"Order ID": "#PO-002", "Merchant": "Fresh Market Co", "Product": "Fresh Dairy", "Amount": "$1,850", "Status": "In Transit"},
        {"Order ID": "#PO-003", "Merchant": "Organic Suppliers", "Product": "Premium Avocados", "Amount": "$3,100", "Status": "Processing"},
    ]
    
    for order in orders_data:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.write(f"**{order['Order ID']}**")
            with col2:
                st.write(order['Merchant'])
            with col3:
                st.write(order['Product'])
            with col4:
                st.write(order['Amount'])
            with col5:
                if order['Status'] == "Delivered":
                    st.success(order['Status'])
                elif order['Status'] == "In Transit":
                    st.info(order['Status'])
                else:
                    st.warning(order['Status'])
            st.markdown("---")

def show_inventory():
    """Producer Inventory"""
    st.title("📦 Inventory Management")
    st.caption("Track stock levels and manage products")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total SKUs", "6")
    with col2:
        st.metric("Stock Value", "$48,250")
    with col3:
        st.metric("Low Stock", "3", delta_color="inverse")
    with col4:
        st.metric("Out of Stock", "1", delta_color="inverse")
    
    st.markdown("---")
    
    # Inventory table
    inventory_data = [
        {"SKU": "AGR-001", "Product": "Organic Wheat", "Category": "Grains", "Stock": "450 tons", "Min": "100", "Price": "$4.20", "Status": "🟢 Good"},
        {"SKU": "AGR-002", "Product": "Fresh Dairy", "Category": "Dairy", "Stock": "35 units", "Min": "50", "Price": "$3.50", "Status": "🟡 Low"},
        {"SKU": "AGR-003", "Product": "Premium Avocados", "Category": "Fruits", "Stock": "12 units", "Min": "40", "Price": "$12.00", "Status": "🔴 Critical"},
        {"SKU": "AGR-004", "Product": "Free Range Eggs", "Category": "Dairy", "Stock": "200 units", "Min": "80", "Price": "$5.50", "Status": "🟢 Good"},
        {"SKU": "AGR-005", "Product": "Organic Rice", "Category": "Grains", "Stock": "45 units", "Min": "60", "Price": "$3.80", "Status": "🟡 Low"},
        {"SKU": "AGR-006", "Product": "Organic Carrots", "Category": "Vegetables", "Stock": "0 units", "Min": "30", "Price": "$2.90", "Status": "🔴 Out of Stock"},
    ]
    
    df = pd.DataFrame(inventory_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add Product", use_container_width=True, type="primary"):
            st.success("Add product form would open here")
    with col2:
        if st.button("📦 Generate Restock Report"):
            st.warning("Restock needed for: Fresh Dairy, Premium Avocados, Organic Carrots")
    with col3:
        if st.button("📥 Export CSV"):
            st.success("Inventory exported to CSV")

def show_orders():
    """Producer Orders & Agreements"""
    st.title("📋 Orders & Agreements")
    st.caption("Manage incoming orders and contracts")
    
    # Tabs
    tab1, tab2 = st.tabs(["📥 Received Orders", "📄 Agreement Preview"])
    
    with tab1:
        st.subheader("Incoming Order Requests")
        
        # Order 1
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write("**#ORD-2024-0891**")
                st.caption("Metro Retail Inc")
            with col2:
                st.write("Organic Wheat (50 tons)")
            with col3:
                st.write("$12,500.00")
            with col4:
                st.write("🟡 Pending")
            
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                if st.button("📄 Review Agreement", key="agree_1"):
                    st.session_state.show_agreement = True
            with btn_col2:
                if st.button("✅ Accept", key="accept_1", type="primary"):
                    st.success("Order accepted! Agreement sent to buyer.")
            with btn_col3:
                if st.button("⏸️ Hold", key="hold_1"):
                    st.info("Order placed on hold")
            st.markdown("---")
        
        # Order 2
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write("**#ORD-2024-0890**")
                st.caption("Fresh Market Co")
            with col2:
                st.write("Premium Avocados (200 units)")
            with col3:
                st.write("$3,400.00")
            with col4:
                st.write("🔵 Awaiting Response")
            
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                if st.button("📄 Review Agreement", key="agree_2"):
                    st.session_state.show_agreement = True
            with btn_col2:
                if st.button("✅ Accept", key="accept_2", type="primary"):
                    st.success("Order accepted! Agreement sent to buyer.")
            with btn_col3:
                if st.button("⏸️ Hold", key="hold_2"):
                    st.info("Order placed on hold")
            st.markdown("---")
    
    with tab2:
        st.subheader("Contract Agreement Preview")
        
        st.markdown("**Order Reference:** #ORD-2024-0891")
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
        st.write("- **Location:** 123 Warehouse District, Metro City")
        st.write("- **Penalty:** 0.5% per day for late delivery")
        st.markdown("---")
        
        st.markdown("### Payment Terms")
        st.write("- **Advance:** 30% ($3,750) on confirmation")
        st.write("- **Balance:** 70% ($8,750) on delivery")
        st.write("- **Escrow:** Platform holds funds until delivery")
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
            if st.button("Sign & Accept Order", type="primary"):
                st.success("✅ Order accepted! Agreement signed.")

def show_marketplace():
    """Producer Merchant Matching"""
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
    """Producer Settings"""
    st.title("⚙️ Settings")
    st.caption("Manage your producer account")
    
    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔔 Notifications", "🔐 Security"])
    
    with tab1:
        st.subheader("Producer Profile")
        with st.form("profile"):
            st.text_input("Farm Name", value="Green Valley Farms")
            st.text_input("Contact Person", value="John Producer")
            st.text_input("Email", value="producer@demo.com")
            st.text_input("Phone", value="+1 555-0123")
            st.text_input("Location", value="California, USA")
            
            if st.form_submit_button("Save Changes", type="primary"):
                st.success("✅ Profile updated!")
    
    with tab2:
        st.subheader("Notifications")
        st.checkbox("Email notifications for new orders", value=True)
        st.checkbox("SMS alerts for low stock", value=True)
        st.checkbox("Daily summary reports", value=False)
        st.checkbox("Price change alerts", value=True)
    
    with tab3:
        st.subheader("Security")
        with st.form("password"):
            st.text_input("Current Password", type="password")
            st.text_input("New Password", type="password")
            st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Update Password"):
                st.success("✅ Password updated!")

def main():
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "role" not in st.session_state:
        st.session_state.role = None
    
    # Check login status
    if not st.session_state.logged_in:
        login_page()
    else:
        # Show only producer portal for testing
        if st.session_state.role == "producer":
            producer_portal()
        else:
            # If not producer, show message and let them switch
            st.warning(f"Only Producer portal is ready now. You selected: {st.session_state.role}")
            if st.button("Switch to Producer Portal"):
                st.session_state.role = "producer"
                st.rerun()

if __name__ == "__main__":
    main()
