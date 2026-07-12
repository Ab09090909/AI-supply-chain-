"""
AI Supply Chain Platform - Root Entry Point
"""
import streamlit as st
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="AI Supply Chain Platform",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default Streamlit elements
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def main():
    # NO SIDEBAR HERE - each role handles its own sidebar
    role = st.radio(
        "Select Portal",
        ["Producer", "Merchant", "Customer", "Admin"],
        format_func=lambda x: {
            "Producer": "🌾 Producer Portal",
            "Merchant": "🛒 Merchant Portal",
            "Customer": "🛍️ Customer Store",
            "Admin": "⚙️ Admin Console"
        }[x],
        label_visibility="visible",
        horizontal=True
    )
    
    st.markdown("---")
    
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
        st.error(f"Portal loading error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
