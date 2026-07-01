# Flask Web Server Implementation

This plan outlines the creation of the "middle-man" Web Server using Python Flask. It will replace the hardcoded Javascript mock data by providing real endpoints that bridge the frontend `api.js` to the MySQL database via `main_api.py`.

## User Review Required
> [!IMPORTANT]
> Since we are moving to a real client-server architecture, you will need to leave the Flask server running in your terminal whenever you want to use the application. I will handle installing Flask and setting it up for you.

## Proposed Changes

### 1. `BackEnd`
#### [NEW] [server.py](file:///c:/Users/Avimo/OneDrive/Desktop/medical system/App/BackEnd/server.py)
Create a lightweight Flask application configured with CORS (Cross-Origin Resource Sharing) so the UI can communicate with it safely. It will instantiate `SmartStrapAPI` and expose the following routes:
- `POST /api/login`: Checks credentials and returns User ID and Role.
- `GET /api/patient/<id>/feedback/last`: Fetches the last feedback date.
- `POST /api/patient/<id>/feedback`: Inserts new feedback using `app.writer.insert_patient_feedback`.
- `POST /api/patient/<id>/config`: Updates the patient's notch configuration using `app.writer.update_device_settings`.

### 2. `FrontEnd/js`
#### [MODIFY] [api.js](file:///c:/Users/Avimo/OneDrive/Desktop/medical system/App/FrontEnd/js/api.js)
- Remove the hardcoded `_users` dictionary and `setTimeout` delays.
- Rewrite `login()`, `getLastFeedbackDate()`, `submitFeedback()`, and `savePatientConfig()` to use standard Javascript `fetch()` commands pointing to `http://127.0.0.1:5000/api/...`.

## Verification Plan
### Automated Verification
- I will run `pip install flask flask-cors`.
- I will start the Flask server in the background using a terminal command.

### Manual Verification
- You will open `index.html` in your browser.
- You will attempt to log in using `patient@demo.com`.
- We will verify that the terminal shows an incoming HTTP request and that the data loading on your screen is coming directly from MySQL.
