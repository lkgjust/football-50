# -*- coding: utf-8 -*-
"""
Beat the Keeper - Headless Frame-Stepping 4K HTML Renderer
Captures the gorgeous HTML canvas directly from headless Chromium frame-by-frame.
"""

import os
import sys
import time
import glob
import base64
import subprocess
import wave
import numpy as np
import cv2

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: 'playwright' is not installed! Installing dependencies...")
    sys.exit(1)

# --- VIDEO CONFIGURATION (TRUE NATIVE 4K ULTRA HD) ---
WIDTH, HEIGHT = 3840, 2160  # Native 4K Canvas resolution
FPS = 30
TEMP_VIDEO_RAW = "temp_raw_4k.mp4"
TEMP_SFX_WAV = "temp_sfx.wav"
FINAL_OUTPUT_FILENAME = "beat_the_keeper_final_video.mp4"
BGM_FILENAME = "Beat the Keeper - 50 Country Elimination Marble Race.m4a"

# Locate the HTML file in the repository root
html_file = "beat_the_keeper_simulation_app.html"
if not os.path.exists(html_file):
    # Fallback check
    html_file = "index.html"

if not os.path.exists(html_file):
    print(f"Error: HTML template file not found in repository root!")
    sys.exit(1)

HTML_PATH = os.path.abspath(html_file)
file_url = f"file:///{HTML_PATH.replace(os.sep, '/')}"

# --- HIGH-QUALITY SYNTHETIC SFX GENERATORS ---
def gen_sound_wave(duration, freq_func, amp_decay):
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), False)
    wave_data = freq_func(t) * amp_decay(t)
    return (wave_data * 14000).astype(np.int16)

sound_wave_cache = {
    'bounce': gen_sound_wave(0.08, lambda t: np.sin(2 * np.pi * 320 * t), lambda t: np.exp(-12 * t)),
    'kick': gen_sound_wave(0.16, lambda t: np.sin(2 * np.pi * np.geomspace(140, 45, len(t)) * t), lambda t: np.exp(-8 * t)),
    'goal': gen_sound_wave(0.35, lambda t: (np.sin(2 * np.pi * 523 * t) + np.sin(2 * np.pi * 659 * t) + np.sin(2 * np.pi * 784 * t)) / 3.0, lambda t: np.exp(-4 * t)),
    'fail': gen_sound_wave(0.25, lambda t: np.sin(2 * np.pi * 100 * t), lambda t: np.exp(-5 * t))
}

# --- JAVASCRIPT DETOUR & FRAME STEPPING HOOKS ---
JS_DETERMINISTIC_HOOK = """
window.champion_declared = false;
window.sound_events = [];
window.current_frame_count = 0;
window.saved_callbacks = [];

// Intercept playSound triggers
window.playSound = function(type) {
    window.sound_events.push([window.current_frame_count, type]);
};

// Intercept requestAnimationFrame to freeze time
window.original_requestAnimationFrame = window.requestAnimationFrame;
window.requestAnimationFrame = function(callback) {
    window.saved_callbacks.push(callback);
};

// Track tournament completion
const originalTriggerOverlay = window.triggerCanvasOverlay;
window.triggerCanvasOverlay = function(mode, sec, callback) {
    if (mode === 'champion') {
        window.champion_declared = true;
    }
    if (originalTriggerOverlay) {
        originalTriggerOverlay(mode, sec, callback);
    }
};

// Frame-stepping hack: advances physics and updates canvas by exactly 1 step
window.step_simulation_frame = function() {
    return new Promise((resolve) => {
        if (window.saved_callbacks.length > 0) {
            const cb = window.saved_callbacks.shift();
            window.current_frame_count++;
            
            // Step timestamp slightly ahead of 33.33ms (30 FPS) to guarantee physics update triggers
            cb(window.current_frame_count * 35); 
            
            const canvas = document.getElementById('physics-canvas');
            if (canvas) {
                // Export high-quality JPEG to minimize memory serialization overhead
                resolve({
                    img: canvas.toDataURL('image/jpeg', 0.82), 
                    champion: window.champion_declared,
                    frame: window.current_frame_count
                });
            } else {
                resolve({img: null, champion: false, frame: window.current_frame_count});
            }
        } else {
            resolve({img: null, champion: false, frame: window.current_frame_count});
        }
    });
};
"""

def render_html_to_4k_video():
    print("Step 1: Launching Headless Chromium with native hardware flags...")
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(TEMP_VIDEO_RAW, fourcc, FPS, (WIDTH, HEIGHT))
    
    sound_events = []
    total_frames = 0
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-gpu",
                "--enable-software-rasterizer",
                "--font-render-hinting=none"
            ]
        )
        
        # Open browser viewport matching 1080p standard ratios
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.add_init_script(JS_DETERMINISTIC_HOOK)
        
        print(f"Step 2: Loading Arena URL: {file_url}")
        page.goto(file_url)
        
        # Start simulation manual trigger
        page.evaluate("startGameManual()")
        print("Step 3: Initializing automated frame-by-frame high fidelity canvas capture...")
        
        start_time = time.time()
        while True:
            # Step browser canvas and get base64 screenshot data
            result = page.evaluate("window.step_simulation_frame()")
            if not result or not result["img"]:
                # Wait briefly if simulation engine is warming up
                time.sleep(0.1)
                continue
                
            img_b64 = result["img"].split(",")[1]
            is_champion = result["champion"]
            frame_num = result["frame"]
            
            # Decode JPEG binary buffer directly in memory (zero disk write lag!)
            img_data = base64.b64decode(img_b64)
            np_arr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            # Ensure the frame matches native 4K output size securely
            if frame.shape[1] != WIDTH or frame.shape[0] != HEIGHT:
                frame = cv2.resize(frame, (WIDTH, HEIGHT), interpolation=cv2.INTER_LANCZOS4)
                
            video_writer.write(frame)
            total_frames = frame_num
            
            # Console logger tracking (unbuffered outputs)
            if frame_num % 150 == 0:
                print(f"-> Captured {frame_num} frames... [Target: ~30 frames per second of video]", flush=True)
                
            if is_champion:
                print("🏆 Champion Declared! Capturing celebratory loop buffer (240 frames)...", flush=True)
                # Capture 8 seconds of celebration (240 frames at 30 FPS)
                for _ in range(240):
                    result = page.evaluate("window.step_simulation_frame()")
                    img_b64 = result["img"].split(",")[1]
                    img_data = base64.b64decode(img_b64)
                    np_arr = np.frombuffer(img_data, np.uint8)
                    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                    if frame.shape[1] != WIDTH or frame.shape[0] != HEIGHT:
                        frame = cv2.resize(frame, (WIDTH, HEIGHT), interpolation=cv2.INTER_LANCZOS4)
                    video_writer.write(frame)
                break
                
        # Gather captured audio events from JavaScript heap
        sound_events = page.evaluate("window.sound_events")
        browser.close()
        
    video_writer.release()
    print(f"Step 4: Visual render complete. Total frames saved: {total_frames} ({int(total_frames/FPS)} seconds of match)", flush=True)

    # --- AUDIO TIMELINE SYNTHESIS ---
    print("Step 5: Synthesizing HD sound effects track from physics events...", flush=True)
    sample_rate = 44100
    total_samples = int((total_frames + 240) / FPS * sample_rate)
    master_audio = np.zeros(total_samples, dtype=np.int16)
    
    for ev_frame, ev_type in sound_events:
        start_sample = int(ev_frame / FPS * sample_rate)
        if start_sample >= total_samples:
            continue
            
        wave_data = sound_wave_cache.get(ev_type)
        if wave_data is not None:
            end_sample = start_sample + len(wave_data)
            if end_sample < total_samples:
                master_audio[start_sample:end_sample] += wave_data

    with wave.open(TEMP_SFX_WAV, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(master_audio.tobytes())

    # --- FFMPEG MIXING & INTEGRATION ---
    print("Step 6: Merging High Fidelity Video, Music and SFX via FFmpeg...", flush=True)
    if os.path.exists(BGM_FILENAME):
        cmd = f'ffmpeg -y -i {TEMP_VIDEO_RAW} -i {TEMP_SFX_WAV} -i "{BGM_FILENAME}" -filter_complex "[1:a][2:a]amix=inputs=2:duration=first[a]" -map 0:v -map "[a]" -c:v libx264 -preset fast -crf 17 -pix_fmt yuv420p "{FINAL_OUTPUT_FILENAME}"'
    else:
        cmd = f'ffmpeg -y -i {TEMP_VIDEO_RAW} -i {TEMP_SFX_WAV} -c:v libx264 -preset fast -crf 17 -pix_fmt yuv420p "{FINAL_OUTPUT_FILENAME}"'

    try:
        subprocess.run(cmd, shell=True, check=True)
        # Clean temp media parts
        if os.path.exists(TEMP_SFX_WAV): os.remove(TEMP_SFX_WAV)
        if os.path.exists(TEMP_VIDEO_RAW): os.remove(TEMP_VIDEO_RAW)
        print(f"\n🎉 NATIVE 4K HIGH FIDELITY VIDEO COMPILED SUCCESSFULLY: {FINAL_OUTPUT_FILENAME}", flush=True)
    except Exception as e:
        print(f"Error during audio compilation: {e}", flush=True)

if __name__ == "__main__":
    render_html_to_4k_video()