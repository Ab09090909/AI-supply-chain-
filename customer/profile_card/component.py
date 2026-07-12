"""
Customer Profile Card Component
"""
import streamlit as st
from customer.utils.constants import CUSTOMER_NAME

def render_profile_header():
    """Render customer profile header"""
    # NO st.sidebar context here!
    
    st.markdown(f"""
    <div style="
        width: 80px; 
        height: 80px; 
        background: linear-gradient(135deg, #28a745, #20c997); 
        border-radius: 50%; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        color: white; 
        font-weight: bold; 
        font-size: 32px;
        margin: 0 auto 1rem auto;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
    ">{CUSTOMER_NAME[0]}</div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='text-align: center; margin: 0; font-size: 1.2rem;'>{CUSTOMER_NAME}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #666; font-size: 0.9rem;'>Customer Store</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Orders", "8", "+1")
    with col2:
        st.metric("Favorites", "12")
    
    st.markdown("---")
