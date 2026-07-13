import streamlit as st

def render():
    st.header("📦 Inventory View")
    
    # Mock inventory data (replace with actual DB query)
    inventory = [
        {"item": "Widget A", "stock": 50, "min_stock": 20, "max_stock": 100},
        {"item": "Widget B", "stock": 5, "min_stock": 10, "max_stock": 50},
    ]
    
    # CRITICAL FIX: Completed the truncated list comprehension
    low_stock_count = sum(1 for item in inventory if item["stock"] < item["min_stock"])
    
    st.metric("⚠️ Low Stock Items", low_stock_count)
    
    for item in inventory:
        status = "🔴 Low" if item["stock"] < item["min_stock"] else "🟢 OK"
        st.write(f"**{item['item']}**: {item['stock']} units {status}")
