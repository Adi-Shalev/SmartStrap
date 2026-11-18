"""
SmartStrap API — Unified Communication Wrapper
-------------------------------------------------
Binds DataReader and DataWriter to a pooled, thread-safe connection.
All external code should interact with the system through this class.

Usage:
    from Communication.main_api import SmartStrapAPI

    app = SmartStrapAPI()
    settings = app.reader.get_device_settings_for_patient(patient_id=1)
    app.close()

How connections work:
    `api.con` is a ScopedConnection. Each thread (= each Flask request)
    borrows its OWN connection from the pool the first time it runs a
    query, and gives it back when `api.release()` is called (the server
    does this automatically at the end of every request).
"""

import sys
import os
import threading

# Ensure BackEnd is importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BackEnd', 'db'))

from db_connection import get_pool, DatabaseUnavailable  # noqa: F401  (re-exported)
from model_query import DataReader
from model_input import DataWriter


class ScopedConnection:
    """
    Looks like a mysql-connector connection (cursor / commit / rollback /
    is_connected), but routes every call to a connection that belongs to the
    current thread only. This is what stops parallel requests from sharing
    one socket and crashing the server.

    All cursors are buffered: results are read fully on execute(), so a
    query that returns more rows than the code reads can never leave the
    connection stuck with "Unread result found".
    """

    def __init__(self, pool):
        self._pool = pool
        self._local = threading.local()

    def _conn(self):
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = self._pool.get()   # raises DatabaseUnavailable if MySQL is down
            self._local.conn = conn
        return conn

    def cursor(self, *args, **kwargs):
        kwargs.setdefault("buffered", True)
        return self._conn().cursor(*args, **kwargs)

    def commit(self):
        self._conn().commit()

    def rollback(self):
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            conn.rollback()

    def is_connected(self):
        try:
            return self._conn().is_connected()
        except DatabaseUnavailable:
            return False

    def release(self):
        """Return this thread's connection to the pool (no-op if it has none)."""
        conn = getattr(self._local, "conn", None)
        if conn is None:
            return
        self._local.conn = None
        try:
            conn.rollback()   # end any open read snapshot / uncommitted work
        except Exception:
            pass
        try:
            conn.close()      # for a pooled connection this returns it to the pool
        except Exception:
            pass


class SmartStrapAPI:
    def __init__(self):
        # Never fails at startup: the pool connects lazily on the first query,
        # so the server can start before MySQL and recover when it comes back.
        self.con = ScopedConnection(get_pool())
        self.reader = DataReader(self.con)
        self.writer = DataWriter(self.con)

    def release(self):
        """Give the current thread's connection back to the pool."""
        self.con.release()

    def close(self):
        """Backwards-compatible alias used by scripts."""
        self.release()


if __name__ == "__main__":
    # Test block to verify system readiness
    app = SmartStrapAPI()

    if app.con.is_connected():
        print("\nVerifying Communication layer functionality...")
        settings = app.reader.get_device_settings_for_patient(patient_id=1)
        print("Hardware Parameters Sample:", settings)
    else:
        print("[ERROR] Database is not reachable.")

    app.close()
