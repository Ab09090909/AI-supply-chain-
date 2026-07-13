"""
Producer Settings - Profile management, notifications, preferences
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from producer.db_helper.db_helper import get_producer_profile, get_producer_id, get_notifications

SETTINGS_CSS = """
<style>
    .settings-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border-radius: 14px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 4px 24px rgba(0,0,0,0.18);
        margin-bottom: 1.2rem;
    }
    .settings-card h3 {
        color: #e2e8f0;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .profile-header {
        display: flex;
        align-items: center;
        gap: 1.2rem;
        margin-bottom: 1.5rem;
    }
    .profile-avatar {
        width: 72px; height: 72px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        color: white;
        font-weight: 700;
        box-shadow: 0 4px 16px rgba(99,102,241,0.3);
    }
    .profile-info .name {
        color: #f1f5f9;
        font-size: 1.3rem;
        font-weight: 700;
    }
    .profile-info .email {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 0.15rem;
    }
    .profile-info .role-badge {
        display: inline-block;
        margin-top: 0.3rem;
        background: rgba(99,102,241,0.15);
        color: #a5b4fc;
        padding: 0.15rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: capitalize;
    }
    .setting-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.8rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .setting-row:last-child {
        border-bottom: none;
    }
    .setting-label {
        color: #cbd5e1;
        font-size: 0.88rem;
    }
    .setting-desc {
        color: #64748b;
        font-size: 0.75rem;
        margin-top: 0.15rem;
    }
    .notif-item {
        display: flex;
        gap: 0.8rem;
        padding: 0.8rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .notif-item:last-child { border-bottom: none; }
    .notif-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        margin-top: 0.4rem;
        flex-shrink: 0;
    }
    .notif-title {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .notif-text {
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 0.15rem;
    }
    .notif-time {
        color: #64748b;
        font-size: 0.72rem;
        margin-top: 0.1rem;
    }
</style>
"""


def render_profile(email: str, producer_id: int):
    profile = get_producer_profile(email)

    st.markdown("""
    <div class="settings-card">
        <h3>Profile</h3>
        <div class="profile-header">
            <div class="profile-avatar">P</div>
            <div class="profile-info">
                <div class="name">Producer</div>
                <div class="email">{email}</div>
                <span class="role-badge">Producer</span>
            </div>
        </div>
    """.format(email=email), unsafe_allow_html=True)

    if profile:
        st.markdown(f"""
        <div style="color:#64748b;font-size:0.78rem;margin-bottom:1rem">
            Member since: {profile.get('created_at', 'N/A')[:10]} | User ID: #{profile.get('id', '?')}
        </div>
        """, unsafe_allow_html=True)

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            company = st.text_input("Company Name", value="Demo Producer Co.", key="set_company")
            phone = st.text_input("Phone", value="+1-555-0100", key="set_phone")
        with col2:
            location = st.text_input("Location", value="New York, USA", key="set_location")
            website = st.text_input("Website", value="https://demo-producer.com", key="set_website")

        bio = st.text_area("Bio", value="Premium agricultural products supplier with 10+ years of experience in organic supply chains.", key="set_bio")

        if st.form_submit_button("Save Profile", use_container_width=True, type="primary"):
            st.success("Profile updated successfully!")

    st.markdown("</div>", unsafe_allow_html=True)


def render_notification_settings():
    st.markdown("""
    <div class="settings-card">
        <h3>Notification Preferences</h3>
    """, unsafe_allow_html=True)

    notif_settings = {
        "email_orders": "Order Notifications",
        "email_orders_desc": "Receive email alerts for new orders and status changes",
        "email_low_stock": "Low Stock Alerts",
        "email_low_stock_desc": "Get notified when products fall below minimum stock levels",
        "email_fraud": "Fraud Alerts",
        "email_fraud_desc": "Instant alerts for flagged transactions and high-risk orders",
        "email_reports": "Weekly Reports",
        "email_reports_desc": "Receive weekly performance summary and analytics digest",
        "email_agreements": "Agreement Updates",
        "email_agreements_desc": "Notifications for new, expiring, or updated B2B agreements",
    }

    defaults = {
        "email_orders": True, "email_low_stock": True,
        "email_fraud": True, "email_reports": False, "email_agreements": True,
    }

    for key in ["email_orders", "email_low_stock", "email_fraud", "email_reports", "email_agreements"]:
        st.markdown(f"""
        <div class="setting-row">
            <div>
                <div class="setting-label">{notif_settings[key]}</div>
                <div class="setting-desc">{notif_settings[key + '_desc']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.toggle(
            "", value=defaults.get(key, True),
            key=f"notif_{key}", label_visibility="collapsed"
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_notification_history(producer_id: int):
    st.markdown("""
    <div class="settings-card">
        <h3>Notification History</h3>
    """, unsafe_allow_html=True)

    notifications = get_notifications(producer_id)
    if not notifications:
        st.info("No notifications yet.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    colors = {"info": "#6366f1", "warning": "#f59e0b", "error": "#ef4444", "success": "#10b981"}
    for n in notifications[:10]:
        dot_color = colors.get(n.get("type", "info"), "#6366f1")
        st.markdown(f"""
        <div class="notif-item">
            <div class="notif-dot" style="background:{dot_color}"></div>
            <div>
                <div class="notif-title">{n.get('title', '')}</div>
                <div class="notif-text">{n.get('message', '')[:100]}</div>
                <div class="notif-time">{n.get('created_at', '')[:16]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_system_settings():
    st.markdown("""
    <div class="settings-card">
        <h3>System Settings</h3>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="setting-row">
        <div>
            <div class="setting-label">Dark Mode</div>
            <div class="setting-desc">Toggle between dark and light theme</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.toggle("", value=True, key="set_dark_mode", label_visibility="collapsed")

    st.markdown("""
    <div class="setting-row">
        <div>
            <div class="setting-label">Auto-Refresh Dashboard</div>
            <div class="setting-desc">Automatically refresh dashboard data every 60 seconds</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.toggle("", value=False, key="set_auto_refresh", label_visibility="collapsed")

    st.markdown("""
    <div class="setting-row">
        <div>
            <div class="setting-label">Compact View</div>
            <div class="setting-desc">Reduce spacing for more data density</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.toggle("", value=False, key="set_compact", label_visibility="collapsed")

    st.markdown('<div style="margin-top:1.5rem"></div>', unsafe_allow_html=True)
    st.subheader("Data Management")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export Data (CSV)", use_container_width=True, key="set_export"):
            st.info("Export functionality - generates CSV of all products and orders.")
    with col2:
        if st.button("Reset Demo Data", use_container_width=True, type="secondary", key="set_reset"):
            st.warning("This will reset all demo data to defaults.")

    st.markdown("</div>", unsafe_allow_html=True)


def render(email: str):
    st.markdown(SETTINGS_CSS, unsafe_allow_html=True)

    producer_id = get_producer_id(email)
    if not producer_id:
        st.error("Producer account not found.")
        return

    st.markdown("""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.2rem">
        <h2 style="color:#e2e8f0;font-size:1.25rem;font-weight:700;display:flex;align-items:center;gap:0.5rem">
            Settings
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Profile", "Notifications", "History", "System"])

    with tab1:
        render_profile(email, producer_id)
    with tab2:
        render_notification_settings()
    with tab3:
        render_notification_history(producer_id)
    with tab4:
        render_system_settings()
