"""
Database Initialization Script
-------------------------------
Responsible for:
  1. Connecting to the MySQL server
  2. Clearing existing rows (to prevent duplicate key constraints)
  3. Loading CSV data into Table objects
  4. Inserting all rows into the database

Run this script directly to reset and repopulate the DB:
    python BackEnd/db_init.py
"""

import os
import mysql.connector
from mysql.connector import Error
from table import Table


# ── Connection ────────────────────────────────────────────────────────────────

def connect_to_db(password, host="127.0.0.1", user="root", db_name="NotchAppDB3"):
    """Establish and return a MySQL connection to the given database."""
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        print(f"Connected to MySQL database '{db_name}'.")
        return conn
    except Error as e:
        print(f"Database connection failed: {e}")
        return None


# ── Clear Tables ──────────────────────────────────────────────────────────────

def clear_tables(db_conn):
    """
    Truncate all tables in insertion-safe order.
    Foreign key checks are disabled temporarily to allow truncation.
    """
    tables_to_clear = [
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
            cursor.execute(f"TRUNCATE TABLE {table_name};")
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

    tables_to_load = [
        Table(tableName="Doctors",          csvFileName=os.path.join(current_dir, "doctors.csv")),
        Table(tableName="Patients",         csvFileName=os.path.join(current_dir, "patients.csv")),
        Table(tableName="Doctor_Patient",   csvFileName=os.path.join(current_dir, "doctor_patient.csv")),
        Table(tableName="Device_Settings",  csvFileName=os.path.join(current_dir, "device_setting.csv")),
        Table(tableName="Patient_Feedback", csvFileName=os.path.join(current_dir, "patient_feedback.csv")),
        Table(tableName="System_Logs",      csvFileName=os.path.join(current_dir, "system_logs.csv")),
    ]

    for table_obj in tables_to_load:
        table_obj.insert_to_db(db_conn)


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    print("--- Starting Database Initialization ---")

    db_conn = connect_to_db(password="206535932")
    if db_conn is None:
        return

    clear_tables(db_conn)
    load_and_insert_tables(db_conn)

    if db_conn.is_connected():
        db_conn.close()
        print("\nDatabase connection closed. Initialization complete.")


if __name__ == "__main__":
    main()
