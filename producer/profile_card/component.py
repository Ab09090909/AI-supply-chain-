"""
Producer Profile Card Component
"""
import streamlit as st
from producer.utils.constants import PRODUCER_NAME

def render_profile_header():
    """Render producer profile header - NO st.sidebar context inside!"""
    # REMOVED: with st.sidebar:
    # Already called from within st.sidebar context in main.py
    
    # Avatar
    st.markdown(f"""
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
        margin: 0 auto 1rem auto;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    ">{PRODUCER_NAME[0]}</div>
    """, unsafe_allow_html=True)
    
    # Name and role
    st.markdown(f"<h2 style='text-align: center; margin: 0; font-size: 1.2rem;'>{PRODUCER_NAME}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #666; font-size: 0.9rem;'>Producer Portal</p>", unsafe_allow_html=True)
    
    # Stats row
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Orders", "24", "+3")
    with col2:
        st.metric("Rating", "4.8", "⭐")
    
    st.markdown("---")
