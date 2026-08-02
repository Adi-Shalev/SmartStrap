# SmartStrap
**Telemedicine MVP for Blast-Induced Hearing Loss**

## 📖 Project Overview
SmartStrap is a clinical web application designed to support a haptic wearable device for individuals with blast-induced hearing loss. The system focuses on two core functionalities:
1. **Real-time Sound Completion (Primary):** Utilizing sensory substitution by mapping missing sound frequencies (due to hearing loss) to haptic vibrations on the user's wrist.
2. **Haptic Music Training (Secondary):** A structured neuroplasticity training module where patients listen to music paired with synchronized haptic feedback to retrain neural auditory pathways.

The system features two main portals:
- **Doctor Portal:** A comprehensive clinical dashboard featuring a Decision Support System (DSS) to monitor patient progress, view feedback history, and adjust device settings remotely.
- **Patient Portal:** A dedicated interface for patients to engage in haptic music training sessions, provide subjective relief feedback, and view real-time spectrogram data.

## 🏗️ System Architecture

The application is structured into five distinct architectural layers to maintain strict separation of concerns:

### 1. FrontEnd UI & Visualization
Provides the primary interface for both Doctors and Patients.
*   **Technologies:** HTML, Vanilla CSS (`styles.css`), JavaScript (`app.js`, `api.js`).
*   **Visualization:** Uses `spectrogram.js` to render real-time or static spectrograms of audio signals on an HTML canvas during training sessions.

### 2. REST API Server & Gateway (Controller)
*   **Technologies:** Python, Flask (`server.py`).
*   **Role:** Acts as the traffic controller, defining HTTP routes, parsing client requests, handling CORS, and formatting JSON responses. It delegates all business logic to the communication layer.

### 3. Communication & API Wrappers
*   **Technologies:** Python (`main_api.py`).
*   **Role:** The service layer (Facade) that abstracts database complexity. It initializes the database connection and coordinates reads and writes through the BackEnd Data Logic models.

### 4. BackEnd Data Logic & OOP Models
*   **Technologies:** Python, Pandas (`model_input.py`, `model_query.py`).
*   **Role:** Encapsulates all raw SQL queries. `model_input.py` handles all `INSERT` and `UPDATE` commands (DataWriter), while `model_query.py` handles all `SELECT` commands (DataReader), securely formatting results for the application.

### 5. Database Infrastructure & Configuration
*   **Technologies:** MySQL, Python (`db_connection.py`, `db_init.py`, `config.py`).
*   **Role:** Manages the MySQL database connection using a Singleton pattern. It includes scripts to initialize the schema (`training_tables.sql`), clear outdated records, and seed the database with mock clinical data from CSV files.

## 🚀 Getting Started

1.  **Database Setup:** Ensure MySQL is running. Configure credentials in `BackEnd/db/config.py`.
2.  **Initialize Database:** Run `python BackEnd/db/db_init.py` to create the schema and seed initial data.
3.  **Start Server:** Run `python server.py` to launch the Flask REST API.
4.  **Access Application:** Open `FrontEnd/index.html` in your browser.

*Note: Default testing credentials are provided in `FrontEnd/js/api.js`.*
