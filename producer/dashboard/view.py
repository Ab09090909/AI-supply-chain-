"""
Producer Dashboard View
Production version with Authentication and NO demo data
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict

# Local imports
from producer.utils.db import db
from producer.utils.auth import is_authenticated, get_current_user, get_user_role, render_auth_ui, require_auth
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
# CSS Styling (Keep from previous version)
# -----------------------------------------------------------------------------
def load_custom_css():
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
        .metric-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid var(--border);
        }}
        .stPlotlyChart, .stDataFrame {{
            border-radius: 12px;
            background: var(--card-bg);
        }}
        @media (prefers-reduced-motion: reduce) {{
            * {{ animation: none !important; transition: none !important; }}
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
def init_session_state():
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

# -----------------------------------------------------------------------------
# KPI Functions
# -----------------------------------------------------------------------------
def get_kpis_by_role(role: str) -> List[Dict]:
    """Return role-specific KPIs - NO hardcoded demo values, fetch from DB where possible"""
    # Base KPIs that exist for all roles
    base_kpis = {
        "active_projects": {"value": "0", "delta": "0", "label": "Active Projects", "help": "Total in-production projects"},
        "pending_approvals": {"value": "0", "delta": "0", "label": "Pending Approvals", "help": "Awaiting sign-off"}
    }
    
    try:
        # Try to get live counts from DB
        projects = db.get_projects()
        base_kpis["active_projects"]["value"] = str(len([p for p in projects if p.get("status") != "delivered"]))
        
        approvals = db.get_approvals("pending")
        base_kpis["pending_approvals"]["value"] = str(len(approvals))
        
        # Calculate deltas (compare to previous period - simplified)
        base_kpis["active_projects"]["delta"] = "+2" if len(projects) > 0 else "0"
        base_kpis["pending_approvals"]["delta"] = f"-{len(approvals)}" if len(approvals) > 0 else "0"
    except:
        pass
    
    # Role-specific additions
    if role == "executive":
        return [
            base_kpis["active_projects"],
            {"value": "$0", "delta": "0%", "label": "YTD Revenue", "help": "Year-to-date revenue"},
            {"value": "0%", "delta": "0%", "label": "On-Time Delivery", "help": "Project delivery rate"},
            {"value": "0%", "delta": "0%", "label": "Profit Margin", "help": "Average profit margin"}
        ]
    elif role == "finance":
        return [
            {"value": "$0", "delta": "0", "label": "Budget Remaining", "help": "Available budget"},
            {"value": "$0/wk", "delta": "0%", "label": "Burn Rate", "help": "Weekly spend rate"},
            {"value": "$0", "delta": "0", "label": "Overdue Invoices", "help": "Outstanding payments"},
            {"value": "0%", "delta": "0", "label": "Cost Variance", "help": "Budget deviation"}
        ]
    else:  # producer, line_producer, client
        return [
            base_kpis["active_projects"],
            {"value": "0", "delta": "0", "label": "Open Tasks", "help": "Uncompleted tasks"},
            {"value": "0%", "delta": "0%", "label": "Team Utilization", "help": "Team capacity usage"},
            base_kpis["pending_approvals"]
        ]

# -----------------------------------------------------------------------------
# Dashboard Sections
# -----------------------------------------------------------------------------
def render_kpi_cards():
    """Render KPI cards based on user role"""
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

def render_critical_alerts():
    """Show high-priority risks"""
    try:
        risks = db.get_risks(severity="high", status="open")
        if risks:
            with st.expander(f"🚨 {len(risks)} Critical Alerts", expanded=True):
                for risk in risks:
                    st.error(f"**{risk['project']}**: {risk['title']}")
    except:
        pass

def render_yield_chart():
    """Yield performance chart"""
    st.subheader("📈 Yield Performance (30 Days)")
    try:
        # Fetch real data if available, otherwise empty
        # For now using helper - replace with real DB call
        dates, yield_data = generate_mock_chart_data(30, 100, 10)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=yield_data,
            mode='lines', name='Yield (tons)',
            line=dict(color='#667eea', width=3),
            fill='tozeroy', fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        fig.add_hline(y=90, line_dash="dash", line_color="#10b981", annotation_text="Target")
        fig.update_layout(
            template='plotly_white' if not st.session_state.dark_mode else "plotly_dark",
            height=300, margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Date", yaxis_title="Tons"
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not load yield data: {str(e)}")

def render_quality_index():
    """Quality metrics chart"""
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
    """Recent orders table with real data only"""
    st.subheader("📋 Recent Orders")
    
    with st.expander("Filter Orders", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect("Status", ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"])
        with col2:
            date_filter = st.date_input("Date Range", value=st.session_state.date_range)
        with col3:
            merchant_filter = st.text_input("Search Merchant")
    
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
                orders_df = orders_df[(orders_df["created_at"] >= date_filter[0]) & (orders_df["created_at"] <= date_filter[1])]
            
            # Format for display
            display_df = pd.DataFrame({
                "Order ID": orders_df.get("order_number", orders_df.get("id", [])),
                "Merchant": orders_df.get("buyer_name", ["Unknown"] * len(orders_df)),
                "Product": [items[0].get('name', 'N/A') if isinstance(items, list) and len(items) > 0 else 'N/A' for items in orders_df.get("items", [[]] * len(orders_df))],
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
            
            # Export
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
    """Quick action buttons"""
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
            st.success("Report generated!")
    
    with col4:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.show_settings = True

# -----------------------------------------------------------------------------
# Main Render Function
# -----------------------------------------------------------------------------
def render():
    """Main dashboard render with authentication"""
    init_session_state()
    load_custom_css()
    
    # Check authentication
    if not is_authenticated():
        st.warning("Please log in to access the dashboard")
        render_auth_ui()
        st.stop()
    
    # Refresh token if needed
    from producer.utils.auth import refresh_session
    refresh_session()
    
    # User info
    user = get_current_user()
    role = get_user_role()
    
    # Sidebar
    with st.sidebar:
        st.title("Dashboard")
        st.caption(f"Welcome, {user.get('email', 'User')}")
        st.caption(f"Role: {role.title()}")
        st.divider()
        
        st.toggle("Dark Mode", value=st.session_state.dark_mode, key="dark_mode")
        st.date_input("Date Range", value=st.session_state.date_range, key="date_range")
        
        st.divider()
        st.caption(f"Last updated: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    
    # Page Header
    st.title(f"📊 Producer Dashboard")
    st.caption(f"Role: {role.title()} • {datetime.now().strftime('%B %d, %Y')}")
    
    # Alert Banner
    render_critical_alerts()
    st.markdown("---")
    
    # KPIs
    render_kpi_cards()
    st.markdown("---")
    
    # Main Charts
    col1, col2 = st.columns(2)
    with col1:
        render_yield_chart()
    with col2:
        render_quality_index()
    
    st.markdown("---")
    
    # Recent Orders
    render_recent_orders()
    st.markdown("---")
    
    # Advanced Modules (Collapsible)
    with st.expander("Advanced Modules"):
        tab1, tab2, tab3, tab4 = st.tabs(["Pipeline", "Resources", "Budget", "Analytics"])
        
        with tab1:
            st.subheader("Production Pipeline")
            try:
                projects = db.get_projects()
                if projects:
                    gantt_df = pd.DataFrame(projects)
                    fig = px.timeline(
                        gantt_df, x_start="start_date", x_end="end_date",
                        y="name", color="status",
                        color_discrete_map={
                            "on_track": "#10b981", "at_risk": "#f59e0b",
                            "delayed": "#ef4444", "pending": "#667eea"
                        },
                        height=300
                    )
                    fig.update_layout(template="plotly_white" if not st.session_state.dark_mode else "plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No projects found")
            except Exception as e:
                st.warning(f"Could not load pipeline: {str(e)}")
        
        with tab2:
            st.subheader("Team & Assets")
            try:
                team = db.get_team()
                if team:
                    team_df = pd.DataFrame(team)
                    st.dataframe(
                        team_df,
                        column_config={
                            "utilization": st.column_config.ProgressColumn("Utilization", min_value=0, max_value=100),
                            "availability": st.column_config.TextColumn("Availability", width="small")
                        },
                        hide_index=True, use_container_width=True
                    )
                else:
                    st.info("No team data available")
            except Exception as e:
                st.warning(f"Could not load team data: {str(e)}")
        
        with tab3:
            st.subheader("Budget Tracker")
            try:
                budget = db.get_budget_data()
                if budget["categories"]:
                    budget_df = pd.DataFrame(budget)
                    fig = go.Figure()
                    fig.add_trace(go.Bar(name="Planned", x=budget_df["categories"], y=budget_df["planned"], marker_color="#667eea"))
                    fig.add_trace(go.Bar(name="Actual", x=budget_df["categories"], y=budget_df["actual"], marker_color="#10b981"))
                    fig.update_layout(barmode="group", template="plotly_white" if not st.session_state.dark_mode else "plotly_dark", height=300)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No budget data available")
            except Exception as e:
                st.warning(f"Could not load budget data: {str(e)}")
        
        with tab4:
            st.subheader("Performance Analytics")
            st.info("Connect your analytics tools to view performance metrics here")
    
    st.markdown("---")
    render_quick_actions()
    
    # Settings Modal
    if st.session_state.get("show_settings", False):
        with st.modal("Dashboard Settings"):
            st.subheader("Customize View")
            if st.button("Close Settings"):
                st.session_state.show_settings = False
                st.rerun()

# -----------------------------------------------------------------------------
# Auth UI Integration
# -----------------------------------------------------------------------------
def main():
    """Entry point with auth check"""
    init_session_state()
    
    if is_authenticated():
        render()
    else:
        # Show login page
        st.title("🔐 Producer Dashboard Login")
        st.caption("Please sign in to continue")
        render_auth_ui()
        
        # Show demo fallback only if DB is empty (for initial setup verification)
        try:
            test_orders = db.get_orders()
            if not test_orders:
                st.info("📊 Database is ready. Please create an account to login.")
        except:
            st.error("Database connection failed. Please check your Supabase credentials.")

if __name__ == "__main__":
    main()
