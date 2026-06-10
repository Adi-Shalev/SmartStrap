"""
Database Connection Manager
----------------------------
Provides a single, reusable way to obtain MySQL connections.
All modules that need DB access import from here — never call
mysql.connector.connect() directly.

Usage:
    from BackEnd.db_connection import get_connection

    conn = get_connection()
    # ... use conn ...
    conn.close()
"""

import mysql.connector
from mysql.connector import Error

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_CONFIG


def get_connection(config=None):
    """
    Create and return a new MySQL connection using centralized config.

    Parameters
    ----------
    config : dict, optional
        Override DB_CONFIG for testing or alternate databases.

    Returns
    -------
    mysql.connector.connection.MySQLConnection or None
        An active connection, or None if the connection failed.
    """
    cfg = config or DB_CONFIG
    try:
        conn = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
        )
        return conn
    except Error as e:
        print(f"❌ Database connection failed: {e}")
        return None


def test_connection(config=None):
    """Quick connectivity check. Returns True if DB is reachable."""
    conn = get_connection(config)
    if conn and conn.is_connected():
        print(f"✅ Connected to MySQL: {conn.get_server_info()}")
        conn.close()
        return True
    return False


if __name__ == "__main__":
    test_connection()
