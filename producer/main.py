"""
Producer Portal - Main Entry Point
Fully self-contained module
"""
import streamlit as st
from producer.dashboard.view import render as render_dashboard
from producer.inventory.view import render as render_inventory
from producer.marketplace.view import render as render_marketplace
from producer.ai_insights.view import render as render_ai_insights
from producer.settings.view import render as render_settings
from producer.profile_card.component import render_profile_header
from producer.utils.constants import PRODUCER_NAME, TABS

def run():
    """Main entry point for producer portal"""
    
    # Render sidebar with profile and navigation
    with st.sidebar:
        render_profile_header()
        st.markdown("---")
        
        # Navigation
        selected = st.radio(
            "Navigation",
            TABS,
            format_func=lambda x: TABS[x],
            label_visibility="collapsed",
            key="producer_nav"
        )
        
        st.markdown("---")
        # Quick sidebar stats
        st.metric("Active Orders", "24", "+3 today")
        st.caption("Last updated: Just now")
        st.markdown("---")
        
        # AI Assistant toggle
        if st.checkbox("🤖 Show AI Assistant", value=False):
            st.session_state.show_ai = True
        else:
            st.session_state.show_ai = False
    
    # Route to selected view
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
    
    # Show AI Assistant if toggled
    if st.session_state.get("show_ai", False):
        from producer.ai_assistant.chat import assistant
        with st.expander("🤖 AI Assistant", expanded=True):
            assistant.render()
