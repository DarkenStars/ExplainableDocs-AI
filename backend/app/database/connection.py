"""Database connection management."""

import os
from typing import Optional
from psycopg2.pool import SimpleConnectionPool


class DatabasePool:
    """Manages PostgreSQL connection pool."""
    
    def __init__(self):
        self.pool: Optional[SimpleConnectionPool] = None
    
    def initialize(self, db_config: dict) -> None:
        """Initialize the connection pool."""
        try:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                dbname=db_config['DB_NAME'],
                user=db_config['DB_USER'],
                password=db_config['DB_PASSWORD'],
                host=db_config['DB_HOST'],
                port=db_config['DB_PORT']
            )
            print("Database connection pool initialized.")
        except Exception as e:
            self.pool = None
            print(f"[WARN] DB pool init failed; caching disabled. Details: {e}")
    
    def get_connection(self):
        """Get a connection from the pool."""
        if self.pool is None:
            return None
        return self.pool.getconn()
    
    def put_connection(self, conn):
        """Return a connection to the pool."""
        if self.pool and conn:
            self.pool.putconn(conn)
    
    def close_all(self):
        """Close all connections in the pool."""
        if self.pool:
            self.pool.closeall()
            self.pool = None


# Global database pool instance
db_pool = DatabasePool()