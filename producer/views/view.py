import streamlit as st

# CRITICAL FIX: REMOVED st.set_page_config() to prevent StreamlitSetPageConfigError

def is_authenticated():
    """Checks unified session state authentication"""
    return st.session_state.get("logged_in", False) and st.session_state.get("role") == "producer"

def render():
    if not is_authenticated():
        st.warning("⚠️ Please log in to access the producer portal.")
        return
    
    st.success("✅ Authentication successful. Producer view rendered.")
    # Additional view logic here

# Kept for clarity, but render() is the intended import for app.py
def main():
    render()
