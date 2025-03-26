"""
Database connection module for PostgreSQL.
"""

import os
import logging
import psycopg2
from psycopg2 import pool

logger = logging.getLogger(__name__)

class Database:
    """
    PostgreSQL database connection handler.
    Uses connection pooling for better performance.
    """
    
    def __init__(self):
        """Initialize database connection pool."""
        try:
            # Get database credentials from environment variables
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '5432')
            db_name = os.getenv('DB_NAME', 'wallet_monitor')
            db_user = os.getenv('DB_USER', 'postgres')
            db_password = os.getenv('DB_PASSWORD', 'postgres')
            
            # Create connection pool
            self.connection_pool = pool.SimpleConnectionPool(
                1,  # minconn
                10,  # maxconn
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            
            logger.info("Database connection pool initialized successfully")
            
        except (Exception, psycopg2.Error) as error:
            logger.error(f"Error while connecting to PostgreSQL: {error}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool."""
        return self.connection_pool.getconn()
    
    def release_connection(self, conn):
        """Release connection back to the pool."""
        self.connection_pool.putconn(conn)
    
    def execute_query(self, query, params=None):
        """
        Execute a query and return the results.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Parameters for the query
            
        Returns:
            list: Query results as a list of tuples
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            # Check if the query returns data
            if cursor.description:
                return cursor.fetchall()
            
            conn.commit()
            return []
            
        except (Exception, psycopg2.Error) as error:
            if conn:
                conn.rollback()
            logger.error(f"Error executing query: {error}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.release_connection(conn)
    
    def execute_many(self, query, params_list):
        """
        Execute multiple queries with different parameters.
        
        Args:
            query (str): SQL query to execute
            params_list (list): List of parameter tuples
            
        Returns:
            bool: True if successful
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return True
            
        except (Exception, psycopg2.Error) as error:
            if conn:
                conn.rollback()
            logger.error(f"Error executing batch query: {error}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.release_connection(conn)
    
    def close(self):
        """Close all database connections."""
        if hasattr(self, 'connection_pool'):
            self.connection_pool.closeall()
            logger.info("All database connections closed") 