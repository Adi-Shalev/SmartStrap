"""
Centralized Configuration
--------------------------
Single source of truth for all environment-specific settings.
Every module imports from here — no hardcoded credentials anywhere else.

Usage:
    from BackEnd.config import DB_CONFIG, APP_CONFIG
"""

import os

# ── Database Configuration ────────────────────────────────────────────────────
# Override via environment variables for production; defaults for local dev.

DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "127.0.0.1"),
    "user":     os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "206535932"),
    "database": os.environ.get("DB_NAME", "NotchAppDB3"),
}

# ── Application Configuration ─────────────────────────────────────────────────

APP_CONFIG = {
    "flask_host":  os.environ.get("FLASK_HOST", "127.0.0.1"),
    "flask_port":  int(os.environ.get("FLASK_PORT", 5000)),
    "debug":       os.environ.get("FLASK_DEBUG", "True").lower() == "true",
    "secret_key":  os.environ.get("SECRET_KEY", "smart-strap-dev-key-change-in-prod"),
}

# ── Signal Processing Defaults ────────────────────────────────────────────────

AUDIO_CONFIG = {
    "sample_rate":    44100,
    "fft_size":       1024,        # samples per FFT window
    "hop_size":       512,         # ~11.6ms hop at 44100 Hz
    "default_notch_center": 4000,  # Hz — overridden by patient profile
    "default_notch_width":  500,   # Hz — overridden by patient profile
    "demo_duration":  30,          # seconds for synthetic demo song
}

# ── File Paths ────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # App/
BACKEND_DIR = os.path.join(BASE_DIR, "BackEnd")
FRONTEND_DIR = os.path.join(BASE_DIR, "FrontEnd")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")  # for stored song files
