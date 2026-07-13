"""
Producer AI Assistant - Chat interface powered by Groq API
"""
import streamlit as st
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

CHAT_CSS = """
<style>
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
    }
    .chat-msg {
        display: flex;
        margin-bottom: 1rem;
        gap: 0.7rem;
    }
    .chat-msg.user {
        flex-direction: row-reverse;
    }
    .chat-avatar {
        width: 32px; height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        flex-shrink: 0;
    }
    .chat-msg.assistant .chat-avatar {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
    }
    .chat-msg.user .chat-avatar {
        background: linear-gradient(135deg, #0ea5e9, #06b6d4);
        color: white;
    }
    .chat-bubble {
        max-width: 75%;
        padding: 0.8rem 1.1rem;
        border-radius: 14px;
        font-size: 0.88rem;
        line-height: 1.6;
    }
    .chat-msg.assistant .chat-bubble {
        background: #1e293b;
        color: #e2e8f0;
        border-bottom-left-radius: 4px;
    }
    .chat-msg.user .chat-bubble {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border-bottom-right-radius: 4px;
    }
    .chat-input-area {
        position: sticky;
        bottom: 0;
        background: #0f172a;
        padding: 1rem;
        border-top: 1px solid rgba(255,255,255,0.06);
    }

    .suggestion-chip {
        display: inline-block;
        background: rgba(99,102,241,0.1);
        border: 1px solid rgba(99,102,241,0.25);
        color: #a5b4fc;
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        margin: 0.2rem;
        cursor: pointer;
    }

    .ai-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border-radius: 14px;
        padding: 1.4rem 1.5rem;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 4px 24px rgba(0,0,0,0.18);
        margin-bottom: 1.2rem;
    }
</style>
"""

SYSTEM_PROMPT = """You are an AI Supply Chain Assistant specialized in helping producers optimize their operations.

Your expertise includes:
- Inventory management and stock optimization
- Demand forecasting and production planning
- Pricing strategies and market analysis
- Supply chain logistics and fulfillment
- B2B negotiations and merchant relationships
- Risk assessment and fraud detection
- Regulatory compliance and quality standards

Always provide actionable, data-driven advice. Use specific numbers and recommendations when possible.
Keep responses concise but informative. Use bullet points for multi-step advice.
If asked about something outside supply chain, politely redirect to supply chain topics."""


def _get_groq_client():
    """Try to create Groq client."""
    try:
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            return None
        return Groq(api_key=api_key)
    except ImportError:
        return None


def _call_groq(chat_history: list, user_message: str) -> str:
    """Call Groq API with chat history."""
    client = _get_groq_client()
    if not client:
        return "Groq API key not configured. Please set GROQ_API_KEY in your .env file."

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_history[-10:])  # Last 10 messages for context
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling Groq API: {str(e)}"


def _fallback_response(user_message: str) -> str:
    """Provide helpful offline responses when Groq is not available."""
    msg = user_message.lower()

    if any(w in msg for w in ["inventory", "stock", "reorder"]):
        return """**Inventory Optimization Advice:**

Based on supply chain best practices, here are my recommendations:

- **ABC Analysis**: Classify your products into A (high value/low quantity), B (moderate), and C (low value/high quantity) categories
- **Safety Stock Formula**: Maintain safety stock = (Max daily usage x Max lead time) - (Average daily usage x Average lead time)
- **Reorder Point**: Set ROP = (Average daily demand x Lead time) + Safety stock
- **Economic Order Quantity (EOQ)**: Minimize total inventory costs by calculating optimal order sizes

Would you like me to analyze specific products from your inventory?"""

    elif any(w in msg for w in ["price", "pricing", "cost"]):
        return """**Pricing Strategy Recommendations:**

- **Cost-Plus Pricing**: Base price = Unit Cost x (1 + Markup %). Typical markup: 20-50% for commodities
- **Value-Based Pricing**: Set prices based on perceived value to merchants, especially for premium/organic products
- **Dynamic Pricing**: Adjust prices based on demand signals, seasonality, and competitor pricing
- **Volume Discounts**: Offer tiered pricing (e.g., 5% off for 100+ units, 10% for 500+ units)

Use the AI Insights > Price Prediction tab for ML-powered optimal pricing!"""

    elif any(w in msg for w in ["demand", "forecast", "predict"]):
        return """**Demand Forecasting Guidance:**

- **Seasonal Patterns**: Most agricultural products show seasonal demand. Review 12-24 months of data
- **Leading Indicators**: Watch for merchant order patterns, market indices, and weather forecasts
- **AI Forecasting**: Use the AI Insights > Demand Forecast tab for ML-powered predictions
- **Safety Buffer**: Always maintain a 15-20% buffer above forecasted demand for unexpected spikes

Check the Demand Forecast tab for real-time ML predictions!"""

    elif any(w in msg for w in ["fraud", "risk", "security"]):
        return """**Fraud Prevention Best Practices:**

- **Order Velocity Checks**: Flag accounts placing unusual volumes of orders in short periods
- **Price Anomaly Detection**: Monitor for orders at prices significantly above or below market rates
- **Geographic Mismatch**: Verify that shipping and billing addresses are consistent
- **New Account Scrutiny**: Apply higher risk thresholds to new merchant accounts

Use the AI Insights > Fraud Analysis tab to review flagged transactions."""

    elif any(w in msg for w in ["supply chain", "logistics", "shipping"]):
        return """**Supply Chain Optimization Tips:**

- **Lead Time Reduction**: Work with logistics partners to reduce average delivery times
- **Consolidation**: Combine multiple small orders into larger shipments to reduce per-unit costs
- **Route Optimization**: Use AI-powered route planning to minimize transportation costs
- **Real-Time Tracking**: Implement tracking systems for end-to-end visibility
- **Supplier Diversification**: Maintain backup suppliers to mitigate disruption risks"""

    else:
        return """I'm your AI Supply Chain Assistant. Here's what I can help with:

- **Inventory Management** - Stock optimization, reorder points, safety stock levels
- **Demand Forecasting** - Predict future demand using ML models
- **Price Optimization** - Get AI-powered pricing recommendations
- **Fraud Detection** - Review risk analysis and prevention strategies
- **Logistics** - Supply chain optimization and shipping efficiency
- **Market Analysis** - Category performance and trend insights

Try asking me about any of these topics, or explore the AI Insights tab for visual analytics!"""


def render_chat_history(chat_history: list):
    """Render chat messages as HTML bubbles."""
    if not chat_history:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;color:#64748b">
            <div style="font-size:2.5rem;margin-bottom:0.8rem">🤖</div>
            <div style="font-size:1rem;font-weight:600;color:#94a3b8;margin-bottom:0.3rem">
                AI Supply Chain Assistant
            </div>
            <div style="font-size:0.85rem">
                Ask me about inventory, pricing, demand forecasting, fraud detection, or supply chain optimization.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    html = '<div class="chat-container">'
    for msg in chat_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        avatar = "🤖" if role == "assistant" else "👤"
        # Basic markdown-like formatting
        content_fmt = content.replace("\n", "<br>").replace("**", "<strong>").replace("**", "</strong>")
        html += f"""
        <div class="chat-msg {role}">
            <div class="chat-avatar">{avatar}</div>
            <div class="chat-bubble">{content_fmt}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render(email: str):
    st.markdown(CHAT_CSS, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.2rem">
        <h2 style="color:#e2e8f0;font-size:1.25rem;font-weight:700;display:flex;align-items:center;gap:0.5rem">
            AI Assistant
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # API status
    groq_available = _get_groq_client() is not None
    status_color = "#34d399" if groq_available else "#fbbf24"
    status_text = "Connected (Groq API)" if groq_available else "Offline Mode (Built-in responses)"
    st.markdown(f"""
    <div class="ai-card">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem">
            <span style="width:8px;height:8px;border-radius:50%;background:{status_color};display:inline-block"></span>
            <span style="color:#94a3b8;font-size:0.8rem;font-weight:600">{status_text}</span>
        </div>
        <div style="color:#64748b;font-size:0.78rem">
            {'Connected to Groq Llama3 for intelligent supply chain advice.' if groq_available else 'Set GROQ_API_KEY in .env for AI-powered responses. Currently using built-in knowledge base.'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    # Suggestion chips
    st.markdown("**Quick Questions:**", unsafe_allow_html=True)
    suggestions = [
        "How can I optimize my inventory levels?",
        "What pricing strategy should I use?",
        "How to forecast demand for next quarter?",
        "Best practices for fraud prevention?",
    ]
    chips_html = " ".join([f'<span class="suggestion-chip">{s}</span>' for s in suggestions])
    st.markdown(chips_html, unsafe_allow_html=True)

    # Chat history
    render_chat_history(st.session_state.ai_chat_history)

    # Input
    user_input = st.chat_input("Ask about supply chain, inventory, pricing...")

    if user_input:
        # Add user message
        st.session_state.ai_chat_history.append({"role": "user", "content": user_input})

        # Get response
        with st.spinner("Thinking..."):
            if groq_available:
                response = _call_groq(st.session_state.ai_chat_history, user_input)
            else:
                response = _fallback_response(user_input)

        st.session_state.ai_chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    # Clear chat button
    if st.session_state.ai_chat_history:
        if st.button("Clear Chat", use_container_width=True, key="clear_chat"):
            st.session_state.ai_chat_history = []
            st.rerun()
