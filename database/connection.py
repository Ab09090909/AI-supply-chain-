"""
Database Connection Manager
Singleton pattern for database access across the application
"""
import sqlite3
import threading
from typing import Optional
from pathlib import Path

class DatabaseConnection:
    """Thread-safe database connection manager"""
    
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
        """Initialize connection pool"""
        self._local.conn = None
        self._connect()
    
    def _connect(self):
        """Create new connection"""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=5000")
            self._local.conn = conn
        except Exception as e:
            print(f"Database connection error: {e}")
            self._local.conn = None
    
    def get_connection(self):
        """Get thread-local connection"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._connect()
        return self._local.conn
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute query with error handling"""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
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

# Global instance
db = DatabaseConnection()
