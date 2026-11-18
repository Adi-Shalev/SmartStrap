"""
Migration: one Device_Settings row per patient
-----------------------------------------------
1. Removes duplicate Device_Settings rows, keeping the most recently
   updated row for each patient (ties -> highest Strap_ID).
2. Adds UNIQUE KEY uq_device_settings_patient (Patient_ID).

Safe to run more than once. Run from anywhere:
    py BackEnd/db/migrate_device_settings_unique.py          # apply
    py BackEnd/db/migrate_device_settings_unique.py --dry-run
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_connection import get_connection

INDEX_NAME = "uq_device_settings_patient"


def main(dry_run=False):
    con = get_connection()
    if con is None:
        print("[ERROR] Cannot connect to MySQL.")
        return 1
    cur = con.cursor(buffered=True)

    # Rows to delete: every row that is not the newest one for its patient.
    cur.execute("""
        SELECT ds.Strap_ID, ds.Patient_ID, ds.Strap_MAC_Address, ds.Vibration_Intensity
        FROM Device_Settings ds
        JOIN Device_Settings newer
          ON newer.Patient_ID = ds.Patient_ID
         AND (COALESCE(newer.Last_Updated_At, 0) > COALESCE(ds.Last_Updated_At, 0)
              OR (COALESCE(newer.Last_Updated_At, 0) = COALESCE(ds.Last_Updated_At, 0)
                  AND newer.Strap_ID > ds.Strap_ID))
        GROUP BY ds.Strap_ID
    """)
    stale = cur.fetchall()
    print(f"Duplicate rows to remove: {len(stale)}")
    for row in stale:
        print(f"  Strap_ID={row[0]} Patient_ID={row[1]} MAC={row[2]} Intensity={row[3]}")

    cur.execute("""
        SELECT COUNT(*) FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'Device_Settings' AND INDEX_NAME = %s
    """, (INDEX_NAME,))
    has_index = cur.fetchone()[0] > 0
    print(f"Unique index present: {has_index}")

    if dry_run:
        print("Dry run — no changes made.")
        return 0

    try:
        if stale:
            cur.executemany("DELETE FROM Device_Settings WHERE Strap_ID = %s", [(r[0],) for r in stale])
        con.commit()
        if not has_index:
            cur.execute(f"ALTER TABLE Device_Settings ADD UNIQUE KEY {INDEX_NAME} (Patient_ID)")
            print(f"[OK] Added UNIQUE KEY {INDEX_NAME} (Patient_ID).")
        print("[OK] Migration complete.")
        return 0
    except Exception as e:
        con.rollback()
        print(f"[ERROR] Migration failed, rolled back: {e}")
        return 1
    finally:
        cur.close()
        con.close()


if __name__ == "__main__":
    sys.exit(main(dry_run="--dry-run" in sys.argv))
