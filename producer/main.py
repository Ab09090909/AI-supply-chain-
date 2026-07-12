def run():
    """Main entry point for producer portal"""
    
    # Entire sidebar is managed here
    with st.sidebar:
        # Profile header (no nested sidebar inside)
        render_profile_header()
        
        # Navigation
        selected = st.radio(
            "Navigation",
            TABS,
            format_func=lambda x: TABS[x],
            label_visibility="collapsed",
            key="producer_nav"
        )
        
        st.markdown("---")
        st.metric("Active Orders", "24", "+3 today")
        st.caption("Last updated: Just now")
        st.markdown("---")
        
        # AI Assistant toggle
        if st.checkbox("🤖 Show AI Assistant", value=False):
            st.session_state.show_ai = True
        else:
            st.session_state.show_ai = False
        
        # Logout
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    # Main content area
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
    
    # AI Assistant overlay (if toggled)
    if st.session_state.get("show_ai", False):
        from producer.ai_assistant.chat import assistant
        with st.expander("🤖 AI Assistant", expanded=True):
            assistant.render()
