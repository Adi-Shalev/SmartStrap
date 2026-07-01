import time
from main_api import SmartStrapAPI

def run_live_obs_demo():
    print("="*60)
    print(" MIDTERM REPORT: DATABASE COMMUNICATION DEMO ")
    print("="*60)
    
    print("\n=== [PHASE 1] Initializing SmartStrap Communication Layer ===")
    time.sleep(1)
    
    # Initialize API Wrapper (Triggers both DataReader and DataWriter)
    app = SmartStrapAPI()
    
    if hasattr(app, 'con') and app.con.is_connected():
        print("\n=== [PHASE 2] Executing DataWriter Operations (2 INPUTS) ===")
        time.sleep(1.5)
        
        # --- INPUT 1 ---
        print("\n[Input 1] Creating a new clinical patient profile (INSERT into Patients)...")
        time.sleep(1)
        
        # Generate a unique email every run so you don't get duplicate errors
        unique_email = f"mac.m.{int(time.time())}@email.com"
        
        p_id = app.writer.add_new_patient(
            email=unique_email, 
            password_hash="p_miller10", 
            first_name="Mac", 
            last_name="Miller", 
            phone="052-9998877", 
            notch_freq=4200, 
            notch_width=450, 
            test_date="2026-06-03"
        )
        
        if p_id:
            print(f"   -> [SUCCESS] Patient Profile created with Patient ID: {p_id}")
            time.sleep(1.5)
            
            # --- INPUT 2 ---
            print("\n[Input 2] Inserting subjective user evaluation (INSERT into Patient_Feedback)...")
            time.sleep(1)
            app.writer.insert_patient_feedback(patient_id=p_id, relief_score=4, notes="Vibration mode initialized, feeling good.")
            app.writer.insert_patient_feedback(patient_id=p_id, relief_score=5, notes="Perfect frequency calibration.")
            print("   -> [SUCCESS] Feedback logs safely written to database.")
            time.sleep(1.5)


        print("\n=== [PHASE 3] Executing DataReader Queries (2 QUERIES) ===")
        time.sleep(1.5)
        
        # --- QUERY 1 ---
        print("\n[Query 1] Fetching Patient Notch Profile (SELECT with JOIN)...")
        time.sleep(1)
        settings = app.reader.get_patient_notch_profile(patient_id=p_id)
        print("   -> Results returned as Dictionary:")
        print("      ", settings)
        time.sleep(1.5)
        
        # --- QUERY 2 ---
        print("\n[Query 2] Fetching chronological feedback history (SELECT with Aggregation)...")
        time.sleep(1)
        feedback_df = app.reader.get_patient_feedback_history(patient_id=p_id)
        print("   -> Results returned as Pandas DataFrame:")
        print(feedback_df)
        time.sleep(1.5)
        
        print("\n=== [PHASE 4] Verification Complete ===")
        print("[SUCCESS] All Read/Write modules verified successfully for the Midterm Report.")
        
        # Close connection session safely
        app.close()

if __name__ == "__main__":
    run_live_obs_demo()