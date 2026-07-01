"""
Database Initialization Script
-------------------------------
Responsible for:
  1. Connecting to the MySQL server (via centralized config)
  2. Clearing existing rows (to prevent duplicate key constraints)
  3. Loading CSV data into Table objects
  4. Inserting all rows into the database

Run this script directly to reset and repopulate the DB:
    python BackEnd/db_init.py
"""

import os
import sys

# Ensure BackEnd is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_connection import get_connection
from table import Table
from mysql.connector import Error


# ── Setup Schema ──────────────────────────────────────────────────────────────

def setup_schema(db_conn):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file = os.path.join(current_dir, "training_tables.sql")
    print("Executing training_tables.sql schema...")
    try:
        cursor = db_conn.cursor()
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        # Split by semicolon to execute statements individually 
        # (CMySQLCursor doesn't always support multi=True)
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        for statement in statements:
            cursor.execute(statement)
            
        db_conn.commit()
        cursor.close()
        print("Schema setup completed.")
    except Exception as e:
        print(f"Error executing schema: {e}")

# ── Clear Tables ──────────────────────────────────────────────────────────────

def clear_tables(db_conn):
    """
    Truncate all tables in insertion-safe order.
    Foreign key checks are disabled temporarily to allow truncation.
    """
    tables_to_clear = [
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
    print("Clearing old tables...")
    try:
        cursor = db_conn.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for table_name in tables_to_clear:
            try:
                cursor.execute(f"TRUNCATE TABLE {table_name};")
            except Error:
                pass  # Table may not exist yet
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        db_conn.commit()
        cursor.close()
        print("Database cleared successfully. Ready for clean injection.")
    except Error as e:
        print(f"Warning during truncation: {e}")


# ── Load & Insert ─────────────────────────────────────────────────────────────

def load_and_insert_tables(db_conn):
    """Load each CSV into a Table object and insert its rows into the DB."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', 'data')

    tables_to_load = [
        Table(tableName="Doctors",          csvFileName=os.path.join(data_dir, "doctors.csv")),
        Table(tableName="Patients",         csvFileName=os.path.join(data_dir, "patients.csv")),
        Table(tableName="Doctor_Patient",   csvFileName=os.path.join(data_dir, "doctor_patient.csv")),
        Table(tableName="Device_Settings",  csvFileName=os.path.join(data_dir, "device_setting.csv")),
        Table(tableName="Patient_Feedback", csvFileName=os.path.join(data_dir, "patient_feedback.csv")),
        Table(tableName="System_Logs",      csvFileName=os.path.join(data_dir, "system_logs.csv")),
    ]

    for table_obj in tables_to_load:
        table_obj.insert_to_db(db_conn)


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    print("--- Starting Database Initialization ---")

    db_conn = get_connection()
    if db_conn is None:
        return

    setup_schema(db_conn)
    clear_tables(db_conn)
    load_and_insert_tables(db_conn)

    if db_conn.is_connected():
        db_conn.close()
        print("\nDatabase connection closed. Initialization complete.")


if __name__ == "__main__":
    main()
