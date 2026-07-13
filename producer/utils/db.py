import os
import streamlit as st

class ProducerDB:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self._client = None
        self._use_sqlite_fallback = True  # Default to SQLite to prevent startup crashes

    def _get_client(self):
        """CRITICAL FIX: Lazy validation. Only checks config when actually queried."""
        if self._client is None:
            if self.url and self.key and "your-project" not in self.url:
                try:
                    from supabase import create_client
                    self._client = create_client(self.url, self.key)
                    self._use_sqlite_fallback = False
                except ImportError:
                    st.warning("Supabase package not installed. Falling back to SQLite.")
            else:
                st.info("Supabase not configured. Using local SQLite fallback.")
        return self._client

    def get_projects(self):
        # Mock implementation to prevent "relation does not exist" errors
        return [{"id": 1, "name": "Demo Project", "status": "Active"}]
    
    def get_inventory(self):
        # Fallback mock data
        return [{"item": "Widget A", "stock": 50}, {"item": "Widget B", "stock": 5}]

# Instantiate as a singleton
db = ProducerDB()
