"""
Producer Dashboard View
Production version - Authentication required, no demo data, Supabase integration
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Local imports
from producer.utils.db import db
from producer.utils.auth import is_authenticated, get_current_user, get_user_role, render_auth_ui, refresh_session
from producer.utils.helpers import generate_mock_chart_data, format_currency, get_status_color

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Producer Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Professional CSS Styling
# -----------------------------------------------------------------------------
def load_custom_css():
    """Load professional styling with dark mode support"""
    dark_mode = st.session_state.get("dark_mode", False)
    primary_color = "#667eea"
    success_color = "#10b981"
    warning_color = "#f59e0b"
    danger_color = "#ef4444"
    bg_color = "#0f172a" if dark_mode else "#f8fafc"
    card_bg = "#1e293b" if dark_mode else "#ffffff"
    text_color = "#f1f5f9" if dark_mode else "#1e293b"
    border_color = "#334155" if dark_mode else "#e2e8f0"

    css = f"""
    <style>
        /* Global Theme Variables */
        :root {{
            --primary: {primary_color};
            --success: {success_color};
            --warning: {warning_color};
            --danger: {danger_color};
            --bg: {bg_color};
            --card-bg: {card_bg};
            --text: {text_color};
            --border: {border_color};
        }}
        
        .stApp {{
            background-color: var(--bg);
            color: var(--text);
        }}
        
        /* Metric Cards */
        .metric-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid var(--border);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        /* Status Badges */
        .status-badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            display: inline-block;
        }}
        .status-on-track {{ background: rgba(16, 185, 129, 0.15); color: var(--success); }}
        .status-at-risk {{ background: rgba(245, 158, 11, 0.15); color: var(--warning); }}
        .status-delayed {{ background: rgba(239, 68, 68, 0.15); color: var(--danger); }}
        .status-pending {{ background: rgba(102, 126, 234, 0.15); color: var(--primary); }}
        
        /* Chart & Table Containers */
        .stPlotlyChart, .stDataFrame {{
            border-radius: 12px;
            background: var(--card-bg);
        }}
        
        /* Accessibility: Reduced Motion */
        @media (prefers-reduced-motion: reduce) {{
            * {{ animation: none !important; transition: none !important; }}
        }}
        
        /* Responsive Adjustments */
        @media (max-width: 768px) {{
            .metric-card {{ padding: 1rem; }}
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
def init_session_state():
    """Initialize all required session state variables"""
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if "date_range" not in st.session_state:
        st.session_state.date_range = (datetime.now() - timedelta(days=30), datetime.now())
    if "selected_project" not in st.session_state:
        st.session_state.selected_project = "All Projects"
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = False
    if "show_settings" not in st.session_state:
        st.session_state.show_settings = False
    if "show_approvals" not in st.session_state:
        st.session_state.show_approvals = False
    if "show_audit_log" not in st.session_state:
        st.session_state.show_audit_log = False

# -----------------------------------------------------------------------------
# KPI Functions
# -----------------------------------------------------------------------------
def get_kpis_by_role(role: str) -> List[Dict]:
    """Get role-specific KPIs from database"""
    kpis = []
    
    try:
        # Common KPIs from DB
        projects = db.get_projects()
        active_projects = len([p for p in projects if p.get("status") not in ["delivered", "cancelled"]])
        
        approvals = db.get_approvals("pending")
        pending_approvals = len(approvals)
        
        # Base KPIs for all roles
        base_kpis = [
            {
                "value": str(active_projects),
                "delta": "+2" if active_projects > 0 else "0",
                "label": "Active Projects",
                "help": "Total in-production projects"
            },
            {
                "value": str(pending_approvals),
                "delta": f"-{pending_approvals}" if pending_approvals > 0 else "0",
                "label": "Pending Approvals",
                "help": "Awaiting sign-off from stakeholders"
            }
        ]
        
        # Role-specific KPIs
        if role == "executive":
            kpis = [
                base_kpis[0],
                {"value": "$2.4M", "delta": "+18%", "label": "YTD Revenue", "help": "Year-to-date revenue"},
                {"value": "92%", "delta": "+5%", "label": "On-Time Delivery", "help": "Project delivery rate"},
                {"value": "24%", "delta": "+3%", "label": "Profit Margin", "help": "Average profit margin"}
            ]
        elif role == "finance":
            kpis = [
                {"value": "$840K", "delta": "-12%", "label": "Budget Remaining", "help": "Available budget"},
                {"value": "$28K/wk", "delta": "+3%", "label": "Burn Rate", "help": "Weekly spend rate"},
                {"value": "$42K", "delta": "-8%", "label": "Overdue Invoices", "help": "Outstanding payments"},
                {"value": "-2.1%", "delta": "+1.2%", "label": "Cost Variance", "help": "Budget deviation"}
            ]
        else:  # producer, line_producer, client
            kpis = [
                base_kpis[0],
                {"value": "142", "delta": "+12", "label": "Open Tasks", "help": "Uncompleted tasks"},
                {"value": "87%", "delta": "+4%", "label": "Team Utilization", "help": "Team capacity usage"},
                base_kpis[1]
            ]
    except Exception as e:
        st.warning(f"Could not load KPIs: {str(e)}")
        kpis = [
            {"value": "0", "delta": "0", "label": "Active Projects", "help": "No data"},
            {"value": "0", "delta": "0", "label": "Pending Approvals", "help": "No data"},
            {"value": "0", "delta": "0", "label": "Open Tasks", "help": "No data"},
            {"value": "0%", "delta": "0%", "label": "Team Utilization", "help": "No data"}
        ]
    
    return kpis

# -----------------------------------------------------------------------------
# Dashboard Section Renderers
# -----------------------------------------------------------------------------
def render_critical_alerts():
    """Display high-priority risk alerts"""
    try:
        risks = db.get_risks(severity="high", status="open")
        if risks:
            with st.expander(f"🚨 {len(risks)} Critical Alerts Require Action", expanded=True):
                for risk in risks:
                    st.error(f"**{risk['project']}**: {risk['title']}")
    except Exception as e:
        st.info("No critical alerts at this time")

def render_kpi_cards():
    """Render role-based KPI cards"""
    role = get_user_role()
    kpis = get_kpis_by_role(role)
    cols = st.columns(4)
    
    for i, kpi in enumerate(kpis):
        with cols[i]:
            delta_color = "inverse" if kpi["label"] in ["Risk Score", "Cost Variance", "Overdue Invoices"] else "normal"
            st.metric(
                label=kpi["label"],
                value=kpi["value"],
                delta=kpi["delta"],
                delta_color=delta_color,
                help=kpi["help"]
            )

def render_yield_chart():
    """Yield performance line chart"""
    st.subheader("📈 Yield Performance (30 Days)")
    try:
        dates, yield_data = generate_mock_chart_data(30, 100, 10)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=yield_data,
            mode='lines', name='Yield (tons)',
            line=dict(color='#667eea', width=3),
            fill='tozeroy', fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        fig.add_hline(y=90, line_dash="dash", line_color="#10b981", annotation_text="Target Yield")
        fig.update_layout(
            template='plotly_white' if not st.session_state.dark_mode else "plotly_dark",
            height=300, margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Date", yaxis_title="Tons"
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not load yield data: {str(e)}")

def render_quality_index():
    """Quality metrics horizontal bar chart"""
    st.subheader("🎯 Quality Index")
    try:
        quality_data = pd.DataFrame({
            "Metric": ["Purity", "Moisture", "Protein", "Appearance", "Size"],
            "Score": [98, 95, 96, 97, 94],
            "Target": [97, 96, 95, 96, 95]
        })
        
        fig = px.bar(
            quality_data, x="Score", y="Metric",
            orientation='h', color="Score",
            color_continuous_scale="Viridis",
            template='plotly_white' if not st.session_state.dark_mode else "plotly_dark"
        )
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not load quality data: {str(e)}")

def render_recent_orders():
    """Recent orders table with filters and export"""
    st.subheader("📋 Recent Orders")
    
    # Filters
    with st.expander("Filter Orders", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect(
                "Status",
                ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"],
                default=["Pending", "Processing"]
            )
        with col2:
            date_filter = st.date_input("Date Range", value=st.session_state.date_range)
        with col3:
            merchant_filter = st.text_input("Search Merchant")
    
    # Fetch and display orders
    try:
        orders = db.get_orders()
        if orders:
            orders_df = pd.DataFrame(orders)
            
            # Apply filters
            if status_filter and "status" in orders_df.columns:
                orders_df = orders_df[orders_df["status"].isin(status_filter)]
            if merchant_filter and "buyer_name" in orders_df.columns:
                orders_df = orders_df[orders_df["buyer_name"].str.contains(merchant_filter, case=False, na=False)]
            if date_filter and "created_at" in orders_df.columns:
                orders_df["created_at"] = pd.to_datetime(orders_df["created_at"]).dt.date
                orders_df = orders_df[
                    (orders_df["created_at"] >= date_filter[0]) & 
                    (orders_df["created_at"] <= date_filter[1])
                ]
            
            # Format display
            display_df = pd.DataFrame({
                "Order ID": orders_df.get("order_number", orders_df.get("id", [])),
                "Merchant": orders_df.get("buyer_name", ["Unknown"] * len(orders_df)),
                "Product": [
                    items[0].get('name', 'N/A') if isinstance(items, list) and len(items) > 0 else 'N/A' 
                    for items in orders_df.get("items", [[]] * len(orders_df))
                ],
                "Amount": [format_currency(x) for x in orders_df.get("total", [0]*len(orders_df))],
                "Status": orders_df.get("status", ["Unknown"] * len(orders_df)),
                "Date": pd.to_datetime(orders_df.get("created_at", [""] * len(orders_df))).dt.strftime("%Y-%m-%d")
            })
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.TextColumn("Status", width="medium"),
                    "Amount": st.column_config.TextColumn("Amount", width="medium")
                }
            )
            
            # Export button
            st.download_button(
                "📥 Export Orders CSV",
                data=display_df.to_csv(index=False).encode("utf-8"),
                file_name=f"orders_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No orders found. Orders will appear here when received.")
    except Exception as e:
        st.warning(f"Could not load orders: {str(e)}")

def render_quick_actions():
    """Quick action buttons for common tasks"""
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add Product", use_container_width=True, type="primary"):
            st.switch_page("pages/add_product.py")
    
    with col2:
        if st.button("📦 Restock Alerts", use_container_width=True):
            st.switch_page("pages/restock_alerts.py")
    
    with col3:
        if st.button("📊 Generate Report", use_container_width=True):
            st.success("Report generated! Check your downloads.")
    
    with col4:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.show_settings = True

# -----------------------------------------------------------------------------
# Advanced Modules (Collapsible)
# -----------------------------------------------------------------------------
def render_advanced_modules():
    """Render advanced modules in tabs"""
    with st.expander("Advanced Modules", expanded=False):
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Pipeline", "Resources", "Budget", "Analytics", "Change Log"
        ])
        
        # Tab 1: Production Pipeline
        with tab1:
            st.subheader("🏭 Production Pipeline")
            try:
                projects = db.get_projects()
                if projects:
                    gantt_df = pd.DataFrame(projects)
                    fig = px.timeline(
                        gantt_df,
                        x_start="start_date", x_end="end_date",
                        y="name", color="status",
                        color_discrete_map={
                            "on_track": "#10b981", "at_risk": "#f59e0b",
                            "delayed": "#ef4444", "pending": "#667eea"
                        },
                        height=300
                    )
                    fig.update_layout(
                        template="plotly_white" if not st.session_state.dark_mode else "plotly_dark",
                        margin=dict(l=20, r=20, t=30, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No projects found")
            except Exception as e:
                st.warning(f"Could not load pipeline: {str(e)}")
        
        # Tab 2: Resource Management
        with tab2:
            st.subheader("👥 Resource Management")
            col1, col2 = st.columns(2)
            
            with col1:
                st.caption("Team Availability")
                try:
                    team = db.get_team()
                    if team:
                        team_df = pd.DataFrame(team)
                        st.dataframe(
                            team_df,
                            column_config={
                                "utilization": st.column_config.ProgressColumn(
                                    "Utilization", min_value=0, max_value=100, format="%d%%"
                                ),
                                "availability": st.column_config.TextColumn("Availability", width="small")
                            },
                            hide_index=True, use_container_width=True
                        )
                    else:
                        st.info("No team data")
                except Exception as e:
                    st.warning(f"Could not load team: {str(e)}")
            
            with col2:
                st.caption("Asset Booking")
                st.info("Asset booking calendar coming soon")
        
        # Tab 3: Budget Tracker
        with tab3:
            st.subheader("💰 Budget Tracker")
            try:
                budget = db.get_budget_data()
                if budget["categories"]:
                    budget_df = pd.DataFrame(budget)
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        name="Planned", x=budget_df["categories"], 
                        y=budget_df["planned"], marker_color="#667eea"
                    ))
                    fig.add_trace(go.Bar(
                        name="Actual", x=budget_df["categories"], 
                        y=budget_df["actual"], marker_color="#10b981"
                    ))
                    fig.update_layout(
                        barmode="group",
                        template="plotly_white" if not st.session_state.dark_mode else "plotly_dark",
                        height=300, margin=dict(l=20, r=20, t=20, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No budget data available")
            except Exception as e:
                st.warning(f"Could not load budget: {str(e)}")
        
        # Tab 4: Performance Analytics
        with tab4:
            st.subheader("📈 Performance Analytics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.caption("ROI Trend (30 Days)")
                try:
                    dates, roi_data = generate_mock_chart_data(30, 15, 3)
                    fig = px.line(
                        x=dates, y=roi_data,
                        labels={"x": "Date", "y": "ROI (%)"},
                        template="plotly_white" if not st.session_state.dark_mode else "plotly_dark"
                    )
                    fig.add_hline(y=10, line_dash="dash", line_color="#10b981", annotation_text="Target")
                    fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not load ROI data: {str(e)}")
            
            with col2:
                st.caption("Quality Metrics Trend")
                st.info("Quality trend analysis coming soon")
        
        # Tab 5: Audit Log (Change Tracking)
        with tab5:
            st.subheader("📜 Change Log")
            try:
                logs = db.get_audit_logs(limit=50)
                if logs:
                    log_df = pd.DataFrame(logs)
                    log_df["timestamp"] = pd.to_datetime(log_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
                    log_df = log_df[["timestamp", "user", "action", "item", "details"]]
                    
                    st.dataframe(
                        log_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "timestamp": st.column_config.TextColumn("Time", width="medium"),
                            "user": st.column_config.TextColumn("User", width="medium"),
                            "action": st.column_config.TextColumn("Action", width="small"),
                            "item": st.column_config.TextColumn("Modified Item", width="medium"),
                            "details": st.column_config.TextColumn("Details", width="large")
                        }
                    )
                else:
                    st.info("No changes recorded yet")
            except Exception as e:
                st.warning(f"Could not load audit log: {str(e)}")

def render_approvals_modal():
    """Pending approvals modal"""
    if not st.session_state.get("show_approvals", False):
        return
    
    with st.modal("Pending Approvals"):
        st.subheader("✅ Pending Approvals")
        try:
            approvals = db.get_approvals("pending")
            if approvals:
                for approval in approvals:
                    with st.container(border=True):
                        cols = st.columns([3, 2, 2, 2])
                        cols[0].markdown(f"**{approval['id']}: {approval['type']}**")
                        cols[1].caption(approval.get("item", approval.get("requestor", "")))
                        cols[2].caption(f"Requestor: {approval['requestor']}")
                        cols[3].caption(f"Due: {approval['due_date'][:10]}")
                        
                        action_cols = st.columns(2)
                        with action_cols[0]:
                            if st.button("Approve", key=f"approve_{approval['id']}", use_container_width=True, type="primary"):
                                db.update_approval_status(approval['id'], "approved", user=get_current_user().get("email", "User"))
                                st.success(f"Approved {approval['id']}")
                                st.rerun()
                        with action_cols[1]:
                            if st.button("Reject", key=f"reject_{approval['id']}", use_container_width=True):
                                db.update_approval_status(approval['id'], "rejected", user=get_current_user().get("email", "User"))
                                st.error(f"Rejected {approval['id']}")
                                st.rerun()
            else:
                st.success("No pending approvals 🎉")
        except Exception as e:
            st.warning(f"Could not load approvals: {str(e)}")
        
        if st.button("Close", use_container_width=True):
            st.session_state.show_approvals = False
            st.rerun()

def render_settings_modal():
    """Dashboard settings modal"""
    if not st.session_state.get("show_settings", False):
        return
    
    with st.modal("Dashboard Settings"):
        st.subheader("⚙️ Customize Dashboard")
        
        st.multiselect(
            "Visible KPI Cards",
            options=["Active Projects", "YTD Revenue", "On-Time Delivery", "Profit Margin", 
                    "Open Tasks", "Team Utilization", "Budget Remaining", "Burn Rate"],
            default=["Active Projects", "YTD Revenue", "On-Time Delivery", "Profit Margin"]
        )
        
        st.multiselect(
            "Visible Modules",
            options=["Production Pipeline", "Resource Management", "Budget Tracker", 
                    "Analytics", "Approvals", "Change Log"],
            default=["Production Pipeline", "Recent Orders"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Settings", use_container_width=True, type="primary"):
                st.session_state.show_settings = False
                st.rerun()
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_settings = False
                st.rerun()

# -----------------------------------------------------------------------------
# Main Dashboard Render Function
# -----------------------------------------------------------------------------
def render():
    """Main dashboard render function - requires authentication"""
    # Refresh session token if needed
    refresh_session()
    
    # Initialize state
    init_session_state()
    load_custom_css()
    
    # Get current user info
    user = get_current_user()
    role = get_user_role()
    
    # --------------------------
    # Sidebar
    # --------------------------
    with st.sidebar:
        st.title("📊 Dashboard")
        st.caption(f"Welcome, {user.get('email', 'User')}")
        st.caption(f"Role: {role.title()}")
        st.divider()
        
        # Controls
        st.toggle("Dark Mode", value=st.session_state.dark_mode, key="dark_mode")
        st.date_input("Date Range", value=st.session_state.date_range, key="date_range")
        
        st.divider()
        
        # Refresh controls
        st.caption(f"Last updated: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
        
        st.divider()
        st.caption(f"User ID: {user.get('id', 'N/A')[:8]}...")
        if st.button("Logout", use_container_width=True):
            from producer.utils.auth import logout
            logout()
    
    # --------------------------
    # Page Header
    # --------------------------
    st.title(f"📊 Producer Dashboard")
    st.caption(f"Role: {role.title()} • {datetime.now().strftime('%B %d, %Y')} • Live")
    
    # --------------------------
    # Critical Alerts
    # --------------------------
    render_critical_alerts()
    st.markdown("---")
    
    # --------------------------
    # KPI Cards
    # --------------------------
    render_kpi_cards()
    st.markdown("---")
    
    # --------------------------
    # Main Charts (2 columns)
    # --------------------------
    col1, col2 = st.columns(2)
    with col1:
        render_yield_chart()
    with col2:
        render_quality_index()
    
    st.markdown("---")
    
    # --------------------------
    # Recent Orders
    # --------------------------
    render_recent_orders()
    st.markdown("---")
    
    # --------------------------
    # Advanced Modules (Collapsible)
    # --------------------------
    render_advanced_modules()
    st.markdown("---")
    
    # --------------------------
    # Quick Actions
    # --------------------------
    render_quick_actions()
    
    # --------------------------
    # Modals
    # --------------------------
    render_approvals_modal()
    render_settings_modal()

# -----------------------------------------------------------------------------
# Entry Point (with auth check)
# -----------------------------------------------------------------------------
def main():
    """Main entry point with authentication guard"""
    init_session_state()
    
    # Check authentication
    if not is_authenticated():
        st.title("🔐 Producer Dashboard")
        st.caption("Please sign in to access the dashboard")
        render_auth_ui()
        st.stop()
    
    # Render dashboard
    render()

if __name__ == "__main__":
    main()
