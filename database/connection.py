"""
Database Connection Manager
Supports both SQLite (local) and PostgreSQL (Supabase)
"""
import os
import sqlite3
import threading
from typing import Optional
from pathlib import Path

# Determine database type
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL connection string
USE_POSTGRES = DATABASE_URL and DATABASE_URL.startswith("postgresql://")

if USE_POSTGRES:
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        raise ImportError("psycopg2 is required for PostgreSQL. Install with: pip install psycopg2-binary")

class DatabaseConnection:
    """Thread-safe database connection manager supporting SQLite and PostgreSQL"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: str = "data/supply_chain.db"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.db_path = db_path
                    cls._instance._local = threading.local()
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize connection"""
        self._local.conn = None
        if USE_POSTGRES:
            self._connect_postgres()
        else:
            self._connect_sqlite()
    
    def _connect_sqlite(self):
        """Connect to SQLite database"""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=5000")
            self._local.conn = conn
            print("✅ Connected to SQLite database")
        except Exception as e:
            print(f"❌ SQLite connection error: {e}")
    
    def _connect_postgres(self):
        """Connect to PostgreSQL database"""
        try:
            conn = psycopg2.connect(
                DATABASE_URL,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            conn.autocommit = False
            self._local.conn = conn
            print("✅ Connected to PostgreSQL database")
        except Exception as e:
            print(f"❌ PostgreSQL connection error: {e}")
    
    def get_connection(self):
        """Get thread-local connection"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            if USE_POSTGRES:
                self._connect_postgres()
            else:
                self._connect_sqlite()
        return self._local.conn
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute query with error handling (works for both SQLite and PostgreSQL)"""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            
            # Convert JSON placeholders for PostgreSQL
            if USE_POSTGRES:
                # Replace ? with %s for psycopg2
                query = query.replace("?", "%s")
                # Convert JSONB operations if needed
                query = query.replace("JSON_EXTRACT", "jsonb_extract_path_text")
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = [dict(row) for row in cursor.fetchall()]
            else:
                result = cursor.lastrowid
            
            conn.commit()
            return result
        except Exception as e:
            print(f"Query error: {e}")
            conn.rollback()
            return None
    
    def close(self):
        """Close connection"""
        if hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None

# Global instance - auto-detects database type
db = DatabaseConnection()
