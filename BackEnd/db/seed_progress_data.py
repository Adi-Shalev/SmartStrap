"""
Seed Script — SmartStrap Progress Data
---------------------------------------
Inserts realistic Training_Sessions and Patient_Feedback rows
for all patients so the Doctor's progress graphs have real data.

Run from the App/ root:
    C:\Windows\py.exe BackEnd/db/seed_progress_data.py
"""

import sys
import os
import random
from datetime import datetime, timedelta

# Build correct paths regardless of where script is run from
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_DIR    = os.path.abspath(os.path.join(_SCRIPT_DIR, '..', '..'))

sys.path.insert(0, _SCRIPT_DIR)          # so config.py is found
sys.path.insert(0, _APP_DIR)             # so BackEnd.db.db_connection is found

from db_connection import get_connection

# ── Patient profiles: each gets a unique learning trajectory ──────────────────
PATIENT_PROFILES = {
    1:  {"start_acc": 55, "trend": "improving",  "sessions": 8, "fb_scores": [8, 9, 9],        "name": "Yossi Cohen"},
    2:  {"start_acc": 40, "trend": "improving",  "sessions": 7, "fb_scores": [3, 5, 6, 7],     "name": "Michal Ansky"},
    3:  {"start_acc": 65, "trend": "stable",     "sessions": 6, "fb_scores": [7, 7, 8, 8],     "name": "Idan Amedi"},
    4:  {"start_acc": 30, "trend": "improving",  "sessions": 8, "fb_scores": [8, 8, 9, 9],     "name": "Maya Dayan"},
    5:  {"start_acc": 50, "trend": "plateau",    "sessions": 5, "fb_scores": [6, 6, 5, 7],     "name": "Tomer Shani"},
    6:  {"start_acc": 20, "trend": "struggling", "sessions": 6, "fb_scores": [2, 3, 2, 4],     "name": "Noa Kirel"},
    7:  {"start_acc": 70, "trend": "stable",     "sessions": 7, "fb_scores": [9, 9, 8, 9],     "name": "Amit Perez"},
    8:  {"start_acc": 45, "trend": "improving",  "sessions": 6, "fb_scores": [8, 8, 9],        "name": "Dana Levy"},
    9:  {"start_acc": 35, "trend": "improving",  "sessions": 7, "fb_scores": [7, 7, 8],        "name": "Guy Zoarez"},
    10: {"start_acc": 60, "trend": "plateau",    "sessions": 5, "fb_scores": [6, 7, 7],        "name": "Gal Gadon"},
}

NOTES_POOL = [
    "Noticing clearer sounds in daily environments.",
    "Hearing feels slightly improved with strap usage.",
    "More aware of environmental sounds.",
    "Training sessions feel more intuitive.",
    "Good progress, less tinnitus at this frequency.",
    "Still struggling with crowded environments.",
    "Getting used to the vibration pattern.",
    "Significant improvement this week.",
    "The haptic feedback is becoming more natural.",
    "Slight regression — stressful week at work.",
]


def generate_accuracy_series(start_acc, trend, n_sessions, seed=42):
    """Return an n-point accuracy list based on the given learning trajectory."""
    rng = random.Random(seed)
    series, acc = [], float(start_acc)
    for i in range(n_sessions):
        if trend == "improving":
            delta = rng.uniform(3, 10)
        elif trend == "stable":
            delta = rng.uniform(-3, 4)
        elif trend == "plateau":
            delta = rng.uniform(-5, 3) if i > 3 else rng.uniform(2, 8)
        else:  # struggling
            delta = rng.uniform(-6, 5)
        acc = min(98.0, max(5.0, acc + delta))
        series.append(round(acc, 1))
    return series


def get_song_id(cur):
    cur.execute("SELECT Song_ID FROM Song_Library LIMIT 1")
    row = cur.fetchone()
    return row[0] if row else None


def seed_training_sessions(con, cur, patient_id, profile, song_id, base_date):
    n          = profile["sessions"]
    accuracies = generate_accuracy_series(profile["start_acc"], profile["trend"], n, seed=patient_id * 7)
    rng        = random.Random(patient_id)
    inserted   = 0

    for i, acc in enumerate(accuracies):
        dt           = base_date + timedelta(days=i * 3 + rng.randint(0, 2))
        total_events = rng.randint(15, 40)
        hits         = round(total_events * acc / 100)
        misses       = total_events - hits
        duration     = round(rng.uniform(60, 300), 1)
        fp           = rng.randint(0, 3)

        cur.execute("""
            INSERT INTO Training_Sessions
                (Patient_ID, Song_ID, Session_Date, Duration_Seconds,
                 Total_Haptic_Events, Correct_Hits, Missed_Events,
                 False_Positives, Final_Accuracy_Score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (patient_id, song_id, dt.strftime("%Y-%m-%d %H:%M:%S"),
              duration, total_events, hits, misses, fp, acc))
        inserted += 1

    con.commit()
    return inserted


def seed_feedback(con, cur, patient_id, profile, base_date):
    scores = profile["fb_scores"]
    rng    = random.Random(patient_id + 99)

    # Wipe old sparse stub entries so we don't duplicate
    cur.execute("DELETE FROM Patient_Feedback WHERE Patient_ID = %s", (patient_id,))
    inserted = 0

    for i, score in enumerate(scores):
        dt   = base_date + timedelta(days=i * 14 + rng.randint(0, 3))
        note = rng.choice(NOTES_POOL)
        cur.execute("""
            INSERT INTO Patient_Feedback (Patient_ID, Timestamp, Relief_Score, Notes)
            VALUES (%s, %s, %s, %s)
        """, (patient_id, dt.strftime("%Y-%m-%d %H:%M:%S"), score, note))
        inserted += 1

    con.commit()
    return inserted


def main():
    print("=" * 58)
    print("  SmartStrap — Seeding progress data into NotchAppDB3")
    print("=" * 58)

    con = get_connection()
    if not con:
        print("[ERROR] Could not connect to database.")
        return

    cur     = con.cursor()
    song_id = get_song_id(cur)
    if not song_id:
        print("[ERROR] No songs in Song_Library. Add one first.")
        cur.close(); con.close(); return

    print(f"[OK] Using Song_ID={song_id} for seeded sessions\n")

    base_date      = datetime.now() - timedelta(days=90)
    total_sessions = 0
    total_feedback = 0

    for pid, profile in PATIENT_PROFILES.items():
        cur.execute("SELECT Patient_ID FROM Patients WHERE Patient_ID = %s", (pid,))
        if not cur.fetchone():
            print(f"  [SKIP] Patient ID {pid} not in DB")
            continue

        # Only insert training sessions if fewer than 3 already exist
        cur.execute("SELECT COUNT(*) FROM Training_Sessions WHERE Patient_ID = %s", (pid,))
        existing = cur.fetchone()[0]

        if existing < 3:
            s = seed_training_sessions(con, cur, pid, profile, song_id, base_date)
            total_sessions += s
            print(f"  [+] {profile['name']:20s} -> {s} training sessions inserted")
        else:
            print(f"  [=] {profile['name']:20s} -> {existing} sessions already exist, skipping")

        fb = seed_feedback(con, cur, pid, profile, base_date)
        total_feedback += fb
        print(f"      {'':20s}   {fb} feedback entries inserted")

    cur.close()
    con.close()

    print()
    print("=" * 58)
    print(f"  Done: {total_sessions} sessions + {total_feedback} feedback rows.")
    print("=" * 58)


if __name__ == "__main__":
    main()
