# 🔥 BLAZE Audio Visualizer — Next-Gen EDM & Audio Engine

A high-performance real-time audio visualizer in Python, featuring **BLAZE Ears 2.0 (Cyber Feline)**, **Blaze Fire Spikes**, **Trap Nation**, **Monstercat**, **Cyber Skyline**, and more.

It automatically captures your PC's audio output (YouTube, Spotify, games, media players), performs real-time Fast Fourier Transform (FFT) analysis, extracts bass transients, and renders a 60 FPS neon visualizer with dynamic ear physics, custom backgrounds, bass screen vibration, and glowing particle bursts.

---

## 🚀 Quick Start

### 1. Requirements
```bash
pip install numpy sounddevice scipy PyQt6
```

### 2. Run the Visualizer
```bash
cd c:\python_visualizer
python visualizer.py
```

Now play any track or video on your PC (YouTube, Spotify, SoundCloud) — the visualizer will instantly detect the audio and pulse to the music in real time!

---

## 🎮 Keyboard Controls & Shortcuts

| Key | Action | Description |
| :---: | :---: | :--- |
| **`V` / `C`** | **Switch Style** | Cycles through **10 Visualizer Styles** (Forward with `V`, backward with `C` or `Shift+V`) |
| **`T`** | **Switch Theme** | Cycles through **10 Curated Color Themes** (Blaze Inferno, UK Rave, Monochrome B&W, Cyberpunk, etc.) |
| **`B`** | **Custom Wallpaper** | Select any custom background image (`.jpg`, `.png`, `.webp`, `.bmp`) |
| **`S`** | **Bass Shake Intensity** | Cycles camera vibration / recoil: **Heavy**, **Intense (Earthquake)**, **Subtle**, and **Off** |
| **`O`** | **Dark Overlay Tint** | Cycles background dimness (45%, 65%, 85%, 25%, 0%) for maximum visualizer contrast |
| **`L`** | **Center Logo / Badge** | Select custom center logo/album art or toggle default **BLAZE** cyber emblem |
| **`D`** | **Switch Audio Device** | Cycles between Stereo Mix, WASAPI Loopback, and Microphone inputs |
| **`F`** | **Open Audio File** | Opens a file picker dialog to play and visualize local audio (`.wav`, `.flac`, `.mp3`) |
| **`F11`** | **Toggle Fullscreen** | Expands the visualizer to an immersive full-screen mode |
| **`H`** | **Toggle HUD** | Shows / hides the glassmorphic status overlay |
| **`SPACE`** | **Pause / Reconnect** | Pauses file playback or re-triggers live audio stream sync |
| **`ESC`** | **Exit** | Quits the visualizer application |

---

## 🌟 10 Visualizer Styles

1. **Blaze Ears 2.0 (Cyber Feline)**: Fully dynamic audio-reactive cat ears with twitch reflex, perk kinematics, inner acoustic neon ribs, multi-layer bloom, and ear-tip spark emitters.
2. **Blaze Fire Spikes (Solar Flare)**: Turbulent blazing plasma bursts and fiery flame needles bursting with audio energy.
3. **Bass Pulse Ring (Trap Nation)**: 360 radial high-density impulse rods with exponential bass extrusion.
4. **Dual Spectrum Arc (Monstercat)**: Symmetrical dual upper-semicircle equalizer towers.
5. **Horizon Double Mirror (Cyber Skyline)**: Mirrored dual horizontal spectrum with neon reflection floor and peak beads.
6. **Vortex Wormhole (3D Audio Tunnel)**: Concentric pulsating depth rings that warp and zoom into the beat in 3D.
7. **Hexagon Cyber Shield (Matrix Pulse)**: Futuristic geometric hexagon with edge equalizers and corner energy nodes.
8. **Oscilloscope Laser (Lightning Wave)**: High-voltage neon laser beam waveform with transient sparks.
9. **Smooth Waveform 360**: Continuous fluid 360-degree organic wave with multi-stop conical gradient.
10. **Radial Equalizer Bars**: Dense 360 radial frequency bars with conical color sweep.

---

## 🎨 10 Curated Color Themes

1. **Blaze Inferno**: Molten neon orange, solar gold, crimson fire, and white-hot flame core.
2. **UK Rave / Acid Underground**: Electric acid lime (`#39ff14`), toxic yellow, rave purple, and neon cyan.
3. **Monochrome Noir (B&W)**: High-contrast deep obsidian black, crystalline white neon glow, and silver smoke.
4. **Cyberpunk Overdrive**: Synthwave magenta pink, electric cyan, and neon violet.
5. **Tokyo Neon**: Vivid violet, electric magenta, and neon lilac.
6. **Matrix Emerald**: High-voltage cyber emerald and phosphor green.
7. **Deep Abyss (Bioluminescent)**: Deep oceanic abyss with radiant bioluminescent aqua and sapphire.
8. **Sunset Horizon**: Retrowave solar gold, sunset coral, and flamingo neon.
9. **Ghost Void / Amethyst**: Phantom lavender, astral void purple, and spectral white.
10. **Blood Moon / Crimson**: Demonic scarlet, crimson burgundy, and fiery gold accents.
