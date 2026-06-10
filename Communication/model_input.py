from mysql.connector import Error

class DataWriter:
    def __init__(self, db_connection):
        """Accepts an active database connection and initializes a cursor."""
        self.con = db_connection
        self.cursor = self.con.cursor()

    def add_new_patient(self, email, password_hash, first_name, last_name, phone, notch_freq, notch_width, test_date):
        """Inserts a new clinical patient profile into the database."""
        query = """
            INSERT INTO Patients (Email, Password_Hash, First_Name, Last_Name, Phone_Number, Notch_Center_Frequency, Notch_Width, Test_Date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(query, (email, password_hash, first_name, last_name, phone, notch_freq, notch_width, test_date))
            self.con.commit()
            print(f"Success: Patient {first_name} {last_name} added to the system.")
            return self.cursor.lastrowid 
        except Error as e:
            print(f"Error adding patient profile: {e}")
            return None

    def insert_patient_feedback(self, patient_id, relief_score, notes):
        """Saves a subjective user evaluation session via the user application interface."""
        query = """
            INSERT INTO Patient_Feedback (Patient_ID, Relief_Score, Notes)
            VALUES (%s, %s, %s)
        """
        try:
            self.cursor.execute(query, (patient_id, relief_score, notes))
            self.con.commit()
            print(f"Success: Feedback recorded for Patient ID {patient_id}.")
            return True
        except Error as e:
            print(f"Error recording patient feedback: {e}")
            return False

    def update_vibration_intensity(self, patient_id, new_intensity):
        """Allows a clinical doctor to remotely modify strap vibration profiles."""
        query = """
            UPDATE Device_Settings 
            SET Vibration_Intensity = %s 
            WHERE Patient_ID = %s
        """
        try:
            self.cursor.execute(query, (new_intensity, patient_id))
            self.con.commit()
            print(f"Success: Intensity adjusted to {new_intensity} for Patient ID {patient_id}.")
            return True
        except Error as e:
            print(f"Error modifying hardware intensity: {e}")
            return False

    def insert_system_log(self, patient_id, doctor_id, duration, vibrations, description="Session logging"):
        """Records objective usage metrics streamed directly from the hardware."""
        query = """
            INSERT INTO System_Logs (Patient_ID, Doctor_ID, Event_Type, Session_Duration_Minutes, Total_Vibration_Events, Action_Description)
            VALUES (%s, %s, 'DEVICE_USAGE', %s, %s, %s)
        """
        try:
            self.cursor.execute(query, (patient_id, doctor_id, duration, vibrations, description))
            self.con.commit()
            print(f"Success: System log recorded for Patient ID {patient_id}.")
            return True
        except Error as e:
            print(f"Error inserting system log metrics: {e}")
            return False