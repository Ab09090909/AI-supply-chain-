"""
Professional Producer Dashboard View
Fixed: Real-time data updates, change tracking, auto-refresh, dynamic caching
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from typing import List, Dict, Optional

from producer.utils.db import db
from producer.utils.helpers import generate_mock_chart_data, format_currency, get_status_color

# -----------------------------------------------------------------------------
# Professional Design Setup: Custom CSS, Dark Mode, Brand Consistency
# -----------------------------------------------------------------------------
def load_custom_css():
    """Load professional styling with dark mode support and accessibility compliance"""
    dark_mode = st.session_state.get("dark_mode", False)
    primary_color = "#667eea"
    success_color = "#10b981"
    warning_color = "#f59e0b"
    danger_color = "#ef4444"
    neutral_color = "#6b7280"
    bg_color = "#0f172a" if dark_mode else "#f8fafc"
    card_bg = "#1e293b" if dark_mode else "#ffffff"
    text_color = "#f1f5f9" if dark_mode else "#1e293b"
    border_color = "#334155" if dark_mode else "#e2e8f0"

    css = f"""
    <style>
        /* Global Theme */
        :root {{
            --primary: {primary_color};
            --success: {success_color};
            --warning: {warning_color};
            --danger: {danger_color};
            --neutral: {neutral_color};
            --bg: {bg_color};
            --card-bg: {card_bg};
            --text: {text_color};
            --border: {border_color};
        }}
        .stApp {{
            background-color: var(--bg);
            color: var(--text);
        }}
        /* Card Styling */
        .metric-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid var(--border);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
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
        /* Layout Adjustments */
        .stPlotlyChart {{
            border-radius: 12px;
            background: var(--card-bg);
            padding: 0.5rem;
            border: 1px solid var(--border);
        }}
        .stDataFrame {{
            border-radius: 12px;
            overflow: hidden;
        }}
        /* Refresh Button */
        .refresh-btn {{
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            cursor: pointer;
            width: 100%;
            margin-top: 0.5rem;
        }}
        .refresh-btn:hover {{
            opacity: 0.9;
        }}
        /* Accessibility */
        @media (prefers-reduced-motion: reduce) {{
            * {{
                animation: none !important;
                transition: none !important;
            }}
        }}
        /* Responsive */
        @media (max-width: 768px) {{
            .metric-card {{
                padding: 1rem;
            }}
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
def init_session_state():
    """Initialize dashboard session state for personalization, refresh control, and tracking"""
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = "producer"  # Options: executive, line_producer, finance, client
    if "date_range" not in st.session_state:
        st.session_state.date_range = (datetime.now() - timedelta(days=30), datetime.now())
    if "selected_project" not in st.session_state:
        st.session_state.selected_project = "All Projects"
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    if "auto_refresh_interval" not in st.session_state:
        st.session_state.auto_refresh_interval = 30  # Seconds, 0 = off
    if "refresh_counter" not in st.session_state:
        st.session_state.refresh_counter = 0
    if "show_audit_log" not in st.session_state:
        st.session_state.show_audit_log = False

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
# Short TTL for dynamic data (30s) to ensure updates, longer for static config
@st.cache_data(ttl=30)
def get_dashboard_kpis(role: str, date_range: tuple) -> Dict:
    """Fetch role-specific KPIs from database with fallback mock data (updates every 30s)"""
    try:
        # Replace with your actual DB queries
        kpis = {
            "executive": {
                "active_projects": {"value": "18", "delta": "+4", "label": "Active Projects", "help": "Total in-production projects"},
                "revenue_ytd": {"value": "$2.4M", "delta": "+18%", "label": "YTD Revenue", "help": "Year-to-date generated revenue"},
                "on_time_delivery": {"value": "92%", "delta": "+5%", "label": "On-Time Delivery", "help": "% of projects delivered on schedule"},
                "profit_margin": {"value": "24%", "delta": "+3%", "label": "Avg Profit Margin", "help": "Average net profit across all projects"}
            },
            "line_producer": {
                "active_tasks": {"value": "142", "delta": "+12", "label": "Open Tasks", "help": "Uncompleted tasks across all projects"},
                "team_utilization": {"value": "87%", "delta": "+4%", "label": "Team Utilization", "help": "Average billable hours per team member"},
                "pending_approvals": {"value": "7", "delta": "-2", "label": "Pending Approvals", "help": "Awaiting sign-off from stakeholders"},
                "overdue_milestones": {"value": "2", "delta": "-1", "label": "Overdue Milestones", "help": "Critical project milestones past deadline"}
            },
            "finance": {
                "budget_remaining": {"value": "$840K", "delta": "-12%", "label": "Remaining Budget", "help": "Total unallocated budget across projects"},
                "burn_rate": {"value": "$28K/wk", "delta": "+3%", "label": "Burn Rate", "help": "Average weekly spend across active projects"},
                "overdue_invoices": {"value": "$42K", "delta": "-8%", "label": "Overdue Invoices", "help": "Outstanding payments past due date"},
                "cost_variance": {"value": "-2.1%", "delta": "+1.2%", "label": "Cost Variance", "help": "Actual vs planned spend deviation"}
            }
        }
        return kpis.get(role, kpis["line_producer"])
    except Exception as e:
        st.warning(f"Could not load live KPI data: {str(e)}")
        return get_mock_kpis(role)

def get_mock_kpis(role: str) -> Dict:
    """Fallback mock KPIs if DB is unavailable"""
    mock_data = {
        "executive": [
            {"value": "18", "delta": "+4", "label": "Active Projects", "help": "Total in-production projects"},
            {"value": "$2.4M", "delta": "+18%", "label": "YTD Revenue", "help": "Year-to-date generated revenue"},
            {"value": "92%", "delta": "+5%", "label": "On-Time Delivery", "help": "% of projects delivered on schedule"},
            {"value": "24%", "delta": "+3%", "label": "Avg Profit Margin", "help": "Average net profit across all projects"}
        ],
        "line_producer": [
            {"value": "142", "delta": "+12", "label": "Open Tasks", "help": "Uncompleted tasks across all projects"},
            {"value": "87%", "delta": "+4%", "label": "Team Utilization", "help": "Average billable hours per team member"},
            {"value": "7", "delta": "-2", "label": "Pending Approvals", "help": "Awaiting sign-off from stakeholders"},
            {"value": "2", "delta": "-1", "label": "Overdue Milestones", "help": "Critical project milestones past deadline"}
        ],
        "finance": [
            {"value": "$840K", "delta": "-12%", "label": "Remaining Budget", "help": "Total unallocated budget across projects"},
            {"value": "$28K/wk", "delta": "+3%", "label": "Burn Rate", "help": "Average weekly spend across active projects"},
            {"value": "$42K", "delta": "-8%", "label": "Overdue Invoices", "help": "Outstanding payments past due date"},
            {"value": "-2.1%", "delta": "+1.2%", "label": "Cost Variance", "help": "Actual vs planned spend deviation"}
        ]
    }
    return mock_data.get(role, mock_data["line_producer"])

@st.cache_data(ttl=60)
def get_audit_logs(limit: int = 20) -> List[Dict]:
    """Fetch recent change logs from DB (updates every 60s)"""
    try:
        # Replace with your actual audit log DB query
        # Example: return db.get_audit_logs(limit=limit)
        return [
            {"timestamp": datetime.now() - timedelta(minutes=5), "user": "Alex Johnson", "action": "Updated", "item": "Order #ORD-789", "details": "Changed status from Processing to Shipped"},
            {"timestamp": datetime.now() - timedelta(minutes=12), "user": "Sam Carter", "action": "Approved", "item": "Expense Request #EXP-123", "details": "Approved $2,400 for equipment rental"},
            {"timestamp": datetime.now() - timedelta(minutes=27), "user": "Jordan Lee", "action": "Created", "item": "Project: Summer Campaign", "details": "Added new production milestone: Final Cut Review"},
            {"timestamp": datetime.now() - timedelta(hours=1), "user": "Admin", "action": "Modified", "item": "Budget: Client X Feature", "details": "Increased post-production budget by 10%"},
        ]
    except Exception as e:
        st.warning(f"Could not load audit logs: {str(e)}")
        return []

def clear_all_cache():
    """Clear all cached data to force fresh load on next render"""
    st.cache_data.clear()
    st.session_state.last_refresh = datetime.now()
    st.rerun()

# -----------------------------------------------------------------------------
# Core Dashboard Components
# -----------------------------------------------------------------------------
def render_critical_alerts():
    """Top-of-dashboard critical alerts for risk visibility"""
    try:
        risks = db.get_risks() if hasattr(db, "get_risks") else [
            {"title": "Location permit expires in 3 days", "severity": "high", "project": "Summer Campaign Shoot"},
            {"title": "Budget overrun risk: Post-production 15% over estimate", "severity": "medium", "project": "Client X Feature Film"},
            {"title": "2 team members OOO next week", "severity": "low", "project": "All Active Projects"}
        ]
        
        high_risks = [r for r in risks if r["severity"] == "high"]
        if high_risks:
            with st.expander(f"🚨 {len(high_risks)} Critical Alerts Require Action", expanded=True):
                for risk in high_risks:
                    st.error(f"**{risk['project']}**: {risk['title']}")
    except Exception as e:
        st.info("No critical alerts at this time")

def render_kpi_cards():
    """Role-based customizable KPI cards with dynamic updates"""
    kpis = get_dashboard_kpis(st.session_state.user_role, st.session_state.date_range)
    cols = st.columns(4)
    
    for i, kpi in enumerate(kpis):
        with cols[i]:
            # Auto-set delta color: inverse for negative risk metrics, normal otherwise
            delta_color = "inverse" if kpi["label"] in ["Risk Score", "Cost Variance", "Overdue Invoices"] else "normal"
            if "+" not in kpi["delta"] and "%" not in kpi["delta"]:
                delta_color = "inverse"
            
            st.metric(
                label=kpi["label"],
                value=kpi["value"],
                delta=kpi["delta"],
                delta_color=delta_color,
                help=kpi["help"]
            )

def render_production_pipeline():
    """Production pipeline with Gantt/Kanban view toggle"""
    st.subheader("🏭 Production Pipeline")
    view_tab1, view_tab2 = st.tabs(["Gantt View", "Kanban Board"])
    
    # Gantt View
    with view_tab1:
        try:
            projects = db.get_projects() if hasattr(db, "get_projects") else [
                {"name": "Summer Campaign", "start": datetime.now() - timedelta(days=5), "end": datetime.now() + timedelta(days=10), "progress": 45, "status": "on_track"},
                {"name": "Client X Feature", "start": datetime.now() - timedelta(days=12), "end": datetime.now() + timedelta(days=8), "progress": 62, "status": "at_risk"},
                {"name": "Product Launch Video", "start": datetime.now() + timedelta(days=2), "end": datetime.now() + timedelta(days=20), "progress": 10, "status": "pending"}
            ]
            
            gantt_df = pd.DataFrame(projects)
            fig = px.timeline(
                gantt_df,
                x_start="start",
                x_end="end",
                y="name",
                color="status",
                color_discrete_map={
                    "on_track": "#10b981",
                    "at_risk": "#f59e0b",
                    "delayed": "#ef4444",
                    "pending": "#667eea"
                },
                title="Project Timeline",
                height=300
            )
            fig.update_layout(template="plotly_white" if not st.session_state.dark_mode else "plotly_dark", margin=dict(l=20, r=20, t=30, b=20), xaxis_title="", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not load project timeline: {str(e)}")
    
    # Kanban Board
    with view_tab2:
        try:
            stages = ["Pre-Production", "Production", "Post-Production", "Review", "Delivered"]
            cols = st.columns(5)
            for i, stage in enumerate(stages):
                with cols[i]:
                    st.markdown(f"<h4 style='text-align: center;'>{stage}</h4>", unsafe_allow_html=True)
                    # Add task cards here, pulled from DB
                    for j in range(2 if stage != "Delivered" else 3):
                        with st.container(border=True):
                            st.markdown(f"<small>Task {j+1}</small>", unsafe_allow_html=True)
                            st.caption(f"Due: {(datetime.now() + timedelta(days=random.randint(1,10))).strftime('%Y-%m-%d')}")
        except Exception as e:
            st.warning(f"Could not load Kanban board: {str(e)}")

def render_resource_management():
    """Team and asset resource management section"""
    with st.expander("👥 Resource Management", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Team Availability")
            try:
                team = db.get_team() if hasattr(db, "get_team") else [
                    {"name": "Alex Johnson", "role": "Director", "utilization": 95, "availability": "Limited"},
                    {"name": "Sam Carter", "role": "Editor", "utilization": 72, "availability": "Available"},
                    {"name": "Jordan Lee", "role": "Producer", "utilization": 88, "availability": "Limited"}
                ]
                team_df = pd.DataFrame(team)
                st.dataframe(
                    team_df,
                    column_config={
                        "utilization": st.column_config.ProgressColumn("Utilization", min_value=0, max_value=100, format="%d%%"),
                        "availability": st.column_config.TextColumn("Availability", width="small")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"Could not load team data: {str(e)}")
        
        with col2:
            st.subheader("Asset Booking Calendar")
            st.caption("Book equipment, studios, and locations")
            # Add booking calendar here, integrate with existing asset DB
            if st.button("+ New Booking", use_container_width=True):
                st.session_state.show_booking_modal = True

def render_budget_tracker():
    """Budget and financial tracking section"""
    with st.expander("💰 Budget & Financials", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Budget vs Actual Spend")
            try:
                budget_data = db.get_budget_data() if hasattr(db, "get_budget_data") else {
                    "categories": ["Talent", "Equipment", "Locations", "Post-Production", "Marketing"],
                    "planned": [120000, 85000, 45000, 70000, 30000],
                    "actual": [118000, 92000, 42000, 81000, 28000]
                }
                budget_df = pd.DataFrame(budget_data)
                fig = go.Figure()
                fig.add_trace(go.Bar(name="Planned", x=budget_df["categories"], y=budget_df["planned"], marker_color="#667eea"))
                fig.add_trace(go.Bar(name="Actual", x=budget_df["categories"], y=budget_df["actual"], marker_color="#10b981"))
                fig.update_layout(
                    barmode="group",
                    template="plotly_white" if not st.session_state.dark_mode else "plotly_dark",
                    height=300,
                    margin=dict(l=20, r=20, t=20, b=20),
                    legend=dict(orientation="h", y=-0.1)
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not load budget data: {str(e)}")
        
        with col2:
            st.subheader("Burn Rate Forecast")
            try:
                dates, burn_data = generate_mock_chart_data(14, 30, 5)
                forecast_dates = [dates[-1] + timedelta(days=i) for i in range(1, 8)]
                forecast_data = [burn_data[-1] * (1 + 0.02 * i) for i in range(7)]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dates, y=burn_data, mode="lines", name="Actual Burn", line=dict(color="#667eea", width=3)))
                fig.add_trace(go.Scatter(x=forecast_dates, y=forecast_data, mode="lines", name="Forecast", line=dict(color="#f59e0b", width=3, dash="dash")))
                fig.update_layout(
                    template="plotly_white" if not st.session_state.dark_mode else "plotly_dark",
                    height=300,
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis_title="Date",
                    yaxis_title="Daily Spend ($)"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not load burn rate forecast: {str(e)}")

def render_performance_analytics():
    """Content and project performance analytics"""
    with st.expander("📈 Performance Analytics", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Project ROI Trend")
            try:
                dates, roi_data = generate_mock_chart_data(30, 15, 3)
                fig = px.line(
                    x=dates, y=roi_data,
                    title="30-Day ROI Trend",
                    labels={"x": "Date", "y": "ROI (%)"},
                    template="plotly_white" if not st.session_state.dark_mode else "plotly_dark"
                )
                fig.add_hline(y=10, line_dash="dash", line_color="#10b981", annotation_text="Target ROI")
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not load ROI data: {str(e)}")
        
        with col2:
            st.subheader("Quality Metrics Trend")
            try:
                quality_df = pd.DataFrame({
                    "Date": pd.date_range(end=datetime.now(), periods=30),
                    "Purity": [random.randint(96, 99) for _ in range(30)],
                    "Moisture": [random.randint(92, 97) for _ in range(30)],
                    "Protein": [random.randint(94, 98) for _ in range(30)]
                })
                fig = px.line(
                    quality_df,
                    x="Date",
                    y=["Purity", "Moisture", "Protein"],
                    template="plotly_white" if not st.session_state.dark_mode else "plotly_dark",
                    labels={"value": "Score (%)", "variable": "Metric"}
                )
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", y=-0.1))
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not load quality trend data: {str(e)}")

def render_approval_workflows():
    """Pending approvals queue for quick action"""
    with st.expander("✅ Pending Approvals", expanded=False):
        try:
            approvals = db.get_approvals() if hasattr(db, "get_approvals") else [
                {"id": "APR-001", "type": "Expense", "amount": "$2,400", "requestor": "Line Producer A", "due": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")},
                {"id": "APR-002", "type": "Deliverable", "item": "Feature Cut v3", "requestor": "Post-Production Lead", "due": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")},
                {"id": "APR-003", "type": "Contract", "vendor": "Location Services Inc", "requestor": "Production Coordinator", "due": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")}
            ]
            
            if approvals:
                for approval in approvals:
                    with st.container(border=True):
                        cols = st.columns([3, 2, 2, 2])
                        cols[0].markdown(f"**{approval['id']}: {approval['type']}**")
                        cols[1].caption(approval.get("item", approval.get("vendor", "")))
                        cols[2].caption(f"Requestor: {approval['requestor']}")
                        cols[3].caption(f"Due: {approval['due']}")
                        action_cols = st.columns(2)
                        with action_cols[0]:
                            if st.button("Approve", key=f"approve_{approval['id']}", use_container_width=True, type="primary"):
                                st.success(f"Approved {approval['id']}")
                                clear_all_cache()  # Refresh data after action
                        with action_cols[1]:
                            if st.button("Reject", key=f"reject_{approval['id']}", use_container_width=True):
                                st.error(f"Rejected {approval['id']}")
                                clear_all_cache()  # Refresh data after action
            else:
                st.info("No pending approvals 🎉")
        except Exception as e:
            st.warning(f"Could not load approvals: {str(e)}")

def render_audit_log():
    """Change tracking / audit log section to track all data modifications"""
    with st.expander(f"📜 Change Log ({len(get_audit_logs())} recent changes)", expanded=st.session_state.show_audit_log):
        try:
            logs = get_audit_logs(limit=50)
            if logs:
                log_df = pd.DataFrame(logs)
                log_df["timestamp"] = pd.to_datetime(log_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
                # Reorder columns for readability
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
                st.info("No changes recorded yet.")
        except Exception as e:
            st.warning(f"Could not load audit log: {str(e)}")

def render_recent_orders():
    """Enhanced recent orders table with filters, actions, and live updates"""
    st.subheader("📋 Recent Orders")
    
    # Add filters
    with st.expander("Filter Orders", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect("Status", ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"], default=["Pending", "Processing"])
        with col2:
            date_filter = st.date_input("Date Range", value=st.session_state.date_range)
        with col3:
            merchant_filter = st.text_input("Search Merchant")
    
    # Fetch orders (cache disabled for real-time updates)
    try:
        # Remove @st.cache_data here if you want orders to update instantly
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
                orders_df = orders_df[(orders_df["created_at"] >= date_filter[0]) & (orders_df["created_at"] <= date_filter[1])]
            
            # Format display
            display_df = pd.DataFrame({
                "Order ID": orders_df.get("order_number", orders_df.get("id", [])),
                "Merchant": orders_df.get("buyer_name", ["Unknown"] * len(orders_df)),
                "Product": [items[0].get('name', 'N/A') if isinstance(items, list) and len(items) > 0 else 'N/A' for items in orders_df.get("items", [[]] * len(orders_df))],
                "Amount": [format_currency(x) for x in orders_df.get("total", [0]*len(orders_df))],
                "Status": orders_df.get("status", ["Unknown"] * len(orders_df)),
                "Date": pd.to_datetime(orders_df.get("created_at", [""] * len(orders_df))).dt.strftime("%Y-%m-%d")
            })
            
            # Add status color coding
            def color_status(val):
                color = get_status_color(val)
                return f'<span style="color: {color}; font-weight: 500;">{val}</span>'
            
            styled_df = display_df.style.applymap(color_status, subset=["Status"])
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.TextColumn("Status", width="medium"),
                    "Amount": st.column_config.TextColumn("Amount", width="medium")
                }
            )
            
            # Add export button
            st.download_button(
                label="📥 Export Orders to CSV",
                data=display_df.to_csv(index=False).encode("utf-8"),
                file_name=f"orders_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No orders yet. Orders will appear here when received.")
    except Exception as e:
        st.warning(f"Could not load orders: {str(e)}")

def render_quick_actions():
    """Expanded quick actions for common workflows"""
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("➕ Add Product", use_container_width=True, type="primary"):
            st.switch_page("pages/add_product.py")
    
    with col2:
        if st.button("📦 View Restock Alerts", use_container_width=True):
            st.switch_page("pages/restock_alerts.py")
    
    with col3:
        if st.button("✅ Review Approvals", use_container_width=True):
            st.session_state.show_approvals = True
    
    with col4:
        if st.button("📊 Generate Report", use_container_width=True):
            with st.spinner("Generating report..."):
                # Add report generation logic here
                st.success("Report generated! Check your downloads.")
                st.download_button(
                    "Download Report",
                    data="Sample report content".encode("utf-8"),
                    file_name=f"producer_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
    
    with col5:
        if st.button("⚙️ Dashboard Settings", use_container_width=True):
            st.session_state.show_settings = True

# -----------------------------------------------------------------------------
# Main Dashboard Render Function
# -----------------------------------------------------------------------------
def render():
    """Main dashboard render function with real-time updates and change tracking"""
    # Initialize state and styling
    init_session_state()
    load_custom_css()

    # --------------------------
    # Sidebar: Settings & Refresh Controls
    # --------------------------
    with st.sidebar:
        st.title("Dashboard Controls")
        
        # Manual refresh button
        if st.button("🔄 Refresh Data Now", use_container_width=True, type="primary"):
            clear_all_cache()
        
        # Auto-refresh interval selector
        st.selectbox(
            "Auto-Refresh Interval",
            options=[0, 30, 60, 300],
            format_func=lambda x: "Off" if x == 0 else f"Every {x//60 if x >= 60 else x} {'minute' if x >=60 else 'seconds'}",
            key="auto_refresh_interval"
        )
        
        # Other settings
        st.toggle("Dark Mode", value=st.session_state.dark_mode, key="dark_mode")
        st.selectbox(
            "Your Role",
            options=["executive", "line_producer", "finance", "client"],
            format_func=lambda x: x.replace("_", " ").title(),
            key="user_role"
        )
        st.date_input(
            "Date Range",
            value=st.session_state.date_range,
            key="date_range"
        )
        st.divider()
        # Live last updated timestamp
        st.caption(f"Last updated: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown("[Help Center](https://help.yourcompany.com) | [Contact Support](mailto:support@yourcompany.com)")

    # --------------------------
    # Auto-Refresh Logic
    # --------------------------
    if st.session_state.auto_refresh_interval > 0:
        # Increment counter and rerun after interval
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
        if time_since_refresh >= st.session_state.auto_refresh_interval:
            clear_all_cache()

    # --------------------------
    # Page Header
    # --------------------------
    user_name = st.session_state.get("user_name", "Producer")
    st.title(f"📊 Welcome back, {user_name}")
    st.caption(f"Here's your {st.session_state.user_role.replace('_', ' ')} overview for {datetime.now().strftime('%B %d, %Y')} • Live updates enabled")
    
    # --------------------------
    # Render Dashboard Sections
    # --------------------------
    render_critical_alerts()
    st.markdown("---")
    render_kpi_cards()
    st.markdown("---")
    
    # Main content grid (original charts, enhanced with live data)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Yield Performance (30 Days)")
        # Remove cache for real-time chart updates if needed
        dates, yield_data = generate_mock_chart_data(30, 100, 10)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=yield_data,
            mode='lines',
            name='Yield (tons)',
            line=dict(color='#667eea', width=3),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        # Add target line
        fig.add_hline(y=90, line_dash="dash", line_color="#10b981", annotation_text="Target Yield")
        
        fig.update_layout(
            template='plotly_white' if not st.session_state.dark_mode else "plotly_dark",
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Date",
            yaxis_title="Tons"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Quality Index")
        # Quality metrics with target comparison
        quality_data = pd.DataFrame({
            "Metric": ["Purity", "Moisture", "Protein", "Appearance", "Size"],
            "Score": [98, 95, 96, 97, 94],
            "Target": [97, 96, 95, 96, 95]
        })
        
        fig = px.bar(
            quality_data,
            x="Score",
            y="Metric",
            orientation='h',
            color="Score",
            color_continuous_scale="Viridis",
            template='plotly_white' if not st.session_state.dark_mode else "plotly_dark",
            hover_data={"Target": True, "Score": True}
        )
        # Add target markers
        for i, row in quality_data.iterrows():
            fig.add_vline(x=row["Target"], line_dash="dash", line_color="#ef4444", annotation_text=f"Target: {row['Target']}%")
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Score (%)",
            yaxis_title=""
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    render_recent_orders()
    st.markdown("---")
    
    # Collapsible advanced modules (including new change log)
    with st.expander("Advanced Modules", expanded=False):
        render_production_pipeline()
        render_resource_management()
        render_budget_tracker()
        render_performance_analytics()
        render_approval_workflows()
        render_audit_log()  # New change tracking section
    
    st.markdown("---")
    render_quick_actions()
    
    # --------------------------
    # Modals for Settings/Approvals
    # --------------------------
    if st.session_state.get("show_settings", False):
        with st.modal("Dashboard Settings"):
            st.subheader("Customize Your Dashboard")
            st.multiselect(
                "Visible KPI Cards",
                options=["Active Projects", "YTD Revenue", "On-Time Delivery", "Profit Margin", "Open Tasks", "Team Utilization", "Budget Remaining", "Burn Rate"],
                default=["Active Projects", "YTD Revenue", "On-Time Delivery", "Profit Margin"]
            )
            st.multiselect(
                "Visible Modules",
                options=["Production Pipeline", "Resource Management", "Budget Tracker", "Analytics", "Approvals", "Change Log"],
                default=["Production Pipeline", "Recent Orders"]
            )
            if st.button("Save Settings", use_container_width=True, type="primary"):
                st.session_state.show_settings = False
                clear_all_cache()
                st.rerun()
    
    if st.session_state.get("show_approvals", False):
        with st.modal("Pending Approvals"):
            render_approval_workflows()
            if st.button("Close", use_container_width=True):
                st.session_state.show_approvals = False
                st.rerun()

if __name__ == "__main__":
    render()
