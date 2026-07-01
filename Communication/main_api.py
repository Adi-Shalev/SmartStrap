"""
SmartStrap API — Unified Communication Wrapper
-------------------------------------------------
Binds DataReader and DataWriter to a single managed connection.
All external code should interact with the system through this class.

Usage:
    from Communication.main_api import SmartStrapAPI

    app = SmartStrapAPI()
    settings = app.reader.get_device_settings_for_patient(patient_id=1)
    app.close()
"""

import sys
import os
from mysql.connector import Error

# Ensure BackEnd is importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BackEnd', 'db'))

from db_connection import get_connection
from model_query import DataReader
from model_input import DataWriter


class SmartStrapAPI:
    def __init__(self):
        """Establishes connection via centralized config and binds read/write services."""
        try:
            self.con = get_connection()
            if self.con is None:
                raise ConnectionError("Failed to establish database connection.")

            print(f"[OK] API connection established.")

            self.reader = DataReader(self.con)
            self.writer = DataWriter(self.con)

        except (Error, ConnectionError) as e:
            print(f"[ERROR] API connection initialization failed: {e}")

    def close(self):
        """Gracefully terminates active database connections."""
        if hasattr(self, 'con') and self.con and self.con.is_connected():
            self.con.close()
            print("[OK] API session safely terminated.")


if __name__ == "__main__":
    # Test block to verify system readiness
    app = SmartStrapAPI()

    if hasattr(app, 'con') and app.con and app.con.is_connected():
        print("\nVerifying Communication layer functionality...")
        settings = app.reader.get_device_settings_for_patient(patient_id=1)
        print("Hardware Parameters Sample:", settings)

        app.close()