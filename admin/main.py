"""
Admin Portal - Main Entry Point
"""
import streamlit as st

ADMIN_NAME = "System Admin"
TABS = {
    "dashboard": "📊 Dashboard",
    "users": "👥 Users",
    "fraud": "🚨 Fraud Monitor",
    "ml": "🤖 ML Performance",
    "reports": "📄 Reports"
}

def run():
    with st.sidebar:
        st.markdown(f"<h1 style='text-align: center; font-size: 3rem;'>⚙️</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{ADMIN_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #666;'>Admin Console</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.subheader("Navigation")
        selected = st.radio(
            "Go to",
            list(TABS.keys()),
            format_func=lambda x: TABS[x],
            label_visibility="collapsed",
            key="admin_navigation"
        )
        
        st.markdown("---")
        st.metric("System Health", "98.5%", "+0.2%")
        st.metric("Active Users", "89")
        
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

def render_dashboard():
    st.header("System Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", "1,245", "+12")
    with col2:
        st.metric("Active Sessions", "89")
    with col3:
        st.metric("System Health", "98.5%")
    with col4:
        st.metric("Fraud Alerts", "3")

def render_users():
    st.header("User Management")
    st.write("Manage platform users")

def render_fraud():
    st.header("Fraud Monitoring")
    st.write("Real-time fraud detection")

def render_ml():
    st.header("ML Performance")
    st.write("Model monitoring and accuracy")

def render_reports():
    st.header("Reports")
    st.write("Generate and download reports")
