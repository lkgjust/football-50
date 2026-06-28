# -*- coding: utf-8 -*-
"""
Beat the Keeper - Headless 30 FPS Offline 4K Video Generator with Auto Audio Synthesis
Optimized for 100% stable execution on GitHub Actions runner.
"""

import os
import math
import random
import subprocess
import wave
import numpy as np
import cv2
import pymunk
from PIL import Image, ImageDraw, ImageFont

# --- VIDEO & AUDIO CONFIGURATION (NATIVELY OPTIMIZED FOR CRISTAL CLEAR 4K) ---
WIDTH, HEIGHT = 3840, 2160  # Native 4K Ultra HD
FPS = 30
TEMP_VIDEO_RAW = "temp_raw_4k.mp4"
TEMP_SFX_WAV = "temp_sfx.wav"
FINAL_OUTPUT_FILENAME = "beat_the_keeper_final_video.mp4"
BGM_FILENAME = "Beat the Keeper - 50 Country Elimination Marble Race.m4a"

# --- PHYSICS CONSTANTS ---
GRAVITY = 1.30 * 60.0 * 60.0  # Synced scale gravity
BALL_RADIUS = 45  # True 4K sphere radius

# --- 50 COUNTRIES DATASET ---
COUNTRIES_DATA = [
    {"name": "Argentina", "code": "AR", "colors": ["#74ACDF", "#FFFFFF", "#F6B426"]},
    {"name": "Australia", "code": "AU", "colors": ["#00008B", "#FF0000", "#FFFFFF"]},
    {"name": "Austria", "code": "AT", "colors": ["#ED2939", "#FFFFFF", "#ED2939"]},
    {"name": "Belgium", "code": "BE", "colors": ["#000000", "#FDE100", "#EB2D3F"]},
    {"name": "Brazil", "code": "BR", "colors": ["#009739", "#FEDF00", "#002776"]},
    {"name": "Canada", "code": "CA", "colors": ["#FF0000", "#FFFFFF", "#FF0000"]},
    {"name": "Chile", "code": "CL", "colors": ["#00209F", "#FFFFFF", "#D52B1E"]},
    {"name": "China", "code": "CN", "colors": ["#DE2910", "#FFDE00", "#DE2910"]},
    {"name": "Colombia", "code": "CO", "colors": ["#FCD116", "#003893", "#CE1126"]},
    {"name": "Croatia", "code": "HR", "colors": ["#FF0000", "#FFFFFF", "#171796"]},
    {"name": "Denmark", "code": "DK", "colors": ["#C60C30", "#FFFFFF", "#C60C30"]},
    {"name": "Egypt", "code": "EG", "colors": ["#C1272D", "#FFFFFF", "#000000"]},
    {"name": "Finland", "code": "FI", "colors": ["#FFFFFF", "#002F6C", "#FFFFFF"]},
    {"name": "France", "code": "FR", "colors": ["#00209F", "#FFFFFF", "#F81A2D"]},
    {"name": "Germany", "code": "DE", "colors": ["#000000", "#FF0000", "#FFCC00"]},
    {"name": "Greece", "code": "GR", "colors": ["#005BA6", "#FFFFFF", "#005BA6"]},
    {"name": "Iceland", "code": "IS", "colors": ["#003897", "#D7282F", "#FFFFFF"]},
    {"name": "India", "code": "IN", "colors": ["#FF9933", "#FFFFFF", "#138808"]},
    {"name": "Indonesia", "code": "ID", "colors": ["#FF0000", "#FFFFFF", "#FF0000"]},
    {"name": "Ireland", "code": "IE", "colors": ["#169B62", "#FFFFFF", "#FF883E"]},
    {"name": "Italy", "code": "IT", "colors": ["#009246", "#FFFFFF", "#CE2B37"]},
    {"name": "Jamaica", "code": "JM", "colors": ["#FED100", "#009B3A", "#000000"]},
    {"name": "Japan", "code": "JP", "colors": ["#FFFFFF", "#BC002D", "#FFFFFF"]},
    {"name": "Kenya", "code": "KE", "colors": ["#000000", "#BB0000", "#006600"]},
    {"name": "Mexico", "code": "MX", "colors": ["#006847", "#FFFFFF", "#CE1126"]},
    {"name": "Morocco", "code": "MA", "colors": ["#C1272D", "#006233", "#C1272D"]},
    {"name": "Netherlands", "code": "NL", "colors": ["#AE1C28", "#FFFFFF", "#21468B"]},
    {"name": "New Zealand", "code": "NZ", "colors": ["#00008B", "#FF0000", "#FFFFFF"]},
    {"name": "Nigeria", "code": "NG", "colors": ["#008751", "#FFFFFF", "#008751"]},
    {"name": "Norway", "code": "NO", "colors": ["#EF2B2D", "#00205B", "#FFFFFF"]},
    {"name": "Pakistan", "code": "PK", "colors": ["#00401A", "#FFFFFF", "#00401A"]},
    {"name": "Peru", "code": "PE", "colors": ["#D91414", "#FFFFFF", "#D91414"]},
    {"name": "Philippines", "code": "PH", "colors": ["#0038A8", "#CE1126", "#FFFFFF"]},
    {"name": "Poland", "code": "PL", "colors": ["#FFFFFF", "#DC143C", "#FFFFFF"]},
    {"name": "Portugal", "code": "PT", "colors": ["#046A38", "#DA291C", "#DA291C"]},
    {"name": "Romania", "code": "RO", "colors": ["#002B7F", "#FCD116", "#CE1126"]},
    {"name": "Russia", "code": "RU", "colors": ["#FFFFFF", "#0039A6", "#D52B1E"]},
    {"name": "Saudi Arabia", "code": "SA", "colors": ["#006C35", "#FFFFFF", "#006C35"]},
    {"name": "South Africa", "code": "ZA", "colors": ["#E03C31", "#007A4D", "#002395"]},
    {"name": "South Korea", "code": "KR", "colors": ["#FFFFFF", "#CD2E3A", "#0F4C81"]},
    {"name": "Spain", "code": "ES", "colors": ["#C11B17", "#FCD116", "#C11B17"]},
    {"name": "Sweden", "code": "SE", "colors": ["#006AA7", "#FECC00", "#006AA7"]},
    {"name": "Switzerland", "code": "CH", "colors": ["#D52B1E", "#FFFFFF", "#D52B1E"]},
    {"name": "Thailand", "code": "TH", "colors": ["#A51931", "#F4F5F7", "#2D2A4A"]},
    {"name": "Turkey", "code": "TR", "colors": ["#E30A17", "#FFFFFF", "#E30A17"]},
    {"name": "Ukraine", "code": "UA", "colors": ["#0057B7", "#FFD700", "#0057B7"]},
    {"name": "United Kingdom", "code": "GB", "colors": ["#00247D", "#CF142B", "#FFFFFF"]},
    {"name": "United States", "code": "US", "colors": ["#3C3B6E", "#B22234", "#FFFFFF"]},
    {"name": "Uruguay", "code": "UY", "colors": ["#0038A8", "#FFFFFF", "#FCD116"]},
    {"name": "Vietnam", "code": "VN", "colors": ["#DA251D", "#FFFF00", "#DA251D"]}
]

# State variables
current_round = 1
round_targets = [40, 30, 20, 10, 8, 6, 4, 2, 1]
active_marbles = []
survivors = []
eliminated = []
live_logs = ["System Initialized - Headless 4K Engine Ready"]

# Gradual spawning queue
spawn_queue = []
last_spawn_time = 0.0

# Audio event logger
sound_events = []

# Video Writer for native 4K MP4
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(TEMP_VIDEO_RAW, fourcc, FPS, (WIDTH, HEIGHT))

# Initialize Pymunk Space
space = pymunk.Space()
space.gravity = (0, GRAVITY)

# Helper function for point to line segment distance
def dist_to_segment(px, py, ax, ay, bx, by):
    ab_x, ab_y = bx - ax, by - ay
    ap_x, ap_y = px - ax, py - ay
    ab_len_sq = ab_x**2 + ab_y**2
    if ab_len_sq == 0:
        return math.sqrt(ap_x**2 + ap_y**2)
    t = max(0.0, min(1.0, (ap_x * ab_x + ap_y * ab_y) / ab_len_sq))
    closest_x = ax + t * ab_x
    closest_y = ay + t * ab_y
    return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)

# --- 4K MAP STATIC OBJECTS ---
# Outer bounds
left_wall = pymunk.Segment(space.static_body, (535, 0), (535, 2160), 10)
right_wall = pymunk.Segment(space.static_body, (2955, 0), (2955, 2160), 10)
left_wall.elasticity = 0.5; right_wall.elasticity = 0.5
space.add(left_wall, right_wall)

# Top Slope
top_slope = pymunk.Segment(space.static_body, (940, 130), (2955, 240), 15)
top_slope.elasticity = 0.4
space.add(top_slope)

# Divider Chute
chute_divider = pymunk.Segment(space.static_body, (940, 130), (940, 2095), 15)
chute_divider.elasticity = 0.3
space.add(chute_divider)

# Plinko Pegs
pegs_coords = [
    (687, 512), (782, 725), (687, 938), (782, 1151), (687, 1364), (782, 1577)
]
for px, py in pegs_coords:
    peg = pymunk.Circle(space.static_body, BALL_RADIUS + 3, (px, py))
    peg.elasticity = 0.95
    space.add(peg)

# Rounded corner segments (Radius = 50)
R_corner = 50
for i in range(13):
    alpha = (i / 12.0) * (math.pi / 2.0)
    lcx = 535 + R_corner - R_corner * math.cos(alpha)
    lcy = 2095 - R_corner + R_corner * math.sin(alpha)
    space.add(pymunk.Circle(space.static_body, 6, (lcx, lcy)))
    
    rcx = 940 - R_corner + R_corner * math.cos(alpha)
    rcy = 2095 - R_corner + R_corner * math.sin(alpha)
    space.add(pymunk.Circle(space.static_body, 6, (rcx, rcy)))

# Boot spinner joint
spinner_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
spinner_body.position = (728, 1995)
space.add(spinner_body)

# Goalkeepers
defenderSweeper = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
sweeper_shape = pymunk.Poly.create_box(defenderSweeper, (70, 220))
defenderSweeper.position = (1365, 1810)
space.add(defenderSweeper, sweeper_shape)

defenderJumper = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
jumper_shape = pymunk.Poly.create_box(defenderJumper, (110, 320))
defenderJumper.position = (1825, 1230)
space.add(defenderJumper, jumper_shape)

defenderGoalie = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
goalie_shape = pymunk.Poly.create_box(defenderGoalie, (80, 240))
defenderGoalie.position = (2503, 1740)
space.add(defenderGoalie, goalie_shape)

# Tall Goal structures
goal_top = pymunk.Segment(space.static_body, (2625, 1100), (2955, 1160), 15)
goal_left_wall = pymunk.Segment(space.static_body, (2625, 1100), (2625, 2095), 15)
space.add(goal_top, goal_left_wall)

ground_left = pymunk.Segment(space.static_body, (940, 2095), (1834, 2095), 15)
ground_right = pymunk.Segment(space.static_body, (2325, 2095), (2955, 2095), 15)
space.add(ground_left, ground_right)

class CountryMarble:
    def __init__(self, data):
        self.data = data
        self.name = data["name"]
        self.code = data["code"]
        self.colors = data["colors"]
        self.status = "racing"
        self.eliminated_round = 0
        self.trail = []
        
        self.last_peg_hits = {}
        self.last_defender_hits = {}
        self.last_spinner_hit = 0
        
        # Spawn
        mass = 1.0
        moment = pymunk.moment_for_circle(mass, 0, BALL_RADIUS)
        self.body = pymunk.Body(mass, moment)
        self.body.position = (2905, 60)
        self.shape = pymunk.Circle(self.body, BALL_RADIUS)
        self.shape.elasticity = 0.95
        self.shape.friction = 0.005
        space.add(self.body, self.shape)

# Cache Fonts with safety fallback
try:
    font_large = ImageFont.truetype("LiberationSans-Bold.ttf", 68)
    font_medium = ImageFont.truetype("LiberationSans-Bold.ttf", 48)
    font_small = ImageFont.truetype("LiberationSans-Bold.ttf", 36)
    font_mono = ImageFont.truetype("LiberationMono-Regular.ttf", 42)
    font_standings = ImageFont.truetype("LiberationSans-Bold.ttf", 36)
    font_badge = ImageFont.truetype("LiberationMono-Bold.ttf", 26)
except IOError:
    font_large = ImageFont.load_default()
    font_medium = font_large
    font_small = font_large
    font_mono = font_large
    font_standings = font_large
    font_badge = font_large

# Pre-render 4K country flags exactly once to avoid memory bottleneck
flag_cache = {}
def pre_render_flags():
    for c in COUNTRIES_DATA:
        flag_img = Image.new("RGBA", (BALL_RADIUS*2, BALL_RADIUS*2), (0,0,0,0))
        f_draw = ImageDraw.Draw(flag_img)
        r = BALL_RADIUS
        
        f_draw.ellipse([0, 0, r*2, r*2], fill=c["colors"][0])
        f_draw.rectangle([0, int(r*0.66), r*2, int(r*1.33)], fill=c["colors"][1])
        if len(c["colors"]) > 2:
            f_draw.rectangle([0, int(r*1.33), r*2, r*2], fill=c["colors"][2])
        else:
            f_draw.rectangle([0, int(r*1.33), r*2, r*2], fill=c["colors"][0])
            
        f_draw.ellipse([0, 0, r*2, r*2], outline="#ffffff", width=4)
        f_draw.text((r, r), c["code"], fill="#ffffff", font=font_small, anchor="mm")
        flag_cache[c["code"]] = flag_img

pre_render_flags()

def draw_proportional_footballer(image, px, py, w, h, shirt_col, pants_col):
    f_draw = ImageDraw.Draw(image)
    head_r = int(h * 0.10)
    head_y = int(py - h/2 + head_r)
    f_draw.ellipse([px - head_r, head_y - head_r, px + head_r, head_y + head_r], fill="#d1a080")
    f_draw.chord([px - int(head_r*1.1), head_y - int(head_r*1.1) - int(h*0.03), px + int(head_r*1.1), head_y + int(head_r*0.9)], 180, 360, fill="#2d1a0a")
    f_draw.rectangle([px - w//2, int(py - h/2 + h*0.20), px + w//2, int(py - h/2 + h*0.56)], fill=shirt_col)
    f_draw.rectangle([px - w//2, int(py - h/2 + h*0.56), px + w//2, int(py - h/2 + h*0.71)], fill=pants_col)
    leg_w = int(w * 0.28)
    f_draw.rectangle([px - int(w*0.35), int(py - h/2 + h*0.71), px - int(w*0.35) + leg_w, int(py - h/2 + h*0.88)], fill="#d1a080")
    f_draw.rectangle([px + int(w*0.35) - leg_w, int(py - h/2 + h*0.71), px + int(w*0.35), int(py - h/2 + h*0.88)], fill="#d1a080")
    f_draw.rectangle([px - int(w*0.42), int(py - h/2 + h*0.88), px - int(w*0.42) + int(w*0.36), int(py + h/2)], fill="#3b82f6")
    f_draw.rectangle([px + int(w*0.42) - int(w*0.36), int(py - h/2 + h*0.88), px + int(w*0.42), int(py + h/2)], fill="#3b82f6")

def spawn_marbles_for_round():
    global active_marbles, survivors, spawn_queue
    survivors = []
    for m in active_marbles:
        try: space.remove(m.body, m.shape)
        except: pass
    active_marbles = []
    racing_countries = [c for c in COUNTRIES_DATA if c.get("status", "racing") == "racing"]
    random.shuffle(racing_countries)
    spawn_queue = list(racing_countries)
    add_log(f"Round {current_round} Started - {len(racing_countries)} Countries on Track!")

def add_log(msg):
    global live_logs
    live_logs.append(msg)
    if len(live_logs) > 15: live_logs.pop(0)

spawn_marbles_for_round()
sim_time = 0.0
frame_count = 0
round_frame_counter = 0
ROUND_TIMEOUT_FRAMES = 2700  # 90 seconds timeout at 30 FPS

# --- HIGH-QUALITY SFX WAVE SYNTHESIS CODES ---
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

# --- MAIN AUTOMATED RENDER LOOP ---
while current_round <= 9:
    frame_count += 1
    round_frame_counter += 1
    
    # Decouple physics step to keep simulation rock-stable (2 physics ticks per 30fps frame)
    for _ in range(2):
        sim_time += 0.0166
        
        # Gradual Spawning
        if len(spawn_queue) > 0 and (round_frame_counter * 2) % 10 == 0:
            c_data = spawn_queue.pop(0)
            active_marbles.append(CountryMarble(c_data))
            
        # Rotate Boot Spinner
        spinner_body.angle += 0.055
        
        # Animate goalkeeper defenders
        sweeper_y = 1750 + math.sin(sim_time * 2.0) * 150
        defenderSweeper.position = (1365, sweeper_y)
        
        jumper_y = 1680 + math.sin(sim_time * 1.8) * 255
        defenderJumper.position = (1825, jumper_y)
        
        goalie_y = 1720 + math.sin(sim_time * 2.4) * 200
        defenderGoalie.position = (2503, goalie_y)
        
        # Update physics world state
        space.step(1.0 / 60.0)

    # Spinner geometry boundaries calculation for frame collision
    cx, cy = 728, 1995
    L = 115
    arm_ends = []
    for idx in range(4):
        arm_angle = spinner_body.angle + idx * (math.pi / 2.0)
        arm_ends.append((cx + L * math.cos(arm_angle), cy + L * math.sin(arm_angle)))

    target_survivor_limit = round_targets[current_round - 1]

    # --- SIMULATED FRAME COLLISION DETECTION ---
    for m in list(active_marbles):
        pos = m.body.position
        m.trail.append((pos.x, pos.y))
        if len(m.trail) > 8: m.trail.pop(0)
        
        # Out of bounds reset
        if pos.y > 2220 or pos.x < 535 or pos.x > 2955:
            m.body.position = (2725 + random.randint(-50, 50), 60)
            m.body.velocity = (-200, 150)
            
        # Stuck prevention
        if pos.x < 940 and pos.y > 1650 and abs(m.body.velocity.x) < 5.0:
            m.body.velocity = (400, -350)
            
        # Spinner kick collision
        for end_x, end_y in arm_ends:
            dist = dist_to_segment(pos.x, pos.y, cx, cy, end_x, end_y)
            if dist < (BALL_RADIUS + 12):
                if frame_count - m.last_spinner_hit > 15:
                    m.body.velocity = (3480 + random.randint(-150, 150), -1440 - random.randint(-50, 50))
                    sound_events.append((frame_count, 'kick'))
                    m.last_spinner_hit = frame_count
                break
                
        # Peg bounce collision
        for p_idx, p_coord in enumerate(pegs_coords):
            px, py = p_coord
            dist = math.sqrt((pos.x - px)**2 + (pos.y - py)**2)
            if dist < (BALL_RADIUS + 15):
                last_hit = m.last_peg_hits.get(p_idx, 0)
                if frame_count - last_hit > 10:
                    sound_events.append((frame_count, 'bounce'))
                    m.last_peg_hits[p_idx] = frame_count

        # Defenders block collision
        defenders_list = [
            ('sweeper', defenderSweeper, 70, 220),
            ('jumper', defenderJumper, 110, 320),
            ('goalie', defenderGoalie, 80, 240)
        ]
        for name, d_body, dw, dh in defenders_list:
            dx = abs(pos.x - d_body.position.x)
            dy = abs(pos.y - d_body.position.y)
            if dx < (dw/2 + BALL_RADIUS) and dy < (dh/2 + BALL_RADIUS):
                last_hit = m.last_defender_hits.get(name, 0)
                if frame_count - last_hit > 15:
                    sound_events.append((frame_count, 'fail'))
                    m.last_defender_hits[name] = frame_count
                    
        # Check Goal Target
        if pos.x > 2625 and pos.x < 2955 and pos.y > 1100 and pos.y < 2095:
            if m not in survivors:
                if len(survivors) < target_survivor_limit:
                    survivors.append(m)
                    m.status = "survived"
                    add_log(f"⚽ {m.name} survived Round {current_round}!")
                    sound_events.append((frame_count, 'goal'))
                    space.remove(m.body, m.shape)
                    active_marbles.remove(m)
                else:
                    m.body.position = (2725 + random.randint(-50, 50), 60)
                    
        # Pit reset
        if pos.x > 1834 and pos.x < 2325 and pos.y > 2050:
            m.body.position = (2725 + random.randint(-50, 50), 60)
            m.body.velocity = (-8, 4)

    # --- ROUND TRANSITIONS LOGIC ---
    if len(survivors) >= target_survivor_limit or round_frame_counter >= ROUND_TIMEOUT_FRAMES:
        # Eliminate trailing ones
        for c in COUNTRIES_DATA:
            if c.get("status") == "racing":
                if not any(s.code == c["code"] for s in survivors):
                    c["status"] = "eliminated"
                    c["eliminated_round"] = current_round
                    eliminated.append(c)
                    
        for s in survivors:
            for c in COUNTRIES_DATA:
                if c["code"] == s.code:
                    c["status"] = "racing"
                    
        add_log(f"Round {current_round} Completed!")
        
        # Write static summary frames (3 seconds at 30 FPS = 90 frames)
        for _ in range(90):
            img = Image.new("RGBA", (WIDTH, HEIGHT), (15, 23, 42, 255))
            draw = ImageDraw.Draw(img)
            
            draw.text((WIDTH//2, 100), f"ROUND {current_round} OUTCOME SUMMARY", fill="#ffffff", font=font_large, anchor="mm")
            draw.text((WIDTH//2, 190), f"Safe: {len(survivors)}  |  Eliminated: {len(eliminated)}", fill="#fbbf24", font=font_medium, anchor="mm")
            
            # Safe list
            draw.text((150, 280), "SAFE COUNTRIES:", fill="#34d399", font=font_medium)
            for idx, c in enumerate(survivors):
                cx = 150 + (idx % 15) * 110
                cy = 380 + (idx // 15) * 110
                flag_thumbnail = flag_cache[c.code].resize((80, 80))
                img.paste(flag_thumbnail, (cx - 40, cy - 40), flag_thumbnail)
                
            # Elim list
            draw.text((150, 680), "ELIMINATED COUNTRIES:", fill="#f87171", font=font_medium)
            for idx, c in enumerate(eliminated[-15:]):
                cx = 150 + (idx % 15) * 110
                cy = 780
                flag_thumbnail = flag_cache[c["code"]].resize((80, 80))
                img.paste(flag_thumbnail, (cx - 40, cy - 40), flag_thumbnail)
                
            draw.text((WIDTH//2, 1000), "Preparing next round in 3 seconds...", fill="#64748b", font=font_small, anchor="mm")
            
            opencv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGR)
            video_writer.write(opencv_image)
            
        current_round += 1
        round_frame_counter = 0
        if current_round <= 9:
            spawn_marbles_for_round()
            continue
            
    # --- RASTEURIZE AND DRAW 4K IMAGES ---
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    
    # Left Box
    draw.rectangle([0, 0, 525, HEIGHT], fill=(15, 23, 42, 230), outline=(30, 41, 59, 255), width=5)
    draw.text((262, 80), "MATCH TELEMETRY", fill="#ffffff", font=font_medium, anchor="mm")
    
    target_count = round_targets[current_round - 1]
    elim_count = (round_targets[current_round - 2] if current_round > 1 else 50) - target_count
    
    draw.text((262, 185), f"TARGET: {round_targets[current_round-2] if current_round > 1 else 50} ➔ {target_count} SAFE", fill="#fbbf24", font=font_medium, anchor="mm")
    draw.text((262, 230), f"(ELIMINATING {elim_count} COUNTRIES)", fill="#fbbf24", font=font_small, anchor="mm")
    
    for idx, log in enumerate(live_logs):
        draw.text((50, 305 + idx * 60), log, fill="#cbd5e1", font=font_small)

    # Right standings (2 symmetric columns)
    draw.rectangle([2965, 0, WIDTH, HEIGHT], fill=(15, 23, 42, 230), outline=(30, 41, 59, 255), width=5)
    draw.text((3402, 80), "STANDINGS", fill="#ffffff", font=font_medium, anchor="mm")
    
    for idx, c in enumerate(COUNTRIES_DATA):
        col = idx // 25
        row = idx % 25
        ly = 195 + row * 76
        
        if col == 0:
            fx, nx, status_x = 3003, 3040, 3384
        else:
            fx, nx, status_x = 3428, 3467, 3828
            
        status_label = "RACING"
        badge_color = "#94a3b8"
        if c.get("status") == "eliminated":
            status_label = f"OUT R{c['eliminated_round']}"
            badge_color = "#f87171"
        elif any(s.code == c["code"] for s in survivors):
            status_label = "SAFE"
            badge_color = "#34d399"
            
        flag_icon = flag_cache[c["code"]]
        small_icon = flag_icon.resize((36, 36))
        img.paste(small_icon, (fx - 18, ly - 18), small_icon)
        
        draw.text((nx, ly), c["name"][:11], fill="#f1f5f9", font=font_standings, anchor="lm")
        # Pristine Roboto 26px matching Font Badge specification
        draw.text((status_x, ly), status_label, fill=badge_color, font=font_badge, anchor="rm")

    # Static Pegs and boundaries
    for p_coord in pegs_coords:
        px, py = p_coord
        draw.ellipse([px - 30, py - 30, px + 30, py + 30], fill="#555555", outline="#333333", width=6)

    # Draw spinner blades
    for end_x, end_y in arm_ends:
        draw.line([(cx, cy), (end_x, end_y)], fill="#2563eb", width=18)
        draw.ellipse([end_x - 14, end_y - 14, end_x + 14, end_y + 14], fill="#ffffff")

    # Draw rolling marbles with trails
    for m in active_marbles:
        mx, my = int(m.body.position.x), int(m.body.position.y)
        for t_idx, trail_p in enumerate(m.trail):
            alpha = int((t_idx + 1) / len(m.trail) * 180)
            draw.ellipse([trail_p[0] - 18, trail_p[1] - 18, trail_p[0] + 18, trail_p[1] + 18], fill=(255, 255, 255, alpha))
        
        flag_img = flag_cache[m.code]
        img.paste(flag_img, (mx - BALL_RADIUS, my - BALL_RADIUS), flag_img)

    # Survivors Box
    draw.rectangle([1145, 140, 2345, 340], fill=(0, 0, 0, 255), outline=(30, 41, 59, 255), width=8)
    draw.text((1745, 95), "Survivors Box", fill="#22c55e", font=font_medium, anchor="mm")
    
    for idx, c in enumerate(survivors):
        col = idx % 20
        row = idx // 20
        fsx = 1190 + col * 58
        fsy = 195 + row * 60
        flag_icon = flag_cache[c.code]
        small_icon = flag_icon.resize((36, 36))
        img.paste(small_icon, (fsx - 18, fsy - 18), small_icon)
        
    draw.text((1745, 410), f"Spots left: {target_count - len(survivors)}", fill="#ffffff", font=font_large, anchor="mm")

    # Draw Goalies
    sw_x, sw_y = int(defenderSweeper.position.x), int(defenderSweeper.position.y)
    draw_proportional_footballer(img, sw_x, sw_y, 70, 220, '#10b981', '#047857')
    ju_x, ju_y = int(defenderJumper.position.x), int(defenderJumper.position.y)
    draw_proportional_footballer(img, ju_x, ju_y, 110, 320, '#2563eb', '#1e40af')
    go_x, go_y = int(defenderGoalie.position.x), int(defenderGoalie.position.y)
    draw_proportional_footballer(img, go_x, go_y, 80, 240, '#a855f7', '#7e22ce')

    draw.rectangle([2625, 1100, 2955, 2065], outline="#ffffff", width=8)
    draw.rectangle([940, 2095, 1834, 2160], fill="#22c55e")
    draw.rectangle([2325, 2095, 2955, 2160], fill="#22c55e")

    # Draw Timer clock HUD
    total_sec = frame_count // FPS
    hrs = total_sec // 3600
    mins = (total_sec % 3600) // 60
    secs = total_sec % 60
    clock_str = f"Elapsed Time: {hrs:02d}:{mins:02d}:{secs:02d}"
    draw.text((WIDTH - 550, 40), clock_str, fill="#34d399", font=font_medium)

    # Frame output
    opencv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGR)
    video_writer.write(opencv_image)
    
    if frame_count % 300 == 0:
        print(f"Progression: Round {current_round}/9 | Captured {frame_count} frames | Time: {hrs:02d}:{mins:02d}:{secs:02d}")

video_writer.release()
print("Success! Visual rendering complete. Starting Audio Track synthesis...")

# --- HIGH-QUALITY SYNTHETIC AUDIO ENGINE ---
try:
    sample_rate = 44100
    total_samples = int((frame_count / FPS) * sample_rate)
    master_audio = np.zeros(total_samples, dtype=np.int16)
    
    # Generate audio segments
    for ev_frame, ev_type in sound_events:
        start_sample = int((ev_frame / FPS) * sample_rate)
        if start_sample >= total_samples: continue
        
        wave_data = sound_wave_cache[ev_type]
        end_sample = start_sample + len(wave_data)
        if end_sample < total_samples:
            master_audio[start_sample:end_sample] += wave_data
            
    with wave.open(TEMP_SFX_WAV, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(master_audio.tobytes())
        
    print("Step 5: Merging Video, Music, and Synthesized SFX via FFmpeg...")
    if os.path.exists(BGM_FILENAME):
        cmd = f'ffmpeg -y -i {TEMP_VIDEO_RAW} -i {TEMP_SFX_WAV} -i "{BGM_FILENAME}" -filter_complex "[1:a][2:a]amix=inputs=2:duration=first[a]" -map 0:v -map "[a]" -c:v libx264 -preset fast -crf 18 -r 30 "{FINAL_OUTPUT_FILENAME}"'
    else:
        cmd = f'ffmpeg -y -i {TEMP_VIDEO_RAW} -i {TEMP_SFX_WAV} -c:v libx264 -preset fast -crf 18 -r 30 "{FINAL_OUTPUT_FILENAME}"'

    subprocess.run(cmd, shell=True, check=True)
    if os.path.exists(TEMP_SFX_WAV): os.remove(TEMP_SFX_WAV)
    if os.path.exists(TEMP_VIDEO_RAW): os.remove(TEMP_VIDEO_RAW)
    print(f"\n🎉 4K VIDEO COMPILED SUCCESSFULLY: {FINAL_OUTPUT_FILENAME}")
except Exception as e:
    print(f"Error during audio compilation: {e}")