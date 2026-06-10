import pandas as pd
from datetime import datetime
# pyrefly: ignore [missing-import]
import numpy as np
from mysql.connector import Error


class Table:
    """
    Represents a database table backed by a CSV file.

    Responsibilities:
      - Load CSV data into a pandas DataFrame
      - Normalize date columns and null values
      - Insert rows into the corresponding DB table

    This class does NOT handle database connections.
    See BackEnd/db_init.py for the initialization runner.
    """

    def __init__(self, tableName, csvFileName, pks=[], fks=[], ref_tables=[], refs=[]):
        self.headers = []
        self.csvFileName = csvFileName
        self.tableName = tableName
        self.data = pd.DataFrame()
        self.pks = pks
        self.fks = fks
        self.ref_tables = ref_tables
        self.refs = refs

        try:
            self.data = pd.read_csv(self.csvFileName)
            # Clean any hidden carriage returns or spaces from columns
            self.data.columns = [c.strip().replace('\ufeff', '').replace('\r', '') for c in self.data.columns]
            self.headers = self.data.columns.values.tolist()
            print(f"[{self.tableName}] CSV loaded successfully.")
        except FileNotFoundError:
            print(f"Error: File '{self.csvFileName}' not found.")
            return
        except Exception as e:
            print(f"Error importing table: {e}")
            return

        for i in self.data.columns:
            if 'Date' in i and i != "Timestamp":
                for j in range(self.data.shape[0]):
                    if isinstance(self.data.loc[j, i], str):
                        try:
                            parsed_date = pd.to_datetime(self.data.loc[j, i]).strftime("%Y-%m-%d")
                            self.data.loc[j, i] = parsed_date
                        except:
                            pass

        self.data = self.data.replace({np.nan: None})

    def insert_to_db(self, db_connection):
        """Insert all rows from the loaded DataFrame into the DB table."""
        if self.data.empty:
            print(f"[{self.tableName}] No data to insert.")
            return

        cursor = db_connection.cursor()
        cols = ", ".join(self.headers)
        placeholders = ", ".join(["%s"] * len(self.headers))
        sql = f"INSERT INTO {self.tableName} ({cols}) VALUES ({placeholders})"

        try:
            data_to_insert = [tuple(x) for x in self.data.to_numpy()]
            cursor.executemany(sql, data_to_insert)
            db_connection.commit()
            print(f"[{self.tableName}] Successfully inserted {cursor.rowcount} rows.")
        except Error as e:
            print(f"[{self.tableName}] Failed to insert data: {e}")
        finally:
            cursor.close()