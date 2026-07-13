"""
Producer Marketplace - Order management, B2B agreements, listings
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from producer.db_helper.db_helper import (
    get_products, get_orders, update_order_status,
    get_agreements, get_producer_id, seed_producer_demo_data,
    get_order_stats
)
from producer.utils.helpers import format_currency, get_time_ago

MARKETPLACE_CSS = """
<style>
    .mk-stats {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.8rem;
        margin-bottom: 1.5rem;
    }
    @media (max-width: 900px) {
        .mk-stats { grid-template-columns: repeat(2, 1fr); }
    }
    .mk-stat {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 2px 16px rgba(0,0,0,0.15);
    }
    .mk-stat .label {
        font-size: 0.73rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    .mk-stat .value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-top: 0.2rem;
    }

    .mk-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border-radius: 14px;
        padding: 1.4rem 1.5rem;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 4px 24px rgba(0,0,0,0.18);
        margin-bottom: 1.2rem;
    }
    .mk-card h3 {
        color: #e2e8f0;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .order-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
    }
    .order-table th {
        background: #1e293b;
        color: #94a3b8;
        font-size: 0.73rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        padding: 0.65rem 0.8rem;
        text-align: left;
        border-bottom: 1px solid #334155;
    }
    .order-table td {
        padding: 0.65rem 0.8rem;
        color: #cbd5e1;
        font-size: 0.85rem;
        border-bottom: 1px solid rgba(255,255,255,0.03);
    }
    .order-table tr:hover td {
        background: rgba(99,102,241,0.04);
    }

    .status-badge {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: capitalize;
    }
    .status-badge.pending    { background: rgba(99,102,241,0.15); color: #818cf8; }
    .status-badge.confirmed  { background: rgba(59,130,246,0.15); color: #60a5fa; }
    .status-badge.processing { background: rgba(6,182,212,0.15);  color: #22d3ee; }
    .status-badge.shipped    { background: rgba(245,158,11,0.15); color: #fbbf24; }
    .status-badge.delivered  { background: rgba(16,185,129,0.15); color: #34d399; }
    .status-badge.cancelled  { background: rgba(239,68,68,0.15);  color: #f87171; }
    .status-badge.active     { background: rgba(16,185,129,0.15); color: #34d399; }
    .status-badge.expired    { background: rgba(239,68,68,0.15);  color: #f87171; }

    .agreement-card {
        background: rgba(30,41,59,0.5);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.7rem;
    }
    .agreement-card .agr-title {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.3rem;
    }
    .agreement-card .agr-desc {
        color: #94a3b8;
        font-size: 0.8rem;
        line-height: 1.5;
        margin-bottom: 0.4rem;
    }
    .agreement-card .agr-meta {
        color: #64748b;
        font-size: 0.73rem;
        display: flex;
        gap: 1rem;
    }
</style>
"""


def render_marketplace_stats(stats: dict):
    html = f"""
    <div class="mk-stats">
        <div class="mk-stat">
            <div class="label">Total Orders</div>
            <div class="value">{stats['total_orders']}</div>
        </div>
        <div class="mk-stat">
            <div class="label">Pending</div>
            <div class="value" style="color:#818cf8">{stats['pending_orders']}</div>
        </div>
        <div class="mk-stat">
            <div class="label">Shipped</div>
            <div class="value" style="color:#fbbf24">{stats['shipped_orders']}</div>
        </div>
        <div class="mk-stat">
            <div class="label">Delivered</div>
            <div class="value" style="color:#34d399">{stats['delivered_orders']}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_orders_management(orders: list, producer_id: int):
    st.markdown("""
    <div class="mk-card">
        <h3>Order Management</h3>
    """, unsafe_allow_html=True)

    if not orders:
        st.info("No orders yet.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Status filter
    statuses = ["All", "pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]
    col_filter, col_search = st.columns([2, 3])
    with col_filter:
        status_filter = st.selectbox("Filter by Status", statuses, key="mk_order_filter")
    with col_search:
        search = st.text_input("Search orders...", key="mk_order_search")

    filtered = orders
    if status_filter != "All":
        filtered = [o for o in filtered if o.get("status") == status_filter]
    if search:
        filtered = [o for o in filtered if str(o.get("id", "")).startswith(search)]

    # Build table HTML
    header = """
    <table class="order-table">
        <thead><tr>
            <th>Order ID</th><th>Product ID</th><th>Qty</th>
            <th>Amount</th><th>Status</th><th>Date</th>
        </tr></thead><tbody>
    """
    rows = ""
    for o in filtered[:15]:
        status = o.get("status", "pending")
        badge = f'<span class="status-badge {status}">{status}</span>'
        date_str = o.get("created_at", "")[:10]
        rows += f"""
        <tr>
            <td style="font-weight:600;color:#e2e8f0">#{o.get("id","?"):04d}</td>
            <td>#{o.get("product_id","?")}</td>
            <td>{o.get("quantity","?")}</td>
            <td style="font-weight:600">{format_currency(o.get("total_amount",0))}</td>
            <td>{badge}</td>
            <td style="color:#64748b">{date_str}</td>
        </tr>"""

    st.markdown(header + rows + "</tbody></table>", unsafe_allow_html=True)

    # Order status update section
    st.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)
    st.subheader("Update Order Status")
    col_oid, col_status, col_btn = st.columns([2, 2, 1])
    with col_oid:
        order_id_input = st.number_input("Order ID", min_value=1, step=1, key="mk_oid")
    with col_status:
        new_status = st.selectbox("New Status", ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"], key="mk_new_status")
    with col_btn:
        st.markdown('<div style="height:2.1rem"></div>', unsafe_allow_html=True)
        if st.button("Update", use_container_width=True, key="mk_update_btn"):
            result = update_order_status(order_id_input, new_status)
            if result:
                st.success(f"Order #{order_id_input} updated to '{new_status}'.")
                st.rerun()
            else:
                st.error("Failed to update order.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_agreements(agreements: list):
    st.markdown("""
    <div class="mk-card">
        <h3>B2B Agreements</h3>
    """, unsafe_allow_html=True)

    if not agreements:
        st.info("No agreements yet.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    for a in agreements:
        status = a.get("status", "pending")
        badge = f'<span class="status-badge {status}">{status}</span>'
        created = a.get("created_at", "")[:10]
        st.markdown(f"""
        <div class="agreement-card">
            <div class="agr-title">Agreement #{a.get("id","?")} {badge}</div>
            <div class="agr-desc">{a.get("terms","No terms specified.")}</div>
            <div class="agr-meta">
                <span>Merchant ID: #{a.get("merchant_id","?")}</span>
                <span>Created: {created}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_listings(products: list):
    st.markdown("""
    <div class="mk-card">
        <h3>Marketplace Listings</h3>
    """, unsafe_allow_html=True)

    if not products:
        st.info("No products listed.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Grid of product cards
    cols = st.columns(3)
    for i, p in enumerate(products[:9]):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="agreement-card" style="text-align:center">
                <div class="agr-title">{p.get('name','Product')}</div>
                <div style="color:#34d399;font-size:1.3rem;font-weight:700;margin:0.4rem 0">
                    {format_currency(p.get('price',0))}
                </div>
                <div style="color:#94a3b8;font-size:0.8rem">
                    {p.get('category','')} | Stock: {p.get('current_stock',0):,}
                </div>
                <div style="color:#64748b;font-size:0.75rem;margin-top:0.3rem">
                    {p.get('description','')[:60]}{'...' if len(p.get('description',''))>60 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_revenue_chart(orders: list):
    if not orders:
        return

    # Revenue by status
    status_rev = {}
    for o in orders:
        s = o.get("status", "unknown")
        status_rev[s] = status_rev.get(s, 0) + o.get("total_amount", 0)

    fig = go.Figure(go.Pie(
        labels=list(status_rev.keys()),
        values=list(status_rev.values()),
        hole=0.6,
        marker=dict(
            colors=["#6366f1", "#06b6d4", "#fbbf24", "#10b981", "#f43f5e", "#8b5cf6"],
            line=dict(color="#0f172a", width=2)
        ),
        textinfo="label+percent",
        textfont=dict(size=11, color="#cbd5e1"),
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#94a3b8"),
        margin=dict(l=5, r=5, t=5, b=5),
        height=280,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=0,
                     bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    )

    st.markdown("""
    <div class="mk-card">
        <h3>Revenue by Order Status</h3>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render(email: str):
    st.markdown(MARKETPLACE_CSS, unsafe_allow_html=True)

    producer_id = get_producer_id(email)
    if not producer_id:
        st.error("Producer account not found.")
        return

    seed_producer_demo_data()

    st.markdown("""
    <div class="inv-header">
        <h2>Marketplace</h2>
    </div>
    """, unsafe_allow_html=True)

    stats = get_order_stats(producer_id)
    render_marketplace_stats(stats)

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Orders", "Agreements", "Listings", "Analytics"])

    orders = get_orders(producer_id)
    agreements = get_agreements(producer_id)
    products_list = [p for p in __import__('producer.db_helper.db_helper', fromlist=['get_products']).get_products(producer_id) if p.get("status") == "active"]

    with tab1:
        render_orders_management(orders, producer_id)
    with tab2:
        render_agreements(agreements)
    with tab3:
        render_listings(products_list)
    with tab4:
        render_revenue_chart(orders)
