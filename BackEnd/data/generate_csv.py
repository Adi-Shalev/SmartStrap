import pandas as pd
import os

def create_local_csvs():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    doctors_data = [
        {"Doctor_ID": 1, "Email": "moshe.cohen@hospital.com", "Password_Hash": "hash_moshe123", "First_Name": "Moshe", "Last_Name": "Cohen", "Phone_Number": "050-1112222"},
        {"Doctor_ID": 2, "Email": "galit.levy@hospital.com", "Password_Hash": "hash_galit123", "First_Name": "Galit", "Last_Name": "Levy", "Phone_Number": "054-3334444"}
    ]
    pd.DataFrame(doctors_data).to_csv(os.path.join(current_dir, "doctors.csv"), index=False)

    patients_data = [
        {"Patient_ID": 1, "Email": "yossi.c@email.com", "Password_Hash": "p_yossi1", "First_Name": "Yossi", "Last_Name": "Cohen", "Phone_Number": "052-1111111", "Notch_Center_Frequency": 4000, "Notch_Width": 500, "Test_Date": "2026-05-10"},
        {"Patient_ID": 2, "Email": "michal.a@email.com", "Password_Hash": "p_michal2", "First_Name": "Michal", "Last_Name": "Ansky", "Phone_Number": "054-2222222", "Notch_Center_Frequency": 3200, "Notch_Width": 400, "Test_Date": "2026-05-12"},
        {"Patient_ID": 3, "Email": "idan.a@email.com", "Password_Hash": "p_idan3", "First_Name": "Idan", "Last_Name": "Amedi", "Phone_Number": "050-3333333", "Notch_Center_Frequency": 4500, "Notch_Width": 600, "Test_Date": "2026-05-14"},
        {"Patient_ID": 4, "Email": "maya.d@email.com", "Password_Hash": "p_maya4", "First_Name": "Maya", "Last_Name": "Dayan", "Phone_Number": "053-4444444", "Notch_Center_Frequency": 3800, "Notch_Width": 450, "Test_Date": "2026-05-15"},
        {"Patient_ID": 5, "Email": "tomer.s@email.com", "Password_Hash": "p_tomer5", "First_Name": "Tomer", "Last_Name": "Shani", "Phone_Number": "058-5555555", "Notch_Center_Frequency": 5100, "Notch_Width": 550, "Test_Date": "2026-05-16"},
        {"Patient_ID": 6, "Email": "noa.k@email.com", "Password_Hash": "p_noa6", "First_Name": "Noa", "Last_Name": "Kirel", "Phone_Number": "052-6666666", "Notch_Center_Frequency": 2900, "Notch_Width": 350, "Test_Date": "2026-05-18"},
        {"Patient_ID": 7, "Email": "amit.p@email.com", "Password_Hash": "p_amit7", "First_Name": "Amit", "Last_Name": "Perez", "Phone_Number": "050-7777777", "Notch_Center_Frequency": 4200, "Notch_Width": 500, "Test_Date": "2026-05-20"},
        {"Patient_ID": 8, "Email": "dana.l@email.com", "Password_Hash": "p_dana8", "First_Name": "Dana", "Last_Name": "Levy", "Phone_Number": "054-8888888", "Notch_Center_Frequency": 4800, "Notch_Width": 600, "Test_Date": "2026-05-22"},
        {"Patient_ID": 9, "Email": "guy.z@email.com", "Password_Hash": "p_guy9", "First_Name": "Guy", "Last_Name": "Zoarez", "Phone_Number": "052-9999999", "Notch_Center_Frequency": 3500, "Notch_Width": 400, "Test_Date": "2026-05-25"},
        {"Patient_ID": 10, "Email": "gal.g@email.com", "Password_Hash": "p_gal10", "First_Name": "Gal", "Last_Name": "Gadon", "Phone_Number": "053-0000000", "Notch_Center_Frequency": 6000, "Notch_Width": 700, "Test_Date": "2026-05-28"}
    ]
    pd.DataFrame(patients_data).to_csv(os.path.join(current_dir, "patients.csv"), index=False)

    doctor_patient_data = [
        {"Doctor_ID": 1, "Patient_ID": 1, "Assignment_Date": "2026-05-10"},
        {"Doctor_ID": 1, "Patient_ID": 2, "Assignment_Date": "2026-05-12"},
        {"Doctor_ID": 1, "Patient_ID": 3, "Assignment_Date": "2026-05-14"},
        {"Doctor_ID": 1, "Patient_ID": 4, "Assignment_Date": "2026-05-15"},
        {"Doctor_ID": 1, "Patient_ID": 5, "Assignment_Date": "2026-05-16"},
        {"Doctor_ID": 1, "Patient_ID": 6, "Assignment_Date": "2026-05-18"},
        {"Doctor_ID": 1, "Patient_ID": 7, "Assignment_Date": "2026-05-20"},
        {"Doctor_ID": 2, "Patient_ID": 8, "Assignment_Date": "2026-05-22"},
        {"Doctor_ID": 2, "Patient_ID": 9, "Assignment_Date": "2026-05-25"},
        {"Doctor_ID": 2, "Patient_ID": 10, "Assignment_Date": "2026-05-28"}
    ]
    pd.DataFrame(doctor_patient_data).to_csv(os.path.join(current_dir, "doctor_patient.csv"), index=False)

    device_setting_data = [
        {"Strap_ID": 101, "Patient_ID": 1, "Strap_MAC_Address": "AA:BB:CC:DD:EE:01", "Vibration_Intensity": 70, "Mapping_Algorithm_ID": "DAILY_MODE"},
        {"Strap_ID": 102, "Patient_ID": 2, "Strap_MAC_Address": "AA:BB:CC:DD:EE:02", "Vibration_Intensity": 40, "Mapping_Algorithm_ID": "DAILY_MODE"},
        {"Strap_ID": 103, "Patient_ID": 3, "Strap_MAC_Address": "AA:BB:CC:DD:EE:03", "Vibration_Intensity": 85, "Mapping_Algorithm_ID": "TRAINING_MODE"},
        {"Strap_ID": 104, "Patient_ID": 4, "Strap_MAC_Address": "AA:BB:CC:DD:EE:04", "Vibration_Intensity": 60, "Mapping_Algorithm_ID": "DAILY_MODE"},
        {"Strap_ID": 105, "Patient_ID": 5, "Strap_MAC_Address": "AA:BB:CC:DD:EE:05", "Vibration_Intensity": 50, "Mapping_Algorithm_ID": "TRAINING_MODE"},
        {"Strap_ID": 106, "Patient_ID": 6, "Strap_MAC_Address": "AA:BB:CC:DD:EE:06", "Vibration_Intensity": 35, "Mapping_Algorithm_ID": "DAILY_MODE"},
        {"Strap_ID": 107, "Patient_ID": 7, "Strap_MAC_Address": "AA:BB:CC:DD:EE:07", "Vibration_Intensity": 80, "Mapping_Algorithm_ID": "DAILY_MODE"},
        {"Strap_ID": 108, "Patient_ID": 8, "Strap_MAC_Address": "AA:BB:CC:DD:EE:08", "Vibration_Intensity": 75, "Mapping_Algorithm_ID": "TRAINING_MODE"},
        {"Strap_ID": 109, "Patient_ID": 9, "Strap_MAC_Address": "AA:BB:CC:DD:EE:09", "Vibration_Intensity": 45, "Mapping_Algorithm_ID": "DAILY_MODE"},
        {"Strap_ID": 110, "Patient_ID": 10, "Strap_MAC_Address": "AA:BB:CC:DD:EE:10", "Vibration_Intensity": 90, "Mapping_Algorithm_ID": "TRAINING_MODE"}
    ]
    pd.DataFrame(device_setting_data).to_csv(os.path.join(current_dir, "device_setting.csv"), index=False)

    patient_feedback_data = [
        {"Feedback_ID": 1, "Patient_ID": 1, "Timestamp": "2026-05-11 10:00:00", "Relief_Score": 8, "Notes": "Tinnitus is fading."},
        {"Feedback_ID": 2, "Patient_ID": 1, "Timestamp": "2026-05-12 11:30:00", "Relief_Score": 9, "Notes": "Relaxing rhythm."},
        {"Feedback_ID": 3, "Patient_ID": 2, "Timestamp": "2026-05-13 09:15:00", "Relief_Score": 3, "Notes": "Vibration too weak."},
        {"Feedback_ID": 4, "Patient_ID": 3, "Timestamp": "2026-05-15 14:20:00", "Relief_Score": 7, "Notes": "Helped me study."},
        {"Feedback_ID": 5, "Patient_ID": 4, "Timestamp": "2026-05-16 16:45:00", "Relief_Score": 8, "Notes": "Comfortable setup."},
        {"Feedback_ID": 6, "Patient_ID": 5, "Timestamp": "2026-05-17 10:10:00", "Relief_Score": 6, "Notes": "Takes time."},
        {"Feedback_ID": 7, "Patient_ID": 6, "Timestamp": "2026-05-19 18:00:00", "Relief_Score": 2, "Notes": "Irritates skin."},
        {"Feedback_ID": 8, "Patient_ID": 7, "Timestamp": "2026-05-21 12:00:00", "Relief_Score": 9, "Notes": "Perfect relief."},
        {"Feedback_ID": 9, "Patient_ID": 8, "Timestamp": "2026-05-23 15:30:00", "Relief_Score": 8, "Notes": "Works as expected."},
        {"Feedback_ID": 10, "Patient_ID": 9, "Timestamp": "2026-05-26 08:45:00", "Relief_Score": 7, "Notes": "Decent mitigation."},
        {"Feedback_ID": 11, "Patient_ID": 10, "Timestamp": "2026-05-29 19:10:00", "Relief_Score": 4, "Notes": "Too intense."},
        {"Feedback_ID": 12, "Patient_ID": 10, "Timestamp": "2026-05-30 20:00:00", "Relief_Score": 5, "Notes": "Slightly better."}
    ]
    pd.DataFrame(patient_feedback_data).to_csv(os.path.join(current_dir, "patient_feedback.csv"), index=False)

    system_logs_data = [
        {"Log_ID": 1, "Patient_ID": 1, "Doctor_ID": 1, "Event_Type": "DEVICE_USAGE", "Timestamp": "2026-05-11 10:30:00", "Session_Duration_Minutes": 30, "Total_Vibration_Events": 150, "Action_Description": "Completed."},
        {"Log_ID": 2, "Patient_ID": 1, "Doctor_ID": 1, "Event_Type": "DEVICE_USAGE", "Timestamp": "2026-05-12 12:15:00", "Session_Duration_Minutes": 45, "Total_Vibration_Events": 220, "Action_Description": "Extended."},
        {"Log_ID": 3, "Patient_ID": 2, "Doctor_ID": 1, "Event_Type": "DEVICE_USAGE", "Timestamp": "2026-05-13 09:35:00", "Session_Duration_Minutes": 20, "Total_Vibration_Events": 90, "Action_Description": "Cut short."},
        {"Log_ID": 4, "Patient_ID": 3, "Doctor_ID": 1, "Event_Type": "DEVICE_USAGE", "Timestamp": "2026-05-15 15:20:00", "Session_Duration_Minutes": 60, "Total_Vibration_Events": 300, "Action_Description": "Full session."},
        {"Log_ID": 5, "Patient_ID": 4, "Doctor_ID": 1, "Event_Type": "DEVICE_USAGE", "Timestamp": "2026-05-16 17:25:00", "Session_Duration_Minutes": 40, "Total_Vibration_Events": 180, "Action_Description": "Completed."},
        {"Log_ID": 6, "Patient_ID": 5, "Doctor_ID": 1, "Event_Type": "DEVICE_USAGE", "Timestamp": "2026-05-17 11:00:00", "Session_Duration_Minutes": 50, "Total_Vibration_Events": 240, "Action_Description": "Completed."},
        {"Log_ID": 7, "Patient_ID": 6, "Doctor_ID": 1, "Event_Type": "DEVICE_USAGE", "Timestamp": "2026-05-19 18:15:00", "Session_Duration_Minutes": 15, "Total_Vibration_Events": 60, "Action_Description": "Discomfort."},
        {"Log_ID": 8, "Patient_ID": 7, "Doctor_ID": 1, "Event_Type": "DEVICE_USAGE", "Timestamp": "2026-05-21 12:45:00", "Session_Duration_Minutes": 45, "Total_Vibration_Events": 210, "Action_Description": "Completed."},
        {"Log_ID": 9, "Patient_ID": 7, "Doctor_ID": 1, "Event_Type": "DEVICE_USAGE", "Timestamp": "2026-05-22 14:35:00", "Session_Duration_Minutes": 35, "Total_Vibration_Events": 160, "Action_Description": "Completed."},
        {"Log_ID": 10, "Patient_ID": 8, "Doctor_ID": 2, "Event_Type": "DEVICE_USAGE", "Timestamp": "2026-05-23 16:25:00", "Session_Duration_Minutes": 55, "Total_Vibration_Events": 270, "Action_Description": "Completed."},
        {"Log_ID": 11, "Patient_ID": 9, "Doctor_ID": 2, "Event_Type": "DEVICE_USAGE", "Timestamp": "2026-05-26 09:25:00", "Session_Duration_Minutes": 40, "Total_Vibration_Events": 190, "Action_Description": "Completed."},
        {"Log_ID": 12, "Patient_ID": 10, "Doctor_ID": 2, "Event_Type": "DEVICE_USAGE", "Timestamp": "2026-05-29 19:40:00", "Session_Duration_Minutes": 30, "Total_Vibration_Events": 140, "Action_Description": "Completed."},
        {"Log_ID": 13, "Patient_ID": 10, "Doctor_ID": 2, "Event_Type": "DEVICE_USAGE", "Timestamp": "2026-05-30 20:25:00", "Session_Duration_Minutes": 25, "Total_Vibration_Events": 110, "Action_Description": "Completed."}
    ]
    pd.DataFrame(system_logs_data).to_csv(os.path.join(current_dir, "system_logs.csv"), index=False)

    print("CSV files populated successfully!")

if __name__ == "__main__":
    create_local_csvs()