"""
Custom Audio Processor
────────────────────────
Scans the audio directory for new MP3/WAV files, analyzes them for 4kHz peaks,
converts them to WAV (if needed), saves peak metadata, and inserts them into the database.

Uses imageio-ffmpeg directly (no ffprobe needed) and scipy for signal analysis.
"""

import os
import glob
import json
import wave
import struct
import subprocess
import numpy as np
from scipy.signal import butter, sosfilt, find_peaks
import imageio_ffmpeg
import sys

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, 'Communication'))
from main_api import SmartStrapAPI

AUDIO_DIR = os.path.join(BASE_DIR, 'audio')
TARGET_SR = 44100

def load_audio_as_numpy(file_path):
    """
    Use ffmpeg directly to decode any audio file into raw PCM samples.
    Returns (samples_np_array, sample_rate, duration_seconds).
    """
    # Step 1: Use ffmpeg to convert to raw 16-bit PCM mono at 44100Hz
    cmd = [
        FFMPEG_EXE,
        '-i', file_path,
        '-f', 's16le',        # raw signed 16-bit little-endian
        '-acodec', 'pcm_s16le',
        '-ac', '1',           # mono
        '-ar', str(TARGET_SR),
        '-'                   # pipe to stdout
    ]
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg error: {result.stderr.decode('utf-8', errors='replace')[-500:]}")
    
    # Convert raw bytes to numpy
    samples = np.frombuffer(result.stdout, dtype=np.int16).astype(np.float32)
    duration_sec = len(samples) / TARGET_SR
    
    return samples, TARGET_SR, duration_sec

def convert_to_wav(input_path, output_path):
    """Use ffmpeg to convert any audio file to WAV."""
    cmd = [
        FFMPEG_EXE,
        '-y',                 # overwrite output
        '-i', input_path,
        '-acodec', 'pcm_s16le',
        '-ar', str(TARGET_SR),
        output_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg conversion error: {result.stderr.decode('utf-8', errors='replace')[-500:]}")

def butter_bandpass(lowcut, highcut, fs, order=5):
    sos = butter(order, [lowcut, highcut], btype='bandpass', fs=fs, output='sos')
    return sos

def extract_4khz_peaks(samples, fs):
    """Analyze audio samples to find prominent 4kHz transients."""
    
    # 1. Bandpass filter around 4kHz (3.5k - 4.5k)
    sos = butter_bandpass(3500, 4500, fs, order=4)
    filtered = sosfilt(sos, samples)
    
    # 2. Envelope extraction (rectify and smooth)
    rectified = np.abs(filtered)
    
    # Simple lowpass to smooth the envelope (approx 20Hz cutoff)
    sos_lp = butter(2, 20, btype='low', fs=fs, output='sos')
    envelope = sosfilt(sos_lp, rectified)
    
    # 3. Find peaks
    # We want prominent peaks that are at least 0.5s apart to avoid overwhelming haptics
    distance_samples = int(fs * 0.5)
    
    # Threshold: Top 15% of envelope amplitude, or a dynamic threshold
    threshold = np.percentile(envelope, 85)
    if threshold < 100: 
        threshold = 100 # minimum floor
        
    peaks, _ = find_peaks(envelope, height=threshold, distance=distance_samples, prominence=threshold*0.5)
    
    # Convert peak sample indices to seconds
    peak_times = peaks / fs
    
    actual_peaks = []
    for t in peak_times:
        actual_peaks.append({
            "time_ms": int(t * 1000),
            "duration_ms": 80,
            "intensity": 1.0
        })
        
    return actual_peaks

def process_new_files():
    print("=" * 60)
    print("  Smart Strap — Custom Audio Processor")
    print("=" * 60)
    print()

    api = SmartStrapAPI()
    if not hasattr(api, 'con') or api.con is None:
        print("[ERROR] Database connection failed. Exiting.")
        return

    os.makedirs(AUDIO_DIR, exist_ok=True)
    # Find all mp3 and wav files in the audio directory
    files = glob.glob(os.path.join(AUDIO_DIR, '*.mp3')) + glob.glob(os.path.join(AUDIO_DIR, '*.wav'))
    
    processed_count = 0
    processed_files = []

    for file_path in files:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        json_path = os.path.join(AUDIO_DIR, f"{base_name}_peaks.json")
        wav_path = os.path.join(AUDIO_DIR, f"{base_name}.wav")
        
        # If peaks json exists AND already in DB, skip entirely
        title_guess = base_name.replace("_", " ").replace("-", " ").title()
        already_in_db = False
        try:
            df = api.reader.get_available_songs()
            if df is not None and not df.empty:
                for fp in df['File_Path'].dropna():
                    if os.path.basename(fp).lower() == os.path.basename(wav_path).lower():
                        already_in_db = True
                        break
        except Exception:
            pass

        if os.path.exists(json_path) and already_in_db:
            continue
        
        if os.path.exists(json_path) and not already_in_db:
            # Peaks already extracted but not in DB — just register it
            print(f"Re-registering existing processed file: {os.path.basename(file_path)}")
            try:
                with open(json_path, 'r') as jf:
                    existing_meta = json.load(jf)
                rel_wav_path = f"audio/{os.path.basename(wav_path)}"
                api.writer.insert_song(
                    title=existing_meta.get('title', title_guess),
                    artist="Custom Upload",
                    duration_seconds=existing_meta.get('duration_seconds', 0),
                    file_path=rel_wav_path
                )
                processed_count += 1
                processed_files.append(existing_meta)
            except Exception as ex:
                print(f"  [ERROR] Re-registration failed: {ex}")
            continue
            
        print(f"Processing new file: {os.path.basename(file_path)}")
        
        try:
            # 1. Load Audio via ffmpeg
            print("  - Loading audio...")
            samples, fs, duration_sec = load_audio_as_numpy(file_path)
            print(f"  - Duration: {duration_sec:.1f}s | {len(samples)} samples")
            
            # 2. Extract 4kHz Peaks
            print("  - Analyzing 4kHz transients...")
            peaks = extract_4khz_peaks(samples, fs)
            
            # 3. Convert to WAV if it's not already
            if not file_path.lower().endswith('.wav'):
                print("  - Converting to WAV for web playback...")
                convert_to_wav(file_path, wav_path)
            
            # 4. Save JSON Metadata
            print(f"  - Found {len(peaks)} prominent 4kHz peaks. Saving metadata...")
            metadata = {
                "title": base_name.replace("_", " ").replace("-", " ").title(),
                "description": "User uploaded custom track",
                "duration_seconds": round(duration_sec, 2),
                "sample_rate": fs,
                "total_peaks": len(peaks),
                "peaks": peaks
            }
            with open(json_path, "w") as f:
                json.dump(metadata, f, indent=2)
                
            # 5. Insert into Database
            print("  - Inserting into Song_Library database...")
            rel_wav_path = f"audio/{os.path.basename(wav_path)}"
            api.writer.insert_song(
                title=metadata['title'],
                artist="Custom Upload",
                duration_seconds=metadata['duration_seconds'],
                file_path=rel_wav_path
            )
            
            print(f"  [OK] Successfully processed '{metadata['title']}'!")
            processed_count += 1
            processed_files.append(metadata)
            
        except Exception as e:
            print(f"  [ERROR] Failed to process {os.path.basename(file_path)}: {e}")

    api.close()
    
    print()
    if processed_count == 0:
        print("No new unprocessed audio files found.")
    else:
        print(f"Successfully processed {processed_count} new track(s).")
    print("=" * 60)
    
    return processed_files

if __name__ == '__main__':
    process_new_files()
