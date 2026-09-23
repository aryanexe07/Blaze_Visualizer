"""
🔥 BLAZE Audio Visualizer — Next-Gen Real-Time EDM & Audio Engine
Built with PyQt6, NumPy, and SoundDevice.
Powered by real-time Fast Fourier Transform (FFT) analysis and dynamic physics.

Features:
- Blaze Ears 2.0 (Cyber Feline) dynamic audio-reactive cat ears with twitch reflex, inner acoustic ribs, and tip sparks
- Blaze Fire Spikes, Trap Nation Bass Ring, Monstercat Dual Spectrum, Horizon Double Mirror, Vortex Tunnel, Hexagon Cyber Shield, Laser Oscilloscope
- 10 Curated Premium Themes: Blaze Inferno, UK Rave / Acid Underground, Monochrome Noir (B&W), Cyberpunk Overdrive, Tokyo Neon, Matrix Emerald, Deep Abyss, Sunset Horizon, Ghost Void, Blood Moon
- Real-time WASAPI Loopback / Stereo Mix / Mic capture & Local Audio File Player
- Camera Shake & Bass Vibration Physics with beat recoil and kick particle emitters
- Center Logo / Album Art support with custom high-tech 'BLAZE' typographic badge
- 60 FPS hardware-accelerated anti-aliased rendering
"""

import sys
import os
import math
import random
import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QWidget, QFileDialog
)
from PyQt6.QtCore import (
    Qt, QTimer, QPointF, QRectF
)
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QRadialGradient,
    QConicalGradient, QLinearGradient, QPainterPath, QFont,
    QKeyEvent, QPixmap, QFontMetrics, QPolygonF
)

from audio_engine import AudioEngine
from player import AudioFilePlayer

# =====================================================================
# 🎨 COLOR THEMES
# =====================================================================
THEMES = [
    {
        "name": "Blaze Inferno",
        "bg": QColor(22, 10, 6),
        "core_center": QColor(255, 60, 0),
        "core_halo": QColor(255, 140, 0, 95),
        "ear_glow": QColor(255, 55, 0),
        "ear_rim": QColor(255, 190, 40),
        "gradient": [
            (0.0, QColor(255, 55, 0)),
            (0.3, QColor(255, 160, 0)),
            (0.6, QColor(255, 0, 70)),
            (0.85, QColor(255, 200, 50)),
            (1.0, QColor(255, 55, 0))
        ],
        "ring": QColor(255, 235, 210),
        "maxbar": QColor(255, 180, 0, 200),
        "particle": QColor(255, 120, 0)
    },
    {
        "name": "UK Rave / Acid Underground",
        "bg": QColor(10, 8, 22),
        "core_center": QColor(57, 255, 20),
        "core_halo": QColor(190, 0, 255, 90),
        "ear_glow": QColor(57, 255, 20),
        "ear_rim": QColor(250, 255, 0),
        "gradient": [
            (0.0, QColor(57, 255, 20)),
            (0.25, QColor(250, 255, 0)),
            (0.5, QColor(220, 0, 255)),
            (0.75, QColor(0, 240, 255)),
            (1.0, QColor(57, 255, 20))
        ],
        "ring": QColor(255, 255, 255),
        "maxbar": QColor(57, 255, 20, 200),
        "particle": QColor(57, 255, 20)
    },
    {
        "name": "Monochrome Noir (B&W)",
        "bg": QColor(8, 8, 10),
        "core_center": QColor(255, 255, 255),
        "core_halo": QColor(200, 200, 210, 75),
        "ear_glow": QColor(255, 255, 255),
        "ear_rim": QColor(230, 235, 245),
        "gradient": [
            (0.0, QColor(255, 255, 255)),
            (0.3, QColor(140, 145, 155)),
            (0.6, QColor(225, 230, 240)),
            (0.85, QColor(90, 95, 105)),
            (1.0, QColor(255, 255, 255))
        ],
        "ring": QColor(255, 255, 255),
        "maxbar": QColor(255, 255, 255, 210),
        "particle": QColor(240, 240, 250)
    },
    {
        "name": "Cyberpunk Overdrive",
        "bg": QColor(14, 10, 24),
        "core_center": QColor(0, 240, 255),
        "core_halo": QColor(255, 0, 127, 85),
        "ear_glow": QColor(255, 0, 127),
        "ear_rim": QColor(0, 240, 255),
        "gradient": [
            (0.0, QColor(255, 0, 127)),
            (0.25, QColor(157, 0, 255)),
            (0.5, QColor(0, 240, 255)),
            (0.75, QColor(255, 0, 127)),
            (1.0, QColor(255, 0, 127))
        ],
        "ring": QColor(255, 255, 255),
        "maxbar": QColor(0, 240, 255, 190),
        "particle": QColor(255, 0, 127)
    },
    {
        "name": "Tokyo Neon",
        "bg": QColor(18, 10, 28),
        "core_center": QColor(255, 80, 255),
        "core_halo": QColor(160, 30, 240, 85),
        "ear_glow": QColor(255, 40, 160),
        "ear_rim": QColor(255, 190, 255),
        "gradient": [
            (0.0, QColor(255, 40, 160)),
            (0.35, QColor(140, 30, 255)),
            (0.7, QColor(255, 180, 255)),
            (1.0, QColor(255, 40, 160))
        ],
        "ring": QColor(255, 240, 255),
        "maxbar": QColor(255, 120, 255, 190),
        "particle": QColor(255, 70, 200)
    },
    {
        "name": "Matrix Emerald",
        "bg": QColor(8, 20, 14),
        "core_center": QColor(0, 255, 170),
        "core_halo": QColor(0, 180, 80, 85),
        "ear_glow": QColor(0, 255, 170),
        "ear_rim": QColor(130, 255, 210),
        "gradient": [
            (0.0, QColor(0, 255, 170)),
            (0.35, QColor(0, 190, 255)),
            (0.7, QColor(60, 255, 100)),
            (1.0, QColor(0, 255, 170))
        ],
        "ring": QColor(235, 255, 245),
        "maxbar": QColor(0, 255, 170, 190),
        "particle": QColor(0, 255, 170)
    },
    {
        "name": "Deep Abyss / Bioluminescent",
        "bg": QColor(6, 12, 24),
        "core_center": QColor(0, 229, 255),
        "core_halo": QColor(0, 110, 255, 80),
        "ear_glow": QColor(0, 245, 212),
        "ear_rim": QColor(0, 130, 255),
        "gradient": [
            (0.0, QColor(0, 245, 212)),
            (0.35, QColor(0, 140, 255)),
            (0.7, QColor(120, 70, 255)),
            (1.0, QColor(0, 245, 212))
        ],
        "ring": QColor(230, 248, 255),
        "maxbar": QColor(0, 229, 255, 190),
        "particle": QColor(0, 245, 212)
    },
    {
        "name": "Sunset Horizon",
        "bg": QColor(22, 12, 18),
        "core_center": QColor(255, 183, 3),
        "core_halo": QColor(251, 133, 0, 85),
        "ear_glow": QColor(255, 0, 110),
        "ear_rim": QColor(255, 183, 3),
        "gradient": [
            (0.0, QColor(255, 0, 110)),
            (0.33, QColor(251, 133, 0)),
            (0.66, QColor(131, 56, 236)),
            (1.0, QColor(255, 0, 110))
        ],
        "ring": QColor(255, 245, 235),
        "maxbar": QColor(255, 183, 3, 190),
        "particle": QColor(251, 133, 0)
    },
    {
        "name": "Ghost Void / Amethyst",
        "bg": QColor(16, 10, 26),
        "core_center": QColor(190, 120, 255),
        "core_halo": QColor(130, 40, 220, 75),
        "ear_glow": QColor(216, 180, 254),
        "ear_rim": QColor(255, 255, 255),
        "gradient": [
            (0.0, QColor(216, 180, 254)),
            (0.35, QColor(130, 60, 240)),
            (0.7, QColor(245, 235, 255)),
            (1.0, QColor(216, 180, 254))
        ],
        "ring": QColor(245, 240, 255),
        "maxbar": QColor(216, 180, 254, 190),
        "particle": QColor(216, 180, 254)
    },
    {
        "name": "Blood Moon / Crimson",
        "bg": QColor(24, 6, 8),
        "core_center": QColor(255, 23, 68),
        "core_halo": QColor(180, 0, 30, 90),
        "ear_glow": QColor(255, 23, 68),
        "ear_rim": QColor(255, 145, 0),
        "gradient": [
            (0.0, QColor(255, 23, 68)),
            (0.35, QColor(255, 110, 0)),
            (0.7, QColor(140, 0, 25)),
            (1.0, QColor(255, 23, 68))
        ],
        "ring": QColor(255, 230, 230),
        "maxbar": QColor(255, 23, 68, 200),
        "particle": QColor(255, 23, 68)
    }
]

# =====================================================================
# 🎛️ VISUALIZER STYLES
# =====================================================================
VISUALIZER_STYLES = [
    "Blaze Ears 2.0 (Cyber Feline)",
    "Blaze Fire Spikes (Solar Flare)",
    "Bass Pulse Ring (Trap Nation)",
    "Dual Spectrum Arc (Monstercat)",
    "Horizon Double Mirror (Cyber Skyline)",
    "Vortex Wormhole (3D Audio Tunnel)",
    "Hexagon Cyber Shield (Matrix Pulse)",
    "Oscilloscope Laser (Lightning Wave)",
    "Smooth Waveform 360",
    "Radial Equalizer Bars"
]

SHAKE_MODES = [
    ("Heavy (Bass Vibrate)", 1.0),
    ("Intense (Earthquake)", 1.6),
    ("Subtle", 0.5),
    ("Off", 0.0)
]

OVERLAY_LEVELS = [
    ("45% Tint (Recommended)", 0.45),
    ("65% Darker", 0.65),
    ("85% Deep Dark", 0.85),
    ("25% Light Tint", 0.25),
    ("0% Clear", 0.0)
]


class Particle:
    def __init__(self, x, y, angle, speed, color, life=40, size=3.5, decay=0.96):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.decay = decay

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.decay
        self.vy *= self.decay
        self.life -= 1
        return self.life > 0

    def draw(self, painter: QPainter):
        ratio = max(0.0, self.life / self.max_life)
        alpha = int(ratio * 240)
        radius = max(0.8, self.size * ratio)
        c = QColor(self.color.red(), self.color.green(), self.color.blue(), alpha)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(c))
        painter.drawEllipse(QPointF(self.x, self.y), radius, radius)


class CircularWaveWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔥 BLAZE Audio Visualizer — Next-Gen EDM Audio Engine")
        self.resize(1080, 1080)
        self.setMinimumSize(640, 640)
        
        # Audio Analysis
        self.num_points = 360
        self.audio_engine = AudioEngine(fft_size=2048, num_bins=self.num_points, smoothing=0.28)
        self.player = AudioFilePlayer(self.audio_engine)
        
        # Visualizer State
        self.style_idx = 0  # 0 = Blaze Ears 2.0
        self.theme_idx = 0  # 0 = Blaze Inferno
        self.r_min = 140.0
        self.r_max = 285.0
        self.particles = []
        self.show_hud = True
        self.mode = "LIVE_SYSTEM"  # "LIVE_SYSTEM" or "FILE_PLAYER"
        
        # Dynamic ear physics state (twitch, perk, flare)
        self.ear_twitch_left = 0.0
        self.ear_twitch_right = 0.0
        self.ear_flare = 0.0
        self.ear_twitch_timer = 0
        
        # Background & Center Logo
        self.bg_pixmap = None
        self.bg_path = None
        self.overlay_idx = 0
        self.custom_logo_pixmap = None
        self.custom_logo_path = None
        self.show_logo = True
        
        # Bass Vibration & Screen Shake Engine
        self.shake_idx = 0
        self.shake_energy = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0
        self.shake_zoom = 1.0
        self.last_bass = 0.0
        
        # Shockwave ripple & rotation
        self.ripple_radius = self.r_min * 0.7
        self.ripple_alpha = 0
        self.rotation_angle = 0.0
        self.time_phase = 0.0

        # Load default background if present
        self._load_default_assets()

        # Start live audio stream
        self.audio_engine.start()

        # 60 FPS Render Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)  # ~60 FPS

    def _load_default_assets(self):
        """Loads default background image from assets directory if available."""
        default_bg = os.path.join(os.path.dirname(__file__), "assets", "default_bg.jpg")
        if os.path.exists(default_bg):
            self.bg_path = default_bg
            self.bg_pixmap = QPixmap(default_bg)

    @property
    def theme(self):
        return THEMES[self.theme_idx]

    @property
    def current_style_name(self):
        return VISUALIZER_STYLES[self.style_idx]

    @property
    def shake_multiplier(self):
        return SHAKE_MODES[self.shake_idx][1]

    @property
    def overlay_alpha(self):
        return OVERLAY_LEVELS[self.overlay_idx][1]

    def update_frame(self):
        self.rotation_angle = (self.rotation_angle + 0.22) % 360.0
        self.time_phase += 0.05
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()
        
        if key == Qt.Key.Key_Escape:
            self.close()
        elif key == Qt.Key.Key_V:
            # Switch Visualizer Style (Forward or backward with Shift)
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                self.style_idx = (self.style_idx - 1) % len(VISUALIZER_STYLES)
            else:
                self.style_idx = (self.style_idx + 1) % len(VISUALIZER_STYLES)
        elif key == Qt.Key.Key_C:
            # Previous style
            self.style_idx = (self.style_idx - 1) % len(VISUALIZER_STYLES)
        elif key == Qt.Key.Key_T:
            # Switch Color Theme
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                self.theme_idx = (self.theme_idx - 1) % len(THEMES)
            else:
                self.theme_idx = (self.theme_idx + 1) % len(THEMES)
        elif key == Qt.Key.Key_B:
            # Custom Background Image
            self.select_custom_background()
        elif key == Qt.Key.Key_S:
            # Toggle / Cycle Shake Intensity
            self.shake_idx = (self.shake_idx + 1) % len(SHAKE_MODES)
        elif key == Qt.Key.Key_O:
            # Cycle background dark tint overlay
            self.overlay_idx = (self.overlay_idx + 1) % len(OVERLAY_LEVELS)
        elif key == Qt.Key.Key_L:
            # Custom Center Logo or Toggle
            self.select_custom_logo()
        elif key == Qt.Key.Key_H:
            self.show_hud = not self.show_hud
        elif key == Qt.Key.Key_D:
            self.cycle_device()
        elif key == Qt.Key.Key_F:
            self.open_audio_file()
        elif key == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif key == Qt.Key.Key_Space:
            if self.mode == "FILE_PLAYER":
                self.player.pause_toggle()
            else:
                self.audio_engine.start()

    def select_custom_background(self):
        """Allows user to select any image file for the visualizer backdrop."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Background Wallpaper",
            "",
            "Image Files (*.jpg *.jpeg *.png *.webp *.bmp);;All Files (*.*)"
        )
        if file_path:
            self.bg_path = file_path
            self.bg_pixmap = QPixmap(file_path)

    def select_custom_logo(self):
        """Allows user to select a center logo/album art or toggle default."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Center Logo / Album Art (or Cancel to toggle)",
            "",
            "Image Files (*.png *.jpg *.jpeg *.webp);;All Files (*.*)"
        )
        if file_path:
            self.custom_logo_path = file_path
            self.custom_logo_pixmap = QPixmap(file_path)
            self.show_logo = True
        else:
            if self.custom_logo_pixmap is not None:
                self.custom_logo_pixmap = None
            else:
                self.show_logo = not self.show_logo

    def cycle_device(self):
        """Cycles through audio capture devices."""
        devs = self.audio_engine.get_audio_devices()
        if not devs:
            return
        cur_id = self.audio_engine.device_id
        next_idx = 0
        for i, d in enumerate(devs):
            if d.get('id') == cur_id:
                next_idx = (i + 1) % len(devs)
                break
        chosen = devs[next_idx]
        self.mode = "LIVE_SYSTEM"
        self.player.stop()
        self.audio_engine.start(device_info=chosen)

    def open_audio_file(self):
        """Prompts user to select an audio file to play."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File to Visualize",
            "",
            "Audio Files (*.wav *.flac *.ogg *.mp3);;All Files (*.*)"
        )
        if file_path:
            self.mode = "FILE_PLAYER"
            self.audio_engine.stop()
            if self.player.load(file_path):
                self.player.play()

    def _update_bass_shake(self, bass_energy):
        """Calculates dynamic camera vibration and bass recoil pulse."""
        mult = self.shake_multiplier
        if mult <= 0.001:
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0
            self.shake_zoom = 1.0
            return

        # Transient kick detection
        bass_diff = max(0.0, bass_energy - self.last_bass)
        self.last_bass = bass_energy

        # Kick impulse
        if bass_energy > 0.45 or bass_diff > 0.12:
            self.shake_energy = min(1.0, self.shake_energy + (bass_energy * 0.55 + bass_diff * 0.9) * mult)

        # Decay shake energy
        self.shake_energy *= 0.82

        if self.shake_energy > 0.01:
            intensity = self.shake_energy * 14.0 * mult
            self.shake_offset_x = random.uniform(-1.0, 1.0) * intensity
            self.shake_offset_y = random.uniform(-1.0, 1.0) * intensity
            self.shake_zoom = 1.0 + (self.shake_energy * 0.038 * mult)
        else:
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0
            self.shake_zoom = 1.0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        w = self.width()
        h = self.height()
        
        # Audio Spectrum & Bass Calculation
        freqs, bass_energy, rms, is_active = self.audio_engine.process_frame()

        # Update Shake Physics
        self._update_bass_shake(bass_energy)

        # Apply Screen Shake Camera Transform
        painter.save()
        if abs(self.shake_offset_x) > 0.1 or abs(self.shake_offset_y) > 0.1 or abs(self.shake_zoom - 1.0) > 0.001:
            painter.translate(w / 2.0, h / 2.0)
            painter.scale(self.shake_zoom, self.shake_zoom)
            painter.translate(-w / 2.0 + self.shake_offset_x, -h / 2.0 + self.shake_offset_y)

        # 1. Render Background (Custom Image or Theme Color)
        self._draw_background(painter, w, h)

        # Scale Factor based on viewport
        scale = min(w, h) / 950.0
        center = QPointF(w / 2.0, h / 2.0)
        
        # Audio Responsive Base Radius
        r_min_scaled = self.r_min * scale
        r_max_scaled = self.r_max * scale
        dynamic_min_r = r_min_scaled + (bass_energy * 32.0 * scale)

        # Particle System on Kicks & Highs
        if bass_energy > 0.50:
            self.ripple_alpha = int(230 * bass_energy)
            self.ripple_radius = dynamic_min_r * 0.82
            if len(self.particles) < 280:
                for i in range(0, len(freqs), 4):
                    if freqs[i] > 0.50 and random.random() < 0.45:
                        th = (i / len(freqs)) * 2 * math.pi
                        pt_x = center.x() + dynamic_min_r * math.cos(th)
                        pt_y = center.y() + dynamic_min_r * math.sin(th)
                        speed = random.uniform(3.5, 9.0) * freqs[i] * scale
                        self.particles.append(Particle(pt_x, pt_y, th, speed, self.theme["particle"], life=random.randint(25, 48), size=random.uniform(2.5, 5.5)))

        # 2. Expanding Shockwave Bass Ripple
        if self.ripple_alpha > 5:
            self.ripple_radius += (3.0 * scale)
            self.ripple_alpha = max(0, self.ripple_alpha - 5)
            halo_color = self.theme["core_halo"]
            ripple_color = QColor(halo_color.red(), halo_color.green(), halo_color.blue(), self.ripple_alpha)
            pen_ripple = QPen(ripple_color, 4.0 * scale)
            painter.setPen(pen_ripple)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, self.ripple_radius, self.ripple_radius)

        # 3. Render Visualizer Waveform based on selected style
        if self.style_idx == 0:
            self._draw_blaze_ears_2(painter, center, dynamic_min_r, r_max_scaled, scale, freqs, bass_energy)
        elif self.style_idx == 1:
            self._draw_blaze_fire_spikes(painter, center, dynamic_min_r, r_max_scaled, scale, freqs, bass_energy)
        elif self.style_idx == 2:
            self._draw_trap_nation_bass_ring(painter, center, dynamic_min_r, r_max_scaled, scale, freqs, bass_energy)
        elif self.style_idx == 3:
            self._draw_monstercat_style(painter, center, dynamic_min_r, r_max_scaled, scale, freqs, bass_energy)
        elif self.style_idx == 4:
            self._draw_horizon_double_mirror(painter, center, w, h, scale, freqs, bass_energy)
        elif self.style_idx == 5:
            self._draw_vortex_wormhole(painter, center, dynamic_min_r, r_max_scaled, scale, freqs, bass_energy)
        elif self.style_idx == 6:
            self._draw_hexagon_cyber_shield(painter, center, dynamic_min_r, r_max_scaled, scale, freqs, bass_energy)
        elif self.style_idx == 7:
            self._draw_oscilloscope_laser(painter, center, dynamic_min_r, r_max_scaled, scale, freqs, bass_energy)
        elif self.style_idx == 8:
            self._draw_smooth_waveform(painter, center, dynamic_min_r, r_max_scaled, scale, freqs)
        else:
            self._draw_radial_bars(painter, center, dynamic_min_r, r_max_scaled, scale, freqs)

        # 4. Center Ring & Logo / Typography Badge (unless full-screen mode like horizon mirror)
        if self.style_idx != 4:
            self._draw_center_badge(painter, center, dynamic_min_r, scale, bass_energy)

        # 5. Particle Burst System
        alive_particles = []
        for p in self.particles:
            if p.update():
                p.draw(painter)
                alive_particles.append(p)
        self.particles = alive_particles

        # Restore camera shake transform
        painter.restore()

        # 6. Sleek Glassmorphic HUD
        if self.show_hud:
            self.draw_hud(painter, is_active, bass_energy, rms)

    def _draw_background(self, painter: QPainter, w: int, h: int):
        """Draws background image or fallback gradient with dark overlay & vignette."""
        if self.bg_pixmap and not self.bg_pixmap.isNull():
            # Aspect fill / cover scaling
            scaled = self.bg_pixmap.scaled(
                w + 60, h + 60,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            sx = (w - scaled.width()) // 2
            sy = (h - scaled.height()) // 2
            painter.drawPixmap(sx, sy, scaled)
        else:
            # Sleek deep gradient fallback
            rad = QRadialGradient(w / 2, h / 2, max(w, h) * 0.75)
            rad.setColorAt(0.0, self.theme["bg"])
            rad.setColorAt(1.0, QColor(4, 4, 8))
            painter.fillRect(0, 0, w, h, QBrush(rad))

        # Dark overlay tint for visualizer clarity
        alpha = int(self.overlay_alpha * 255)
        if alpha > 0:
            painter.fillRect(0, 0, w, h, QColor(0, 0, 0, alpha))

        # Radial vignette for dramatic depth
        vignette = QRadialGradient(w / 2, h / 2, max(w, h) * 0.62)
        vignette.setColorAt(0.0, QColor(0, 0, 0, 0))
        vignette.setColorAt(0.65, QColor(0, 0, 0, 50))
        vignette.setColorAt(1.0, QColor(0, 0, 0, 180))
        painter.fillRect(0, 0, w, h, QBrush(vignette))

    # =================================================================
    # 🐾 STYLE 1: BLAZE EARS 2.0 (Dynamic Cyber Feline)
    # =================================================================
    def _draw_blaze_ears_2(self, painter: QPainter, center: QPointF, r_min: float, r_max: float, scale: float, freqs: np.ndarray, bass: float):
        """
        Next-Generation Ultra-Dynamic Cat Ears / Cyber Feline Visualizer.
        Includes dynamic ear flick/twitch physics, treble reactivity on ear tips,
        sub-bass ear flare, inner acoustic neon ribs, multi-layer neon bloom,
        and spark emitters from ear tips.
        """
        N = len(freqs)
        angles_deg = np.linspace(0, 360, N, endpoint=False)
        
        # Audio band analysis
        treble_energy = float(np.mean(freqs[int(N * 0.65):]))
        mid_energy = float(np.mean(freqs[int(N * 0.2):int(N * 0.65)]))
        
        # Dynamic ear twitch & perk mechanics
        self.ear_twitch_timer += 1
        if treble_energy > 0.48 and random.random() < 0.35:
            # Highs/snare trigger ear tip flick
            if random.random() < 0.5:
                self.ear_twitch_left = min(1.0, self.ear_twitch_left + 0.65)
            else:
                self.ear_twitch_right = min(1.0, self.ear_twitch_right + 0.65)
        
        # Decay twitches smoothly
        self.ear_twitch_left *= 0.84
        self.ear_twitch_right *= 0.84
        self.ear_flare = (self.ear_flare * 0.82) + (bass * 0.18)
        
        # Dynamic ear peak angles (ears perk up and twitch dynamically)
        left_peak = 128.0 + (self.ear_twitch_left * 5.0) - (self.ear_flare * 3.5)
        right_peak = 52.0 - (self.ear_twitch_right * 5.0) + (self.ear_flare * 3.5)

        # Smooth frequencies with hanning window for fluid curves
        kernel_size = 9
        kernel = np.hanning(kernel_size)
        kernel /= kernel.sum()
        smoothed_f = np.convolve(np.pad(freqs, (kernel_size // 2, kernel_size // 2), mode='wrap'), kernel, mode='valid')
        
        points_outer = []
        points_inner_rib_1 = []
        points_inner_rib_2 = []
        
        ear_boost = 1.0 + (bass * 0.75) + (mid_energy * 0.35)
        
        for i, deg in enumerate(angles_deg):
            # Dynamic envelope based on twitching peak angles
            envelope = 0.0
            if 0.0 <= deg <= 180.0:
                # Right ear lobe
                d_r = abs((deg - right_peak + 180) % 360 - 180)
                ear_r = math.exp(-(d_r / 20.5) ** 2)
                
                # Left ear lobe
                d_l = abs((deg - left_peak + 180) % 360 - 180)
                ear_l = math.exp(-(d_l / 20.5) ** 2)
                
                # Crown dip between ears at 90 deg
                d_c = abs((deg - 90.0 + 180) % 360 - 180)
                saddle = 0.32 * math.exp(-(d_c / 17.0) ** 2)
                
                # Outer side tapers near 12 deg and 168 deg
                taper = 1.0
                if deg < 28.0:
                    taper = max(0.0, deg / 28.0)
                elif deg > 152.0:
                    taper = max(0.0, (180.0 - deg) / 28.0)
                
                envelope = max(0.0, ((ear_r + ear_l) * 1.45 - saddle) * taper)
            
            f_val = smoothed_f[i]
            
            # Ear height + dynamic audio reaction + treble crackle
            ear_height = envelope * (95.0 * scale * ear_boost)
            audio_wave = (f_val ** 0.82) * (70.0 * scale) * max(0.25, envelope)
            
            # Sub-bass breathing on lower half
            lower_breath = (bass * 6.0 * scale) * (1.0 + 0.3 * math.sin(math.radians(deg) + self.time_phase * 2)) if (180.0 < deg < 360.0) else 0.0
            
            total_r = r_min + ear_height + audio_wave + lower_breath
            rad = math.radians(deg)
            
            ox = center.x() + total_r * math.cos(rad)
            oy = center.y() - total_r * math.sin(rad)
            points_outer.append(QPointF(ox, oy))
            
            # Inner acoustic folds / neon ribs inside ears
            if envelope > 0.35 and 0.0 <= deg <= 180.0:
                rib1_r = r_min + (ear_height * 0.58) + (f_val * 25.0 * scale)
                rx1 = center.x() + rib1_r * math.cos(rad)
                ry1 = center.y() - rib1_r * math.sin(rad)
                points_inner_rib_1.append(QPointF(rx1, ry1))
                
                rib2_r = r_min + (ear_height * 0.28) + (f_val * 14.0 * scale)
                rx2 = center.x() + rib2_r * math.cos(rad)
                ry2 = center.y() - rib2_r * math.sin(rad)
                points_inner_rib_2.append(QPointF(rx2, ry2))

        # Emit spark particles from ear tips on treble/bass kicks
        if (treble_energy > 0.45 or bass > 0.65) and len(self.particles) < 260:
            for peak_deg in [right_peak, left_peak]:
                p_rad = math.radians(peak_deg)
                tip_r = r_min + (95.0 * scale * ear_boost) + (treble_energy * 40.0 * scale)
                tip_x = center.x() + tip_r * math.cos(p_rad)
                tip_y = center.y() - tip_r * math.sin(p_rad)
                if random.random() < 0.6:
                    angle = p_rad + random.uniform(-0.4, 0.4)
                    speed = random.uniform(4.0, 9.5) * scale
                    self.particles.append(Particle(tip_x, tip_y, -angle, speed, self.theme.get("ear_rim", QColor(255, 200, 0)), life=random.randint(18, 35), size=random.uniform(2.0, 4.2)))

        # 1. Outer Silhouette Body Path
        body_path = QPainterPath()
        body_path.moveTo(points_outer[0])
        for pt in points_outer[1:]:
            body_path.lineTo(pt)
        body_path.closeSubpath()

        # Inner cutout
        inner_path = QPainterPath()
        inner_path.addEllipse(center, r_min, r_min)
        filled_body = body_path.subtracted(inner_path)

        # Silhouette Gradient
        body_grad = QLinearGradient(center.x(), center.y() - r_max * 1.1, center.x(), center.y() + r_min)
        body_grad.setColorAt(0.0, QColor(28, 16, 38, 245))
        body_grad.setColorAt(0.5, QColor(12, 8, 20, 250))
        body_grad.setColorAt(1.0, QColor(4, 4, 10, 220))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(body_grad))
        painter.drawPath(filled_body)

        # 2. Inner Ear Acoustic Fold Ribs (Dynamic Glowing Highlights)
        if len(points_inner_rib_1) > 4:
            rib_pen = QPen(QColor(self.theme.get("ear_glow").red(), self.theme.get("ear_glow").green(), self.theme.get("ear_glow").blue(), 160), 2.2 * scale)
            rib_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(rib_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for j in range(len(points_inner_rib_1) - 1):
                painter.drawLine(points_inner_rib_1[j], points_inner_rib_1[j+1])
                
        if len(points_inner_rib_2) > 4:
            rib_pen2 = QPen(QColor(self.theme.get("ear_rim").red(), self.theme.get("ear_rim").green(), self.theme.get("ear_rim").blue(), 140), 1.8 * scale)
            rib_pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(rib_pen2)
            for j in range(len(points_inner_rib_2) - 1):
                painter.drawLine(points_inner_rib_2[j], points_inner_rib_2[j+1])

        # 3. Multi-layered Glowing Neon Rim on the Cat Ears
        outer_rim_path = QPainterPath()
        outer_rim_path.moveTo(points_outer[0])
        for pt in points_outer[1:]:
            outer_rim_path.lineTo(pt)
        outer_rim_path.closeSubpath()

        neon_conical = QConicalGradient(center, 90)
        neon_conical.setColorAt(0.0, self.theme.get("ear_rim", QColor(255, 200, 0)))
        neon_conical.setColorAt(0.25, self.theme.get("ear_glow", QColor(255, 50, 0)))
        neon_conical.setColorAt(0.5, self.theme.get("ear_rim", QColor(255, 200, 0)))
        neon_conical.setColorAt(0.75, self.theme.get("ear_glow", QColor(255, 50, 0)))
        neon_conical.setColorAt(1.0, self.theme.get("ear_rim", QColor(255, 200, 0)))

        glow_c = self.theme.get("ear_glow", QColor(255, 50, 0))
        
        # Outer Deep Atmosphere Bloom
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(glow_c.red(), glow_c.green(), glow_c.blue(), 55), 22.0 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawPath(outer_rim_path)

        # Mid-Intensity Bloom
        painter.setPen(QPen(QColor(glow_c.red(), glow_c.green(), glow_c.blue(), 130), 10.0 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawPath(outer_rim_path)

        # Razor-Sharp Neon Rim
        painter.setPen(QPen(QBrush(neon_conical), 3.8 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawPath(outer_rim_path)

    # =================================================================
    # 🔥 STYLE 2: BLAZE FIRE SPIKES (Solar Flare / Plasma Spikes)
    # =================================================================
    def _draw_blaze_fire_spikes(self, painter: QPainter, center: QPointF, r_min: float, r_max: float, scale: float, freqs: np.ndarray, bass: float):
        """
        Fiery plasma bursts & blazing solar flare spikes oscillating with turbulence.
        """
        num_spikes = 180
        step = len(freqs) // num_spikes
        
        conical = QConicalGradient(center, self.rotation_angle * 1.5)
        for stop, color in self.theme["gradient"]:
            conical.setColorAt(stop, color)

        # Multi-pass flame rendering (outer aura + core flame spikes)
        for i in range(num_spikes):
            f = freqs[min(len(freqs) - 1, i * step)]
            angle = (i / num_spikes) * 2 * math.pi
            
            # Flame turbulence & flutter
            flutter = math.sin(i * 0.45 + self.time_phase * 6.0) * (12.0 * scale)
            flame_len = (f ** 0.75) * (r_max - r_min) * 1.35 * (1.0 + bass * 0.6) + flutter
            r_out = r_min + max(0.0, flame_len)
            
            x1 = center.x() + r_min * math.cos(angle)
            y1 = center.y() + r_min * math.sin(angle)
            x2 = center.x() + r_out * math.cos(angle)
            y2 = center.y() + r_out * math.sin(angle)
            
            # Wide glowing heat ray
            glow_c = self.theme["particle"]
            painter.setPen(QPen(QColor(glow_c.red(), glow_c.green(), glow_c.blue(), 55), 8.0 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            
            # Sharp flame needle
            painter.setPen(QPen(QBrush(conical), 2.8 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            
            # Flaming tip bead on loud frequencies
            if f > 0.45:
                bead_r = (3.5 + f * 4.0) * scale
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(self.theme["ring"]))
                painter.drawEllipse(QPointF(x2, y2), bead_r, bead_r)

    # =================================================================
    # ⚡ STYLE 3: TRAP NATION BASS RING
    # =================================================================
    def _draw_trap_nation_bass_ring(self, painter: QPainter, center: QPointF, r_min: float, r_max: float, scale: float, freqs: np.ndarray, bass: float):
        """Draws dynamic 360 frequency bars with heavy bass kick scaling and sharp caps."""
        num_bars = 160
        step = len(freqs) // num_bars
        
        conical = QConicalGradient(center, self.rotation_angle)
        for stop, color in self.theme["gradient"]:
            conical.setColorAt(stop, color)

        bar_pen = QPen(QBrush(conical), 3.2 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(bar_pen)
        
        for i in range(num_bars):
            f = freqs[min(len(freqs)-1, i * step)]
            angle = (i / num_bars) * 2 * math.pi
            r_out = r_min + (f ** 0.8) * (r_max - r_min) * (1.0 + bass * 0.45)
            
            x1 = center.x() + r_min * math.cos(angle)
            y1 = center.y() + r_min * math.sin(angle)
            x2 = center.x() + r_out * math.cos(angle)
            y2 = center.y() + r_out * math.sin(angle)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    # =================================================================
    # 🐱 STYLE 4: MONSTERCAT DUAL SPECTRUM ARC
    # =================================================================
    def _draw_monstercat_style(self, painter: QPainter, center: QPointF, r_min: float, r_max: float, scale: float, freqs: np.ndarray, bass: float):
        """Draws symmetrical Monstercat style dual frequency spectrums on upper semicircle."""
        half_n = len(freqs) // 2
        
        conical = QConicalGradient(center, 90)
        conical.setColorAt(0.0, self.theme.get("ear_rim", QColor(255, 200, 0)))
        conical.setColorAt(0.5, self.theme.get("ear_glow", QColor(255, 50, 0)))
        conical.setColorAt(1.0, self.theme.get("ear_rim", QColor(255, 200, 0)))

        painter.setPen(QPen(QBrush(conical), 3.6 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        
        for i in range(half_n):
            f = freqs[i]
            th_l = math.pi / 2 + (i / half_n) * (math.pi / 2)
            th_r = math.pi / 2 - (i / half_n) * (math.pi / 2)
            h = (f ** 0.85) * (r_max - r_min) * (1.15 + bass * 0.35)
            
            for th in [th_l, th_r]:
                x1 = center.x() + r_min * math.cos(th)
                y1 = center.y() - r_min * math.sin(th)
                x2 = center.x() + (r_min + h) * math.cos(th)
                y2 = center.y() - (r_min + h) * math.sin(th)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    # =================================================================
    # 🌆 STYLE 5: HORIZON DOUBLE MIRROR (Cyber Skyline)
    # =================================================================
    def _draw_horizon_double_mirror(self, painter: QPainter, center: QPointF, w: int, h: int, scale: float, freqs: np.ndarray, bass: float):
        """
        Dual horizontal mirrored skyline spectrum with glowing grid reflection floor.
        """
        num_bars = 120
        step = len(freqs) // num_bars
        bar_w = (w * 0.92) / num_bars
        start_x = w * 0.04
        mid_y = h * 0.52
        
        max_h = h * 0.38
        
        grad = QLinearGradient(0, mid_y - max_h, 0, mid_y + max_h)
        for stop, color in self.theme["gradient"]:
            grad.setColorAt(stop, color)

        # Baseline horizon glow line
        painter.setPen(QPen(self.theme["ring"], 2.5 * scale))
        painter.drawLine(QPointF(start_x, mid_y), QPointF(w - start_x, mid_y))
        
        for i in range(num_bars):
            f = freqs[min(len(freqs) - 1, i * step)]
            bar_h = (f ** 0.85) * max_h * (1.0 + bass * 0.4)
            bx = start_x + i * bar_w
            
            # Upper Skyline Bar
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(QRectF(bx, mid_y - bar_h, bar_w * 0.78, bar_h), 3, 3)
            
            # Lower Mirror Reflection (Subtle translucent)
            refl_color = QColor(self.theme["particle"].red(), self.theme["particle"].green(), self.theme["particle"].blue(), 75)
            painter.setBrush(QBrush(refl_color))
            painter.drawRoundedRect(QRectF(bx, mid_y + 2, bar_w * 0.78, bar_h * 0.65), 3, 3)
            
            # Floating peak beacon
            if f > 0.40:
                painter.setBrush(QBrush(self.theme["ring"]))
                painter.drawEllipse(QPointF(bx + (bar_w * 0.78) / 2.0, mid_y - bar_h - 4.0 * scale), 2.5 * scale, 2.5 * scale)

    # =================================================================
    # 🌀 STYLE 6: VORTEX WORMHOLE (3D Audio Tunnel)
    # =================================================================
    def _draw_vortex_wormhole(self, painter: QPainter, center: QPointF, r_min: float, r_max: float, scale: float, freqs: np.ndarray, bass: float):
        """
        Concentric pulsating depth rings that warp and zoom into the beat like a 3D wormhole.
        """
        num_rings = 9
        for ring_i in range(num_rings):
            depth = (ring_i + 1) / num_rings
            ring_r = r_min * depth * 2.1 + (bass * 35.0 * scale * depth)
            
            # Rotational warp offset
            rot = self.rotation_angle * (ring_i % 2 == 0 and 1 or -1) * (1.0 + depth)
            
            pts = []
            num_pts = 64
            step = len(freqs) // num_pts
            for p in range(num_pts):
                f = freqs[min(len(freqs) - 1, p * step)]
                ang = (p / num_pts) * 2 * math.pi + math.radians(rot)
                deform = (f ** 0.9) * (45.0 * scale * depth)
                curr_r = ring_r + deform
                px = center.x() + curr_r * math.cos(ang)
                py = center.y() + curr_r * math.sin(ang)
                pts.append(QPointF(px, py))
            
            if len(pts) > 2:
                path = QPainterPath()
                path.moveTo(pts[0])
                for pt in pts[1:]:
                    path.lineTo(pt)
                path.closeSubpath()
                
                ring_color = self.theme["particle"]
                alpha = int(220 * depth)
                pen = QPen(QColor(ring_color.red(), ring_color.green(), ring_color.blue(), alpha), (2.0 + depth * 2.5) * scale)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawPath(path)

    # =================================================================
    # 🛡️ STYLE 7: HEXAGON CYBER SHIELD (Matrix Pulse)
    # =================================================================
    def _draw_hexagon_cyber_shield(self, painter: QPainter, center: QPointF, r_min: float, r_max: float, scale: float, freqs: np.ndarray, bass: float):
        """
        Futuristic geometric audio hexagon with corner energy relays and edge equalizer bursts.
        """
        hex_sides = 6
        hex_pts = []
        hex_r = r_min * 1.35 + (bass * 28.0 * scale)
        
        for s in range(hex_sides):
            ang = math.radians(60 * s + self.rotation_angle * 0.5)
            hx = center.x() + hex_r * math.cos(ang)
            hy = center.y() + hex_r * math.sin(ang)
            hex_pts.append(QPointF(hx, hy))
            
        # Draw Hexagon Hull
        hex_poly = QPolygonF(hex_pts)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.theme["ring"], 3.5 * scale))
        painter.drawPolygon(hex_poly)
        
        # Edge Frequency Bursts along 6 facets
        step = len(freqs) // hex_sides
        for s in range(hex_sides):
            p1 = hex_pts[s]
            p2 = hex_pts[(s + 1) % hex_sides]
            
            sub_bars = 16
            for b in range(sub_bars):
                t = (b + 0.5) / sub_bars
                bx = p1.x() + t * (p2.x() - p1.x())
                by = p1.y() + t * (p2.y() - p1.y())
                
                f_idx = min(len(freqs) - 1, s * step + b * 2)
                f = freqs[f_idx]
                
                # Normal vector to face
                dx = p2.x() - p1.x()
                dy = p2.y() - p1.y()
                nx = -dy / (math.hypot(dx, dy) + 1e-5)
                ny = dx / (math.hypot(dx, dy) + 1e-5)
                
                burst_len = (f ** 0.85) * (70.0 * scale) * (1.0 + bass * 0.5)
                ex = bx + nx * burst_len
                ey = by + ny * burst_len
                
                painter.setPen(QPen(self.theme["particle"], 2.8 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                painter.drawLine(QPointF(bx, by), QPointF(ex, ey))

    # =================================================================
    # ⚡ STYLE 8: OSCILLOSCOPE LASER (Lightning Wave)
    # =================================================================
    def _draw_oscilloscope_laser(self, painter: QPainter, center: QPointF, r_min: float, r_max: float, scale: float, freqs: np.ndarray, bass: float):
        """
        High-voltage neon laser oscilloscope waveform with phosphor trail and transient sparks.
        """
        N = len(freqs)
        angles = np.linspace(0, 2 * math.pi, N, endpoint=False)
        rad_offset = math.radians(self.rotation_angle)
        
        pts = []
        for i, (f, th) in enumerate(zip(freqs, angles)):
            # Audio wave oscillating around base circle
            osc = math.sin(th * 12.0 + self.time_phase * 4.0) * (f * 55.0 * scale)
            r = r_min + osc + (f * (r_max - r_min) * 0.75)
            x = center.x() + r * math.cos(th + rad_offset)
            y = center.y() + r * math.sin(th + rad_offset)
            pts.append(QPointF(x, y))

        if len(pts) > 2:
            path = QPainterPath()
            path.moveTo(pts[0])
            for pt in pts[1:]:
                path.lineTo(pt)
            path.closeSubpath()

            conical = QConicalGradient(center, self.rotation_angle)
            for stop, color in self.theme["gradient"]:
                conical.setColorAt(stop, color)

            # Wide Laser Bloom
            glow_c = self.theme["particle"]
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(glow_c.red(), glow_c.green(), glow_c.blue(), 65), 16.0 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(path)

            # Mid Glow
            painter.setPen(QPen(QColor(glow_c.red(), glow_c.green(), glow_c.blue(), 140), 7.0 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(path)

            # Laser Core (White-hot)
            painter.setPen(QPen(self.theme["ring"], 2.8 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(path)

    # =================================================================
    # 🌊 STYLE 9: SMOOTH WAVEFORM 360
    # =================================================================
    def _draw_smooth_waveform(self, painter: QPainter, center: QPointF, r_min: float, r_max: float, scale: float, freqs: np.ndarray):
        """Draws continuous 360 conical gradient smooth wave."""
        angles = np.linspace(0, 2 * math.pi, len(freqs), endpoint=False)
        rad_offset = math.radians(self.rotation_angle)
        
        points = []
        for f, th in zip(freqs, angles):
            r = r_min + (f * (r_max - r_min))
            x = center.x() + r * math.cos(th + rad_offset)
            y = center.y() + r * math.sin(th + rad_offset)
            points.append(QPointF(x, y))

        if len(points) > 2:
            path = QPainterPath()
            path.moveTo(points[0])
            for pt in points[1:]:
                path.lineTo(pt)
            path.closeSubpath()

            conical = QConicalGradient(center, self.rotation_angle)
            for stop, color in self.theme["gradient"]:
                conical.setColorAt(stop, color)

            # Soft bloom
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QBrush(conical), 9.0 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(path)

            # Sharp foreground
            painter.setPen(QPen(QBrush(conical), 3.2 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawPath(path)

    # =================================================================
    # 📊 STYLE 10: RADIAL EQUALIZER BARS
    # =================================================================
    def _draw_radial_bars(self, painter: QPainter, center: QPointF, r_min: float, r_max: float, scale: float, freqs: np.ndarray):
        """Draws 360 radial frequency bars with conical gradient."""
        num_bars = 180
        step = len(freqs) // num_bars
        conical = QConicalGradient(center, self.rotation_angle)
        for stop, color in self.theme["gradient"]:
            conical.setColorAt(stop, color)

        painter.setPen(QPen(QBrush(conical), 2.8 * scale, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        for i in range(num_bars):
            f = freqs[min(len(freqs)-1, i * step)]
            angle = (i / num_bars) * 2 * math.pi
            r_out = r_min + f * (r_max - r_min)
            x1 = center.x() + r_min * math.cos(angle)
            y1 = center.y() + r_min * math.sin(angle)
            x2 = center.x() + r_out * math.cos(angle)
            y2 = center.y() + r_out * math.sin(angle)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    # =================================================================
    # 🌟 CENTER BADGE & 'BLAZE' BRANDING
    # =================================================================
    def _draw_center_badge(self, painter: QPainter, center: QPointF, r_min: float, scale: float, bass: float):
        """
        Draws the central circular ring with glowing white/neon border and
        custom logo or the high-tech 'BLAZE' brand crest.
        """
        # 1. Center backdrop with subtle dark glassmorphism
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(8, 8, 16, 200)))
        painter.drawEllipse(center, r_min, r_min)

        # 2. Custom or Preset Center Logo
        if self.show_logo:
            if self.custom_logo_pixmap and not self.custom_logo_pixmap.isNull():
                # Draw custom user logo
                logo_size = r_min * 1.4
                scaled_logo = self.custom_logo_pixmap.scaled(
                    int(logo_size), int(logo_size),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                lx = center.x() - scaled_logo.width() / 2.0
                ly = center.y() - scaled_logo.height() / 2.0
                painter.drawPixmap(int(lx), int(ly), scaled_logo)
            else:
                # Draw sleek 'BLAZE' brand crest
                self._draw_blaze_center_badge(painter, center, r_min, scale, bass)

        # 3. Glowing Solid White/Neon Boundary Ring (The iconic circle outline)
        ring_color = self.theme.get("ring", QColor(255, 255, 255))
        
        # Outer Ring Glow
        glow_color = QColor(ring_color.red(), ring_color.green(), ring_color.blue(), 110)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(glow_color, 8.0 * scale))
        painter.drawEllipse(center, r_min, r_min)

        # Crisp Inner Ring
        painter.setPen(QPen(ring_color, 4.2 * scale))
        painter.drawEllipse(center, r_min, r_min)

    def _draw_blaze_center_badge(self, painter: QPainter, center: QPointF, r_min: float, scale: float, bass: float):
        """Renders high-tech 'BLAZE' cyber flame emblem and neon typography."""
        painter.save()
        
        # Pulsating radial glow behind badge
        core_r = r_min * (0.72 + bass * 0.12)
        rad_glow = QRadialGradient(center, core_r * 1.25)
        c_glow = self.theme.get("core_center", QColor(255, 70, 0))
        rad_glow.setColorAt(0.0, QColor(c_glow.red(), c_glow.green(), c_glow.blue(), 210))
        rad_glow.setColorAt(0.5, QColor(c_glow.red(), c_glow.green(), c_glow.blue(), 70))
        rad_glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(rad_glow))
        painter.drawEllipse(center, core_r * 1.25, core_r * 1.25)
        
        # Geometric Cyber Flame Crest / Wings
        flame_size = 28.0 * scale * (1.0 + bass * 0.18)
        cx, cy = center.x(), center.y() - 14.0 * scale
        
        flame_path = QPainterPath()
        flame_path.moveTo(cx, cy - flame_size)
        flame_path.cubicTo(cx + flame_size * 0.85, cy - flame_size * 0.3, cx + flame_size * 0.75, cy + flame_size * 0.65, cx, cy + flame_size * 0.85)
        flame_path.cubicTo(cx - flame_size * 0.75, cy + flame_size * 0.65, cx - flame_size * 0.85, cy - flame_size * 0.3, cx, cy - flame_size)
        flame_path.closeSubpath()
        
        flame_grad = QLinearGradient(cx, cy - flame_size, cx, cy + flame_size)
        flame_grad.setColorAt(0.0, self.theme.get("ear_rim", QColor(255, 220, 100)))
        flame_grad.setColorAt(1.0, self.theme.get("ear_glow", QColor(255, 50, 0)))
        painter.setBrush(QBrush(flame_grad))
        painter.drawPath(flame_path)
        
        # Inner white flame core
        inner_size = flame_size * 0.48
        inner_path = QPainterPath()
        inner_path.moveTo(cx, cy - inner_size * 0.7)
        inner_path.cubicTo(cx + inner_size * 0.7, cy, cx + inner_size * 0.5, cy + inner_size * 0.6, cx, cy + inner_size * 0.75)
        inner_path.cubicTo(cx - inner_size * 0.5, cy + inner_size * 0.6, cx - inner_size * 0.7, cy, cx, cy - inner_size * 0.7)
        inner_path.closeSubpath()
        painter.setBrush(QBrush(QColor(255, 255, 255, 240)))
        painter.drawPath(inner_path)
        
        # Typography: "BLAZE"
        painter.setFont(QFont("Arial Black", int(22 * scale), QFont.Weight.Black))
        painter.setPen(QPen(self.theme["ring"]))
        font_metrics = QFontMetrics(painter.font())
        title_text = "BLAZE"
        tw = font_metrics.horizontalAdvance(title_text)
        painter.drawText(int(center.x() - tw / 2.0), int(center.y() + 32.0 * scale), title_text)
        
        # Subtext: "AUDIO ENGINE"
        painter.setFont(QFont("Segoe UI", int(8.5 * scale), QFont.Weight.Bold))
        painter.setPen(QPen(QColor(200, 205, 225, 200)))
        sub_metrics = QFontMetrics(painter.font())
        sub_text = "AUDIO ENGINE"
        sub_w = sub_metrics.horizontalAdvance(sub_text)
        painter.drawText(int(center.x() - sub_w / 2.0), int(center.y() + 47.0 * scale), sub_text)
        
        painter.restore()

    # =================================================================
    # 🖥️ GLASSMORPHIC HUD
    # =================================================================
    def draw_hud(self, painter: QPainter, is_active: bool, bass_energy: float, rms: float):
        """Draws overlay metrics, active audio source, style, shake mode, and hotkeys."""
        painter.setFont(QFont("Segoe UI", 9))
        
        hud_w, hud_h = 500, 195
        margin = 20
        
        # Glassmorphic panel background
        painter.setPen(QPen(QColor(255, 255, 255, 35), 1))
        painter.setBrush(QBrush(QColor(8, 8, 18, 205)))
        painter.drawRoundedRect(margin, margin, hud_w, hud_h, 12, 12)

        # Status badge
        status_text = "🔥 BLAZE ACTIVE (60 FPS)" if is_active else "○ LISTENING / WAITING FOR AUDIO..."
        status_color = QColor(255, 120, 0) if is_active else QColor(255, 190, 60)
        
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QPen(status_color))
        painter.drawText(margin + 15, margin + 26, status_text)

        # Info lines
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QPen(QColor(225, 225, 240)))
        mode_str = f"Source: {'Live PC Audio (Loopback/Stereo Mix)' if self.mode == 'LIVE_SYSTEM' else 'Audio File Player'}"
        painter.drawText(margin + 15, margin + 50, mode_str)

        painter.setPen(QPen(QColor(180, 180, 205)))
        painter.drawText(margin + 15, margin + 72, f"Style [{self.style_idx+1}/10]: {self.current_style_name}")
        painter.drawText(margin + 15, margin + 92, f"Theme [{self.theme_idx+1}/10]: {self.theme['name']}")
        
        bg_name = os.path.basename(self.bg_path) if self.bg_path else "Default Dark Horizon"
        if len(bg_name) > 20:
            bg_name = bg_name[:18] + ".."
        shake_name = SHAKE_MODES[self.shake_idx][0]
        tint_name = OVERLAY_LEVELS[self.overlay_idx][0].split(" ")[0]
        painter.drawText(margin + 15, margin + 114, f"Wallpaper: {bg_name}  |  Tint: {tint_name}  |  Shake: {shake_name}")

        dev_name = self.audio_engine.device_name
        if len(dev_name) > 36:
            dev_name = dev_name[:34] + "..."
        painter.drawText(margin + 15, margin + 134, f"Device: {dev_name}  |  RMS: {rms:.4f}")

        # Bass kick meter
        painter.setPen(QPen(self.theme.get("core_center", QColor(255, 70, 0))))
        bars = int(bass_energy * 28)
        painter.drawText(margin + 15, margin + 154, f"Bass Kick: [{'=' * bars}{' ' * (28 - bars)}]")

        # Hotkey footer
        painter.setPen(QPen(QColor(150, 150, 175)))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(margin + 15, margin + 175, "[V/C] Style  [T] Theme  [B] Wallpaper  [S] Shake  [O] Tint  [L] Logo")
        painter.drawText(margin + 15, margin + 190, "[D] Device  [F] Audio File  [Space] Play/Pause  [F11] Fullscreen  [H] Hide")

    def closeEvent(self, event):
        self.timer.stop()
        self.player.stop()
        self.audio_engine.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CircularWaveWidget()
    window.show()
    sys.exit(app.exec())
