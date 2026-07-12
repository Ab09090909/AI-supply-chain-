"""
Admin Portal - Main Entry Point
"""
import streamlit as st  # REQUIRED
from admin.dashboard.view import render as render_dashboard
from admin.user_management.view import render as render_users
from admin.fraud_monitoring.view import render as render_fraud
from admin.ml_performance.view import render as render_ml
from admin.reports.view import render as render_reports
from admin.profile_card.component import render_profile_header
from admin.utils.constants import ADMIN_NAME, TABS

def run():
    with st.sidebar:
        render_profile_header()
        st.markdown("---")
        
        selected = st.radio(
            "Navigation",
            TABS,
            format_func=lambda x: TABS[x],
            label_visibility="collapsed",
            key="admin_nav"
        )
        
        st.markdown("---")
        st.metric("System Health", "98.5%", "+0.2%")
        st.caption("All systems operational")
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
    elif selected == "users":
        render_users()
    elif selected == "fraud":
        render_fraud()
    elif selected == "ml":
        render_ml()
    elif selected == "reports":
        render_reports()
    
    if st.session_state.get("show_ai", False):
        from admin.ai_assistant.chat import assistant
        with st.expander("🤖 AI Assistant", expanded=True):
            assistant.render()
