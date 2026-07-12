"""
AI Supply Chain Platform - Login & Producer Portal
"""
import streamlit as st

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
                st.text_input("Email", value="producer@demo.com")
                st.text_input("Password", value="password", type="password")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    submit = st.form_submit_button("Login", use_container_width=True, type="primary")
                with col_b:
                    demo = st.form_submit_button("Demo Mode", use_container_width=True)
                
                if submit or demo:
                    st.session_state.logged_in = True
                    st.session_state.role = role.lower()
                    st.rerun()

def producer_portal():
    """Producer portal using separate sidebar file"""
    # Import sidebar function
    from producer.sidebar import render as render_sidebar
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
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

def merchant_portal():
    """Merchant portal using separate sidebar file"""
    from merchant.sidebar import render as render_sidebar
    page = render_sidebar()
    
    st.title(f"Merchant - {page}")
    st.write(f"Merchant {page} content coming soon...")

def customer_portal():
    """Customer portal using separate sidebar file"""
    from customer.sidebar import render as render_sidebar
    page = render_sidebar()
    
    st.title(f"Customer - {page}")
    st.write(f"Customer {page} content coming soon...")

def admin_portal():
    """Admin portal using separate sidebar file"""
    from admin.sidebar import render as render_sidebar
    page = render_sidebar()
    
    st.title(f"Admin - {page}")
    st.write(f"Admin {page} content coming soon...")

def show_dashboard():
    """Dashboard content"""
    st.title("📊 Producer Dashboard")
    st.caption("Welcome back! Here's your supply chain overview.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Orders", "24", "+3 today")
    with col2:
        st.metric("Inventory Turn", "4.2x", "+0.3")
    with col3:
        st.metric("Avg Price", "$4.85", "+2.1%")
    with col4:
        st.metric("Risk Score", "12%", "-3%", delta_color="inverse")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Yield Performance")
        import pandas as pd
        import plotly.express as px
        from datetime import datetime, timedelta
        
        dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
        values = [100 + x * 0.5 for x in range(30)]
        df = pd.DataFrame({"Date": dates, "Yield": values})
        st.plotly_chart(px.line(df, x="Date", y="Yield", template="plotly_white"), use_container_width=True)
    
    with col2:
        st.subheader("🎯 Quality Index")
        quality_data = pd.DataFrame({
            "Metric": ["Purity", "Moisture", "Protein"],
            "Score": [98, 95, 96]
        })
        st.plotly_chart(px.bar(quality_data, x="Score", y="Metric", orientation="h", template="plotly_white"), use_container_width=True)

def show_inventory():
    """Inventory content"""
    st.title("📦 Inventory Management")
    
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
    
    import pandas as pd
    inventory_data = [
        {"SKU": "AGR-001", "Product": "Organic Wheat", "Stock": 450, "Min": 100, "Price": 4.20},
        {"SKU": "AGR-002", "Product": "Fresh Dairy", "Stock": 35, "Min": 50, "Price": 3.50},
        {"SKU": "AGR-003", "Product": "Premium Avocados", "Stock": 12, "Min": 40, "Price": 12.00},
    ]
    st.dataframe(pd.DataFrame(inventory_data), use_container_width=True)

def show_orders():
    """Orders content"""
    st.title("📋 Orders & Agreements")
    
    tab1, tab2 = st.tabs(["Received Orders", "Agreement Preview"])
    
    with tab1:
        st.subheader("Incoming Orders")
        
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
                if st.button("📄 Review", key="agree_1"):
                    st.session_state.show_agreement = True
            with btn_col2:
                if st.button("✅ Accept", key="accept_1", type="primary"):
                    st.success("Order accepted!")
            with btn_col3:
                if st.button("⏸️ Hold", key="hold_1"):
                    st.info("On hold")
            st.markdown("---")
        
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
                if st.button("📄 Review", key="agree_2"):
                    st.session_state.show_agreement = True
            with btn_col2:
                if st.button("✅ Accept", key="accept_2", type="primary"):
                    st.success("Order accepted!")
            with btn_col3:
                if st.button("⏸️ Hold", key="hold_2"):
                    st.info("On hold")
            st.markdown("---")
    
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
        # Route to appropriate portal
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
