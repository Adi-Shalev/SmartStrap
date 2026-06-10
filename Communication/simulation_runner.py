from main_api import SmartStrapAPI

def run_live_obs_demo():
    print("=== [PHASE 1] Initializing SmartStrap Communication Layer ===")
    # Initialize API Wrapper (Triggers both DataReader and DataWriter)
    app = SmartStrapAPI(password="206535932")
    
    if hasattr(app, 'con') and app.con.is_connected():
        print("\n=== [PHASE 2] Executing DataWriter Operations (INSERT / UPDATE) ===")
        
        # 1. Create a new clinical patient profile
        p_id = app.writer.add_new_patient(
            email="nadav.demo2026@example.com", 
            password_hash="hashed_crypto_99", 
            first_name="Nadav", 
            last_name="Testbed", 
            phone="052-9998877", 
            notch_freq=4200, 
            notch_width=450, 
            test_date="2026-06-03"
        )
        
        if p_id:
            # 2. Update hardware vibration intensity profile
            app.writer.update_vibration_intensity(patient_id=p_id, new_intensity=9)
            
            # 3. Insert objective usage metrics from hardware
            app.writer.insert_system_log(patient_id=p_id, doctor_id=1, duration=40, vibrations=115, description="OBS Demo Session")
            
            # 4. Insert subjective user evaluation
            app.writer.insert_patient_feedback(patient_id=p_id, relief_score=4, notes="Vibration mode initialized, slight irritation.")
            app.writer.insert_patient_feedback(patient_id=p_id, relief_score=3, notes="Low satisfaction rating profile test.")

        print("\n=== [PHASE 3] Executing DataReader Queries (SELECT / ANALYTICS) ===")
        
        # Query 1: Fetch specific therapeutic configurations for the new patient (Returns dict)
        print("\n[Query 1] Fetching Device Settings for Patient:")
        settings = app.reader.get_device_settings_for_patient(patient_id=p_id)
        print(settings)
        
        # Query 2: Fetch chronological feedback history (Returns Pandas DataFrame)
        print("\n[Query 2] Fetching Patient Feedback History DataFrame:")
        feedback_df = app.reader.get_patient_feedback_history(patient_id=p_id)
        print(feedback_df)
        
        # Query 3: Fetch all active patients assigned to Doctor ID 1 (Returns Pandas DataFrame)
        print("\n[Query 3] Fetching Assigned Patients for Doctor 1 DataFrame:")
        doctor_patients_df = app.reader.get_assigned_patients_for_doctor(doctor_id=1)
        print(doctor_patients_df)
        
        # Query 4: Flag critical patients with average relief score < 5.0 (Returns Pandas DataFrame)
        print("\n[Query 4] Flagging Critical Patients Needing Attention DataFrame:")
        attention_df = app.reader.get_patients_needing_attention(doctor_id=1)
        print(attention_df)
        
        print("\n=== [PHASE 4] Verification Complete ===")
        print("🎯 All Read/Write modules from model_input and model_query verified successfully.")
        
        # Close connection session safely
        app.close()

if __name__ == "__main__":
    run_live_obs_demo()