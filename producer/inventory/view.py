"""
Producer Inventory View
"""
import streamlit as st
import pandas as pd
from producer.utils.db import db
from producer.utils.helpers import get_stock_status, format_currency

def render():
    """Render inventory management page"""
    st.title("📦 Inventory Management")
    st.caption("Track stock levels and manage products")
    
    # Use db (ProducerDB instance)
    inventory = db.get_inventory()
    
    # KPI Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total SKUs", len(inventory))
    
    with col2:
        total_value = sum(item.get('stock', 0) * item.get('price', 0) for item in inventory)
        st.metric("Stock Value", f"${total_value:,.2f}")
    
    with col3:
        low_stock = sum(1 for item in inventory 
                       if 0 < item.get('stock', 0) <= item.get('reorder_point', 0) * 1.2)
        st.metric("Low Stock", low_stock, delta_color="inverse")
    
    with col4:
        out_of_stock = sum(1 for item in inventory if item.get('stock', 0) == 0)
        st.metric("Out of Stock", out_of_stock, delta_color="inverse")
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("🔍 Search", placeholder="Search products...")
    with col2:
        category_filter = st.selectbox("Category", ["All", "Grains", "Dairy", "Fruits", "Vegetables"])
    with col3:
        stock_filter = st.selectbox("Stock Status", ["All", "Critical", "Low", "Good"])
    
    # Filter inventory
    filtered_inventory = inventory
    if search:
        filtered_inventory = [item for item in filtered_inventory 
                             if search.lower() in item.get('name', '').lower() 
                             or search.lower() in item.get('sku', '').lower()]
    if category_filter != "All":
        filtered_inventory = [item for item in filtered_inventory if item.get('category') == category_filter]
    
    # Inventory Table
    st.subheader("Inventory Items")
    
    if filtered_inventory:
        df_data = []
        for item in filtered_inventory:
            stock = item.get('stock', 0)
            min_stock = item.get('reorder_point', 0)
            status, emoji = get_stock_status(stock, min_stock)
            
            df_data.append({
                "SKU": item.get('sku', ''),
                "Product": item.get('name', ''),
                "Category": item.get('category', ''),
                "Stock": f"{stock} {item.get('unit', 'units')}",
                "Min Level": min_stock,
                "Status": f"{emoji} {status}",
                "Price": format_currency(item.get('price', 0)),
                "Value": format_currency(stock * item.get('price', 0))
            })
        
        df = pd.DataFrame(df_data)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn("Status", width="small")
            }
        )
    else:
        st.warning("No inventory items found matching your criteria.")
    
    # Restock Actions
    st.subheader("📦 Restock Management")
    low_items = [item for item in inventory if item.get('stock', 0) <= item.get('reorder_point', 0) * 1.2]
    
    if low_items:
        st.warning(f"⚠️ {len(low_items)} items need restocking:")
        
        for item in low_items:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{item.get('name')}** ({item.get('sku')})")
                    st.caption(f"Current: {item.get('stock')} | Min: {item.get('reorder_point')}")
                with col2:
                    if st.button("📦 Restock", key=f"restock_{item.get('sku')}"):
                        st.session_state[f"restock_{item.get('sku')}"] = True
                with col3:
                    if st.button("📊 History", key=f"history_{item.get('sku')}"):
                        st.info(f"Stock history for {item.get('name')}: Last 30 days average = {item.get('reorder_point', 10) * 2} units")
                st.markdown("---")
    else:
        st.success("✅ All stock levels are healthy!")
    
    # Export
    if st.button("📥 Export Inventory CSV"):
        csv = pd.DataFrame(inventory).to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            "inventory.csv",
            "text/csv",
            key='download-csv'
        )
