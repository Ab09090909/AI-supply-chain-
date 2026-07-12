"""
Producer Sidebar - Separate file for clean context
"""
import streamlit as st

def render():
    """Render the complete producer sidebar"""
    
    # Profile Header
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
    st.metric("Revenue", "$45.2K", "+5.3%")
    
    st.markdown("---")
    
    # AI Assistant toggle
    show_ai = st.checkbox("🤖 AI Assistant", value=False)
    st.session_state.show_ai = show_ai
    
    st.markdown("---")
    
    # Logout
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()
    
    return page
