# -*- coding: utf-8 -*-
"""
Beat the Keeper - Headless Widescreen 4K Screen Grabber (Real-Time)
Uses Xvfb virtual display server and FFmpeg x11grab to capture the HTML canvas 
natively in headed mode at true 4K (3840x2160) without any browser throttling.
"""

import os
import sys
import time
import subprocess
import wave
import numpy as np

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: 'playwright' is not installed! Installing on the fly...")
    sys.exit(1)

# --- VIDEO CONFIGURATION (TRUE NATIVE 4K ULTRA HD) ---
WIDTH, HEIGHT = 3840, 2160  # Native 4K Capture
FPS = 30
TEMP_VIDEO_RAW = "temp_raw_4k.mp4"
TEMP_SFX_WAV = "temp_sfx.wav"
FINAL_OUTPUT_FILENAME = "beat_the_keeper_final_video.mp4"
BGM_FILENAME = "Beat the Keeper - 50 Country Elimination Marble Race.m4a"

# Locate the HTML file
html_file = "beat_the_keeper_simulation_app.html"
if not os.path.exists(html_file):
    html_file = "index.html"

if not os.path.exists(html_file):
    print("Error: HTML template file not found!")
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

# --- JAVASCRIPT SOUND LOGGER HOOKS ---
JS_AUDIO_TRACK_HOOK = """
window.champion_declared = false;
window.sound_events = [];
window.start_time_stamp = null;

// Intercept playSound triggers and log exact elapsed seconds
window.playSound = function(type) {
    if (!window.start_time_stamp) {
        window.start_time_stamp = performance.now();
    }
    const elapsedSec = (performance.now() - window.start_time_stamp) / 1000;
    window.sound_events.push([elapsedSec, type]);
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
"""

def render_html_to_4k_screengrab():
    # 1. Start Xvfb Virtual Framebuffer Server at true 4K resolution
    print("Step 1: Spawning virtual 4K X11 frame-buffer server (:99)...", flush=True)
    xvfb_proc = subprocess.Popen([
        "Xvfb", ":99", "-screen", "0", "3840x2160x24", "+extension", "RANDR"
    ])
    
    # Expose DISPLAY env so Chromium & FFmpeg bind to the virtual monitor
    os.environ["DISPLAY"] = ":99"
    time.sleep(3.0)  # Wait for Xvfb server to successfully spin up
    
    # 2. Spawn FFmpeg process to capture the X11 screen directly to raw video stream
    print("Step 2: Starting FFmpeg x11grab at 4K 30 FPS...", flush=True)
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-f", "x11grab", "-video_size", "3840x2160",
        "-framerate", "30", "-i", ":99.0", "-c:v", "libx264",
        "-preset", "ultrafast", "-crf", "15", "-pix_fmt", "yuv420p", TEMP_VIDEO_RAW
    ]
    ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    sound_events = []
    total_match_seconds = 0
    
    try:
        with sync_playwright() as p:
            # 3. Launch headed Chromium inside the virtual monitor
            print("Step 3: Launching Chromium in kiosk mode...", flush=True)
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--start-fullscreen",
                    "--kiosk",
                    "--no-sandbox",
                    "--disable-infobars",
                    "--window-size=3840,2160"
                ]
            )
            
            page = browser.new_page(viewport={"width": 3840, "height": 2160})
            page.add_init_script(JS_AUDIO_TRACK_HOOK)
            
            # Go to URL
            page.goto(file_url)
            time.sleep(2.0)
            
            # Click manually to start
            page.evaluate("startGameManual()")
            print("Step 4: Simulation running! Monitoring match loop...", flush=True)
            
            start_wait_time = time.time()
            while True:
                time.sleep(2.0)
                is_winner = page.evaluate("window.champion_declared")
                if is_winner:
                    print("🏆 Grand Champion Crowned! Delaying capture for victory screen...", flush=True)
                    time.sleep(8.0)
                    break
                    
                elapsed = time.time() - start_wait_time
                if int(elapsed) % 60 < 2.0:
                    print(f"-> Captured {int(elapsed // 60)} minutes of 4K match video...", flush=True)
            
            # Retrieve generated sound events
            sound_events = page.evaluate("window.sound_events")
            total_match_seconds = time.time() - start_wait_time + 10.0
            
            browser.close()
            
    except Exception as error:
        print(f"An error occurred during Playwright simulation: {error}", flush=True)
        
    finally:
        # 4. Gracefully terminate video recording and display servers
        print("Step 5: Closing Virtual Monitor & FFmpeg capturer...", flush=True)
        try:
            ffmpeg_proc.stdin.write(b'q')  # Tell FFmpeg to stop recording cleanly
            ffmpeg_proc.stdin.flush()
            ffmpeg_proc.wait(timeout=10)
        except:
            ffmpeg_proc.terminate()
            
        xvfb_proc.terminate()
        xvfb_proc.wait()

    # --- AUDIO SYNTHESIS TIMELINE ---
    print("Step 6: Generating high fidelity audio track from logged collisions...", flush=True)
    sample_rate = 44100
    total_samples = int(total_match_seconds * sample_rate)
    master_audio = np.zeros(total_samples, dtype=np.int16)
    
    s_cache = {
        'bounce': gen_sound_wave(0.08, lambda t: np.sin(2 * np.pi * 320 * t), lambda t: np.exp(-12 * t)),
        'kick': gen_sound_wave(0.16, lambda t: np.sin(2 * np.pi * np.geomspace(140, 45, len(t)) * t), lambda t: np.exp(-8 * t)),
        'goal': gen_sound_wave(0.35, lambda t: (np.sin(2 * np.pi * 523 * t) + np.sin(2 * np.pi * 659 * t) + np.sin(2 * np.pi * 784 * t)) / 3.0, lambda t: np.exp(-4 * t)),
        'fail': gen_sound_wave(0.25, lambda t: np.sin(2 * np.pi * 100 * t), lambda t: np.exp(-5 * t))
    }
    
    for ev_sec, ev_type in sound_events:
        start_sample = int(ev_sec * sample_rate)
        if start_sample >= total_samples:
            continue
        wave_data = s_cache.get(ev_type)
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
    print("Step 7: Merging Raw Video, Music and SFX via FFmpeg...", flush=True)
    if os.path.exists(BGM_FILENAME):
        cmd = f'ffmpeg -y -i {TEMP_VIDEO_RAW} -i {TEMP_SFX_WAV} -i "{BGM_FILENAME}" -filter_complex "[1:a][2:a]amix=inputs=2:duration=first[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k "{FINAL_OUTPUT_FILENAME}"'
    else:
        cmd = f'ffmpeg -y -i {TEMP_VIDEO_RAW} -i {TEMP_SFX_WAV} -c:v copy -c:a aac -b:a 192k "{FINAL_OUTPUT_FILENAME}"'

    try:
        subprocess.run(cmd, shell=True, check=True)
        # Clean temp media parts
        if os.path.exists(TEMP_SFX_WAV): os.remove(TEMP_SFX_WAV)
        if os.path.exists(TEMP_VIDEO_RAW): os.remove(TEMP_VIDEO_RAW)
        print(f"\n🎉 NATIVE 4K HIGH FIDELITY VIDEO COMPILED SUCCESSFULLY: {FINAL_OUTPUT_FILENAME}", flush=True)
    except Exception as e:
        print(f"Error during audio compilation: {e}", flush=True)

if __name__ == "__main__":
    render_html_to_4k_screengrab()