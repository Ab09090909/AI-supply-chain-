"""
Producer AI Assistant Chat
Self-contained module
"""
import streamlit as st
import os
from datetime import datetime

class AIAssistant:
    """AI Assistant for Producer Portal"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.history_key = "producer_chat_history"
        self.context = "producer"
    
    def render(self):
        """Render AI assistant chat interface"""
        st.subheader("🤖 AI Supply Chain Assistant")
        st.caption("Ask me anything about inventory, pricing, demand, or logistics")
        
        # Initialize history
        if self.history_key not in st.session_state:
            st.session_state[self.history_key] = []
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display last 10 messages
            for msg in st.session_state[self.history_key][-10:]:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about your supply chain..."):
            # Add user message
            st.session_state[self.history_key].append({
                "role": "user",
                "content": prompt,
                "time": datetime.now().strftime("%H:%M")
            })
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    response = self._generate_response(prompt)
                    st.write(response)
            
            # Add assistant response to history
            st.session_state[self.history_key].append({
                "role": "assistant",
                "content": response,
                "time": datetime.now().strftime("%H:%M")
            })
            
            st.rerun()
        
        # Clear button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state[self.history_key] = []
                st.rerun()
        with col2:
            if st.button("💾 Export Chat"):
                st.success("Chat exported!")
    
    def _generate_response(self, prompt: str) -> str:
        """Generate context-aware responses for producer"""
        prompt_lower = prompt.lower()
        
        # Inventory related
        if any(word in prompt_lower for word in ["inventory", "stock", "restock"]):
            return ("📦 **Inventory Status:**\n\n"
                   "- **Avocados** (AGR-003): 12 units - **CRITICAL** (min: 40)\n"
                   "- **Fresh Dairy** (AGR-002): 35 units - **LOW** (min: 50)\n"
                   "- **Organic Carrots** (AGR-006): 0 units - **OUT OF STOCK**\n\n"
                   "💡 Recommendation: Restock avocados immediately. Consider increasing reorder point to 50 based on recent demand.")
        
        # Price related
        elif any(word in prompt_lower for word in ["price", "forecast", "cost"]):
            return ("💰 **Price Analysis:**\n\n"
                   "- **Current wheat price:** $4.20/ton\n"
                   "- **30-day forecast:** $4.42/ton (+5%)\n"
                   "- **Market trend:** Rising due to seasonal demand\n\n"
                   "💡 Recommendation: Lock in current contracts for 60-day supply to avoid price increases.")
        
        # Demand related
        elif any(word in prompt_lower for word in ["demand", "sales", "trend"]):
            return ("📈 **Demand Forecast:**\n\n"
                   "- **Dairy products:** +15% spike expected this weekend\n"
                   "- **Grains:** Steady increase (+3%)\n"
                   "- **Fruits:** Stable demand\n"
                   "- **Vegetables:** Seasonal dip (-5%)\n\n"
                   "💡 Recommendation: Increase dairy production by 20% for weekend supply.")
        
        # Order related
        elif any(word in prompt_lower for word in ["order", "pending", "agreement"]):
            return ("📋 **Pending Orders:**\n\n"
                   "1. **#ORD-2024-0891** - Metro Retail Inc - Organic Wheat - $12,500 - **Pending**\n"
                   "2. **#ORD-2024-0890** - Fresh Market Co - Avocados - $3,400 - **Awaiting Response**\n\n"
                   "💡 Recommendation: Review agreements for both orders. Metro Retail has excellent payment history.")
        
        # Merchant related
        elif any(word in prompt_lower for word in ["merchant", "match", "partner"]):
            return ("🤝 **Top Merchant Matches:**\n\n"
                   "1. **FoodCo Distributors** - 95% match, 15mi away\n"
                   "2. **FreshChain Inc** - 87% match, 25mi away\n"
                   "3. **OrganicMarket** - 82% match, 30mi away\n\n"
                   "💡 Recommendation: Contact FoodCo Distributors first - highest match score and closest proximity.")
        
        # General
        else:
            return ("I'm your AI supply chain assistant! I can help with:\n\n"
                   "- 📦 **Inventory** - Stock levels, restocking, optimization\n"
                   "- 💰 **Pricing** - Market trends, forecasts, contracts\n"
                   "- 📈 **Demand** - Sales predictions, seasonal trends\n"
                   "- 📋 **Orders** - Status, agreements, contracts\n"
                   "- 🤝 **Merchants** - Matching, partnerships\n\n"
                   "What would you like to know?")

# Create singleton instance
assistant = AIAssistant()

def render():
    """Main render function"""
    assistant.render()
