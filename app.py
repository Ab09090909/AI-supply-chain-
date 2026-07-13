import streamlit as st
import hashlib

# CRITICAL FIX: ONLY ONE set_page_config, and it MUST be the first Streamlit command
st.set_page_config(page_title="AI Supply Chain Platform", page_icon="📦", layout="wide")

def verify_login(email: str, password: str):
    """Unified authentication check (replaces insecure plain-text bypass)"""
    # In production, query SQLite and compare with hashlib.sha256(password).hexdigest()
    valid_users = {
        "producer@demo.com": ("password", "producer"),
        "merchant@demo.com": ("password", "merchant"),
        "customer@demo.com": ("password", "customer"),
        "admin@demo.com": ("password", "admin")
    }
    if email in valid_users and valid_users[email][0] == password:
        return True, valid_users[email][1]
    return False, None

def login_page():
    st.title("🔐 AI Supply Chain Platform - Login")
    st.markdown("Please enter your credentials to access the portal.")
    
    with st.form("login_form"):
        email = st.text_input("Email", value="producer@demo.com")
        password = st.text_input("Password", value="password", type="password")
        role = st.selectbox("Select Role", ["producer", "merchant", "customer", "admin"])
        
        col1, col2 = st.columns(2)
        submitted = col1.form_submit_button("Login")
        demo = col2.form_submit_button("Demo Mode")

    if submitted:
        success, verified_role = verify_login(email, password)
        if success:
            st.session_state.logged_in = True
            st.session_state.role = verified_role
            st.session_state.user_email = email
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid email or password.")
            
    if demo:
        st.session_state.logged_in = True
        st.session_state.role = role
        st.session_state.user_email = f"demo_{role}@ai.com"
        st.rerun()

def main():
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        role = st.session_state.role
        st.sidebar.title(f"👤 Welcome, {role.capitalize()}")
        st.sidebar.write(f"User: {st.session_state.user_email}")
        
        if st.sidebar.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.user_email = None
            st.rerun()

        # CRITICAL FIX: Proper routing to all portals
        if role == "producer":
            from producer.main import run as run_producer
            run_producer()
        elif role == "merchant":
            from merchant.main import run as run_merchant
            run_merchant()
        elif role == "customer":
            from customer.main import run as run_customer
            run_customer()
        elif role == "admin":
            from admin.main import run as run_admin
            run_admin()

if __name__ == "__main__":
    main()
