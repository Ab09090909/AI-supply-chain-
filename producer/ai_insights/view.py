"""
Producer AI Insights
Independent module
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

def render():
    """Render AI insights page"""
    st.title("💡 AI Insights")
    st.caption("Machine learning powered analytics and predictions")
    
    tab1, tab2, tab3 = st.tabs(["📈 Price Forecasts", "📊 Demand Predictions", "🎯 Recommendations"])
    
    with tab1:
        st.subheader("📈 Price Forecast - Next 30 Days")
        
        # Generate forecast data
        dates = [datetime.now() + timedelta(days=x) for x in range(30)]
        base_price = 4.20
        forecast = [base_price + random.uniform(-0.3, 0.8) + (x * 0.02) for x in range(30)]
        upper = [p + 0.3 for p in forecast]
        lower = [p - 0.3 for p in forecast]
        
        df = pd.DataFrame({
            "Date": dates,
            "Forecast": forecast,
            "Upper Bound": upper,
            "Lower Bound": lower
        })
        
        fig = go.Figure()
        
        # Add confidence interval
        fig.add_trace(go.Scatter(
            x=dates + dates[::-1],
            y=upper + lower[::-1],
            fill='toself',
            fillcolor='rgba(102, 126, 234, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=False,
            name='Confidence Interval'
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=forecast,
            mode='lines',
            name='Forecast',
            line=dict(color='#667eea', width=3)
        ))
        
        fig.update_layout(
            template='plotly_white',
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Date",
            yaxis_title="Price ($/ton)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Insights
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price", f"${base_price:.2f}", "+$0.15")
        with col2:
            st.metric("30-Day Forecast", f"${forecast[-1]:.2f}", f"+{((forecast[-1]-base_price)/base_price*100):.1f}%")
        with col3:
            st.metric("Confidence", "85%", "High")
        
        st.info("💡 **Insight:** Price expected to rise 5% next week due to seasonal demand. Consider locking in current contracts for 60-day supply.")
    
    with tab2:
        st.subheader("📊 Demand Predictions")
        
        categories = ["Grains", "Dairy", "Fruits", "Vegetables", "Meat"]
        current_demand = [65, 78, 82, 45, 55]
        predicted_demand = [75, 92, 79, 58, 52]
        
        df = pd.DataFrame({
            "Category": categories,
            "Current": current_demand,
            "Predicted": predicted_demand
        })
        
        fig = px.bar(
            df,
            x="Category",
            y=["Current", "Predicted"],
            barmode="group",
            template="plotly_white",
            color_discrete_sequence=['#667eea', '#764ba2']
        )
        
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis_title="Demand Score"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.warning("⚠️ **Alert:** Dairy demand predicted to spike 15% this weekend. Ensure adequate supply and cold storage capacity.")
    
    with tab3:
        st.subheader("🎯 AI Recommendations")
        
        recommendations = [
            {
                "icon": "💰",
                "title": "Price Optimization",
                "desc": "Increase wheat price by $0.15 based on market trends and demand forecast",
                "impact": "+$2,400/mo",
                "priority": "High"
            },
            {
                "icon": "📦",
                "title": "Inventory Action",
                "desc": "Reorder avocados immediately - stock critically low (12 units, min 40)",
                "impact": "Prevents stockout",
                "priority": "Critical"
            },
            {
                "icon": "🤝",
                "title": "New Partnership",
                "desc": "Metro Retail showing 40% growth - offer exclusive supply contract",
                "impact": "+$15K potential",
                "priority": "Medium"
            },
            {
                "icon": "🚚",
                "title": "Logistics Optimization",
                "desc": "Consolidate shipments to reduce delivery costs by 12%",
                "impact": "-$800/mo",
                "priority": "Low"
            }
        ]
        
        for rec in recommendations:
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                
                with col1:
                    st.markdown(f"<div style='font-size:2.5rem;text-align:center;'>{rec['icon']}</div>", unsafe_allow_html=True)
                
                with col2:
                    st.write(f"**{rec['title']}**")
                    st.write(rec['desc'])
                
                with col3:
                    st.metric("Impact", rec['impact'])
                
                with col4:
                    priority_color = {
                        "Critical": "🔴",
                        "High": "🟡",
                        "Medium": "🔵",
                        "Low": "🟢"
                    }.get(rec['priority'], "⚪")
                    st.write(f"**{priority_color} {rec['priority']}**")
                
                st.markdown("---")
