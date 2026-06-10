-- ============================================================================
-- Smart Strap — Training Module Tables
-- ============================================================================
-- Run AFTER the main schema (project_1.sql) has been executed.
-- These tables extend NotchAppDB3 without modifying existing tables.
--
-- Usage:
--   mysql -u root -p NotchAppDB3 < BackEnd/training_tables.sql
-- ============================================================================

USE NotchAppDB3;

-- ── Re-create System_Logs (missing from project_1.sql) ───────────────────────

DROP TABLE IF EXISTS System_Logs;

CREATE TABLE System_Logs (
    Log_ID                    INT PRIMARY KEY AUTO_INCREMENT,
    Patient_ID                INT,
    Doctor_ID                 INT,
    Event_Type                VARCHAR(50) DEFAULT 'DEVICE_USAGE',
    Timestamp                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Session_Duration_Minutes  INT,
    Total_Vibration_Events    INT,
    Action_Description        TEXT,
    FOREIGN KEY (Patient_ID)  REFERENCES Patients(Patient_ID),
    FOREIGN KEY (Doctor_ID)   REFERENCES Doctors(Doctor_ID)
);

-- ── Song Library ─────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS Session_Events;
DROP TABLE IF EXISTS Training_Sessions;
DROP TABLE IF EXISTS Song_Library;

CREATE TABLE Song_Library (
    Song_ID             INT PRIMARY KEY AUTO_INCREMENT,
    Title               VARCHAR(255) NOT NULL,
    Artist              VARCHAR(255),
    Duration_Seconds    FLOAT,
    File_Path           VARCHAR(500),
    Created_At          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Training Sessions (summary — feeds Doctor's graphs) ──────────────────────

CREATE TABLE Training_Sessions (
    Session_ID           INT PRIMARY KEY AUTO_INCREMENT,
    Patient_ID           INT NOT NULL,
    Song_ID              INT,
    Session_Date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Duration_Seconds     FLOAT,
    Total_Haptic_Events  INT,
    Correct_Hits         INT DEFAULT 0,
    Missed_Events        INT DEFAULT 0,
    False_Positives      INT DEFAULT 0,
    Final_Accuracy_Score FLOAT,
    Cognitive_Load       INT CHECK (Cognitive_Load >= 1 AND Cognitive_Load <= 10),
    Notes                TEXT,
    FOREIGN KEY (Patient_ID) REFERENCES Patients(Patient_ID),
    FOREIGN KEY (Song_ID)    REFERENCES Song_Library(Song_ID)
);

-- ── Session Events (raw gameplay log — exact timestamps per event) ───────────

CREATE TABLE Session_Events (
    Event_ID            INT PRIMARY KEY AUTO_INCREMENT,
    Session_ID          INT NOT NULL,
    Event_Time_Ms       INT NOT NULL,
    Event_Type          ENUM('HAPTIC_PEAK','USER_TAP','HIT','MISS','FALSE_POSITIVE') NOT NULL,
    Intensity           FLOAT,
    Reaction_Time_Ms    INT,
    FOREIGN KEY (Session_ID) REFERENCES Training_Sessions(Session_ID) ON DELETE CASCADE
);

-- ── Seed: insert a demo song ─────────────────────────────────────────────────

INSERT INTO Song_Library (Title, Artist, Duration_Seconds, File_Path)
VALUES ('Synthetic Demo', 'System Generated', 30.0, NULL);
