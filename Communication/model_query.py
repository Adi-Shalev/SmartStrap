import pandas as pd
from mysql.connector import Error

class DataReader:
    def __init__(self, db_connection):
        """Accepts an active database connection and initializes a cursor."""
        self.con = db_connection
        self.cursor = self.con.cursor()

    def get_assigned_patients_for_doctor(self, doctor_id):
        """Retrieves all active patients assigned to a specific clinician."""
        query = """
            SELECT p.Patient_ID, p.First_Name, p.Last_Name, p.Phone_Number, p.Email 
            FROM Patients p
            JOIN Doctor_Patient dp ON p.Patient_ID = dp.Patient_ID
            WHERE dp.Doctor_ID = %s
        """
        try:
            self.cursor.execute(query, (doctor_id,))
            result = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            return pd.DataFrame(result, columns=columns)
        except Error as e:
            print(f"Error fetching assigned patients: {e}")
            return pd.DataFrame()

    def get_device_settings_for_patient(self, patient_id):
        """Fetches therapeutic configurations and MAC address for hardware initialization."""
        query = """
            SELECT Vibration_Intensity, Mapping_Algorithm_ID, Strap_MAC_Address
            FROM Device_Settings
            WHERE Patient_ID = %s
        """
        try:
            self.cursor.execute(query, (patient_id,))
            result = self.cursor.fetchone()
            if result:
                return {
                    "Vibration_Intensity": result[0],
                    "Mapping_Algorithm_ID": result[1],
                    "Strap_MAC_Address": result[2]
                }
            return None
        except Error as e:
            print(f"Error fetching device settings: {e}")
            return None

    def get_patient_feedback_history(self, patient_id):
        """Retrieves a chronological log of relief scores and clinical notes for analysis."""
        query = """
            SELECT Timestamp, Relief_Score, Notes 
            FROM Patient_Feedback
            WHERE Patient_ID = %s
            ORDER BY Timestamp DESC
        """
        try:
            self.cursor.execute(query, (patient_id,))
            result = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            return pd.DataFrame(result, columns=columns)
        except Error as e:
            print(f"Error fetching feedback history: {e}")
            return pd.DataFrame()

    def get_patients_needing_attention(self, doctor_id):
        """Identifies patients with a low average clinical satisfaction rating (< 5.0)."""
        query = """
            SELECT p.Patient_ID, p.First_Name, p.Last_Name, AVG(f.Relief_Score) as Avg_Relief
            FROM Patients p
            JOIN Doctor_Patient dp ON p.Patient_ID = dp.Patient_ID
            JOIN Patient_Feedback f ON p.Patient_ID = f.Patient_ID
            WHERE dp.Doctor_ID = %s
            GROUP BY p.Patient_ID
            HAVING Avg_Relief < 5.0
        """
        try:
            self.cursor.execute(query, (doctor_id,))
            result = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            return pd.DataFrame(result, columns=columns)
        except Error as e:
            print(f"Error flagging critical patients: {e}")
            return pd.DataFrame()