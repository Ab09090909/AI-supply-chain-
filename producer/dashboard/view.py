"""
Producer Dashboard View
Independent module - no imports from other roles
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

from producer.utils.db import db
from producer.utils.helpers import generate_mock_chart_data, format_currency

def render():
    """Render producer dashboard"""
    st.title("📊 Producer Dashboard")
    st.caption("Welcome back! Here's your supply chain overview.")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Active Orders",
            value="24",
            delta="+3 today",
            help="Orders currently being processed"
        )
    
    with col2:
        st.metric(
            label="Inventory Turn",
            value="4.2x",
            delta="+0.3",
            help="Average inventory turnover rate"
        )
    
    with col3:
        st.metric(
            label="Avg Price",
            value="$4.85",
            delta="+2.1%",
            help="Average selling price per unit"
        )
    
    with col4:
        st.metric(
            label="Risk Score",
            value="12%",
            delta="-3%",
            delta_color="inverse",
            help="Fraud risk assessment score"
        )
    
    st.markdown("---")
    
    # Charts Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Yield Performance (30 Days)")
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
        
        fig.update_layout(
            template='plotly_white',
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Date",
            yaxis_title="Tons"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Quality Index")
        
        # Quality metrics
        quality_data = pd.DataFrame({
            "Metric": ["Purity", "Moisture", "Protein", "Appearance", "Size"],
            "Score": [98, 95, 96, 97, 94]
        })
        
        fig = px.bar(
            quality_data,
            x="Score",
            y="Metric",
            orientation='h',
            color="Score",
            color_continuous_scale="Viridis",
            template='plotly_white'
        )
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Score (%)",
            yaxis_title=""
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent Orders Table
    st.subheader("📋 Recent Orders")
    
    orders = db.get_orders(1)
    if orders:
        orders_df = pd.DataFrame(orders[:5])
        
        # Format the dataframe for display
        display_df = pd.DataFrame({
            "Order ID": orders_df.get("order_number", orders_df.get("id", [])),
            "Merchant": orders_df.get("merchant", ["Unknown"] * len(orders_df)),
            "Product": orders_df.get("product", ["N/A"] * len(orders_df)),
            "Amount": [format_currency(x) for x in orders_df.get("total", orders_df.get("amount", [0]*len(orders_df)))],
            "Status": orders_df.get("status", ["Unknown"] * len(orders_df)),
            "Date": orders_df.get("date", orders_df.get("created_at", [""] * len(orders_df)))
        })
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn("Status", width="medium")
            }
        )
    else:
        st.info("No orders yet. Orders will appear here when received.")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add Product", use_container_width=True, type="primary"):
            st.switch_page("app.py")
    
    with col2:
        if st.button("📦 Restock Alerts", use_container_width=True):
            st.switch_page("app.py")
    
    with col3:
        if st.button("🤝 Find Merchants", use_container_width=True):
            st.switch_page("app.py")
    
    with col4:
        if st.button("📊 Generate Report", use_container_width=True):
            st.success("Report generated! Check your downloads.")
