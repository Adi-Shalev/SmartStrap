"""
SmartStrap API Server
──────────────────────
OOP-based Flask server for the SmartStrap medical system.
Encapsulates the Flask app, database API, and all route definitions
in a single SmartStrapServer class.

Usage:
    from server import SmartStrapServer

    server = SmartStrapServer()
    server.run()
"""

import sys
import os
# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import datetime
import pandas as pd
import json
import numpy as np

# Add Communication folder to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Communication'))
from main_api import SmartStrapAPI, DatabaseUnavailable
from mysql.connector import Error as MySQLError


class SmartStrapServer:
    """
    Main application server for the SmartStrap system.
    Encapsulates the Flask app, database API connection, and all route definitions.
    """

    ADMIN_CREDENTIALS = {
        'email': 'admin@smartstrap.com',
        'password': 'admin123',
        'name': 'Adi Shalev',
        'id': 0,
    }

    def __init__(self, host='127.0.0.1', port=5000, debug=True):
        """
        Initialize the server with Flask app and database connection.

        Parameters
        ----------
        host : str
            Host address to bind to.
        port : int
            Port number to listen on.
        debug : bool
            Whether to run Flask in debug mode.
        """
        self._host = host
        self._port = port
        self._debug = debug

        self._app = Flask(__name__, static_folder='FrontEnd', static_url_path='')
        CORS(self._app)

        self._api = SmartStrapAPI()

        self._register_hooks()
        self._register_routes()

    @property
    def app(self):
        """Expose the Flask app instance (useful for testing or WSGI deployment)."""
        return self._app

    @property
    def api(self):
        """Expose the database API instance."""
        return self._api

    def run(self):
        """Start the Flask development server."""
        print(f"Starting Smart Strap API Server on port {self._port}...")
        self._app.run(debug=self._debug, host=self._host, port=self._port)

    # ══════════════════════════════════════════════════════════════════════════
    #  Request Hooks
    # ══════════════════════════════════════════════════════════════════════════

    def _register_hooks(self):
        """Register request lifecycle hooks and JSON error handlers."""
        @self._app.teardown_request
        def release_db_connection(_exc):
            # Each request borrowed its own pooled connection — give it back.
            self._api.release()

        @self._app.errorhandler(DatabaseUnavailable)
        def handle_db_unavailable(e):
            print(f"[ERROR] {e}")
            return jsonify({
                "success": False,
                "error": "The database is not reachable right now. Please try again in a moment.",
            }), 503

        @self._app.errorhandler(MySQLError)
        def handle_db_error(e):
            print(f"[ERROR] Database error: {e}")
            return jsonify({"success": False, "error": "A database error occurred. Please try again."}), 503

        @self._app.errorhandler(500)
        def handle_internal_error(e):
            # Return JSON instead of an HTML page so the frontend can show a message.
            if request.path.startswith('/api/'):
                return jsonify({"success": False, "error": "Internal server error."}), 500
            return e

    # ══════════════════════════════════════════════════════════════════════════
    #  Route Registration — Master Method
    # ══════════════════════════════════════════════════════════════════════════

    def _register_routes(self):
        """Register all route groups."""
        self._register_static_routes()
        self._register_auth_routes()
        self._register_patient_routes()
        self._register_training_routes()
        self._register_audio_routes()
        self._register_doctor_routes()
        self._register_admin_routes()

    # ══════════════════════════════════════════════════════════════════════════
    #  Static File Routes
    # ══════════════════════════════════════════════════════════════════════════

    def _register_static_routes(self):
        """Serve the main frontend pages."""
        @self._app.route('/')
        def serve_index():
            return send_from_directory(self._app.static_folder, 'index.html')

        @self._app.route('/admin')
        def serve_admin():
            return send_from_directory(self._app.static_folder, 'admin.html')

    # ══════════════════════════════════════════════════════════════════════════
    #  Authentication Routes
    # ══════════════════════════════════════════════════════════════════════════

    def _register_auth_routes(self):
        """Handle login for patients, doctors, and admins."""
        @self._app.route('/api/login', methods=['POST'])
        def login():
            data = request.get_json(silent=True) or {}
            email = data.get('email', '').lower().strip()
            password = data.get('password', '')
            role = data.get('role', '')

            if role == 'patient':
                user = self._api.reader.authenticate_patient_by_email(email, password)
                if user:
                    self._api.writer.insert_system_log('USER_LOGIN', f"Patient {user['name']} logged in.", patient_id=user['id'])
                    return jsonify({"success": True, "user": user})
                return jsonify({"success": False, "error": "Invalid email or password for patient."}), 401

            elif role == 'doctor':
                user = self._api.reader.authenticate_doctor_by_email(email, password)
                if user:
                    self._api.writer.insert_system_log('USER_LOGIN', f"{user['name']} logged in.", doctor_id=user['id'])
                    return jsonify({"success": True, "user": user})
                return jsonify({"success": False, "error": "Invalid email or password for doctor."}), 401

            elif role == 'admin':
                if email == self.ADMIN_CREDENTIALS['email'] and password == self.ADMIN_CREDENTIALS['password']:
                    self._api.writer.insert_system_log('ADMIN_LOGIN', "System Administrator logged into the portal.")
                    return jsonify({"success": True, "user": {
                        "id": self.ADMIN_CREDENTIALS['id'],
                        "name": self.ADMIN_CREDENTIALS['name'],
                        "role": "admin",
                    }})
                return jsonify({"success": False, "error": "Invalid admin credentials."}), 401

            else:
                return jsonify({"success": False, "error": "Unknown role."}), 400

    # ══════════════════════════════════════════════════════════════════════════
    #  Patient Routes
    # ══════════════════════════════════════════════════════════════════════════

    def _register_patient_routes(self):
        """Handle patient feedback, configuration, and profile endpoints."""

        @self._app.route('/api/patient/<int:patient_id>/feedback/last', methods=['GET'])
        def get_last_feedback(patient_id):
            try:
                df = self._api.reader.get_patient_feedback_history(patient_id)
                if df is not None and not df.empty:
                    latest_record = df.iloc[0].to_dict()
                    return jsonify({"success": True, "date": str(latest_record.get('Timestamp', ''))})
                return jsonify({"success": True, "date": None})
            except Exception as e:
                print(e)
                d = datetime.datetime.now() - datetime.timedelta(days=3)
                return jsonify({"success": True, "date": d.isoformat()})

        @self._app.route('/api/patient/<int:patient_id>/feedback/history', methods=['GET'])
        def get_feedback_history(patient_id):
            try:
                df = self._api.reader.get_patient_feedback_history(patient_id)
                if df is not None and not df.empty:
                    if 'Timestamp' in df.columns:
                        df['Timestamp'] = df['Timestamp'].astype(str)
                    df = df.replace({np.nan: None})
                    feedback = df.to_dict(orient='records')
                    return jsonify({"success": True, "feedback": feedback})
                return jsonify({"success": True, "feedback": []})
            except Exception as e:
                print(f"Error fetching feedback history: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

        @self._app.route('/api/patient/<int:patient_id>/feedback', methods=['POST'])
        def submit_feedback(patient_id):
            data = request.json
            score = data.get('score', 5)
            notes = data.get('notes', '')
            try:
                self._api.writer.insert_patient_feedback(patient_id, score, notes)
                return jsonify({"success": True})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self._app.route('/api/patient/<int:patient_id>/config', methods=['POST'])
        def save_config(patient_id):
            data = request.json
            try:
                intensity = data.get('intensity', 50)
                self._api.writer.update_vibration_intensity(patient_id, intensity)
                return jsonify({"success": True})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

    # ══════════════════════════════════════════════════════════════════════════
    #  Training Routes
    # ══════════════════════════════════════════════════════════════════════════

    def _register_training_routes(self):
        """Handle training session lifecycle: history, start, stop."""

        @self._app.route('/api/patient/<int:patient_id>/training/history', methods=['GET'])
        def get_training_history(patient_id):
            try:
                df = self._api.reader.get_training_history(patient_id)
                if df is not None and not df.empty:
                    if 'Session_Date' in df.columns:
                        df['Session_Date'] = df['Session_Date'].astype(str)
                    df = df.replace({np.nan: None})
                    sessions = df.to_dict(orient='records')
                    return jsonify({"success": True, "history": sessions})
                return jsonify({"success": True, "history": []})
            except Exception as e:
                print(f"Error fetching training history: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

        @self._app.route('/api/patient/<int:patient_id>/training/start', methods=['POST'])
        def start_training(patient_id):
            data = request.json
            song_id = data.get('song_id')
            try:
                session_id = self._api.writer.create_training_session(patient_id, song_id)
                if session_id:
                    return jsonify({"success": True, "session_id": session_id})
                return jsonify({"success": False, "error": "Failed to create session in database"}), 500
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self._app.route('/api/patient/<int:patient_id>/training/stop', methods=['POST'])
        def stop_training(patient_id):
            data = request.json
            session_id = data.get('session_id')
            duration_seconds = data.get('duration_seconds', 0)
            total_events = data.get('total_events', 0)
            hits = data.get('hits', 0)
            misses = data.get('misses', 0)
            false_positives = data.get('false_positives', 0)
            accuracy = data.get('accuracy', 0)
            events = data.get('events', [])

            try:
                if session_id:
                    success = self._api.writer.complete_training_session(
                        session_id=session_id,
                        duration_seconds=duration_seconds,
                        total_haptic_events=total_events,
                        correct_hits=hits,
                        missed_events=misses,
                        false_positives=false_positives,
                        final_accuracy_score=accuracy
                    )
                    if success:
                        if events:
                            self._api.writer.log_session_events_batch(session_id, events)
                        self._api.writer.insert_system_log(
                            'TRAINING_COMPLETED',
                            f"Patient ID {patient_id} completed training session",
                            patient_id=patient_id,
                            duration=duration_seconds / 60.0,
                            vibrations=total_events
                        )
                        return jsonify({"success": True})
                return jsonify({"success": False, "error": "No session_id provided"}), 400
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self._app.route('/api/patient/<int:patient_id>/night/complete', methods=['POST'])
        def complete_night_session(patient_id):
            data = request.get_json(silent=True) or {}
            mode = data.get('mode', 'both')
            sound = data.get('sound')
            duration_seconds = int(data.get('duration_seconds', 0) or 0)
            pulses = int(data.get('pulses', 0) or 0)
            planned = data.get('planned_minutes')
            completed = bool(data.get('completed'))

            description = (
                f"Night session {'completed' if completed else 'stopped early'}: "
                f"mode={mode}" + (f", sound={sound}" if sound else "") +
                f", planned={planned} min, actual={duration_seconds} s, pulses={pulses}"
            )
            ok = self._api.writer.insert_system_log(
                'NIGHT_SESSION', description,
                patient_id=patient_id,
                duration=round(duration_seconds / 60),
                vibrations=pulses,
            )
            if ok:
                return jsonify({"success": True})
            return jsonify({"success": False, "error": "Failed to log night session."}), 500

    # ══════════════════════════════════════════════════════════════════════════
    #  Audio Routes
    # ══════════════════════════════════════════════════════════════════════════

    def _register_audio_routes(self):
        """Handle song listing, audio streaming, and file uploads."""

        @self._app.route('/api/songs', methods=['GET'])
        def get_songs():
            try:
                df = self._api.reader.get_available_songs()
                if df is not None and not df.empty:
                    if 'Created_At' in df.columns:
                        df['Created_At'] = df['Created_At'].astype(str)
                    df = df.replace({np.nan: None})
                    songs = df.to_dict(orient='records')

                    for song in songs:
                        file_path = song.get('File_Path')
                        if file_path and isinstance(file_path, str):
                            base = os.path.splitext(os.path.basename(file_path))[0]
                            json_path = os.path.join(
                                os.path.dirname(os.path.abspath(__file__)), 'audio', f"{base}_peaks.json"
                            )
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

        @self._app.route('/api/audio/<path:filename>', methods=['GET'])
        def serve_audio(filename):
            audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio')
            return send_from_directory(audio_dir, filename)

        @self._app.route('/api/audio/upload', methods=['POST'])
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
                sys.path.insert(0, os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), 'BackEnd', 'audio'
                ))
                import process_custom_audio
                processed_list = process_custom_audio.process_new_files()

                return jsonify({"success": True, "processed": processed_list})
            except Exception as e:
                print(f"Error processing audio upload: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

    # ══════════════════════════════════════════════════════════════════════════
    #  Doctor Routes
    # ══════════════════════════════════════════════════════════════════════════

    def _register_doctor_routes(self):
        """Handle doctor-specific endpoints: patient list, profile updates."""

        @self._app.route('/api/doctor/<int:doctor_id>/patients', methods=['GET'])
        def doctor_get_patients(doctor_id):
            df = self._api.reader.get_assigned_patients_for_doctor(doctor_id)
            if df is not None and not df.empty:
                df = df.replace({np.nan: None})
                patients = df.to_dict(orient='records')
                return jsonify({"success": True, "patients": patients})
            return jsonify({"success": True, "patients": []})

        @self._app.route('/api/doctor/patient/<int:patient_id>/profile', methods=['POST'])
        def doctor_update_patient_profile(patient_id):
            data = request.json
            notch_freq = data.get('notch_freq')
            notch_width = data.get('notch_width')
            intensity = data.get('intensity')

            success_notch = True
            if notch_freq is not None and notch_width is not None:
                success_notch = self._api.writer.update_patient_notch_profile(patient_id, notch_freq, notch_width)

            success_intensity = True
            if intensity is not None:
                success_intensity = self._api.writer.update_vibration_intensity(patient_id, intensity)

            if success_notch and success_intensity:
                self._api.writer.insert_system_log(
                    'CLINICAL_CONFIG',
                    f"Doctor updated medical profile for patient ID {patient_id}",
                    patient_id=patient_id
                )
                return jsonify({"success": True})
            return jsonify({"success": False, "error": "Failed to update profile."}), 500

    # ══════════════════════════════════════════════════════════════════════════
    #  Admin Routes
    # ══════════════════════════════════════════════════════════════════════════

    def _register_admin_routes(self):
        """Handle admin operations: registration, stats, logs, performance."""

        @self._app.route('/api/admin/register/doctor', methods=['POST'])
        def admin_register_doctor():
            data = request.json
            email = data.get('email')
            password = data.get('password')
            name_parts = email.split('@')[0].split('.')
            first_name = name_parts[0].capitalize() if len(name_parts) > 0 else 'Doctor'
            last_name = name_parts[1].capitalize() if len(name_parts) > 1 else 'Unknown'
            phone = '000-000-0000'

            doctor_id = self._api.writer.add_new_doctor(email, password, first_name, last_name, phone)
            if doctor_id:
                self._api.writer.insert_system_log(
                    'STAFF_REGISTRATION',
                    f"Admin registered new doctor: {email}",
                    doctor_id=doctor_id
                )
                return jsonify({"success": True, "doctor_id": doctor_id})
            return jsonify({"success": False, "error": "Failed to create doctor"}), 500

        @self._app.route('/api/admin/register/patient', methods=['POST'])
        def admin_register_patient():
            data = request.json
            email = data.get('email')
            password = data.get('password')
            doctor_id = data.get('doctor_id')

            first_name = data.get('first_name')
            last_name = data.get('last_name')
            phone = data.get('phone')
            test_date = data.get('test_date')

            if not first_name:
                name_parts = email.split('@')[0].split('.')
                first_name = name_parts[0].capitalize() if len(name_parts) > 0 else 'Patient'
            if not last_name:
                name_parts = email.split('@')[0].split('.')
                last_name = name_parts[1].capitalize() if len(name_parts) > 1 else 'Unknown'
            if not phone:
                phone = '000-000-0000'
            if not test_date:
                test_date = datetime.datetime.now().strftime('%Y-%m-%d')

            patient_id = self._api.writer.add_new_patient(
                email, password, first_name, last_name, phone, None, None, test_date
            )

            if patient_id:
                if doctor_id:
                    self._api.writer.assign_patient_to_doctor(doctor_id, patient_id)
                self._api.writer.insert_system_log(
                    'PATIENT_REGISTRATION',
                    f"Admin registered new patient: {email}",
                    patient_id=patient_id,
                    doctor_id=doctor_id
                )
                return jsonify({"success": True, "patient_id": patient_id})
            return jsonify({"success": False, "error": "Failed to create patient"}), 500

        @self._app.route('/api/admin/stats', methods=['GET'])
        def admin_get_stats():
            stats = self._api.reader.get_system_stats()
            if stats:
                return jsonify({"success": True, "stats": stats})
            return jsonify({"success": False, "error": "Failed to fetch stats"}), 500

        @self._app.route('/api/admin/logs', methods=['GET'])
        def admin_get_logs():
            df = self._api.reader.get_system_logs()
            if df is not None and not df.empty:
                df['Timestamp'] = df['Timestamp'].astype(str)
                logs = df.to_dict(orient='records')
                return jsonify({"success": True, "logs": logs})
            return jsonify({"success": True, "logs": []})

        @self._app.route('/api/admin/performance', methods=['GET'])
        def admin_get_performance():
            df = self._api.reader.get_global_performance_trends()
            if df is not None and not df.empty:
                df['Date'] = df['Date'].astype(str)
                df = df.replace({np.nan: 0})
                trends = df.to_dict(orient='records')
                return jsonify({"success": True, "trends": trends})
            return jsonify({"success": True, "trends": []})

        @self._app.route('/api/admin/doctors', methods=['GET'])
        def admin_get_doctors():
            df = self._api.reader.get_all_doctors()
            if df is not None and not df.empty:
                doctors = df.to_dict(orient='records')
                return jsonify({"success": True, "doctors": doctors})
            return jsonify({"success": True, "doctors": []})


# ══════════════════════════════════════════════════════════════════════════════
#  Entry Point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    server = SmartStrapServer()
    server.run()
