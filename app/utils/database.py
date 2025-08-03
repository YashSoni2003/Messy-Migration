import sqlite3
import threading
from contextlib import contextmanager
import time

class DatabaseManager:
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self._local = threading.local()
        self._connection_count = 0
        self._max_connections = 10
    
    def get_connection(self):
        if not hasattr(self._local, 'connection'):
            if self._connection_count >= self._max_connections:
                time.sleep(0.1) 
            
            self._local.connection = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,
                timeout=30.0
            )
            self._local.connection.row_factory = sqlite3.Row
            self._local.connection.execute("PRAGMA journal_mode=WAL")  
            self._connection_count += 1
        return self._local.connection
    
    @contextmanager
    def get_cursor(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query, params=()):
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_single_query(self, query, params=()):
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def execute_update(self, query, params=()):
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def close_connection(self):
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            del self._local.connection
            self._connection_count -= 1

db_manager = DatabaseManager()
