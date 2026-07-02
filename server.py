import sys
import os
# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import datetime
import pandas as pd
import json

# Add Communication folder to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Communication'))
from main_api import SmartStrapAPI

app = Flask(__name__, static_folder='FrontEnd', static_url_path='')
CORS(app)  # Enable CORS for all routes so frontend can communicate

# Initialize the Database connection
db_api = SmartStrapAPI()

@app.before_request
def ensure_db_connection():
    try:
        if db_api.con:
            db_api.con.ping(reconnect=True, attempts=3, delay=1)
    except Exception as e:
        print(f"Error ensuring DB connection: {e}")

# ── Admin credentials (no Admins table in DB, so kept here) ──
ADMIN_CREDENTIALS = {
    'email': 'admin@smartstrap.com',
    'password': 'admin123',
    'name': 'Adi Shalev',
    'id': 0,
}

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/admin')
def serve_admin():
    return send_from_directory(app.static_folder, 'admin.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    role = data.get('role', '')

    if role == 'patient':
        user = db_api.reader.authenticate_patient_by_email(email, password)
        if user:
            return jsonify({"success": True, "user": user})
        return jsonify({"success": False, "error": "Invalid email or password for patient."}), 401

    elif role == 'doctor':
        user = db_api.reader.authenticate_doctor_by_email(email, password)
        if user:
            return jsonify({"success": True, "user": user})
        return jsonify({"success": False, "error": "Invalid email or password for doctor."}), 401

    elif role == 'admin':
        if email == ADMIN_CREDENTIALS['email'] and password == ADMIN_CREDENTIALS['password']:
            return jsonify({"success": True, "user": {
                "id": ADMIN_CREDENTIALS['id'],
                "name": ADMIN_CREDENTIALS['name'],
                "role": "admin",
            }})
        return jsonify({"success": False, "error": "Invalid admin credentials."}), 401

    else:
        return jsonify({"success": False, "error": "Unknown role."}), 400

@app.route('/api/songs', methods=['GET'])
def get_songs():
    try:
        df = db_api.reader.get_available_songs()
        if df is not None and not df.empty:
            if 'Created_At' in df.columns:
                df['Created_At'] = df['Created_At'].astype(str)
                
            # Replace NaN with None for valid JSON serialization
            import numpy as np
            df = df.replace({np.nan: None})
            songs = df.to_dict(orient='records')
            
            for song in songs:
                file_path = song.get('File_Path')
                if file_path and isinstance(file_path, str):
                    base = os.path.splitext(os.path.basename(file_path))[0]
                    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio', f"{base}_peaks.json")
                    if os.path.exists(json_path):
                        with open(json_path, 'r') as f:
                            peak_meta = json.load(f)
                            song['peaks'] = peak_meta.get('peaks', [])
                    else:
                        song['peaks'] = []
                else:
                    song['peaks'] = []
            
            return jsonify({"success": True, "songs": songs})
        return jsonify({"success": True, "songs": []})
    except Exception as e:
        print(f"Error fetching songs: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/audio/<path:filename>', methods=['GET'])
def serve_audio(filename):
    audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio')
    return send_from_directory(audio_dir, filename)

@app.route('/api/audio/upload', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
    
    try:
        audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        file_path = os.path.join(audio_dir, file.filename)
        file.save(file_path)
        
        # Trigger processing
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BackEnd', 'audio'))
        import process_custom_audio
        processed_list = process_custom_audio.process_new_files()
        
        return jsonify({"success": True, "processed": processed_list})
    except Exception as e:
        print(f"Error processing audio upload: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/patient/<int:patient_id>/feedback/last', methods=['GET'])
def get_last_feedback(patient_id):
    try:
        df = db_api.reader.get_patient_feedback_history(patient_id)
        if df is not None and not df.empty:
            latest_record = df.iloc[0].to_dict()  # Already ordered DESC
            return jsonify({"success": True, "date": str(latest_record.get('Timestamp', ''))})
        return jsonify({"success": True, "date": None})
    except Exception as e:
        print(e)
        d = datetime.datetime.now() - datetime.timedelta(days=3)
        return jsonify({"success": True, "date": d.isoformat()})

@app.route('/api/patient/<int:patient_id>/feedback/history', methods=['GET'])
def get_feedback_history(patient_id):
    try:
        df = db_api.reader.get_patient_feedback_history(patient_id)
        if df is not None and not df.empty:
            if 'Timestamp' in df.columns:
                df['Timestamp'] = df['Timestamp'].astype(str)
            import numpy as np
            df = df.replace({np.nan: None})
            feedback = df.to_dict(orient='records')
            return jsonify({"success": True, "feedback": feedback})
        return jsonify({"success": True, "feedback": []})
    except Exception as e:
        print(f"Error fetching feedback history: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/patient/<int:patient_id>/feedback', methods=['POST'])
def submit_feedback(patient_id):
    data = request.json
    score = data.get('score', 5)
    notes = data.get('notes', '')
    
    try:
        db_api.writer.insert_patient_feedback(patient_id, score, notes)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/patient/<int:patient_id>/config', methods=['POST'])
def save_config(patient_id):
    data = request.json
    try:
        # Here we would normally update notch width, freq etc.
        # But for now, we just update intensity as supported by model_input
        intensity = data.get('intensity', 50)
        db_api.writer.update_vibration_intensity(patient_id, intensity)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/patient/<int:patient_id>/training/history', methods=['GET'])
def get_training_history(patient_id):
    try:
        df = db_api.reader.get_training_history(patient_id)
        if df is not None and not df.empty:
            # Convert datetime to string
            if 'Session_Date' in df.columns:
                df['Session_Date'] = df['Session_Date'].astype(str)
            
            import numpy as np
            df = df.replace({np.nan: None})
            sessions = df.to_dict(orient='records')
            return jsonify({"success": True, "history": sessions})
        return jsonify({"success": True, "history": []})
    except Exception as e:
        print(f"Error fetching training history: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/patient/<int:patient_id>/training/start', methods=['POST'])
def start_training(patient_id):
    data = request.json
    song_id = data.get('song_id')
    try:
        session_id = db_api.writer.create_training_session(patient_id, song_id)
        if session_id:
            return jsonify({"success": True, "session_id": session_id})
        return jsonify({"success": False, "error": "Failed to create session in database"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/patient/<int:patient_id>/training/stop', methods=['POST'])
def stop_training(patient_id):
    data = request.json
    session_id = data.get('session_id')
    duration_seconds = data.get('duration_seconds', 0)
    total_events = data.get('total_events', 0)
    hits = data.get('hits', 0)
    misses = data.get('misses', 0)
    false_positives = data.get('false_positives', 0)
    accuracy = data.get('accuracy', 0)
    
    try:
        if session_id:
            success = db_api.writer.complete_training_session(
                session_id=session_id,
                duration_seconds=duration_seconds,
                total_haptic_events=total_events,
                correct_hits=hits,
                missed_events=misses,
                false_positives=false_positives,
                final_accuracy_score=accuracy
            )
            return jsonify({"success": success})
        return jsonify({"success": False, "error": "No session_id provided"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Smart Strap API Server on port 5000...")
    app.run(debug=True, port=5000)
