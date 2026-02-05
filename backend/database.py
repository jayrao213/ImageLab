"""
Database connection utilities
Migrated from photoapp.py get_dbConn logic
"""

import pymysql
import logging
from contextlib import contextmanager
from config import settings


def get_dbConn():
    """
    Creates and returns a pymysql connection object based on configuration.
    You should call close() on the object when you are done.
    
    This function preserves the exact logic from the original photoapp.py
    
    Returns:
        pymysql connection object
    
    Raises:
        Exception: If connection fails
    """
    try:
        dbConn = pymysql.connect(
            host=settings.rds_endpoint,
            port=settings.rds_port,
            user=settings.rds_username,
            passwd=settings.rds_password,
            database=settings.rds_database,
            # Allow execution of a query string with multiple SQL queries
            client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
        )
        return dbConn
    
    except Exception as err:
        logging.error("get_dbConn():")
        logging.error(str(err))
        raise


@contextmanager
def get_db_cursor():
    """
    Context manager for database operations.
    Automatically handles connection and cursor cleanup.
    
    Usage:
        with get_db_cursor() as (conn, cursor):
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
    
    Yields:
        tuple: (connection, cursor)
    """
    dbConn = None
    dbCursor = None
    try:
        dbConn = get_dbConn()
        dbCursor = dbConn.cursor()
        yield dbConn, dbCursor
    finally:
        if dbCursor:
            try:
                dbCursor.close()
            except:
                pass
        if dbConn:
            try:
                dbConn.close()
            except:
                pass
