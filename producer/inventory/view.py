"""
Producer Inventory Management - Full CRUD with professional UI
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from producer.db_helper.db_helper import (
    get_products, add_product, update_product, delete_product,
    get_product_by_id, get_product_categories, get_producer_id,
    get_stock_summary, seed_producer_demo_data
)
from producer.utils.helpers import format_currency, get_stock_status


INVENTORY_CSS = """
<style>
    .inv-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.2rem;
    }
    .inv-header h2 {
        color: #e2e8f0;
        font-size: 1.25rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .stock-summary-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.8rem;
        margin-bottom: 1.5rem;
    }
    @media (max-width: 900px) {
        .stock-summary-grid { grid-template-columns: repeat(2, 1fr); }
    }
    .stock-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 2px 16px rgba(0,0,0,0.15);
    }
    .stock-card .label {
        font-size: 0.73rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    .stock-card .value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-top: 0.2rem;
    }
    .stock-card .value.green  { color: #34d399; }
    .stock-card .value.amber  { color: #fbbf24; }
    .stock-card .value.red    { color: #f87171; }
    .stock-card .value.blue   { color: #60a5fa; }

    /* Product Table */
    .prod-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
    }
    .prod-table th {
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
    .prod-table td {
        padding: 0.65rem 0.8rem;
        color: #cbd5e1;
        font-size: 0.85rem;
        border-bottom: 1px solid rgba(255,255,255,0.03);
    }
    .prod-table tr:hover td {
        background: rgba(99,102,241,0.04);
    }

    .stock-badge {
        display: inline-block;
        padding: 0.15rem 0.55rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .stock-badge.in-stock    { background: rgba(16,185,129,0.15); color: #34d399; }
    .stock-badge.low-stock   { background: rgba(251,191,36,0.15); color: #fbbf24; }
    .stock-badge.overstocked { background: rgba(99,102,241,0.15); color: #818cf8; }
    .stock-badge.out-of-stock{ background: rgba(239,68,68,0.15);  color: #f87171; }

    .form-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border-radius: 14px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 4px 24px rgba(0,0,0,0.18);
        margin-bottom: 1.2rem;
    }
    .form-card h3 {
        color: #e2e8f0;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
</style>
"""


def render_stock_summary_cards(stock: dict):
    html = f"""
    <div class="stock-summary-grid">
        <div class="stock-card">
            <div class="label">Total Products</div>
            <div class="value blue">{stock['total_items']}</div>
        </div>
        <div class="stock-card">
            <div class="label">Healthy Stock</div>
            <div class="value green">{stock['healthy_stock']}</div>
        </div>
        <div class="stock-card">
            <div class="label">Low Stock</div>
            <div class="value amber">{stock['low_stock']}</div>
        </div>
        <div class="stock-card">
            <div class="label">Out of Stock</div>
            <div class="value red">{stock['out_of_stock']}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_stock_chart(products: list):
    if not products:
        return
    df = pd.DataFrame(products)
    fig = go.Figure()
    df_sorted = df.sort_values("current_stock", ascending=True)
    
    colors = []
    for _, p in df_sorted.iterrows():
        status = get_stock_status(
            p.get("current_stock", 0),
            p.get("min_stock", 0),
            p.get("current_stock", 0) * 3  # approximate max
        )
        if status == "Out of Stock":
            colors.append("#f43f5e")
        elif status == "Low Stock":
            colors.append("#fbbf24")
        elif status == "Overstocked":
            colors.append("#6366f1")
        else:
            colors.append("#10b981")

    fig.add_trace(go.Bar(
        y=df_sorted["name"],
        x=df_sorted["current_stock"],
        orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(0,0,0,0)", width=0)),
        text=df_sorted["current_stock"],
        textposition="outside",
        textfont=dict(size=10, color="#94a3b8"),
        hovertemplate="%{y}: %{x} units<extra></extra>"
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        yaxis=dict(showgrid=False, showline=False),
        height=max(280, len(df_sorted) * 38),
        showlegend=False,
    )

    st.markdown("""
    <div class="form-card">
        <h3>Stock Levels Overview</h3>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_products_table(products: list):
    if not products:
        st.info("No products found. Add your first product above.")
        return

    header = """
    <div class="form-card" style="overflow-x:auto">
    <table class="prod-table">
        <thead><tr>
            <th>ID</th><th>Product Name</th><th>Category</th>
            <th>Price</th><th>Stock</th><th>Min Stock</th>
            <th>Status</th><th>Actions</th>
        </tr></thead>
        <tbody>
    """
    rows = ""
    for p in products:
        pid = p.get("id", "?")
        name = p.get("name", "")
        cat = p.get("category", "-")
        price = format_currency(p.get("price", 0))
        stock = p.get("current_stock", 0)
        min_s = p.get("min_stock", 0)
        status = get_stock_status(stock, min_s, stock * 3)
        badge_cls = status.lower().replace(" ", "-")
        badge = f'<span class="stock-badge {badge_cls}">{status}</span>'
        rows += f"""
        <tr>
            <td style="font-weight:600;color:#e2e8f0">#{pid}</td>
            <td><strong>{name}</strong></td>
            <td>{cat}</td>
            <td style="font-weight:600">{price}</td>
            <td>{stock:,}</td>
            <td>{min_s:,}</td>
            <td>{badge}</td>
            <td>
                <span style="color:#818cf8;cursor:pointer;font-size:0.8rem">Edit</span>
            </td>
        </tr>"""

    st.markdown(header + rows + "</tbody></table></div>", unsafe_allow_html=True)


def render_add_product_form(categories: list, producer_id: int):
    st.markdown("""
    <div class="form-card">
        <h3>Add New Product</h3>
    """, unsafe_allow_html=True)

    with st.form("add_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Product Name*", placeholder="e.g. Organic Wheat Grain")
            category = st.selectbox("Category*", options=categories + ["Other"], index=0)
            if category == "Other":
                category = st.text_input("Custom Category", placeholder="Enter category name")
        with col2:
            price = st.number_input("Price per Unit ($)*", min_value=0.01, value=10.0, step=0.01, format="%.2f")
            stock = st.number_input("Current Stock*", min_value=0, value=100, step=1)
            min_stock = st.number_input("Min Stock Alert Level*", min_value=0, value=20, step=1)

        description = st.text_area("Description", placeholder="Brief product description...")

        submitted = st.form_submit_button("Add Product", use_container_width=True, type="primary")
        if submitted:
            if not name or not category:
                st.error("Product name and category are required.")
            else:
                result = add_product(
                    name=name, category=category, price=price,
                    stock=stock, min_stock=min_stock,
                    description=description, producer_id=producer_id
                )
                if result:
                    st.success(f"Product '{name}' added successfully! (ID: {result})")
                    st.rerun()
                else:
                    st.error("Failed to add product. Check database connection.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_inventory_value_chart(products: list):
    if not products:
        return
    df = pd.DataFrame(products)
    df["inventory_value"] = df["price"] * df["current_stock"]
    df = df.sort_values("inventory_value", ascending=False).head(8)

    fig = go.Figure(go.Bar(
        x=df["name"],
        y=df["inventory_value"],
        marker=dict(
            color=df["inventory_value"],
            colorscale="Teal",
            line=dict(color="rgba(0,0,0,0)", width=0)
        ),
        text=[format_currency(v) for v in df["inventory_value"]],
        textposition="outside",
        textfont=dict(size=10, color="#94a3b8"),
        hovertemplate="%{x}: %{y:$,.2f}<extra></extra>"
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, showline=False, tickangle=-25),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        height=300,
        showlegend=False,
    )

    st.markdown("""
    <div class="form-card">
        <h3>Top Inventory by Value</h3>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render(email: str):
    st.markdown(INVENTORY_CSS, unsafe_allow_html=True)

    producer_id = get_producer_id(email)
    if not producer_id:
        st.error("Producer account not found.")
        return

    seed_producer_demo_data()

    st.markdown("""
    <div class="inv-header">
        <h2>Inventory Management</h2>
    </div>
    """, unsafe_allow_html=True)

    # Stock summary
    stock = get_stock_summary(producer_id)
    render_stock_summary_cards(stock)

    # Filters
    categories = get_product_categories()
    col_search, col_cat, col_status = st.columns([3, 2, 2])
    with col_search:
        search = st.text_input("Search products...", placeholder="Type to search...", key="inv_search")
    with col_cat:
        cat_filter = st.selectbox("Category", ["All"] + categories, key="inv_cat")
    with col_status:
        status_filter = st.selectbox("Stock Status", ["All", "In Stock", "Low Stock", "Out of Stock", "Overstocked"], key="inv_status")

    # Fetch filtered products
    products = get_products(
        producer_id=producer_id,
        category=cat_filter if cat_filter != "All" else None,
        search=search if search else None
    )

    # Filter by stock status
    if status_filter != "All":
        filtered = []
        for p in products:
            s = get_stock_status(
                p.get("current_stock", 0),
                p.get("min_stock", 0),
                p.get("current_stock", 0) * 3
            )
            if s == status_filter:
                filtered.append(p)
        products = filtered

    # Charts row
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        render_stock_chart(products)
    with chart_col2:
        render_inventory_value_chart(products)

    # Add product form
    render_add_product_form(categories, producer_id)

    # Products table
    st.markdown('<div style="color:#e2e8f0;font-size:1.1rem;font-weight:700;margin:1.5rem 0 0.8rem 0">All Products</div>', unsafe_allow_html=True)
    render_products_table(products)
