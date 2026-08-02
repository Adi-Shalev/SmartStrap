"""
Database Initialization Script
-------------------------------
Provides a DatabaseInitializer class responsible for:
  1. Connecting to the MySQL server (via DatabaseManager)
  2. Executing the SQL schema file
  3. Clearing existing rows (to prevent duplicate key constraints)
  4. Loading CSV data into Table objects and inserting into the database

Usage:
    from db_init import DatabaseInitializer

    initializer = DatabaseInitializer()
    initializer.run()

Run this script directly to reset and repopulate the DB:
    python BackEnd/db/db_init.py
"""

import os
import sys

# Ensure BackEnd is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_connection import DatabaseManager
from table import Table
from mysql.connector import Error


class DatabaseInitializer:
    """
    Handles complete database initialization:
    schema creation, table clearing, and CSV data seeding.
    """

    # Tables to clear in safe order (children first, then parents)
    TABLES_TO_CLEAR = [
        "Session_Events",
        "Training_Sessions",
        "Song_Library",
        "System_Logs",
        "Patient_Feedback",
        "Device_Settings",
        "Doctor_Patient",
        "Patients",
        "Doctors",
    ]

    def __init__(self, db_manager=None):
        """
        Parameters
        ----------
        db_manager : DatabaseManager, optional
            If not provided, uses the singleton instance.
        """
        self._db = db_manager or DatabaseManager.get_instance()
        self._current_dir = os.path.dirname(os.path.abspath(__file__))
        self._data_dir = os.path.join(self._current_dir, '..', 'data')
        self._schema_file = os.path.join(self._current_dir, 'training_tables.sql')

    @property
    def connection(self):
        """Returns the active database connection."""
        return self._db.get_connection()

    def setup_schema(self):
        """
        Execute the SQL schema file to create or update all tables.
        Reads training_tables.sql and runs each statement individually.
        """
        print("Executing training_tables.sql schema...")
        try:
            cursor = self.connection.cursor()
            with open(self._schema_file, 'r', encoding='utf-8') as f:
                sql_script = f.read()

            # Split by semicolon to execute statements individually
            # (CMySQLCursor doesn't always support multi=True)
            statements = [s.strip() for s in sql_script.split(';') if s.strip()]
            for statement in statements:
                cursor.execute(statement)

            self.connection.commit()
            cursor.close()
            print("Schema setup completed.")
        except Exception as e:
            print(f"Error executing schema: {e}")

    def clear_tables(self):
        """
        Truncate all tables in insertion-safe order.
        Foreign key checks are disabled temporarily to allow truncation.
        """
        print("Clearing old tables...")
        try:
            cursor = self.connection.cursor()
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            for table_name in self.TABLES_TO_CLEAR:
                try:
                    cursor.execute(f"TRUNCATE TABLE {table_name};")
                except Error:
                    pass  # Table may not exist yet
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            self.connection.commit()
            cursor.close()
            print("Database cleared successfully. Ready for clean injection.")
        except Error as e:
            print(f"Warning during truncation: {e}")

    def load_and_insert_tables(self):
        """Load each CSV into a Table object and insert its rows into the DB."""
        tables_to_load = [
            Table(tableName="Doctors",          csvFileName=os.path.join(self._data_dir, "doctors.csv")),
            Table(tableName="Patients",         csvFileName=os.path.join(self._data_dir, "patients.csv")),
            Table(tableName="Doctor_Patient",   csvFileName=os.path.join(self._data_dir, "doctor_patient.csv")),
            Table(tableName="Device_Settings",  csvFileName=os.path.join(self._data_dir, "device_setting.csv")),
            Table(tableName="Patient_Feedback", csvFileName=os.path.join(self._data_dir, "patient_feedback.csv")),
            Table(tableName="System_Logs",      csvFileName=os.path.join(self._data_dir, "system_logs.csv")),
        ]

        for table_obj in tables_to_load:
            table_obj.insert_to_db(self.connection)

    def run(self):
        """
        Full initialization pipeline: schema → clear → seed.
        Call this to completely reset and repopulate the database.
        """
        print("--- Starting Database Initialization ---")
        self.setup_schema()
        self.clear_tables()
        self.load_and_insert_tables()
        print("\nDatabase initialization complete.")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    initializer = DatabaseInitializer()
    initializer.run()

    if initializer.connection and initializer.connection.is_connected():
        initializer._db.close()
        print("\nDatabase connection closed. Initialization complete.")
