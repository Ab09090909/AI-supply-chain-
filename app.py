"""
AI Supply Chain Platform - Root Entry Point
Routes to role-specific portals. NO business logic here.
"""
import streamlit as st
import importlib
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure page
st.set_page_config(
    page_title="AI Supply Chain Platform",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default Streamlit UI elements
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def main():
    """Main router - loads role-specific module"""
    
    # Professional sidebar branding
    with st.sidebar:
        st.title("🔗 AI Supply Chain")
        st.caption("v2.1.0 | Production Ready")
        st.markdown("---")
        
        # Role selector
        st.subheader("Select Portal")
        role = st.radio(
            "Choose your access level",
            ["Producer", "Merchant", "Customer", "Admin"],
            format_func=lambda x: {
                "Producer": "🌾 Producer Portal",
                "Merchant": "🛒 Merchant Portal",
                "Customer": "🛍️ Customer Store",
                "Admin": "⚙️ Admin Console"
            }[x],
            label_visibility="collapsed",
            key="role_selector"
        )
        
        st.markdown("---")
        st.caption("💡 Each portal is fully independent")
        st.caption("🔒 Secure role-based access")
    
    # Route to selected role
    role_modules = {
        "Producer": "producer.main",
        "Merchant": "merchant.main",
        "Customer": "customer.main",
        "Admin": "admin.main"
    }
    
    try:
        module = importlib.import_module(role_modules[role])
        module.run()
    except Exception as e:
        st.error(f"❌ Portal loading error: {str(e)}")
        st.info(f"Ensure the {role.lower()} folder and main.py exist.")
        
        with st.expander("🔧 Debug Information"):
            import traceback
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
