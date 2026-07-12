"""
Customer Portal - Main Entry Point
"""
import streamlit as st  # REQUIRED
from customer.home.view import render as render_home
from customer.marketplace.view import render as render_marketplace
from customer.recommendations.view import render as render_recommendations
from customer.favorites.view import render as render_favorites
from customer.profile_card.component import render_profile_header
from customer.utils.constants import CUSTOMER_NAME, TABS

def run():
    with st.sidebar:
        render_profile_header()
        st.markdown("---")
        
        selected = st.radio(
            "Navigation",
            TABS,
            format_func=lambda x: TABS[x],
            label_visibility="collapsed",
            key="customer_nav"
        )
        
        st.markdown("---")
        st.metric("Cart Items", "3", "+1")
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
    
    if selected == "home":
        render_home()
    elif selected == "marketplace":
        render_marketplace()
    elif selected == "recommendations":
        render_recommendations()
    elif selected == "favorites":
        render_favorites()
    
    if st.session_state.get("show_ai", False):
        from customer.ai_assistant.chat import assistant
        with st.expander("🤖 AI Assistant", expanded=True):
            assistant.render()
          
