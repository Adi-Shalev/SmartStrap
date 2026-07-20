/**
 * Smart Strap - API Interface
 * ─────────────────────────────
 * Communicates with the Flask backend server.
 * Login authenticates against real Patients / Doctors tables in NotchAppDB3.
 *
 * Credential map (auto-filled for quick demo access):
 *   yossi.c@email.com         / p_yossi1       → Patient  (Yossi Cohen,  ID 1)
 *   moshe.cohen@hospital.com  / hash_moshe123   → Doctor   (Dr. Moshe Cohen, ID 1)
 *   admin@smartstrap.com      / admin123        → Admin    (Adi Shalev, ID 0)
 */

const API = {
    // The URL where our Python Flask server is running
    _baseUrl: 'http://127.0.0.1:5000/api',

    /**
     * Authenticate a user via the Flask server (real DB lookup).
     */
    async login(email, password, role) {
        const response = await fetch(`${this._baseUrl}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, role })
        });

        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Invalid credentials. Please check your email and try again.');
        }
        return data.user;
    },

    /**
     * Fetch last feedback date from MySQL via Flask.
     */
    async getLastFeedbackDate(patientId) {
        const response = await fetch(`${this._baseUrl}/patient/${patientId}/feedback/last`);
        const data = await response.json();

        if (data.success && data.date) {
            return new Date(data.date);
        }
        return null;
    },

    /**
     * Submit patient feedback to MySQL via Flask.
     */
    async submitFeedback(patientId, score, notes) {
        const response = await fetch(`${this._baseUrl}/patient/${patientId}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ score, notes })
        });
        const data = await response.json();
        return { ok: data.success };
    },

    /**
     * Save doctor configuration to MySQL via Flask.
     */
    async savePatientConfig(patientId, config) {
        const response = await fetch(`${this._baseUrl}/patient/${patientId}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        const data = await response.json();
        return { ok: data.success };
    },

    /**
     * Fetch available songs with their peak metadata.
     */
    async getSongs() {
        try {
            const response = await fetch(`${this._baseUrl}/songs?t=${new Date().getTime()}`);
            const data = await response.json();
            return data.success ? data.songs : [];
        } catch (error) {
            console.error('Error fetching songs:', error);
            return [];
        }
    },

    /**
     * Start a training session.
     */
    async startTrainingSession(patientId, songId) {
        const response = await fetch(`${this._baseUrl}/patient/${patientId}/training/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ song_id: songId })
        });
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Failed to start training session.');
        }
        return data.session_id;
    },

    /**
     * Fetch patient training history
     */
    async getTrainingHistory(patientId) {
        try {
            const response = await fetch(`${this._baseUrl}/patient/${patientId}/training/history?t=${new Date().getTime()}`);
            const data = await response.json();
            return data.success ? data.history : [];
        } catch (error) {
            console.error('Error fetching training history:', error);
            return [];
        }
    },

    /**
     * Stop a training session and save stats.
     */
    async stopTrainingSession(patientId, sessionId, stats) {
        const response = await fetch(`${this._baseUrl}/patient/${patientId}/training/stop`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                duration_seconds: stats.duration_seconds,
                total_events: stats.total_events,
                hits: stats.hits,
                misses: stats.misses,
                false_positives: stats.false_positives,
                accuracy: stats.accuracy
            })
        });
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Failed to stop training session.');
        }
        return data.success;
    },

    /**
     * Fetch full feedback history for a patient (timestamps + notes).
     */
    async getFeedbackHistory(patientId) {
        try {
            const response = await fetch(`${this._baseUrl}/patient/${patientId}/feedback/history`);
            const data = await response.json();
            return data.success ? data.feedback : [];
        } catch (error) {
            console.error('Error fetching feedback history:', error);
            return [];
        }
    },

    // ─── ADMIN API METHODS ───────────────────────────────────────────────────

    async getAdminStats() {
        const response = await fetch(`${this._baseUrl}/admin/stats`);
        const data = await response.json();
        return data.success ? data.stats : null;
    },

    async getAdminLogs() {
        const response = await fetch(`${this._baseUrl}/admin/logs`);
        const data = await response.json();
        return data.success ? data.logs : [];
    },

    async getAdminPerformance() {
        const response = await fetch(`${this._baseUrl}/admin/performance`);
        const data = await response.json();
        return data.success ? data.trends : [];
    },

    async getAllDoctors() {
        const response = await fetch(`${this._baseUrl}/admin/doctors`);
        const data = await response.json();
        return data.success ? data.doctors : [];
    },

    async registerDoctor(email, password) {
        const response = await fetch(`${this._baseUrl}/admin/register/doctor`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Failed to register doctor.');
        }
        return data;
    },

    async registerPatient(email, password, doctorId, firstName, lastName, phone, testDate) {
        const response = await fetch(`${this._baseUrl}/admin/register/patient`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                email, 
                password, 
                doctor_id: doctorId,
                first_name: firstName,
                last_name: lastName,
                phone: phone,
                test_date: testDate
            })
        });
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Failed to register patient.');
        }
        return data;
    },

    // ─── DOCTOR API METHODS ──────────────────────────────────────────────────

    async getDoctorPatients(doctorId) {
        try {
            const response = await fetch(`${this._baseUrl}/doctor/${doctorId}/patients`);
            const data = await response.json();
            return data.success ? data.patients : [];
        } catch (error) {
            console.error('Error fetching doctor patients:', error);
            return [];
        }
    },

    async updatePatientProfile(patientId, notchFreq, notchWidth, intensity) {
        const response = await fetch(`${this._baseUrl}/doctor/patient/${patientId}/profile`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                notch_freq: notchFreq,
                notch_width: notchWidth,
                intensity: intensity
            })
        });
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Failed to update patient profile.');
        }
        return data;
    }
};
