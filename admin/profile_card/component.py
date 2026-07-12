"""
Admin Profile Card Component
"""
import streamlit as st
from admin.utils.constants import ADMIN_NAME

def render_profile_header():
    """Render admin profile header"""
    # NO st.sidebar context here!
    
    st.markdown(f"""
    <div style="
        width: 80px; 
        height: 80px; 
        background: linear-gradient(135deg, #dc3545, #c82333); 
        border-radius: 50%; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        color: white; 
        font-weight: bold; 
        font-size: 32px;
        margin: 0 auto 1rem auto;
        box-shadow: 0 4px 12px rgba(220, 53, 69, 0.4);
    ">{ADMIN_NAME[0]}</div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='text-align: center; margin: 0; font-size: 1.2rem;'>{ADMIN_NAME}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #666; font-size: 0.9rem;'>Admin Console</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Users", "1,245", "+12")
    with col2:
        st.metric("Health", "98.5%", "+0.2%")
    
    st.markdown("---")
