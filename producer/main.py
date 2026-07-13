"""
Producer Portal - Main entry point with professional sidebar navigation
Routes to: Dashboard, Inventory, Marketplace, AI Insights, AI Assistant, Settings
"""
import streamlit as st
import sys
from pathlib import Path

# CRITICAL: No st.set_page_config() here — it's already called in app.py

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ===================================================================
# SIDEBAR STYLING
# ===================================================================
SIDEBAR_CSS = """
<style>
    /* Hide default Streamlit sidebar elements */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c1220 0%, #0f172a 100%);
    }
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 3px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4);
    }

    /* Navigation Items */
    .nav-section-label {
        color: #475569;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 700;
        padding: 0.8rem 1rem 0.3rem 1rem;
        margin-top: 0.5rem;
    }
    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.55rem 1rem;
        margin: 0.1rem 0.5rem;
        border-radius: 8px;
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.15s;
        text-decoration: none;
    }
    .nav-item:hover {
        background: rgba(99,102,241,0.08);
        color: #e2e8f0;
    }
    .nav-item.active {
        background: rgba(99,102,241,0.12);
        color: #a5b4fc;
        font-weight: 600;
    }
    .nav-item .nav-icon {
        font-size: 1rem;
        width: 1.4rem;
        text-align: center;
    }

    /* Sidebar Header */
    .sidebar-header {
        padding: 1.2rem 1rem 0.5rem 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 0.5rem;
    }
    .sidebar-brand {
        color: #f1f5f9;
        font-size: 1rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .sidebar-role {
        color: #6366f1;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        background: rgba(99,102,241,0.12);
        padding: 0.1rem 0.5rem;
        border-radius: 4px;
        margin-top: 0.4rem;
        display: inline-block;
    }
    .sidebar-email {
        color: #64748b;
        font-size: 0.78rem;
        margin-top: 0.3rem;
    }

    /* Sidebar Footer */
    .sidebar-footer {
        position: absolute;
        bottom: 0;
        left: 0; right: 0;
        padding: 0.8rem 1rem;
        border-top: 1px solid rgba(255,255,255,0.06);
    }

    /* Main content area */
    .main-content {
        padding-top: 0.5rem;
    }

    /* Streamlit hide default menu/radio */
    [data-testid="stSidebar"] [data-testid="stRadio"] {
        display: none;
    }
</style>
"""

# Global dark page config for the main area
PAGE_CSS = """
<style>
    /* Global dark background */
    .stApp {
        background-color: #0b1120 !important;
    }
    [data-testid="stMain"] {
        background-color: #0b1120 !important;
        padding-top: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Style all streamlit inputs/ widgets for dark theme */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border-color: #334155 !important;
    }
    .stTextArea > div > div > textarea {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    .stButton > button[kind="secondary"] {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.2rem;
        background: rgba(15,23,42,0.5);
        border-radius: 10px;
        padding: 0.2rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 0.4rem 1rem !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(99,102,241,0.15) !important;
        color: #a5b4fc !important;
    }

    /* Form container */
    .stForm {
        background: transparent !important;
        border: none !important;
    }

    /* Chat input */
    .stChatInputContainer {
        border-color: #334155 !important;
    }

    /* Info/Success/Error boxes */
    .stAlert {
        border-radius: 10px !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-size: 0.9rem !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }

    /* Selectbox dropdown */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
    }
</style>
"""

# ===================================================================
# NAVIGATION CONFIG
# ===================================================================
NAV_ITEMS = [
    {"id": "dashboard",    "icon": "📊", "label": "Dashboard",     "section": "Main"},
    {"id": "inventory",    "icon": "📦", "label": "Inventory",     "section": "Main"},
    {"id": "marketplace",  "icon": "🏪", "label": "Marketplace",   "section": "Main"},
    {"id": "ai_insights",  "icon": "🤖", "label": "AI Insights",   "section": "Intelligence"},
    {"id": "ai_assistant", "icon": "💬", "label": "AI Assistant",  "section": "Intelligence"},
    {"id": "settings",     "icon": "⚙️", "label": "Settings",      "section": "System"},
]


def render_sidebar(email: str):
    """Render professional sidebar with navigation."""
    # Header
    st.markdown(f"""
    <div class="sidebar-header">
        <div class="sidebar-brand">📦 AI Supply Chain</div>
        <div class="sidebar-role">Producer Portal</div>
        <div class="sidebar-email">{email}</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation grouped by section
    current_section = None
    for item in NAV_ITEMS:
        if item["section"] != current_section:
            current_section = item["section"]
            st.markdown(f'<div class="nav-section-label">{current_section}</div>', unsafe_allow_html=True)

        active = "active" if st.session_state.get("producer_page") == item["id"] else ""
        st.markdown(
            f'<div class="nav-item {active}">'
            f'<span class="nav-icon">{item["icon"]}</span>'
            f'{item["label"]}</div>',
            unsafe_allow_html=True
        )

    # Selection radio (hidden with CSS, but functional for Streamlit)
    menu_labels = [item["label"] for item in NAV_ITEMS]
    menu_keys = [item["id"] for item in NAV_ITEMS]
    current_idx = 0
    if "producer_page" in st.session_state and st.session_state.producer_page in menu_keys:
        current_idx = menu_keys.index(st.session_state.producer_page)

    selected_label = st.sidebar.radio(
        "Navigation", menu_labels, index=current_idx, label_visibility="collapsed"
    )

    # Map selection to page id
    selected_id = menu_keys[menu_labels.index(selected_label)]
    st.session_state.producer_page = selected_id

    # Sidebar footer
    st.sidebar.markdown("""
    <div class="sidebar-footer">
        <div style="color:#475569;font-size:0.7rem;text-align:center">
            AI Supply Chain v1.0<br>
            Built with Streamlit + ML
        </div>
    </div>
    """, unsafe_allow_html=True)


def run():
    """Main entry point for the producer portal."""
    # Inject CSS
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)
    st.markdown(PAGE_CSS, unsafe_allow_html=True)

    # Get email from session state
    email = st.session_state.get("user_email", "producer@demo.com")

    # Initialize page state
    if "producer_page" not in st.session_state:
        st.session_state.producer_page = "dashboard"

    # Render sidebar
    render_sidebar(email)

    # Route to page
    page = st.session_state.producer_page

    try:
        if page == "dashboard":
            from producer.dashboard.dashboard import render as render_dashboard
            render_dashboard(email)
        elif page == "inventory":
            from producer.inventory.inventory import render as render_inventory
            render_inventory(email)
        elif page == "marketplace":
            from producer.marketplace.marketplace import render as render_marketplace
            render_marketplace(email)
        elif page == "ai_insights":
            from producer.ai_insights.ai_insights import render as render_ai
            render_ai(email)
        elif page == "ai_assistant":
            from producer.ai_assistant.ai_assistant import render as render_assistant
            render_assistant(email)
        elif page == "settings":
            from producer.settings.settings import render as render_settings
            render_settings(email)
        else:
            from producer.dashboard.dashboard import render as render_dashboard
            render_dashboard(email)
    except Exception as e:
        st.error(f"Error loading page: {e}")
        import traceback
        st.code(traceback.format_exc())
