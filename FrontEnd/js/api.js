/**
 * Smart Strap - Mock API Interface
 * ─────────────────────────────────
 * Simulates backend HTTP responses so the front-end can be fully
 * tested without a running Flask server.
 *
 * Credential map (for demo login auto-fill):
 *   patient@demo.com  / password  → Patient  (Yossi Cohen,  ID 1)
 *   doctor@demo.com   / password  → Doctor   (Dr. Moshe Cohen, ID 1)
 *   admin@demo.com    / password  → Admin    (System Admin, ID 0)
 */

const API = {

    // ── Mock user store ────────────────────────────────────────────
    _users: {
        'patient@demo.com': {
            role:   'patient',
            name:   'Yossi Cohen',
            id:     1,
            notch:  4000,
            width:  500,
            intensity: 70
        },
        'doctor@demo.com': {
            role:   'doctor',
            name:   'Dr. Moshe Cohen',
            id:     1
        },
        'admin@demo.com': {
            role:   'admin',
            name:   'Adi Shalev',
            id:     0
        }
    },

    // ── Simulated network delay (ms) ───────────────────────────────
    _delay: 500,

    /**
     * Authenticate a user.
     * @param {string} email
     * @param {string} password   (ignored in mock – any value passes)
     * @param {string} role       Must match the stored role.
     * @returns {Promise<Object>} Resolved user object on success.
     */
    login(email, password, role) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                const user = this._users[email.toLowerCase().trim()];
                if (user && user.role === role) {
                    resolve({ ...user });            // return a copy
                } else if (user && user.role !== role) {
                    reject(new Error(
                        `Role mismatch — this account is registered as "${user.role}".`
                    ));
                } else {
                    reject(new Error('Invalid credentials. Please check your email and try again.'));
                }
            }, this._delay);
        });
    },

    /**
     * Fetch last feedback date for a patient (mock).
     * Returns null if no feedback has been submitted yet.
     * @param {number} patientId
     * @returns {Promise<Date|null>}
     */
    getLastFeedbackDate(patientId) {
        return new Promise(resolve => {
            setTimeout(() => {
                // Mock: patient 1 submitted feedback 3 days ago
                if (patientId === 1) {
                    const d = new Date();
                    d.setDate(d.getDate() - 3);
                    resolve(d);
                } else {
                    resolve(null);
                }
            }, this._delay);
        });
    },

    /**
     * Submit patient feedback (mock).
     * @param {number} patientId
     * @param {number} score       1 – 10
     * @param {string} notes
     * @returns {Promise<{ok: boolean}>}
     */
    submitFeedback(patientId, score, notes) {
        return new Promise(resolve => {
            setTimeout(() => resolve({ ok: true }), this._delay);
        });
    },

    /**
     * Save doctor configuration for a patient (mock).
     * @param {number} patientId
     * @param {Object} config     { notch, width, intensity, algorithm }
     * @returns {Promise<{ok: boolean}>}
     */
    savePatientConfig(patientId, config) {
        return new Promise(resolve => {
            setTimeout(() => resolve({ ok: true }), this._delay);
        });
    }
};
