"""
Producer Marketplace / Merchant Matching
"""
import streamlit as st
import random
import time

def render():
    """Render merchant matching page"""
    st.title("🤝 AI Merchant Matching")
    st.caption("Find the best merchants for your products using AI-powered matching")
    
    # Matching Criteria
    st.subheader("🎯 Matching Criteria")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category = st.selectbox(
            "Product Category",
            ["Grains", "Dairy", "Fruits", "Vegetables", "All"]
        )
    
    with col2:
        radius = st.slider(
            "Delivery Radius (miles)",
            min_value=10,
            max_value=500,
            value=100,
            step=10
        )
    
    with col3:
        min_rating = st.slider(
            "Minimum Merchant Rating",
            min_value=1.0,
            max_value=5.0,
            value=4.0,
            step=0.1
        )
    
    st.markdown("---")
    
    # Run Matching
    if st.button("🔍 Find Matches", type="primary", use_container_width=True):
        with st.spinner("Analyzing 2,400 merchants..."):
            time.sleep(1.5)  # Simulate processing
            
            # Generate mock matches
            matches = [
                {"name": "FoodCo Distributors", "match": 95, "distance": 15, "rating": 4.8, "capacity": "1000 units/week"},
                {"name": "FreshChain Inc", "match": 87, "distance": 25, "rating": 4.6, "capacity": "800 units/week"},
                {"name": "OrganicMarket", "match": 82, "distance": 30, "rating": 4.5, "capacity": "600 units/week"},
                {"name": "Global Foods Ltd", "match": 78, "distance": 45, "rating": 4.4, "capacity": "1200 units/week"},
                {"name": "LocalHarvest Co", "match": 75, "distance": 60, "rating": 4.3, "capacity": "500 units/week"},
            ]
            
            st.subheader("🏆 Top Merchant Matches")
            
            for idx, match in enumerate(matches, 1):
                with st.container():
                    col_a, col_b, col_c, col_d, col_e = st.columns([3, 1, 1, 2, 1])
                    
                    with col_a:
                        st.write(f"**{idx}. {match['name']}**")
                        st.caption(f"Capacity: {match['capacity']}")
                    
                    with col_b:
                        st.metric("Match", f"{match['match']}%")
                    
                    with col_c:
                        st.caption(f"📍 {match['distance']} mi")
                    
                    with col_d:
                        st.metric("Rating", f"{match['rating']}⭐")
                    
                    with col_e:
                        if st.button("Contact", key=f"contact_{idx}"):
                            st.success(f"Contact request sent to {match['name']}!")
                    
                    st.markdown("---")
    
    # Past Matches
    st.subheader("📜 Matching History")
    
    history = [
        {"date": "2024-01-18", "merchant": "Metro Retail Inc", "product": "Organic Wheat", "status": "Accepted"},
        {"date": "2024-01-15", "merchant": "Fresh Market Co", "product": "Dairy", "status": "Pending"},
        {"date": "2024-01-10", "merchant": "Organic Suppliers", "product": "Avocados", "status": "Accepted"},
    ]
    
    for h in history:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"**{h['date']}**")
        with col2:
            st.write(h['merchant'])
        with col3:
            st.write(h['product'])
        with col4:
            if h['status'] == "Accepted":
                st.success(h['status'])
            else:
                st.warning(h['status'])
        st.markdown("---")
