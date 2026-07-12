"""
Producer Portal - Main Entry Point
"""
import streamlit as st

PRODUCER_NAME = "Green Valley Farms"
TABS = {
    "dashboard": "📊 Dashboard",
    "inventory": "📦 Inventory",
    "marketplace": "🤝 Merchant Matching",
    "ai_insights": "💡 AI Insights",
    "settings": "⚙️ Settings"
}

def run():
    # ============ SIDEBAR ============
    with st.sidebar:
        st.markdown(f"<h1 style='text-align: center;'>👨‍🌾</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>{PRODUCER_NAME}</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Producer Portal</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        selected = st.radio(
            "Navigation",
            list(TABS.keys()),
            format_func=lambda x: TABS[x],
            label_visibility="collapsed",
            key="producer_nav"
        )
        
        st.markdown("---")
        st.metric("Orders", "24", "+3")
        st.caption("Last updated: Just now")
        
        st.markdown("---")
        show_ai = st.checkbox("🤖 AI Assistant", value=False)
        st.session_state.show_ai = show_ai
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()
    
    # ============ FALLBACK TOP NAVIGATION (for mobile) ============
    st.markdown("### Navigation")
    selected_top = st.radio(
        "Go to page",
        list(TABS.keys()),
        format_func=lambda x: TABS[x],
        label_visibility="collapsed",
        horizontal=True,
        key="producer_top_nav"
    )
    
    # Use whichever was selected (sidebar or top nav)
    if selected_top:
        selected = selected_top
    
    st.markdown("---")
    
    # Main Content
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
    
    if st.session_state.get("show_ai", False):
        from producer.ai_assistant.chat import assistant
        with st.expander("🤖 AI Assistant", expanded=True):
            assistant.render()

def render_dashboard():
    st.header("📊 Producer Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Orders", "24", "+3")
    with col2:
        st.metric("Turn", "4.2x", "+0.3")
    with col3:
        st.metric("Price", "$4.85", "+2.1%")
    with col4:
        st.metric("Risk", "12%", "-3%")
    
    st.subheader("Yield Performance")
    import pandas as pd
    import plotly.express as px
    from datetime import datetime, timedelta
    
    dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
    values = [100 + x * 0.5 for x in range(30)]
    df = pd.DataFrame({"Date": dates, "Yield": values})
    st.plotly_chart(px.line(df, x="Date", y="Yield", template="plotly_white"), use_container_width=True)

def render_inventory():
    st.header("📦 Inventory")
    
    import pandas as pd
    
    # Get inventory from DB or use mock
    try:
        from producer.utils.db import db
        inventory = db.get_inventory()
    except:
        inventory = [
            {"sku": "AGR-001", "name": "Organic Wheat", "stock": 450, "min": 100, "price": 4.20},
            {"sku": "AGR-002", "name": "Fresh Dairy", "stock": 35, "min": 50, "price": 3.50},
        ]
    
    if inventory:
        df = pd.DataFrame(inventory)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No inventory items")

def render_marketplace():
    st.header("🤝 Merchant Matching")
    category = st.selectbox("Category", ["Grains", "Dairy", "Fruits", "Vegetables"])
    if st.button("🔍 Find Matches"):
        st.success("Found matches!")
        st.write("- FoodCo Distributors: 95% match")
        st.write("- FreshChain Inc: 87% match")

def render_ai_insights():
    st.header("💡 AI Insights")
    st.info("AI-powered recommendations coming soon")

def render_settings():
    st.header("⚙️ Settings")
    with st.form("settings"):
        st.text_input("Farm Name", value="Green Valley Farms")
        st.text_input("Email", value="producer@demo.com")
        if st.form_submit_button("Save"):
            st.success("Saved!")
