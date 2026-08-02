"""
Database Connection Manager
----------------------------
Provides a singleton DatabaseManager class for MySQL connections.
All modules that need DB access should use this class — never call
mysql.connector.connect() directly.

Usage:
    from db_connection import DatabaseManager

    db = DatabaseManager.get_instance()
    conn = db.get_connection()
    # ... use conn ...
    db.close()
"""

import mysql.connector
from mysql.connector import Error

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_CONFIG


class DatabaseManager:
    """
    Singleton class that manages the MySQL database connection.
    Ensures a single, reusable connection across the application.
    """
    _instance = None

    def __init__(self, config=None):
        """
        Initialize with database configuration.

        Parameters
        ----------
        config : dict, optional
            Override DB_CONFIG for testing or alternate databases.
        """
        self._config = config or DB_CONFIG
        self._connection = None

    @classmethod
    def get_instance(cls, config=None):
        """
        Returns the singleton DatabaseManager instance.
        Creates one on first call.
        """
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance

    def get_connection(self):
        """
        Returns an active MySQL connection.
        Creates a new one if none exists or the current one is disconnected.

        Returns
        -------
        mysql.connector.connection.MySQLConnection
            An active database connection.

        Raises
        ------
        ConnectionError
            If the connection cannot be established.
        """
        try:
            if self._connection is None or not self._connection.is_connected():
                self._connection = mysql.connector.connect(
                    host=self._config["host"],
                    user=self._config["user"],
                    password=self._config["password"],
                    database=self._config["database"],
                )
            return self._connection
        except Error as e:
            print(f"[ERROR] Database connection failed: {e}")
            return None

    def ensure_alive(self):
        """
        Ping the connection and reconnect if dropped.
        Should be called before each request to prevent stale connections.
        """
        try:
            conn = self.get_connection()
            if conn:
                conn.ping(reconnect=True, attempts=3, delay=1)
        except Exception as e:
            print(f"[ERROR] Connection health check failed: {e}")

    def close(self):
        """Gracefully close the active database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None
            print("[OK] Database connection closed.")

    def test(self):
        """
        Quick connectivity check.

        Returns
        -------
        bool
            True if the database is reachable, False otherwise.
        """
        try:
            conn = self.get_connection()
            if conn and conn.is_connected():
                print(f"[OK] Connected to MySQL: {conn.server_info}")
                return True
        except Error as e:
            print(f"[ERROR] Connection test failed: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
#  Backwards-Compatible Wrappers
#  These keep existing imports (main_api.py, db_init.py, table.py) working.
# ══════════════════════════════════════════════════════════════════════════════

def get_connection(config=None):
    """
    Legacy wrapper — returns an active MySQL connection.
    Delegates to the DatabaseManager singleton.
    """
    if config:
        return DatabaseManager(config).get_connection()
    return DatabaseManager.get_instance().get_connection()


def test_connection(config=None):
    """
    Legacy wrapper — quick connectivity check.
    Delegates to the DatabaseManager singleton.
    """
    if config:
        return DatabaseManager(config).test()
    return DatabaseManager.get_instance().test()


if __name__ == "__main__":
    db = DatabaseManager.get_instance()
    db.test()
    db.close()
