import sys
import os

# Add BackEnd directory to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'BackEnd', 'db'))

from main_api import SmartStrapAPI
import time

def demo_patient_flow():
    print("="*60)
    print(" SMART STRAP - BACKEND DATA FLOW DEMONSTRATION")
    print("="*60)
    
    # 1. Initialize API connection
    print("\n[STEP 1] Connecting to the MySQL Database...")
    time.sleep(1)
    app = SmartStrapAPI()
    
    if not hasattr(app, 'con') or not app.con.is_connected():
        print("Failed to connect to database. Please check your MySQL server.")
        return

    # 2. Simulate Doctor input
    print("\n[STEP 2] Doctor submits 'Add New Patient' form in the UI...")
    new_patient_data = {
        "email": "demo.patient2024@example.com",
        "password_hash": "hashed_pw_123",
        "first_name": "Demo",
        "last_name": "Patient",
        "phone": "555-0101",
        "notch_freq": 4000,
        "notch_width": 250,
        "test_date": "2024-06-25"
    }
    print(f"   -> Data received from UI: {new_patient_data['first_name']} {new_patient_data['last_name']} (Notch: {new_patient_data['notch_freq']}Hz)")
    time.sleep(1.5)

    # 3. Write to Database using DataWriter (model_input.py)
    print("\n[STEP 3] Routing to DataWriter (model_input.py) to execute INSERT query...")
    time.sleep(1)
    
    patient_id = app.writer.add_new_patient(
        new_patient_data["email"],
        new_patient_data["password_hash"],
        new_patient_data["first_name"],
        new_patient_data["last_name"],
        new_patient_data["phone"],
        new_patient_data["notch_freq"],
        new_patient_data["notch_width"],
        new_patient_data["test_date"]
    )

    if not patient_id:
        print("\n[ERROR] Failed to insert patient. (Does this email already exist in the DB?)")
        app.close()
        return

    print(f"   -> SQL INSERT Successful! Database assigned Patient_ID: {patient_id}")
    time.sleep(1.5)

    # 4. Read from Database using DataReader (model_query.py)
    print("\n[STEP 4] UI requests updated patient list via DataReader (model_query.py)...")
    print("   -> Executing SELECT query on 'Patients' table...")
    time.sleep(1.5)
    
    profile = app.reader.get_patient_notch_profile(patient_id)
    
    if profile:
        print("\n[STEP 5] Data successfully retrieved from SQL tables:")
        print("   -------------------------------------------------")
        print(f"   ID:          {profile['Patient_ID']}")
        print(f"   Name:        {profile['First_Name']} {profile['Last_Name']}")
        print(f"   Email:       {profile['Email']}")
        print(f"   Notch Freq:  {profile['Notch_Center_Frequency']} Hz")
        print("   -------------------------------------------------")
        print("\n   [SUCCESS] DATA FLOW VERIFIED: UI -> Python API -> SQL Database -> Python API -> UI")
    else:
        print("\n[ERROR] Failed to read patient profile.")

    print("\nClosing connection...")
    app.close()
    print("="*60)

if __name__ == "__main__":
    demo_patient_flow()
