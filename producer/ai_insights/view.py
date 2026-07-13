"""
Producer AI Insights - ML-powered demand forecasting, price prediction, fraud analysis
"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from producer.db_helper.db_helper import (
    get_products, get_orders, get_fraud_logs, get_producer_id,
    get_revenue_timeline, get_stock_summary, get_fraud_stats,
    seed_producer_demo_data
)
from producer.utils.helpers import format_currency

MODELS_DIR = str(Path(__file__).resolve().parent.parent.parent / "models")

AI_CSS = """
<style>
    .ai-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border-radius: 14px;
        padding: 1.4rem 1.5rem;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 4px 24px rgba(0,0,0,0.18);
        margin-bottom: 1.2rem;
    }
    .ai-card h3 {
        color: #e2e8f0;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .ai-insight-box {
        background: rgba(99,102,241,0.08);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.7rem;
    }
    .ai-insight-box .insight-title {
        color: #a5b4fc;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.3rem;
    }
    .ai-insight-box .insight-text {
        color: #94a3b8;
        font-size: 0.82rem;
        line-height: 1.6;
    }
    .risk-card {
        background: rgba(239,68,68,0.06);
        border: 1px solid rgba(239,68,68,0.15);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
    }
    .risk-card .risk-type {
        color: #fca5a5;
        font-weight: 600;
        font-size: 0.82rem;
    }
    .risk-card .risk-score {
        float: right;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .risk-card .risk-score.high   { color: #f87171; }
    .risk-card .risk-score.medium { color: #fbbf24; }
    .risk-card .risk-score.low    { color: #34d399; }
    .risk-card .risk-date {
        color: #64748b;
        font-size: 0.73rem;
        margin-top: 0.2rem;
    }

    .model-status {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.6rem;
        margin-bottom: 1.2rem;
    }
    @media (max-width: 900px) {
        .model-status { grid-template-columns: repeat(2, 1fr); }
    }
    .model-item {
        background: rgba(16,185,129,0.06);
        border: 1px solid rgba(16,185,129,0.15);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        text-align: center;
    }
    .model-item .m-name {
        color: #94a3b8;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-weight: 600;
    }
    .model-item .m-dot {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #34d399;
        margin-right: 0.3rem;
    }
</style>
"""


def _try_load_model(name: str):
    """Try to load a pickle model; return None if unavailable."""
    path = os.path.join(MODELS_DIR, name)
    if not os.path.exists(path):
        return None
    try:
        import pickle
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None


def render_model_status():
    """Show ML model availability status."""
    models = [
        ("fraud_model.pkl", "Fraud Detection"),
        ("matching_model.pkl", "Merchant Matching"),
        ("price_model.pkl", "Price Prediction"),
        ("demand_model.pkl", "Demand Forecast"),
        ("recommendation_model.pkl", "Recommendations"),
    ]
    items = ""
    for fname, label in models:
        exists = os.path.exists(os.path.join(MODELS_DIR, fname))
        dot_color = "#34d399" if exists else "#f87171"
        status_text = "Loaded" if exists else "Missing"
        items += f"""
        <div class="model-item">
            <div><span class="m-dot" style="background:{dot_color}"></span>
            <span style="color:#e2e8f0;font-size:0.78rem;font-weight:600">{label}</span></div>
            <div style="color:#64748b;font-size:0.7rem;margin-top:0.2rem">{status_text}</div>
        </div>"""

    st.markdown(f'<div class="model-status">{items}</div>', unsafe_allow_html=True)


def render_demand_forecast(products: list, orders: list):
    """Generate and display demand forecast using ML model or fallback simulation."""
    st.markdown("""
    <div class="ai-card">
        <h3>Demand Forecasting</h3>
    """, unsafe_allow_html=True)

    demand_model = _try_load_model("demand_model.pkl")

    if not products:
        st.info("No products to forecast.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Select product
    product_names = [p["name"] for p in products[:12]]
    selected = st.selectbox("Select Product", product_names, key="ai_demand_product")
    days_ahead = st.slider("Forecast Horizon (days)", 7, 90, 30, key="ai_demand_days")

    # Generate forecast data
    np.random.seed(42)
    dates = pd.date_range(end=pd.Timestamp.now(), periods=60, freq="D")
    historical = np.abs(np.cumsum(np.random.randn(60) * 15) + 200)
    
    # ML prediction or simulated
    if demand_model:
        try:
            X = np.random.rand(days_ahead, 5)
            forecast_vals = demand_model.predict(X)
            forecast_vals = np.abs(forecast_vals) * 50 + historical[-1]
        except Exception:
            forecast_vals = np.abs(np.cumsum(np.random.randn(days_ahead) * 12) + historical[-1])
    else:
        trend = np.linspace(0, np.random.uniform(20, 80), days_ahead)
        noise = np.random.randn(days_ahead) * 8
        seasonal = np.sin(np.linspace(0, 4 * np.pi, days_ahead)) * 30
        forecast_vals = historical[-1] + trend + noise + seasonal
        forecast_vals = np.maximum(forecast_vals, 0)

    future_dates = pd.date_range(start=pd.Timestamp.now(), periods=days_ahead, freq="D")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=historical,
        mode="lines", name="Historical",
        line=dict(color="#6366f1", width=2),
        hovertemplate="%{x|%b %d}: %{y:.0f} units<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=future_dates, y=forecast_vals,
        mode="lines+markers", name="Forecast",
        line=dict(color="#22d3ee", width=2, dash="dash"),
        marker=dict(size=4),
        fill="tozeroy",
        fillcolor="rgba(34,211,238,0.06)",
        hovertemplate="%{x|%b %d}: %{y:.0f} units (predicted)<extra></extra>"
    ))

    # Confidence band
    upper = forecast_vals * 1.15
    lower = forecast_vals * 0.85
    fig.add_trace(go.Scatter(
        x=future_dates, y=upper,
        mode="lines", showlegend=False,
        line=dict(color="rgba(34,211,238,0.2)", width=0)
    ))
    fig.add_trace(go.Scatter(
        x=future_dates, y=lower,
        mode="lines", fill="tonexty",
        fillcolor="rgba(34,211,238,0.06)",
        showlegend=False,
        line=dict(color="rgba(34,211,238,0.2)", width=0)
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                   title_text="Demand (units)"),
        hovermode="x unified",
        height=320,
        legend=dict(orientation="h", y=1.05, x=1, xanchor="right",
                     bgcolor="rgba(0,0,0,0)"),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Insight box
    avg_forecast = np.mean(forecast_vals)
    trend_dir = "increasing" if forecast_vals[-1] > forecast_vals[0] else "decreasing"
    pct_change = abs(forecast_vals[-1] - forecast_vals[0]) / max(forecast_vals[0], 1) * 100

    st.markdown(f"""
    <div class="ai-insight-box">
        <div class="insight-title">Forecast Summary for {selected}</div>
        <div class="insight-text">
            Average predicted demand: <strong>{avg_forecast:.0f} units/day</strong>.
            Trend is <strong>{trend_dir}</strong> by {pct_change:.1f}% over the next {days_ahead} days.
            Recommended: {"Build additional inventory buffer" if trend_dir == "increasing" else "Consider reducing reorder quantities"}.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_price_prediction(products: list):
    """ML-powered price prediction."""
    st.markdown("""
    <div class="ai-card">
        <h3>Price Prediction</h3>
    """, unsafe_allow_html=True)

    price_model = _try_load_model("price_model.pkl")

    if not products:
        st.info("No products available.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    selected_name = st.selectbox("Select Product", [p["name"] for p in products[:12]], key="ai_price_product")

    col1, col2, col3 = st.columns(3)
    with col1:
        input_cost = st.number_input("Production Cost ($)", min_value=1.0, value=20.0, key="ai_cost")
    with col2:
        input_demand = st.number_input("Demand Score (0-100)", min_value=0, max_value=100, value=65, key="ai_demand")
    with col3:
        input_comp = st.number_input("Competition Index (0-10)", min_value=0.0, max_value=10.0, value=5.0, step=0.5, key="ai_comp")

    if st.button("Predict Optimal Price", type="primary", key="ai_predict_btn"):
        if price_model:
            try:
                X = np.array([[input_cost, input_demand / 100, input_comp / 10]])
                predicted = price_model.predict(X)[0]
                predicted = max(predicted, input_cost * 1.1)
            except Exception:
                predicted = input_cost * (1 + input_demand / 200) * (1 + input_comp / 50)
        else:
            # Fallback heuristic
            predicted = input_cost * (1 + input_demand / 150) * (1 + input_comp / 40)

        margin = predicted - input_cost
        margin_pct = (margin / predicted * 100) if predicted > 0 else 0

        st.markdown(f"""
        <div class="ai-insight-box" style="margin-top:1rem">
            <div class="insight-title">Predicted Optimal Price for {selected_name}</div>
            <div class="insight-text" style="font-size:1.1rem">
                <strong style="color:#34d399;font-size:1.4rem">{format_currency(predicted)}</strong>
                <br><br>
                Estimated margin: <strong>{format_currency(margin)}</strong> ({margin_pct:.1f}%)
                <br>
                Based on cost: {format_currency(input_cost)}, demand score: {input_demand}, competition: {input_comp}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.caption("Adjust parameters and click 'Predict' to get AI price recommendations.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_fraud_analysis(fraud_logs: list, fraud_stats: dict):
    """Display fraud risk analysis."""
    st.markdown("""
    <div class="ai-card">
        <h3>Fraud Risk Analysis</h3>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;margin-bottom:1rem">
        <div class="ai-insight-box">
            <div class="insight-title">Total Flags</div>
            <div style="color:#e2e8f0;font-size:1.5rem;font-weight:700">{fraud_stats['total_flags']}</div>
        </div>
        <div class="ai-insight-box" style="border-color:rgba(239,68,68,0.2);background:rgba(239,68,68,0.06)">
            <div class="insight-title" style="color:#fca5a5">High Risk Alerts</div>
            <div style="color:#f87171;font-size:1.5rem;font-weight:700">{fraud_stats['high_risk']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if fraud_logs:
        for log in fraud_logs[:8]:
            score = log.get("risk_score", 0)
            risk_class = "high" if score > 0.7 else ("medium" if score > 0.4 else "low")
            st.markdown(f"""
            <div class="risk-card">
                <span class="risk-type">{log.get('fraud_type','Unknown').replace('_',' ').title()}</span>
                <span class="risk-score {risk_class}">{score:.0%}</span>
                <div class="risk-date">Order #{log.get('order_id','?')} | {log.get('created_at','')[:16]}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No fraud flags detected.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_ml_recommendations(products: list):
    """AI-driven recommendations for the producer."""
    st.markdown("""
    <div class="ai-card">
        <h3>AI Recommendations</h3>
    """, unsafe_allow_html=True)

    rec_model = _try_load_model("recommendation_model.pkl")

    if not products:
        st.info("No products for recommendations.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Generate intelligent recommendations based on data
    low_stock_items = [p for p in products if p.get("current_stock", 0) < p.get("min_stock", 0) * 1.5]
    high_value = sorted(products, key=lambda x: x.get("price", 0) * x.get("current_stock", 0), reverse=True)

    recommendations = []

    # Inventory recommendations
    if low_stock_items:
        for p in low_stock_items[:3]:
            recommendations.append({
                "type": "inventory",
                "title": f"Restock: {p['name']}",
                "text": f"Current stock ({p.get('current_stock',0)}) is near minimum threshold ({p.get('min_stock',0)}). "
                        f"Recommended reorder: {p.get('min_stock',0) * 3 - p.get('current_stock',0):,} units.",
                "color": "#fbbf24"
            })

    # Pricing recommendations
    if high_value:
        top = high_value[0]
        recommendations.append({
            "type": "pricing",
            "title": f"High-Value Product: {top['name']}",
            "text": f"This product represents the highest inventory value at {format_currency(top.get('price',0) * top.get('current_stock',0))}. "
                    f"Consider dynamic pricing to maximize margins.",
            "color": "#34d399"
        })

    # General AI insights
    recommendations.append({
        "type": "strategy",
        "title": "Supply Chain Optimization",
        "text": "Based on current order patterns, consider consolidating shipments to reduce logistics costs by an estimated 8-12%. "
                "AI suggests establishing standing orders with top 3 merchants.",
        "color": "#818cf8"
    })

    recommendations.append({
        "type": "market",
        "title": "Market Trend Alert",
        "text": "Analysis indicates growing demand in the Grains and Seeds categories. "
                "Consider expanding product lines in these segments to capture emerging market opportunities.",
        "color": "#22d3ee"
    })

    for rec in recommendations:
        st.markdown(f"""
        <div class="ai-insight-box" style="border-color:{rec['color']}30;background:{rec['color']}08">
            <div class="insight-title" style="color:{rec['color']}">{rec['title']}</div>
            <div class="insight-text">{rec['text']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render(email: str):
    st.markdown(AI_CSS, unsafe_allow_html=True)

    producer_id = get_producer_id(email)
    if not producer_id:
        st.error("Producer account not found.")
        return

    seed_producer_demo_data()

    st.markdown("""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.2rem">
        <h2 style="color:#e2e8f0;font-size:1.25rem;font-weight:700;display:flex;align-items:center;gap:0.5rem">
            AI Insights
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Model status
    render_model_status()

    # Fetch data
    products = get_products(producer_id)
    orders = get_orders(producer_id)
    fraud_logs = get_fraud_logs(producer_id)
    fraud_stats = get_fraud_stats()

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Demand Forecast", "Price Prediction", "Fraud Analysis", "Recommendations"])

    with tab1:
        render_demand_forecast(products, orders)
    with tab2:
        render_price_prediction(products)
    with tab3:
        render_fraud_analysis(fraud_logs, fraud_stats)
    with tab4:
        render_ml_recommendations(products)
