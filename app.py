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
    initial_sidebar_state="expanded"  # FORCE SIDEBAR OPEN
)

# Force sidebar open with JavaScript (fixes mobile/Streamlit Cloud issues)
st.markdown("""
<script>
// Force sidebar to open on load
window.addEventListener('load', function() {
    setTimeout(function() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar && sidebar.style.display === 'none') {
            sidebar.style.display = 'block';
            sidebar.style.width = '260px';
        }
    }, 100);
});

// Keep sidebar open
window.addEventListener('resize', function() {
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        sidebar.style.display = 'block';
        sidebar.style.width = '260px';
    }
});
</script>
""", unsafe_allow_html=True)

# Hide default Streamlit elements
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
section[data-testid="stSidebar"] {
    width: 260px !important;
    min-width: 260px !important;
}
</style>
""", unsafe_allow_html=True)

def main():
    # Role selector in main area (for mobile friendliness)
    st.markdown("### 🔗 Select Portal")
    role = st.radio(
        "Select your access level",
        ["Producer", "Merchant", "Customer", "Admin"],
        format_func=lambda x: {
            "Producer": "🌾 Producer Portal",
            "Merchant": "🛒 Merchant Portal",
            "Customer": "🛍️ Customer Store",
            "Admin": "⚙️ Admin Console"
        }[x],
        label_visibility="collapsed",
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
