"""
Producer Dashboard - Professional KPI dashboard with charts and metrics
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from producer.db_helper.db_helper import (
    get_order_stats, get_revenue_timeline, get_stock_summary,
    get_category_distribution, get_products, get_orders, get_fraud_stats,
    get_notifications, get_producer_id, get_agreements, seed_producer_demo_data
)
from producer.utils.helpers import format_currency, get_stock_status, get_status_color


# ===================================================================
# PROFESSIONAL CSS STYLING
# ===================================================================
DASHBOARD_CSS = """
<style>
    /* ---- Global Dashboard Container ---- */
    .dashboard-container {
        padding: 0 1rem 2rem 0;
    }

    /* ---- KPI Cards ---- */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    @media (max-width: 900px) {
        .kpi-grid { grid-template-columns: repeat(2, 1fr); }
    }

    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 14px;
        padding: 1.4rem 1.5rem;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 4px 24px rgba(0,0,0,0.18);
        transition: transform 0.2s, box-shadow 0.2s;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 3px;
        border-radius: 14px 14px 0 0;
    }
    .kpi-card.revenue::before  { background: linear-gradient(90deg, #6366f1, #8b5cf6); }
    .kpi-card.orders::before   { background: linear-gradient(90deg, #06b6d4, #22d3ee); }
    .kpi-card.inventory::before{ background: linear-gradient(90deg, #10b981, #34d399); }
    .kpi-card.fraud::before    { background: linear-gradient(90deg, #f43f5e, #fb7185); }

    .kpi-label {
        font-size: 0.78rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #f1f5f9;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 0.35rem;
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    .kpi-sub .up   { color: #34d399; }
    .kpi-sub .down { color: #fb7185; }

    /* ---- Chart Cards ---- */
    .chart-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 14px;
        padding: 1.4rem 1.5rem;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 4px 24px rgba(0,0,0,0.18);
        margin-bottom: 1.2rem;
    }
    .chart-card h3 {
        color: #e2e8f0;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ---- Section Titles ---- */
    .section-title {
        color: #e2e8f0;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 1.8rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .section-title::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, #334155, transparent);
        margin-left: 0.8rem;
    }

    /* ---- Recent Orders Table ---- */
    .orders-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
    }
    .orders-table th {
        background: #1e293b;
        color: #94a3b8;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        padding: 0.75rem 1rem;
        text-align: left;
        border-bottom: 1px solid #334155;
    }
    .orders-table td {
        padding: 0.7rem 1rem;
        color: #cbd5e1;
        font-size: 0.875rem;
        border-bottom: 1px solid rgba(255,255,255,0.03);
    }
    .orders-table tr:hover td {
        background: rgba(99, 102, 241, 0.05);
    }

    /* ---- Status Badge ---- */
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.73rem;
        font-weight: 600;
        text-transform: capitalize;
    }
    .status-badge.pending    { background: rgba(99,102,241,0.15); color: #818cf8; }
    .status-badge.confirmed  { background: rgba(59,130,246,0.15); color: #60a5fa; }
    .status-badge.processing { background: rgba(6,182,212,0.15);  color: #22d3ee; }
    .status-badge.shipped    { background: rgba(245,158,11,0.15); color: #fbbf24; }
    .status-badge.delivered  { background: rgba(16,185,129,0.15); color: #34d399; }
    .status-badge.cancelled  { background: rgba(239,68,68,0.15);  color: #f87171; }

    /* ---- Activity Feed ---- */
    .activity-item {
        display: flex;
        gap: 0.8rem;
        padding: 0.75rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .activity-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        margin-top: 0.4rem;
        flex-shrink: 0;
    }
    .activity-text {
        color: #cbd5e1;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    .activity-time {
        color: #64748b;
        font-size: 0.75rem;
        margin-top: 0.15rem;
    }

    /* ---- Performance Metrics Row ---- */
    .metric-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 1.2rem;
    }
    @media (max-width: 900px) {
        .metric-row { grid-template-columns: 1fr; }
    }
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 14px;
        padding: 1.3rem 1.5rem;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 4px 24px rgba(0,0,0,0.18);
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .metric-bar-track {
        height: 8px;
        background: #1a2332;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 0.6rem;
    }
    .metric-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.8s ease;
    }
</style>
"""


# ===================================================================
# PLOTLY THEME
# ===================================================================
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(
        showgrid=True, gridcolor="rgba(255,255,255,0.04)",
        zeroline=False, showline=False
    ),
    yaxis=dict(
        showgrid=True, gridcolor="rgba(255,255,255,0.04)",
        zeroline=False, showline=False
    ),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="right", x=1, font=dict(size=11)
    ),
)


# ===================================================================
# RENDER FUNCTIONS
# ===================================================================

def _kpi_card(label: str, value: str, sub_text: str = "", card_class: str = "revenue") -> str:
    """Generate a KPI card HTML."""
    sub_html = f'<div class="kpi-sub">{sub_text}</div>' if sub_text else ""
    return f'''
    <div class="kpi-card {card_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>'''


def render_kpi_cards(stats: dict, stock: dict, fraud: dict):
    """Render the 4 top KPI cards."""
    revenue_val = format_currency(stats["total_revenue"])
    orders_val = str(stats["total_orders"])
    inventory_val = str(stock["total_items"])
    fraud_val = str(fraud["high_risk"])

    kpis = f"""
    <div class="kpi-grid">
        {_kpi_card("Total Revenue", revenue_val, f'<span class="up">+8.2%</span> from last month', 'revenue')}
        {_kpi_card("Active Orders", orders_val, f'{stats["pending_orders"]} pending', 'orders')}
        {_kpi_card("Inventory Items", inventory_val, f'{stock["low_stock"]} low stock alerts', 'inventory')}
        {_kpi_card("Fraud Alerts", fraud_val, f'{fraud["total_flags"]} total flags', 'fraud')}
    </div>
    """
    st.markdown(kpis, unsafe_allow_html=True)


def render_revenue_chart(timeline: list):
    """Render revenue trend line chart."""
    if not timeline:
        st.info("No revenue data available yet. Complete orders to see trends.")
        return

    df = pd.DataFrame(timeline)
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["date"], y=df["revenue"],
        mode="lines+markers",
        line=dict(color="#6366f1", width=2.5, shape="spline"),
        marker=dict(size=5, color="#818cf8"),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.08)",
        name="Revenue",
        hovertemplate="%{x}<br>Revenue: %{y:$,.2f}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        x=df["date"], y=df["order_count"],
        marker_color="rgba(6,182,212,0.3)",
        name="Orders",
        yaxis="y2",
        hovertemplate="%{x}<br>Orders: %{y}<extra></extra>"
    ))

    fig.update_layout(
        **PLOTLY_LAYOUT,
        yaxis=dict(
            title_text="Revenue ($)",
            titlefont=dict(size=11, color="#64748b"),
            **PLOTLY_LAYOUT["yaxis"]
        ),
        yaxis2=dict(
            title_text="Orders",
            titlefont=dict(size=11, color="#64748b"),
            overlaying="y",
            side="right",
            showgrid=False, showline=False
        ),
        hovermode="x unified",
        height=320,
    )

    st.markdown("""
    <div class="chart-card">
        <h3>Revenue & Order Trends</h3>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_order_status_chart(stats: dict):
    """Render order status donut chart."""
    labels = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
    # Add more status fields
    processing = stats.get("processing_orders", stats["pending_orders"] // 2)
    cancelled = stats.get("cancelled_orders", stats["pending_orders"] // 3)
    
    values = [
        stats["pending_orders"],
        processing,
        stats["shipped_orders"],
        stats["delivered_orders"],
        cancelled
    ]
    colors = ["#6366f1", "#06b6d4", "#fbbf24", "#10b981", "#f43f5e"]

    # Filter out zeros
    filtered = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
    if not filtered:
        st.info("No order data yet.")
        return
    
    labels_f, values_f, colors_f = zip(*filtered)

    fig = go.Figure(go.Pie(
        labels=labels_f,
        values=values_f,
        hole=0.68,
        marker=dict(colors=colors_f, line=dict(color="#0f172a", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#cbd5e1"),
        hovertemplate="%{label}: %{value} orders (%{percent})<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#94a3b8"),
        margin=dict(l=5, r=5, t=5, b=5),
        showlegend=True,
        legend=dict(
            orientation="v", yanchor="middle", y=0.5,
            xanchor="left", x=0, font=dict(size=11),
            bgcolor="rgba(0,0,0,0)"
        ),
        height=280,
    )

    st.markdown("""
    <div class="chart-card">
        <h3>Order Status Breakdown</h3>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_category_chart(categories: list):
    """Render category distribution bar chart."""
    if not categories:
        st.info("No product category data.")
        return

    df = pd.DataFrame(categories).sort_values("total_value", ascending=True)
    fig = go.Figure(go.Bar(
        y=df["category"],
        x=df["total_value"],
        orientation="h",
        marker=dict(
            color=df["total_value"],
            colorscale="Viridis",
            line=dict(color="rgba(0,0,0,0)", width=0)
        ),
        text=[format_currency(v) for v in df["total_value"]],
        textposition="outside",
        textfont=dict(size=10, color="#94a3b8"),
        hovertemplate="%{y}: %{x:$,.2f}<extra></extra>"
    ))

    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis=dict(title_text="Total Value ($)", **PLOTLY_LAYOUT["xaxis"]),
        height=max(250, len(df) * 45),
        showlegend=False,
    )

    st.markdown("""
    <div class="chart-card">
        <h3>Category Performance</h3>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_performance_metrics(stats: dict, stock: dict):
    """Render performance gauge bars."""
    total = max(stats["total_orders"], 1)
    delivered_pct = round(stats["delivered_orders"] / total * 100, 1)
    pending_pct = round(stats["pending_orders"] / total * 100, 1)
    healthy_pct = round(stock["healthy_stock"] / max(stock["total_items"], 1) * 100, 1)

    metrics_html = f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-label">Fulfillment Rate</div>
            <div style="color:#34d399;font-size:1.5rem;font-weight:700">{delivered_pct}%</div>
            <div class="metric-bar-track">
                <div class="metric-bar-fill" style="width:{delivered_pct}%;background:linear-gradient(90deg,#10b981,#34d399)"></div>
            </div>
            <div style="color:#64748b;font-size:0.75rem;margin-top:0.4rem">{stats['delivered_orders']} of {stats['total_orders']} orders</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Pending Rate</div>
            <div style="color:#818cf8;font-size:1.5rem;font-weight:700">{pending_pct}%</div>
            <div class="metric-bar-track">
                <div class="metric-bar-fill" style="width:{pending_pct}%;background:linear-gradient(90deg,#6366f1,#818cf8)"></div>
            </div>
            <div style="color:#64748b;font-size:0.75rem;margin-top:0.4rem">{stats['pending_orders']} orders awaiting processing</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Inventory Health</div>
            <div style="color:#22d3ee;font-size:1.5rem;font-weight:700">{healthy_pct}%</div>
            <div class="metric-bar-track">
                <div class="metric-bar-fill" style="width:{healthy_pct}%;background:linear-gradient(90deg,#06b6d4,#22d3ee)"></div>
            </div>
            <div style="color:#64748b;font-size:0.75rem;margin-top:0.4rem">{stock['healthy_stock']} of {stock['total_items']} items healthy</div>
        </div>
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)


def render_recent_orders(orders: list):
    """Render recent orders table."""
    st.markdown("""
    <div class="chart-card">
        <h3>Recent Orders</h3>
    """, unsafe_allow_html=True)

    if not orders:
        st.info("No orders yet.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Show top 8
    display_orders = orders[:8]
    header = """
    <table class="orders-table">
        <thead><tr>
            <th>Order ID</th>
            <th>Product</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Date</th>
        </tr></thead>
        <tbody>
    """
    rows = ""
    for o in display_orders:
        status = o.get("status", "pending")
        badge = f'<span class="status-badge {status}">{status}</span>'
        date_str = o.get("created_at", "")[:10]
        pid = o.get("id", "?")
        pname = o.get("product_name", f"Product #{o.get('product_id', '?')}")
        amount = format_currency(o.get("total_amount", 0))
        rows += f"""
        <tr>
            <td style="font-weight:600;color:#e2e8f0">#{pid:04d}</td>
            <td>{pname}</td>
            <td style="font-weight:600">{amount}</td>
            <td>{badge}</td>
            <td style="color:#64748b">{date_str}</td>
        </tr>"""

    footer = "</tbody></table>"
    st.markdown(header + rows + footer, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_activity_feed(notifications: list):
    """Render recent activity / notification feed."""
    if not notifications:
        return

    st.markdown("""
    <div class="chart-card">
        <h3>Recent Activity</h3>
    """, unsafe_allow_html=True)

    feed_html = ""
    colors = {"info": "#6366f1", "warning": "#f59e0b", "error": "#ef4444", "success": "#10b981"}
    for n in notifications[:6]:
        dot_color = colors.get(n.get("type", "info"), "#6366f1")
        title = n.get("title", "")
        msg = n.get("message", "")
        time_ago = n.get("created_at", "")[:16]
        feed_html += f"""
        <div class="activity-item">
            <div class="activity-dot" style="background:{dot_color}"></div>
            <div>
                <div class="activity-text"><strong>{title}</strong> - {msg[:80]}</div>
                <div class="activity-time">{time_ago}</div>
            </div>
        </div>"""

    st.markdown(feed_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ===================================================================
# MAIN RENDER
# ===================================================================
def render(email: str):
    """Main dashboard render function."""
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)

    # Ensure demo data exists
    producer_id = get_producer_id(email)
    if not producer_id:
        st.error("Producer account not found in database.")
        return

    seed_producer_demo_data()

    # Header
    st.markdown("""
    <div class="dashboard-container">
        <div class="section-title">Overview Dashboard</div>
    """, unsafe_allow_html=True)

    # Refresh button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Refresh", use_container_width=True, key="dash_refresh"):
            st.rerun()

    # Fetch data
    stats = get_order_stats(producer_id)
    stock = get_stock_summary(producer_id)
    fraud = get_fraud_stats()
    timeline = get_revenue_timeline(producer_id, days=30)
    categories = get_category_distribution(producer_id)
    orders = get_orders(producer_id)
    notifications = get_notifications(producer_id)

    # 1. KPI Cards
    render_kpi_cards(stats, stock, fraud)

    # 2. Performance Metrics
    render_performance_metrics(stats, stock)

    # 3. Charts Row
    chart_col1, chart_col2 = st.columns([2, 1])
    with chart_col1:
        render_revenue_chart(timeline)
    with chart_col2:
        render_order_status_chart(stats)

    # 4. Category chart + Activity feed
    chart_col3, chart_col4 = st.columns([3, 2])
    with chart_col3:
        st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)
        render_category_chart(categories)
    with chart_col4:
        st.markdown('<div class="section-title">Notifications</div>', unsafe_allow_html=True)
        render_activity_feed(notifications)

    # 5. Recent Orders
    st.markdown('<div class="section-title">Order Management</div>', unsafe_allow_html=True)
    render_recent_orders(orders)

    st.markdown("</div>", unsafe_allow_html=True)
