"""
Merchant Portal - Main Entry Point
"""
import streamlit as st

MERCHANT_NAME = "Metro Retail Inc"
TABS = {
    "dashboard": "📈 Dashboard",
    "marketplace": "🛍️ Marketplace",
    "orders": "📦 Orders",
    "fraud_check": "🛡️ Fraud Check",
    "settings": "⚙️ Settings"
}

def run():
    with st.sidebar:
        st.markdown(f"<h1 style='text-align: center; font-size: 3rem;'>🛒</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{MERCHANT_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #666;'>Merchant Portal</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.subheader("Navigation")
        selected = st.radio(
            "Go to",
            list(TABS.keys()),
            format_func=lambda x: TABS[x],
            label_visibility="collapsed",
            key="merchant_navigation"
        )
        
        st.markdown("---")
        st.metric("Active Orders", "12", "+2 today")
        
        st.markdown("---")
        show_ai = st.checkbox("🤖 AI Assistant", value=False)
        st.session_state.show_ai = show_ai
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    st.title(f"{TABS[selected]}")
    
    if selected == "dashboard":
        render_dashboard()
    elif selected == "marketplace":
        render_marketplace()
    elif selected == "orders":
        render_orders()
    elif selected == "fraud_check":
        render_fraud_check()
    elif selected == "settings":
        render_settings()
    
    if st.session_state.get("show_ai", False):
        from merchant.ai_assistant.chat import assistant
        with st.expander("🤖 AI Assistant", expanded=True):
            assistant.render()

def render_dashboard():
    st.header("Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Spend", "$45.2K", "+5.3%")
    with col2:
        st.metric("Suppliers", "12", "-2")
    with col3:
        st.metric("Fulfillment", "98.5%", "+0.5%")
    with col4:
        st.metric("Lead Time", "2.4d", "-0.3")

def render_marketplace():
    st.header("Marketplace")
    st.write("Browse products from producers")

def render_orders():
    st.header("My Orders")
    st.write("Track your orders")

def render_fraud_check():
    st.header("Fraud Detection")
    st.write("Check supplier trustworthiness")

def render_settings():
    st.header("Settings")
    st.write("Manage your account")
