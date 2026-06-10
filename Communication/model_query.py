"""
DataReader — All SELECT / READ Operations
-------------------------------------------
Provides query methods for both the existing system and the new
training module. Each method returns either a dict or a pandas DataFrame.

Dependencies:
    - BackEnd.db_connection (for connection management)

This module does NOT manage connections — it receives one from the caller.
"""

import pandas as pd
from mysql.connector import Error


class DataReader:
    def __init__(self, db_connection):
        """Accepts an active database connection."""
        self.con = db_connection

    # ══════════════════════════════════════════════════════════════════════════
    #  EXISTING QUERIES (preserved from original)
    # ══════════════════════════════════════════════════════════════════════════

    def get_assigned_patients_for_doctor(self, doctor_id):
        """Retrieves all active patients assigned to a specific clinician."""
        query = """
            SELECT p.Patient_ID, p.First_Name, p.Last_Name, p.Phone_Number, p.Email 
            FROM Patients p
            JOIN Doctor_Patient dp ON p.Patient_ID = dp.Patient_ID
            WHERE dp.Doctor_ID = %s
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (doctor_id,))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
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
            cursor = self.con.cursor()
            cursor.execute(query, (patient_id,))
            result = cursor.fetchone()
            cursor.close()
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
            cursor = self.con.cursor()
            cursor.execute(query, (patient_id,))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return pd.DataFrame(result, columns=columns)
        except Error as e:
            print(f"Error fetching feedback history: {e}")
            return pd.DataFrame()

    def get_patients_needing_attention(self, doctor_id):
        """
        DSS — Decision Support System.
        Flags patients with average Relief_Score < 5.0.
        Returns patient info + average score + their latest feedback notes.
        """
        query = """
            SELECT 
                p.Patient_ID, 
                p.First_Name, 
                p.Last_Name,
                p.Email,
                p.Phone_Number,
                ROUND(AVG(f.Relief_Score), 1) AS Avg_Relief,
                COUNT(f.Feedback_ID) AS Total_Feedback
            FROM Patients p
            JOIN Doctor_Patient dp ON p.Patient_ID = dp.Patient_ID
            JOIN Patient_Feedback f ON p.Patient_ID = f.Patient_ID
            WHERE dp.Doctor_ID = %s
            GROUP BY p.Patient_ID
            HAVING Avg_Relief < 5.0
            ORDER BY Avg_Relief ASC
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (doctor_id,))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return pd.DataFrame(result, columns=columns)
        except Error as e:
            print(f"Error flagging critical patients: {e}")
            return pd.DataFrame()

    # ══════════════════════════════════════════════════════════════════════════
    #  NEW: Patient Profile Queries
    # ══════════════════════════════════════════════════════════════════════════

    def get_patient_notch_profile(self, patient_id):
        """
        Returns the patient's audiometric notch parameters.
        This is the AUTHORITATIVE source for training frequency.
        """
        query = """
            SELECT Patient_ID, First_Name, Last_Name, Email, Phone_Number,
                   Notch_Center_Frequency, Notch_Width, Test_Date
            FROM Patients
            WHERE Patient_ID = %s
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (patient_id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return {
                    "Patient_ID": result[0],
                    "First_Name": result[1],
                    "Last_Name": result[2],
                    "Email": result[3],
                    "Phone_Number": result[4],
                    "Notch_Center_Frequency": result[5],
                    "Notch_Width": result[6],
                    "Test_Date": str(result[7]) if result[7] else None,
                }
            return None
        except Error as e:
            print(f"Error fetching patient notch profile: {e}")
            return None

    def get_patient_full_profile(self, patient_id):
        """
        Returns complete patient data: personal info + device settings + notch profile.
        Used by the Patient Portal dashboard.
        """
        profile = self.get_patient_notch_profile(patient_id)
        if not profile:
            return None

        settings = self.get_device_settings_for_patient(patient_id)
        profile["device_settings"] = settings
        return profile

    # ══════════════════════════════════════════════════════════════════════════
    #  NEW: Training Queries (feed Doctor's graphs + Patient progress)
    # ══════════════════════════════════════════════════════════════════════════

    def get_available_songs(self):
        """Returns all songs in the Song_Library."""
        query = """
            SELECT Song_ID, Title, Artist, Duration_Seconds, File_Path, Created_At
            FROM Song_Library
            ORDER BY Created_At DESC
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return pd.DataFrame(result, columns=columns)
        except Error as e:
            print(f"Error fetching songs: {e}")
            return pd.DataFrame()

    def get_training_history(self, patient_id):
        """
        Returns all training sessions for a patient, ordered by date.
        This is the data source for the Doctor's progress graph.
        """
        query = """
            SELECT 
                ts.Session_ID,
                ts.Session_Date,
                ts.Duration_Seconds,
                ts.Total_Haptic_Events,
                ts.Correct_Hits,
                ts.Missed_Events,
                ts.False_Positives,
                ts.Final_Accuracy_Score,
                ts.Cognitive_Load,
                ts.Notes,
                sl.Title AS Song_Title
            FROM Training_Sessions ts
            LEFT JOIN Song_Library sl ON ts.Song_ID = sl.Song_ID
            WHERE ts.Patient_ID = %s
            ORDER BY ts.Session_Date ASC
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (patient_id,))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return pd.DataFrame(result, columns=columns)
        except Error as e:
            print(f"Error fetching training history: {e}")
            return pd.DataFrame()

    def get_session_events(self, session_id):
        """
        Returns all raw events for a specific training session.
        Used for detailed replay/analysis.
        """
        query = """
            SELECT Event_ID, Event_Time_Ms, Event_Type, Intensity, Reaction_Time_Ms
            FROM Session_Events
            WHERE Session_ID = %s
            ORDER BY Event_Time_Ms ASC
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (session_id,))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return pd.DataFrame(result, columns=columns)
        except Error as e:
            print(f"Error fetching session events: {e}")
            return pd.DataFrame()

    def get_doctor_training_overview(self, doctor_id):
        """
        Returns training summary for ALL patients assigned to a doctor.
        Shows each patient's latest accuracy score and total sessions.
        Used for the Doctor's dashboard training column.
        """
        query = """
            SELECT 
                p.Patient_ID,
                p.First_Name,
                p.Last_Name,
                COUNT(ts.Session_ID) AS Total_Sessions,
                ROUND(AVG(ts.Final_Accuracy_Score), 1) AS Avg_Accuracy,
                MAX(ts.Session_Date) AS Last_Session_Date
            FROM Patients p
            JOIN Doctor_Patient dp ON p.Patient_ID = dp.Patient_ID
            LEFT JOIN Training_Sessions ts ON p.Patient_ID = ts.Patient_ID
            WHERE dp.Doctor_ID = %s
            GROUP BY p.Patient_ID
            ORDER BY p.Last_Name ASC
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (doctor_id,))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return pd.DataFrame(result, columns=columns)
        except Error as e:
            print(f"Error fetching doctor training overview: {e}")
            return pd.DataFrame()

    # ══════════════════════════════════════════════════════════════════════════
    #  NEW: Authentication Queries
    # ══════════════════════════════════════════════════════════════════════════

    def authenticate_doctor(self, email, password_hash):
        """Validates doctor credentials. Returns doctor dict or None."""
        query = """
            SELECT Doctor_ID, First_Name, Last_Name, Email
            FROM Doctors
            WHERE Email = %s AND Password_Hash = %s
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (email, password_hash))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return {
                    "Doctor_ID": result[0],
                    "First_Name": result[1],
                    "Last_Name": result[2],
                    "Email": result[3],
                    "role": "doctor"
                }
            return None
        except Error as e:
            print(f"Error authenticating doctor: {e}")
            return None

    def authenticate_patient(self, email, password_hash):
        """Validates patient credentials. Returns patient dict or None."""
        query = """
            SELECT Patient_ID, First_Name, Last_Name, Email
            FROM Patients
            WHERE Email = %s AND Password_Hash = %s
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (email, password_hash))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return {
                    "Patient_ID": result[0],
                    "First_Name": result[1],
                    "Last_Name": result[2],
                    "Email": result[3],
                    "role": "patient"
                }
            return None
        except Error as e:
            print(f"Error authenticating patient: {e}")
            return None