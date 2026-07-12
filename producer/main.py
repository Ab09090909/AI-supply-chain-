"""
Producer Portal - Main Entry Point
"""
import streamlit as st

# Simple constants - no complex imports at top level
PRODUCER_NAME = "Green Valley Farms"
TABS = {
    "dashboard": "📊 Dashboard",
    "inventory": "📦 Inventory",
    "marketplace": "🤝 Merchant Matching",
    "ai_insights": "💡 AI Insights",
    "settings": "⚙️ Settings"
}

def run():
    # ============ SIDEBAR STARTS HERE ============
    with st.sidebar:
        # Profile Section
        st.markdown(f"<h1 style='text-align: center; font-size: 3rem;'>👨‍🌾</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{PRODUCER_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #666;'>Producer Portal</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Navigation - Simple and clean
        st.subheader("Navigation")
        selected = st.radio(
            "Go to",
            list(TABS.keys()),
            format_func=lambda x: TABS[x],
            label_visibility="collapsed",
            key="producer_navigation"
        )
        
        st.markdown("---")
        
        # Quick Stats
        st.subheader("Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Orders", "24", "+3")
        with col2:
            st.metric("Rating", "4.8", "⭐")
        
        st.markdown("---")
        
        # AI Toggle
        show_ai = st.checkbox("🤖 AI Assistant", value=False)
        st.session_state.show_ai = show_ai
        
        st.markdown("---")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()
    # ============ SIDEBAR ENDS HERE ============
    
    # Main Content Area (outside sidebar context)
    st.title(f"{TABS[selected]}")
    
    # Route to selected page
    if selected == "dashboard":
        render_dashboard()
    elif selected == "inventory":
        render_inventory()
    elif selected == "marketplace":
        render_marketplace()
    elif selected == "ai_insights":
        render_ai_insights()
    elif selected == "settings":
        render_settings()

def render_dashboard():
    """Simple dashboard to test"""
    st.header("Dashboard")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Orders", "24", "+3 today")
    with col2:
        st.metric("Inventory Turn", "4.2x", "+0.3")
    with col3:
        st.metric("Avg Price", "$4.85", "+2.1%")
    with col4:
        st.metric("Risk Score", "12%", "-3%")
    
    st.markdown("---")
    
    # Simple chart
    st.subheader("Yield Performance (30 Days)")
    import pandas as pd
    import plotly.express as px
    from datetime import datetime, timedelta
    
    dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
    values = [100 + x * 0.5 + (x % 5) * 2 for x in range(30)]
    
    df = pd.DataFrame({"Date": dates, "Yield (tons)": values})
    fig = px.line(df, x="Date", y="Yield (tons)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

def render_inventory():
    """Simple inventory page"""
    st.header("Inventory Management")
    
    # Simple table
    import pandas as pd
    
    inventory_data = [
        {"SKU": "AGR-001", "Product": "Organic Wheat", "Stock": 450, "Min": 100, "Price": 4.20},
        {"SKU": "AGR-002", "Product": "Fresh Dairy", "Stock": 35, "Min": 50, "Price": 3.50},
        {"SKU": "AGR-003", "Product": "Premium Avocados", "Stock": 12, "Min": 40, "Price": 12.00},
    ]
    
    df = pd.DataFrame(inventory_data)
    st.dataframe(df, use_container_width=True)

def render_marketplace():
    """Simple marketplace page"""
    st.header("Merchant Matching")
    st.write("Find the best merchants for your products")
    
    category = st.selectbox("Category", ["Grains", "Dairy", "Fruits", "Vegetables"])
    radius = st.slider("Radius (miles)", 10, 500, 100)
    
    if st.button("Find Matches"):
        st.success("Found 3 matches!")
        for i, merchant in enumerate(["FoodCo Distributors", "FreshChain Inc", "OrganicMarket"], 1):
            st.write(f"{i}. **{merchant}** - {90-i*3}% match")

def render_ai_insights():
    """Simple AI insights page"""
    st.header("AI Insights")
    st.info("Price forecasts, demand predictions, and recommendations will appear here.")

def render_settings():
    """Simple settings page"""
    st.header("Settings")
    
    with st.form("settings_form"):
        st.text_input("Farm Name", value="Green Valley Farms")
        st.text_input("Contact Person", value="John Producer")
        st.text_input("Email", value="producer@demo.com")
        
        if st.form_submit_button("Save Changes"):
            st.success("Settings saved!")
