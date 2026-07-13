"""
Producer Authentication Module (Supabase Auth)
Handles login, logout, session management, and role-based access
"""
import streamlit as st
from supabase import create_client, Client
from datetime import datetime
from typing import Optional, Dict
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "your-anon-key")  # Public key, safe for client-side

# -----------------------------------------------------------------------------
# Session State Keys
# -----------------------------------------------------------------------------
SESSION_USER = "producer_user"
SESSION_ACCESS_TOKEN = "producer_access_token"
SESSION_REFRESH_TOKEN = "producer_refresh_token"
SESSION_EXPIRY = "producer_token_expiry"
AUTH_ERROR = "auth_error"

# -----------------------------------------------------------------------------
# Authentication Functions
# -----------------------------------------------------------------------------
def get_supabase_client() -> Client:
    """Get Supabase client with current user's session"""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def is_authenticated() -> bool:
    """Check if user is currently logged in"""
    return (
        st.session_state.get(SESSION_USER) is not None and
        st.session_state.get(SESSION_ACCESS_TOKEN) is not None
    )

def get_current_user() -> Optional[Dict]:
    """Get current logged-in user info"""
    return st.session_state.get(SESSION_USER)

def require_auth() -> bool:
    """
    Protect routes - returns True if authenticated, False otherwise.
    Use this at the top of protected pages.
    """
    if not is_authenticated():
        st.session_state[AUTH_ERROR] = "Please log in to access this page"
        st.switch_page("app.py")  # Redirect to login page
        return False
    return True

def get_user_role() -> str:
    """Get current user's role (defaults to 'viewer' if not set)"""
    user = get_current_user()
    if user and "role" in user:
        return user["role"]
    return "viewer"

# -----------------------------------------------------------------------------
# Login/Signup UI
# -----------------------------------------------------------------------------
def render_auth_ui():
    """Render login/signup form in sidebar"""
    with st.sidebar:
        st.title("🔐 Account")
        
        if is_authenticated():
            user = get_current_user()
            st.success(f"Logged in as: **{user.get('email', 'User')}**")
            st.caption(f"Role: {user.get('role', 'Producer').title()}")
            
            if st.button("Logout", use_container_width=True, type="secondary"):
                logout()
        else:
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
            with tab1:
                with st.form("login_form"):
                    email = st.text_input("Email", placeholder="you@company.com")
                    password = st.text_input("Password", type="password")
                    submit = st.form_submit_button("Login", use_container_width=True, type="primary")
                    
                    if submit and email and password:
                        login(email, password)
            
            with tab2:
                with st.form("signup_form"):
                    email = st.text_input("Email", placeholder="you@company.com")
                    password = st.text_input("Password", type="password", min_value=8)
                    confirm_password = st.text_input("Confirm Password", type="password")
                    role = st.selectbox("Role", ["producer", "executive", "finance", "client"])
                    submit = st.form_submit_button("Create Account", use_container_width=True)
                    
                    if submit and email and password and password == confirm_password:
                        signup(email, password, role)

# -----------------------------------------------------------------------------
# Core Auth Methods
# -----------------------------------------------------------------------------
def login(email: str, password: str) -> bool:
    """Authenticate user with Supabase"""
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Get user profile from database (assuming you have a profiles table)
            # Or extract role from user metadata if stored there
            user_metadata = response.user.user_metadata or {}
            user_data = {
                "id": response.user.id,
                "email": response.user.email,
                "role": user_metadata.get("role", "producer"),
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_at": datetime.fromtimestamp(response.session.expires_at).isoformat()
            }
            
            st.session_state[SESSION_USER] = user_data
            st.session_state[SESSION_ACCESS_TOKEN] = response.session.access_token
            st.session_state[SESSION_REFRESH_TOKEN] = response.session.refresh_token
            st.session_state[SESSION_EXPIRY] = user_data["expires_at"]
            
            st.success("Login successful!")
            st.rerun()
            return True
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False
    return False

def signup(email: str, password: str, role: str = "producer") -> bool:
    """Create new user account"""
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "role": role
                }
            }
        })
        
        if response.user:
            st.success("Account created! Please check your email to verify.")
            return True
    except Exception as e:
        st.error(f"Signup failed: {str(e)}")
        return False
    return False

def logout():
    """Logout user and clear session"""
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
    except Exception as e:
        print(f"Sign out error: {str(e)}")
    
    # Clear session state
    st.session_state.pop(SESSION_USER, None)
    st.session_state.pop(SESSION_ACCESS_TOKEN, None)
    st.session_state.pop(SESSION_REFRESH_TOKEN, None)
    st.session_state.pop(SESSION_EXPIRY, None)
    
    st.success("Logged out successfully")
    st.rerun()

def refresh_session():
    """Refresh access token if expired"""
    if not is_authenticated():
        return False
    
    try:
        supabase = get_supabase_client()
        refresh_token = st.session_state.get(SESSION_REFRESH_TOKEN)
        
        if refresh_token:
            response = supabase.auth.refresh_session(refresh_token)
            if response.session:
                st.session_state[SESSION_ACCESS_TOKEN] = response.session.access_token
                st.session_state[SESSION_REFRESH_TOKEN] = response.session.refresh_token
                st.session_state[SESSION_EXPIRY] = datetime.fromtimestamp(response.session.expires_at).isoformat()
                return True
    except Exception as e:
        print(f"Token refresh failed: {str(e)}")
        logout()
    return False
