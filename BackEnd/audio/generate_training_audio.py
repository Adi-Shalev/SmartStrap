"""
Training Audio Generator — 4kHz Notch Training Tracks
──────────────────────────────────────────────────────
Generates synthetic WAV audio files with controlled 4kHz energy
for use in the haptic training mode.

Each track simulates a musical piece with:
  - A baseline harmonic structure (chords, bass)
  - Prominent 4kHz peaks (simulating hi-hats, vocal sibilance, guitar shimmer)
  - Varied timing patterns for the 4kHz events

The 4kHz peak timestamps are exported alongside each WAV file
so the training game knows exactly when haptic events should fire.

Usage:
    python BackEnd/generate_training_audio.py
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
import json
import os
import sys

# Ensure Communication and BackEnd are importable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, 'Communication'))
sys.path.insert(0, os.path.join(BASE_DIR, 'BackEnd', 'db'))

SAMPLE_RATE = 44100
AUDIO_DIR = os.path.join(BASE_DIR, "audio")


def generate_sine(freq, duration, sr=SAMPLE_RATE, amplitude=0.3):
    """Generate a pure sine wave."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return amplitude * np.sin(2 * np.pi * freq * t)


def generate_noise_burst(duration, sr=SAMPLE_RATE, amplitude=0.15):
    """Generate a short noise burst (simulates cymbal/hi-hat transient)."""
    n_samples = int(sr * duration)
    noise = amplitude * np.random.randn(n_samples)
    # Apply exponential decay envelope
    envelope = np.exp(-np.linspace(0, 8, n_samples))
    return noise * envelope


def bandpass_filter(signal, low, high, sr=SAMPLE_RATE, order=4):
    """Apply a bandpass filter to isolate a frequency range."""
    sos = butter(order, [low, high], btype='bandpass', fs=sr, output='sos')
    return sosfilt(sos, signal)


def generate_4khz_peak(duration=0.08, sr=SAMPLE_RATE, amplitude=0.5):
    """
    Generate a 4kHz-centered transient event.
    Combines a 4kHz sine burst with filtered noise for realism.
    """
    n_samples = int(sr * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # 4kHz sine burst with fast attack and decay
    sine_4k = amplitude * np.sin(2 * np.pi * 4000 * t)
    # Add harmonics for richness
    sine_8k = (amplitude * 0.3) * np.sin(2 * np.pi * 8000 * t)

    # Noise component filtered to 3.5-4.5 kHz band
    noise = generate_noise_burst(duration, sr, amplitude * 0.4)
    if len(noise) > 0:
        noise = bandpass_filter(noise, 3500, 4500, sr)

    # Attack-decay envelope
    attack = int(n_samples * 0.05)
    decay = n_samples - attack
    envelope = np.concatenate([
        np.linspace(0, 1, attack),
        np.exp(-np.linspace(0, 5, decay))
    ])

    peak = (sine_4k + sine_8k + noise[:n_samples]) * envelope
    return peak


def generate_backing_track(duration, sr=SAMPLE_RATE):
    """
    Generate a warm background track WITHOUT 4kHz content.
    Uses low-frequency harmonics to simulate bass + chords.
    """
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    track = np.zeros_like(t)

    # Bass line (80-200 Hz) — alternating notes
    bass_freqs = [82.4, 110.0, 98.0, 130.8]  # E2, A2, G2, C3
    beat_dur = duration / len(bass_freqs)
    for i, freq in enumerate(bass_freqs):
        start = int(i * beat_dur * sr)
        end = int((i + 1) * beat_dur * sr)
        segment = np.linspace(0, beat_dur, end - start, endpoint=False)
        track[start:end] += 0.2 * np.sin(2 * np.pi * freq * segment)

    # Warm pad (200-1500 Hz) — chord tones
    chord_freqs = [261.6, 329.6, 392.0, 523.3]  # C4, E4, G4, C5
    for freq in chord_freqs:
        track += 0.08 * np.sin(2 * np.pi * freq * t)

    # Gentle amplitude modulation for movement
    lfo = 0.8 + 0.2 * np.sin(2 * np.pi * 0.5 * t)
    track *= lfo

    # Low-pass filter to remove any content above 2kHz
    sos = butter(6, 2000, btype='low', fs=sr, output='sos')
    track = sosfilt(sos, track)

    return track


def generate_training_track(name, duration, peak_pattern, description=""):
    """
    Generate a complete training WAV file with 4kHz peaks at specified times.

    Parameters
    ----------
    name : str
        Filename (without extension)
    duration : float
        Total duration in seconds
    peak_pattern : list of float
        Timestamps (in seconds) where 4kHz peaks should occur
    description : str
        Human-readable description of the track

    Returns
    -------
    dict : Metadata about the generated track
    """
    sr = SAMPLE_RATE
    n_samples = int(sr * duration)

    # Generate warm backing track
    track = generate_backing_track(duration, sr)

    # Insert 4kHz peaks at specified timestamps
    peak_duration = 0.08  # 80ms per peak
    actual_peaks = []

    for peak_time in peak_pattern:
        start_sample = int(peak_time * sr)
        peak_signal = generate_4khz_peak(peak_duration, sr)
        end_sample = start_sample + len(peak_signal)

        if end_sample <= n_samples:
            track[start_sample:end_sample] += peak_signal
            actual_peaks.append({
                "time_ms": int(peak_time * 1000),
                "duration_ms": int(peak_duration * 1000),
                "intensity": 1.0
            })

    # Normalize to prevent clipping
    max_val = np.max(np.abs(track))
    if max_val > 0:
        track = track / max_val * 0.85

    # Convert to 16-bit PCM
    track_int16 = (track * 32767).astype(np.int16)

    # Save WAV file
    os.makedirs(AUDIO_DIR, exist_ok=True)
    wav_path = os.path.join(AUDIO_DIR, f"{name}.wav")
    wavfile.write(wav_path, sr, track_int16)

    # Save peak metadata as JSON (for the training game)
    metadata = {
        "title": name.replace("_", " ").title(),
        "description": description,
        "duration_seconds": duration,
        "sample_rate": sr,
        "total_peaks": len(actual_peaks),
        "peaks": actual_peaks
    }
    json_path = os.path.join(AUDIO_DIR, f"{name}_peaks.json")
    with open(json_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"  [OK] Generated: {wav_path} ({duration}s, {len(actual_peaks)} peaks)")
    return metadata


def generate_all_training_tracks():
    """Generate the full set of training tracks for the MVP."""

    print("=" * 60)
    print("  Smart Strap — Training Audio Generator")
    print("=" * 60)
    print()

    tracks = []

    # ── Track 1: Steady Rhythm (Beginner) ─────────────────────
    # Regular, predictable 4kHz peaks — like a metronome hi-hat
    duration_1 = 30.0
    bpm = 100
    beat_interval = 60.0 / bpm
    peaks_1 = [i * beat_interval for i in range(int(duration_1 / beat_interval))
               if i * beat_interval < duration_1 - 0.1]

    tracks.append(generate_training_track(
        name="steady_rhythm",
        duration=duration_1,
        peak_pattern=peaks_1,
        description="Regular hi-hat pattern at 100 BPM. Predictable timing for beginners."
    ))

    # ── Track 2: Syncopated Beat (Intermediate) ──────────────
    # Off-beat accents, some gaps — requires more attention
    duration_2 = 30.0
    peaks_2 = []
    t = 0.0
    beat = 60.0 / 120  # 120 BPM base
    while t < duration_2 - 0.1:
        peaks_2.append(t)
        # Syncopation: sometimes skip a beat, sometimes add an off-beat
        r = np.random.random()
        if r < 0.3:
            t += beat * 1.5  # Dotted rhythm
        elif r < 0.5:
            t += beat * 0.5  # Double-time
        else:
            t += beat  # Normal
    np.random.seed(42)  # Reset for reproducibility on re-run

    tracks.append(generate_training_track(
        name="syncopated_beat",
        duration=duration_2,
        peak_pattern=peaks_2,
        description="Syncopated rhythm with off-beat accents. Tests attention and reaction time."
    ))

    # ── Track 3: Vocal Sibilance Simulation (Intermediate) ───
    # Irregular peaks simulating speech consonants — natural timing
    duration_3 = 30.0
    np.random.seed(123)
    peaks_3 = sorted(np.random.uniform(0.5, duration_3 - 0.5, 35).tolist())
    # Remove peaks that are too close together (< 300ms apart)
    filtered_3 = [peaks_3[0]]
    for p in peaks_3[1:]:
        if p - filtered_3[-1] > 0.3:
            filtered_3.append(p)
    peaks_3 = filtered_3

    tracks.append(generate_training_track(
        name="vocal_sibilance",
        duration=duration_3,
        peak_pattern=peaks_3,
        description="Simulates vocal consonant patterns (s, t, f sounds). Irregular timing."
    ))

    # ── Track 4: Guitar Shimmer (Advanced) ───────────────────
    # Sparse, subtle peaks — requires careful listening
    duration_4 = 45.0
    np.random.seed(456)
    peaks_4 = sorted(np.random.uniform(1.0, duration_4 - 1.0, 20).tolist())
    filtered_4 = [peaks_4[0]]
    for p in peaks_4[1:]:
        if p - filtered_4[-1] > 1.0:  # At least 1 second apart
            filtered_4.append(p)
    peaks_4 = filtered_4

    tracks.append(generate_training_track(
        name="guitar_shimmer",
        duration=duration_4,
        peak_pattern=peaks_4,
        description="Sparse 4kHz events over warm acoustic backing. Advanced difficulty."
    ))

    # ── Track 5: Progressive Challenge (Full Session) ────────
    # Starts easy (regular), gets harder (irregular + fewer cues)
    duration_5 = 60.0
    peaks_5 = []
    # Phase 1 (0-20s): Regular beats
    t = 0.5
    while t < 20.0:
        peaks_5.append(t)
        t += 0.6
    # Phase 2 (20-40s): Semi-regular with gaps
    t = 20.5
    np.random.seed(789)
    while t < 40.0:
        peaks_5.append(t)
        t += 0.6 + np.random.uniform(-0.15, 0.3)
        if np.random.random() < 0.2:
            t += 1.0  # Skip
    # Phase 3 (40-60s): Sparse and unpredictable
    sparse_peaks = sorted(np.random.uniform(41.0, 59.0, 10).tolist())
    filtered_sparse = [sparse_peaks[0]]
    for p in sparse_peaks[1:]:
        if p - filtered_sparse[-1] > 1.5:
            filtered_sparse.append(p)
    peaks_5.extend(filtered_sparse)

    tracks.append(generate_training_track(
        name="progressive_challenge",
        duration=duration_5,
        peak_pattern=peaks_5,
        description="60-second session. Starts with regular beats, progressively becomes harder."
    ))

    # ── Summary ──────────────────────────────────────────────
    print()
    print(f"Generated {len(tracks)} training tracks in: {AUDIO_DIR}")
    print()
    for t in tracks:
        print(f"  - {t['title']} -- {t['duration_seconds']}s, {t['total_peaks']} peaks")
    print()
    print("Peak metadata saved as JSON files alongside each WAV.")

    return tracks


def seed_song_library():
    """
    Connect to the database and insert all generated tracks into Song_Library.
    Clears existing auto-generated entries first to prevent duplicates.
    """
    from main_api import SmartStrapAPI

    print()
    print("=" * 60)
    print("  Seeding Song_Library in NotchAppDB3")
    print("=" * 60)
    print()

    api = SmartStrapAPI()
    if not hasattr(api, 'con') or api.con is None:
        print("[ERROR] Could not connect to database. Skipping DB seed.")
        return

    # Clear old auto-generated songs (keep manually added ones)
    try:
        cursor = api.con.cursor()
        cursor.execute("DELETE FROM Song_Library WHERE Artist = 'Smart Strap Generator'")
        api.con.commit()
        deleted = cursor.rowcount
        cursor.close()
        if deleted > 0:
            print(f"  Cleared {deleted} old auto-generated songs.")
    except Exception as e:
        print(f"  Warning during cleanup: {e}")

    # Define the tracks to seed (must match generate_all_training_tracks output)
    songs_to_seed = [
        {
            "title": "Steady Rhythm",
            "artist": "Smart Strap Generator",
            "duration": 30.0,
            "file_path": "audio/steady_rhythm.wav",
        },
        {
            "title": "Syncopated Beat",
            "artist": "Smart Strap Generator",
            "duration": 30.0,
            "file_path": "audio/syncopated_beat.wav",
        },
        {
            "title": "Vocal Sibilance",
            "artist": "Smart Strap Generator",
            "duration": 30.0,
            "file_path": "audio/vocal_sibilance.wav",
        },
        {
            "title": "Guitar Shimmer",
            "artist": "Smart Strap Generator",
            "duration": 45.0,
            "file_path": "audio/guitar_shimmer.wav",
        },
        {
            "title": "Progressive Challenge",
            "artist": "Smart Strap Generator",
            "duration": 60.0,
            "file_path": "audio/progressive_challenge.wav",
        },
    ]

    inserted_ids = []
    for song in songs_to_seed:
        song_id = api.writer.insert_song(
            title=song["title"],
            artist=song["artist"],
            duration_seconds=song["duration"],
            file_path=song["file_path"]
        )
        if song_id:
            inserted_ids.append(song_id)

    print()
    print(f"  Inserted {len(inserted_ids)} songs into Song_Library.")
    print(f"  Song IDs: {inserted_ids}")

    api.close()
    return inserted_ids


if __name__ == "__main__":
    generate_all_training_tracks()
    seed_song_library()
