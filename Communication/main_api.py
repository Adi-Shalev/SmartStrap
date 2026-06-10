import mysql.connector
from mysql.connector import Error
from model_query import DataReader
from model_input import DataWriter

class SmartStrapAPI:
    def __init__(self, password, db_name="NotchAppDB3"):
        """Establishes connections and binds read/write operational services."""
        try:
            self.con = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password=password,  
                database=db_name
            )
            print(f"✅ API connection established with schema: {db_name}")
            
            self.reader = DataReader(self.con)
            self.writer = DataWriter(self.con)
            
        except Error as e:
            print(f"❌ API connection initialization failed: {e}")

    def close(self):
        """Gracefully terminates active database connections."""
        if hasattr(self, 'con') and self.con.is_connected():
            self.con.close()
            print("🔒 API session safely terminated.")

if __name__ == "__main__":
    # Test block to verify system readiness (Replace with your actual SQL root password)
    app = SmartStrapAPI(password="206535932")
    
    if hasattr(app, 'con') and app.con.is_connected():
        print("\nVerifying Communication layer functionality...")
        # Check if patient settings retrieval works flawlessly
        settings = app.reader.get_device_settings_for_patient(patient_id=1)
        print("Hardware Parameters Sample:", settings)
        
        app.close()