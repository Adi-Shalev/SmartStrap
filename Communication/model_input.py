"""
DataWriter — All INSERT / UPDATE Operations
---------------------------------------------
Provides write methods for both the existing system and the new
training module. Each method commits its own transaction.

Dependencies:
    - BackEnd.db_connection (for connection management)

This module does NOT manage connections — it receives one from the caller.
"""

from mysql.connector import Error


class DataWriter:
    def __init__(self, db_connection):
        """Accepts an active database connection."""
        self.con = db_connection

    # ══════════════════════════════════════════════════════════════════════════
    #  EXISTING WRITE OPERATIONS (preserved from original)
    # ══════════════════════════════════════════════════════════════════════════

    def add_new_patient(self, email, password_hash, first_name, last_name, phone, notch_freq, notch_width, test_date):
        """Inserts a new clinical patient profile into the database."""
        query = """
            INSERT INTO Patients (Email, Password_Hash, First_Name, Last_Name, Phone_Number, Notch_Center_Frequency, Notch_Width, Test_Date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (email, password_hash, first_name, last_name, phone, notch_freq, notch_width, test_date))
            self.con.commit()
            last_id = cursor.lastrowid
            cursor.close()
            print(f"Success: Patient {first_name} {last_name} added to the system.")
            return last_id
        except Error as e:
            print(f"Error adding patient profile: {e}")
            return None

    def assign_patient_to_doctor(self, doctor_id, patient_id):
        """Assigns a patient to a doctor in the M:N table."""
        query = """
            INSERT INTO Doctor_Patient (Doctor_ID, Patient_ID)
            VALUES (%s, %s)
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (doctor_id, patient_id))
            self.con.commit()
            cursor.close()
            print(f"Success: Patient {patient_id} assigned to Doctor {doctor_id}.")
            return True
        except Error as e:
            print(f"Error assigning patient to doctor: {e}")
            return False

    def add_new_doctor(self, email, password_hash, first_name, last_name, phone):
        """Inserts a new clinical doctor profile into the database."""
        query = """
            INSERT INTO Doctors (Email, Password_Hash, First_Name, Last_Name, Phone_Number)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (email, password_hash, first_name, last_name, phone))
            self.con.commit()
            last_id = cursor.lastrowid
            cursor.close()
            print(f"Success: Doctor {first_name} {last_name} added to the system.")
            return last_id
        except Error as e:
            print(f"Error adding doctor profile: {e}")
            return None

    def insert_patient_feedback(self, patient_id, relief_score, notes):
        """Saves a subjective user evaluation session via the user application interface."""
        query = """
            INSERT INTO Patient_Feedback (Patient_ID, Relief_Score, Notes)
            VALUES (%s, %s, %s)
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (patient_id, relief_score, notes))
            self.con.commit()
            cursor.close()
            print(f"Success: Feedback recorded for Patient ID {patient_id}.")
            return True
        except Error as e:
            print(f"Error recording patient feedback: {e}")
            return False

    def update_vibration_intensity(self, patient_id, new_intensity):
        """Allows a clinical doctor to remotely modify strap vibration profiles."""
        query = """
            INSERT INTO Device_Settings (Patient_ID, Vibration_Intensity, Mapping_Algorithm_ID, Strap_MAC_Address)
            VALUES (%s, %s, 1, %s)
            ON DUPLICATE KEY UPDATE Vibration_Intensity = VALUES(Vibration_Intensity)
        """
        try:
            cursor = self.con.cursor()
            dummy_mac = f"00:00:00:00:{patient_id:02x}:00"
            cursor.execute(query, (patient_id, new_intensity, dummy_mac))
            self.con.commit()
            cursor.close()
            print(f"Success: Intensity adjusted to {new_intensity} for Patient ID {patient_id}.")
            return True
        except Error as e:
            print(f"Error modifying hardware intensity: {e}")
            return False

    def update_patient_notch_profile(self, patient_id, notch_freq, notch_width):
        """Allows a clinical doctor to set the patient's audiometric notch parameters."""
        query = """
            UPDATE Patients 
            SET Notch_Center_Frequency = %s, Notch_Width = %s 
            WHERE Patient_ID = %s
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (notch_freq, notch_width, patient_id))
            self.con.commit()
            cursor.close()
            print(f"Success: Notch profile updated for Patient ID {patient_id}.")
            return True
        except Error as e:
            print(f"Error updating notch profile: {e}")
            return False

    def insert_system_log(self, event_type, description, patient_id=None, doctor_id=None, duration=None, vibrations=None):
        """Records system events and objective usage metrics into the log."""
        query = """
            INSERT INTO System_Logs (Patient_ID, Doctor_ID, Event_Type, Session_Duration_Minutes, Total_Vibration_Events, Action_Description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (patient_id, doctor_id, event_type, duration, vibrations, description))
            self.con.commit()
            cursor.close()
            print(f"Success: System log recorded: {description}")
            return True
        except Error as e:
            print(f"Error inserting system log metrics: {e}")
            return False

    # ══════════════════════════════════════════════════════════════════════════
    #  NEW: Song Library Operations
    # ══════════════════════════════════════════════════════════════════════════

    def insert_song(self, title, artist=None, duration_seconds=None, file_path=None):
        """Adds a new song to the training library."""
        query = """
            INSERT INTO Song_Library (Title, Artist, Duration_Seconds, File_Path)
            VALUES (%s, %s, %s, %s)
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (title, artist, duration_seconds, file_path))
            self.con.commit()
            song_id = cursor.lastrowid
            cursor.close()
            print(f"Success: Song '{title}' added with ID {song_id}.")
            return song_id
        except Error as e:
            print(f"Error adding song: {e}")
            return None

    # ══════════════════════════════════════════════════════════════════════════
    #  NEW: Training Session Operations
    # ══════════════════════════════════════════════════════════════════════════

    def create_training_session(self, patient_id, song_id=None):
        """
        Starts a new training session. Returns the new Session_ID.
        Called when the patient clicks "Start Training".
        """
        query = """
            INSERT INTO Training_Sessions (Patient_ID, Song_ID)
            VALUES (%s, %s)
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (patient_id, song_id))
            self.con.commit()
            session_id = cursor.lastrowid
            cursor.close()
            print(f"Success: Training session {session_id} created for Patient ID {patient_id}.")
            return session_id
        except Error as e:
            print(f"Error creating training session: {e}")
            return None

    def log_session_event(self, session_id, event_time_ms, event_type, intensity=None, reaction_time_ms=None):
        """
        Logs a single raw event during gameplay.
        event_type: 'HAPTIC_PEAK', 'USER_TAP', 'HIT', 'MISS', 'FALSE_POSITIVE'
        """
        query = """
            INSERT INTO Session_Events (Session_ID, Event_Time_Ms, Event_Type, Intensity, Reaction_Time_Ms)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (session_id, event_time_ms, event_type, intensity, reaction_time_ms))
            self.con.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error logging session event: {e}")
            return False

    def log_session_events_batch(self, session_id, events):
        """
        Batch-insert multiple events at once (more efficient than one-by-one).
        events: list of dicts with keys: event_time_ms, event_type, intensity, reaction_time_ms
        """
        query = """
            INSERT INTO Session_Events (Session_ID, Event_Time_Ms, Event_Type, Intensity, Reaction_Time_Ms)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            cursor = self.con.cursor()
            data = [
                (session_id, e["event_time_ms"], e["event_type"],
                 e.get("intensity"), e.get("reaction_time_ms"))
                for e in events
            ]
            cursor.executemany(query, data)
            self.con.commit()
            count = cursor.rowcount
            cursor.close()
            print(f"Success: {count} events logged for Session ID {session_id}.")
            return True
        except Error as e:
            print(f"Error batch-logging session events: {e}")
            return False

    def complete_training_session(self, session_id, duration_seconds, total_haptic_events,
                                   correct_hits, missed_events, false_positives,
                                   final_accuracy_score, cognitive_load=None, notes=None):
        """
        Finalizes a training session with summary statistics.
        Called when the training session ends.
        This row is what feeds the Doctor's progress graph.
        """
        query = """
            UPDATE Training_Sessions
            SET Duration_Seconds     = %s,
                Total_Haptic_Events  = %s,
                Correct_Hits         = %s,
                Missed_Events        = %s,
                False_Positives      = %s,
                Final_Accuracy_Score = %s,
                Cognitive_Load       = %s,
                Notes                = %s
            WHERE Session_ID = %s
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (
                duration_seconds, total_haptic_events,
                correct_hits, missed_events, false_positives,
                final_accuracy_score, cognitive_load, notes,
                session_id
            ))
            self.con.commit()
            cursor.close()
            print(f"Success: Session {session_id} finalized — Accuracy: {final_accuracy_score:.1%}")
            return True
        except Error as e:
            print(f"Error completing training session: {e}")
            return False