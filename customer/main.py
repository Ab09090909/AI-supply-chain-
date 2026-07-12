"""
Customer Portal - Main Entry Point
"""
import streamlit as st

CUSTOMER_NAME = "John Consumer"
TABS = {
    "home": "🏠 Home",
    "marketplace": "🛍️ Marketplace",
    "recommendations": "💡 Recommendations",
    "favorites": "💝 Favorites"
}

def run():
    with st.sidebar:
        st.markdown(f"<h1 style='text-align: center; font-size: 3rem;'>🛍️</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{CUSTOMER_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #666;'>Customer Store</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.subheader("Navigation")
        selected = st.radio(
            "Go to",
            list(TABS.keys()),
            format_func=lambda x: TABS[x],
            label_visibility="collapsed",
            key="customer_navigation"
        )
        
        st.markdown("---")
        st.metric("Cart Items", "3", "+1")
        
        st.markdown("---")
        show_ai = st.checkbox("🤖 AI Assistant", value=False)
        st.session_state.show_ai = show_ai
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    st.title(f"{TABS[selected]}")
    
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

def render_home():
    st.header("Home")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🌾 Fresh Grains")
        st.write("Organically grown wheat and rice")
    with col2:
        st.markdown("### 🥛 Dairy Products")
        st.write("Fresh from the farm daily")
    with col3:
        st.markdown("### 🍎 Organic Fruits")
        st.write("Hand-picked seasonal selections")

def render_marketplace():
    st.header("Marketplace")
    st.write("Browse all products")

def render_recommendations():
    st.header("Recommendations")
    st.write("Personalized for you")

def render_favorites():
    st.header("Favorites")
    st.write("Your saved items")
