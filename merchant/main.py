"""
Merchant Portal - Main Entry Point
"""
import streamlit as st  # REQUIRED
from merchant.dashboard.view import render as render_dashboard
from merchant.marketplace.view import render as render_marketplace
from merchant.orders.view import render as render_orders
from merchant.fraud_check.view import render as render_fraud_check
from merchant.settings.view import render as render_settings
from merchant.profile_card.component import render_profile_header
from merchant.utils.constants import MERCHANT_NAME, TABS

def run():
    with st.sidebar:
        render_profile_header()
        st.markdown("---")
        
        selected = st.radio(
            "Navigation",
            TABS,
            format_func=lambda x: TABS[x],
            label_visibility="collapsed",
            key="merchant_nav"
        )
        
        st.markdown("---")
        st.metric("Active Orders", "12", "+2 today")
        st.caption("Last updated: Just now")
        st.markdown("---")
        
        if st.checkbox("🤖 Show AI Assistant", value=False):
            st.session_state.show_ai = True
        else:
            st.session_state.show_ai = False
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
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
