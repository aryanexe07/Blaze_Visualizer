import './style.css';
import { AudioEngine } from './audioEngine.js';
import { THEMES, VISUALIZER_STYLES, SHAKE_LEVELS } from './presets.js';

class Particle {
  constructor(x, y, angle, speed, colorHex, life = 35, size = 3.5) {
    this.x = x;
    this.y = y;
    this.vx = Math.cos(angle) * speed;
    this.vy = Math.sin(angle) * speed;
    this.colorHex = colorHex;
    this.maxLife = life;
    this.life = life;
    this.size = size;
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.vx *= 0.96;
    this.vy *= 0.96;
    this.life -= 1;
    return this.life > 0;
  }

  draw(ctx) {
    const alpha = Math.max(0, this.life / this.maxLife);
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = this.colorHex;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size * alpha, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

export class BlazeVisualizerApp {
  constructor() {
    this.audioEngine = new AudioEngine(360);
    this.canvas = document.getElementById('visualizer-canvas');
    this.ctx = this.canvas.getContext('2d', { alpha: false });

    // Config state
    this.styleIndex = 0;
    this.themeIndex = 0;
    this.shakeIndex = 0; // 0: heavy, 1: intense, 2: subtle, 3: off
    this.overlayIndex = 1; // 0: 45%, 1: 65%, 2: 85%, 3: 25%, 4: 0%
    this.overlayAlphas = [0.45, 0.65, 0.85, 0.25, 0.0];

    // Visualizer dynamics
    this.rMin = 135;
    this.rMax = 290;
    this.timePhase = 0;
    this.rotationAngle = 0;
    
    // Shake physics
    this.shakeEnergy = 0.0;
    this.lastBass = 0.0;
    this.shakeOffsetX = 0;
    this.shakeOffsetY = 0;
    this.shakeZoom = 1.0;

    // Cat ears dynamic physics
    this.earTwitchLeft = 0.0;
    this.earTwitchRight = 0.0;
    this.earFlare = 0.0;

    // Particles & Shockwave
    this.particles = [];
    this.rippleAlpha = 0;
    this.rippleRadius = 0;

    // Custom Assets
    this.bgImage = null;
    this.bgName = "Default Dark Horizon";
    this.customLogoImage = null;
    this.showLogo = true;
    this.showHud = true;

    // FPS calculation
    this.fps = 60;
    this.frameCount = 0;
    this.lastFpsUpdate = performance.now();

    this._initElements();
    this._loadDefaultBackground();
    this._setupResize();
    this._setupEventListeners();
    this._setupShortcuts();
    this._startRenderLoop();
  }

  get currentTheme() {
    return THEMES[this.themeIndex] || THEMES[0];
  }

  get currentStyle() {
    return VISUALIZER_STYLES[this.styleIndex] || VISUALIZER_STYLES[0];
  }

  get shakeMultiplier() {
    return SHAKE_LEVELS[this.shakeIndex].multiplier;
  }

  _initElements() {
    // Style select
    const styleSel = document.getElementById('style-select');
    if (styleSel) {
      styleSel.innerHTML = VISUALIZER_STYLES.map((s, idx) => 
        `<option value="${idx}">${idx + 1}. ${s.name}</option>`
      ).join('');
      styleSel.addEventListener('change', (e) => {
        this.styleIndex = parseInt(e.target.value);
        this._showToast(`Style: ${this.currentStyle.name}`);
      });
    }

    // Theme select
    const themeSel = document.getElementById('theme-select');
    if (themeSel) {
      themeSel.innerHTML = THEMES.map((t, idx) => 
        `<option value="${idx}">${idx + 1}. ${t.name}</option>`
      ).join('');
      themeSel.addEventListener('change', (e) => {
        this.themeIndex = parseInt(e.target.value);
        this._showToast(`Theme: ${this.currentTheme.name}`);
      });
    }
  }

  _loadDefaultBackground() {
    const img = new Image();
    img.src = '/assets/default_bg.jpg';
    img.onload = () => {
      this.bgImage = img;
    };
    img.onerror = () => {
      // Fallback to procedural dark theme gradient
      this.bgImage = null;
    };
  }

  _setupResize() {
    const handleResize = () => {
      const dpr = window.devicePixelRatio || 1;
      this.width = window.innerWidth;
      this.height = window.innerHeight;
      this.canvas.width = Math.floor(this.width * dpr);
      this.canvas.height = Math.floor(this.height * dpr);
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    window.addEventListener('resize', handleResize);
    handleResize();
  }

  _setupEventListeners() {
    // Audio source buttons
    const btnDemo = document.getElementById('btn-demo-beat');
    if (btnDemo) {
      btnDemo.addEventListener('click', () => {
        this.audioEngine.startDemoBeat();
        this._showToast('Playing EDM Demo Beat (128 BPM)');
        this._updateActiveSourceCard('card-demo');
      });
    }

    const btnUpload = document.getElementById('btn-load-file');
    const fileAudio = document.getElementById('audio-file-input');
    if (btnUpload && fileAudio) {
      btnUpload.addEventListener('click', () => fileAudio.click());
      fileAudio.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
          this.audioEngine.loadAudioFile(e.target.files[0]);
          this._showToast(`Loaded: ${e.target.files[0].name}`);
          this._updateActiveSourceCard('card-file');
        }
      });
    }

    const btnSystem = document.getElementById('btn-system-audio');
    if (btnSystem) {
      btnSystem.addEventListener('click', async () => {
        try {
          await this.audioEngine.startSystemAudio();
          this._showToast('Capturing Live System / Tab Audio');
          this._updateActiveSourceCard('card-system');
        } catch (err) {
          this._showToast(err.message || 'System Audio Share cancelled');
        }
      });
    }

    const btnMic = document.getElementById('btn-mic-audio');
    if (btnMic) {
      btnMic.addEventListener('click', async () => {
        try {
          await this.audioEngine.startMicrophone();
          this._showToast('Capturing Live Microphone');
          this._updateActiveSourceCard('card-mic');
        } catch (err) {
          this._showToast('Microphone access denied');
        }
      });
    }

    // Wallpaper upload
    const btnBg = document.getElementById('btn-bg-upload');
    const fileBg = document.getElementById('bg-file-input');
    if (btnBg && fileBg) {
      btnBg.addEventListener('click', () => fileBg.click());
      fileBg.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
          const file = e.target.files[0];
          const url = URL.createObjectURL(file);
          const img = new Image();
          img.onload = () => {
            this.bgImage = img;
            this.bgName = file.name;
            this._showToast(`Wallpaper: ${file.name}`);
          };
          img.src = url;
        }
      });
    }

    // Logo upload
    const btnLogo = document.getElementById('btn-logo-upload');
    const fileLogo = document.getElementById('logo-file-input');
    if (btnLogo && fileLogo) {
      btnLogo.addEventListener('click', () => fileLogo.click());
      fileLogo.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
          const file = e.target.files[0];
          const url = URL.createObjectURL(file);
          const img = new Image();
          img.onload = () => {
            this.customLogoImage = img;
            this.showLogo = true;
            this._showToast(`Custom Logo Loaded`);
          };
          img.src = url;
        }
      });
    }

    // Shake toggle
    const btnShake = document.getElementById('btn-toggle-shake');
    if (btnShake) {
      btnShake.addEventListener('click', () => {
        this.cycleShake();
      });
    }

    // Tint toggle
    const btnTint = document.getElementById('btn-toggle-tint');
    if (btnTint) {
      btnTint.addEventListener('click', () => {
        this.cycleTint();
      });
    }

    // HUD toggle
    const btnHud = document.getElementById('btn-toggle-hud');
    if (btnHud) {
      btnHud.addEventListener('click', () => {
        this.toggleHud();
      });
    }

    // Fullscreen toggle
    const btnFs = document.getElementById('btn-toggle-fs');
    if (btnFs) {
      btnFs.addEventListener('click', () => {
        this.toggleFullscreen();
      });
    }

    // Audio scrubber
    const scrubBar = document.getElementById('audio-scrub');
    if (scrubBar) {
      scrubBar.addEventListener('input', (e) => {
        this.audioEngine.seek(parseFloat(e.target.value) / 100);
      });
    }

    this.audioEngine.onProgressUpdate = (currentTime, duration) => {
      if (scrubBar && duration > 0) {
        scrubBar.value = (currentTime / duration) * 100;
        const curEl = document.getElementById('time-current');
        const durEl = document.getElementById('time-duration');
        if (curEl) curEl.textContent = this._formatTime(currentTime);
        if (durEl) durEl.textContent = this._formatTime(duration);
      }
    };

    // Drag and drop support
    const appContainer = document.getElementById('app-container');
    const dragOverlay = document.getElementById('drag-overlay');

    window.addEventListener('dragover', (e) => {
      e.preventDefault();
      if (dragOverlay) dragOverlay.classList.add('active');
    });

    window.addEventListener('dragleave', (e) => {
      if (e.clientX <= 0 || e.clientY <= 0) {
        if (dragOverlay) dragOverlay.classList.remove('active');
      }
    });

    window.addEventListener('drop', (e) => {
      e.preventDefault();
      if (dragOverlay) dragOverlay.classList.remove('active');
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        if (file.type.startsWith('audio/')) {
          this.audioEngine.loadAudioFile(file);
          this._showToast(`Dropped Audio: ${file.name}`);
          this._updateActiveSourceCard('card-file');
        } else if (file.type.startsWith('image/')) {
          const url = URL.createObjectURL(file);
          const img = new Image();
          img.onload = () => {
            this.bgImage = img;
            this.bgName = file.name;
            this._showToast(`Dropped Wallpaper: ${file.name}`);
          };
          img.src = url;
        }
      }
    });
  }

  _setupShortcuts() {
    window.addEventListener('keydown', (e) => {
      // Ignore if typing in an input
      if (['INPUT', 'SELECT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
        return;
      }

      const key = e.key.toUpperCase();

      if (key === 'V') {
        if (e.shiftKey) {
          this.cycleStyle(-1);
        } else {
          this.cycleStyle(1);
        }
      } else if (key === 'C') {
        this.cycleStyle(-1);
      } else if (key === 'T') {
        this.cycleTheme(1);
      } else if (key === 'B') {
        const fileBg = document.getElementById('bg-file-input');
        if (fileBg) fileBg.click();
      } else if (key === 'S') {
        this.cycleShake();
      } else if (key === 'O') {
        this.cycleTint();
      } else if (key === 'L') {
        this.toggleLogo();
      } else if (key === 'D') {
        this.cycleAudioSource();
      } else if (key === 'F') {
        const fileAudio = document.getElementById('audio-file-input');
        if (fileAudio) fileAudio.click();
      } else if (key === 'F11') {
        e.preventDefault();
        this.toggleFullscreen();
      } else if (key === 'H') {
        this.toggleHud();
      } else if (e.code === 'Space') {
        e.preventDefault();
        const playing = this.audioEngine.togglePlayPause();
        this._showToast(playing ? 'Playback Resumed' : 'Playback Paused');
      }
    });
  }

  cycleStyle(dir = 1) {
    this.styleIndex = (this.styleIndex + dir + VISUALIZER_STYLES.length) % VISUALIZER_STYLES.length;
    const styleSel = document.getElementById('style-select');
    if (styleSel) styleSel.value = this.styleIndex;
    this._showToast(`Style [${this.styleIndex + 1}/10]: ${this.currentStyle.name}`);
  }

  cycleTheme(dir = 1) {
    this.themeIndex = (this.themeIndex + dir + THEMES.length) % THEMES.length;
    const themeSel = document.getElementById('theme-select');
    if (themeSel) themeSel.value = this.themeIndex;
    this._showToast(`Theme [${this.themeIndex + 1}/10]: ${this.currentTheme.name}`);
  }

  cycleShake() {
    this.shakeIndex = (this.shakeIndex + 1) % SHAKE_LEVELS.length;
    this._showToast(`Shake: ${SHAKE_LEVELS[this.shakeIndex].name}`);
  }

  cycleTint() {
    this.overlayIndex = (this.overlayIndex + 1) % this.overlayAlphas.length;
    const pct = Math.round(this.overlayAlphas[this.overlayIndex] * 100);
    this._showToast(`Tint Dimness: ${pct}%`);
  }

  toggleLogo() {
    if (this.customLogoImage) {
      this.customLogoImage = null;
      this.showLogo = true;
      this._showToast('Reset to Default BLAZE Crest');
    } else {
      this.showLogo = !this.showLogo;
      this._showToast(this.showLogo ? 'Center Emblem: ON' : 'Center Emblem: OFF');
    }
  }

  toggleHud() {
    this.showHud = !this.showHud;
    const hud = document.getElementById('hud-panel');
    if (hud) {
      if (this.showHud) {
        hud.classList.remove('collapsed');
      } else {
        hud.classList.add('collapsed');
      }
    }
    this._showToast(this.showHud ? 'HUD: Visible' : 'HUD: Hidden (Press H)');
  }

  toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
      this._showToast('Fullscreen Enabled');
    } else {
      document.exitFullscreen().catch(() => {});
      this._showToast('Fullscreen Exited');
    }
  }

  async cycleAudioSource() {
    const modes = ['DEMO', 'SYSTEM', 'MIC'];
    const cur = this.audioEngine.sourceMode;
    let nextIdx = 0;
    if (cur === 'SYNTH_DEMO') nextIdx = 1;
    else if (cur === 'SYSTEM') nextIdx = 2;
    else if (cur === 'MIC') nextIdx = 0;

    if (nextIdx === 0) {
      this.audioEngine.startDemoBeat();
      this._showToast('Source: Built-in EDM Synth Demo');
      this._updateActiveSourceCard('card-demo');
    } else if (nextIdx === 1) {
      try {
        await this.audioEngine.startSystemAudio();
        this._showToast('Source: Live System / Tab Audio');
        this._updateActiveSourceCard('card-system');
      } catch (e) {
        this.audioEngine.startDemoBeat();
        this._updateActiveSourceCard('card-demo');
      }
    } else {
      try {
        await this.audioEngine.startMicrophone();
        this._showToast('Source: Live Microphone');
        this._updateActiveSourceCard('card-mic');
      } catch (e) {
        this.audioEngine.startDemoBeat();
        this._updateActiveSourceCard('card-demo');
      }
    }
  }

  _updateActiveSourceCard(cardId) {
    document.querySelectorAll('.source-card-btn').forEach(btn => btn.classList.remove('active'));
    const target = document.getElementById(cardId);
    if (target) target.classList.add('active');
  }

  _showToast(msg) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'toast-msg';
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('fadeout');
      setTimeout(() => toast.remove(), 300);
    }, 2200);
  }

  _formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  }

  // =========================================================================
  // BASS CAMERA SHAKE & PHYSICS
  // =========================================================================
  _updateBassShake(bassEnergy) {
    const mult = this.shakeMultiplier;
    if (mult <= 0.001) {
      this.shakeOffsetX = 0;
      this.shakeOffsetY = 0;
      this.shakeZoom = 1.0;
      return;
    }

    const bassDiff = Math.max(0.0, bassEnergy - this.lastBass);
    this.lastBass = bassEnergy;

    if (bassEnergy > 0.42 || bassDiff > 0.1) {
      this.shakeEnergy = Math.min(1.0, this.shakeEnergy + (bassEnergy * 0.55 + bassDiff * 0.9) * mult);
    }

    this.shakeEnergy *= 0.82;

    if (this.shakeEnergy > 0.01) {
      const intensity = this.shakeEnergy * 14.0 * mult;
      this.shakeOffsetX = (Math.random() * 2 - 1) * intensity;
      this.shakeOffsetY = (Math.random() * 2 - 1) * intensity;
      this.shakeZoom = 1.0 + (this.shakeEnergy * 0.038 * mult);
    } else {
      this.shakeOffsetX = 0;
      this.shakeOffsetY = 0;
      this.shakeZoom = 1.0;
    }
  }

  // =========================================================================
  // MAIN RENDER LOOP (60 FPS)
  // =========================================================================
  _startRenderLoop() {
    const loop = (timestamp) => {
      this._updateFps(timestamp);
      this._renderFrame();
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  _updateFps(now) {
    this.frameCount++;
    if (now - this.lastFpsUpdate >= 500) {
      this.fps = Math.round((this.frameCount * 1000) / (now - this.lastFpsUpdate));
      this.frameCount = 0;
      this.lastFpsUpdate = now;
      const fpsEl = document.getElementById('hud-fps');
      if (fpsEl) fpsEl.textContent = `${this.fps} FPS`;
    }
  }

  _renderFrame() {
    const { ctx, width, height } = this;
    const { freqs, bassEnergy, rms, isActive } = this.audioEngine.processFrame();

    this.timePhase += 0.035;
    this.rotationAngle = (this.rotationAngle + 0.35) % 360;

    // Update bass shake
    this._updateBassShake(bassEnergy);

    // Save context for camera shake
    ctx.save();
    if (Math.abs(this.shakeOffsetX) > 0.1 || Math.abs(this.shakeOffsetY) > 0.1 || Math.abs(this.shakeZoom - 1.0) > 0.001) {
      ctx.translate(width / 2, height / 2);
      ctx.scale(this.shakeZoom, this.shakeZoom);
      ctx.translate(-width / 2 + this.shakeOffsetX, -height / 2 + this.shakeOffsetY);
    }

    // 1. Background
    this._drawBackground(ctx, width, height);

    const scale = Math.min(width, height) / 950.0;
    const center = { x: width / 2, y: height / 2 };
    const rMinScaled = this.rMin * scale;
    const rMaxScaled = this.rMax * scale;
    const dynamicMinR = rMinScaled + (bassEnergy * 32.0 * scale);

    // Particle Burst Spawn on Kicks
    if (bassEnergy > 0.48) {
      this.rippleAlpha = Math.floor(230 * bassEnergy);
      this.rippleRadius = dynamicMinR * 0.82;
      if (this.particles.length < 280) {
        for (let i = 0; i < freqs.length; i += 4) {
          if (freqs[i] > 0.48 && Math.random() < 0.45) {
            const th = (i / freqs.length) * 2 * Math.PI;
            const px = center.x + dynamicMinR * Math.cos(th);
            const py = center.y + dynamicMinR * Math.sin(th);
            const speed = (3.5 + Math.random() * 5.5) * freqs[i] * scale;
            this.particles.push(new Particle(px, py, th, speed, this.currentTheme.particle, 25 + Math.floor(Math.random() * 25), (2.5 + Math.random() * 3.0) * scale));
          }
        }
      }
    }

    // 2. Expanding Shockwave Bass Ripple
    if (this.rippleAlpha > 5) {
      this.rippleRadius += (3.2 * scale);
      this.rippleAlpha = Math.max(0, this.rippleAlpha - 6);
      ctx.save();
      ctx.beginPath();
      ctx.arc(center.x, center.y, this.rippleRadius, 0, Math.PI * 2);
      ctx.strokeStyle = this.currentTheme.coreHalo;
      ctx.lineWidth = 4.0 * scale;
      ctx.stroke();
      ctx.restore();
    }

    // 3. Render Visualizer Waveform Style
    switch (this.styleIndex) {
      case 0:
        this._drawBlazeEars(ctx, center, dynamicMinR, rMaxScaled, scale, freqs, bassEnergy);
        break;
      case 1:
        this._drawBlazeFireSpikes(ctx, center, dynamicMinR, rMaxScaled, scale, freqs, bassEnergy);
        break;
      case 2:
        this._drawTrapNationBassRing(ctx, center, dynamicMinR, rMaxScaled, scale, freqs, bassEnergy);
        break;
      case 3:
        this._drawMonstercatStyle(ctx, center, dynamicMinR, rMaxScaled, scale, freqs, bassEnergy);
        break;
      case 4:
        this._drawHorizonDoubleMirror(ctx, center, width, height, scale, freqs, bassEnergy);
        break;
      case 5:
        this._drawVortexWormhole(ctx, center, dynamicMinR, rMaxScaled, scale, freqs, bassEnergy);
        break;
      case 6:
        this._drawHexagonCyberShield(ctx, center, dynamicMinR, rMaxScaled, scale, freqs, bassEnergy);
        break;
      case 7:
        this._drawOscilloscopeLaser(ctx, center, dynamicMinR, rMaxScaled, scale, freqs, bassEnergy);
        break;
      case 8:
        this._drawSmoothWaveform(ctx, center, dynamicMinR, rMaxScaled, scale, freqs);
        break;
      default:
        this._drawRadialBars(ctx, center, dynamicMinR, rMaxScaled, scale, freqs);
        break;
    }

    // 4. Center Ring & Brand Crest (except full-width styles like Horizon Double Mirror)
    if (this.styleIndex !== 4) {
      this._drawCenterBadge(ctx, center, dynamicMinR, scale, bassEnergy);
    }

    // 5. Update and render active particles
    const alive = [];
    for (const p of this.particles) {
      if (p.update()) {
        p.draw(ctx);
        alive.push(p);
      }
    }
    this.particles = alive;

    // Restore shake transform
    ctx.restore();

    // 6. Update UI Metrics in HUD
    this._updateHudMetrics(isActive, bassEnergy, rms);
  }

  _drawBackground(ctx, w, h) {
    if (this.bgImage && this.bgImage.complete && this.bgImage.naturalWidth > 0) {
      // Draw image cover
      const img = this.bgImage;
      const imgRatio = img.naturalWidth / img.naturalHeight;
      const screenRatio = w / h;
      let drawW, drawH, dx, dy;

      if (screenRatio > imgRatio) {
        drawW = w;
        drawH = w / imgRatio;
        dx = 0;
        dy = (h - drawH) / 2;
      } else {
        drawH = h;
        drawW = h * imgRatio;
        dx = (w - drawW) / 2;
        dy = 0;
      }
      ctx.drawImage(img, dx, dy, drawW, drawH);
    } else {
      // Radial gradient fallback
      const grad = ctx.createRadialGradient(w / 2, h / 2, 10, w / 2, h / 2, Math.max(w, h) * 0.75);
      grad.addColorStop(0.0, this.currentTheme.bg);
      grad.addColorStop(1.0, '#040408');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, w, h);
    }

    // Overlay tint
    const alpha = this.overlayAlphas[this.overlayIndex];
    if (alpha > 0) {
      ctx.fillStyle = `rgba(0, 0, 0, ${alpha})`;
      ctx.fillRect(0, 0, w, h);
    }

    // Vignette
    const vig = ctx.createRadialGradient(w / 2, h / 2, Math.min(w, h) * 0.25, w / 2, h / 2, Math.max(w, h) * 0.65);
    vig.addColorStop(0, 'rgba(0,0,0,0)');
    vig.addColorStop(0.7, 'rgba(0,0,0,0.3)');
    vig.addColorStop(1.0, 'rgba(0,0,0,0.85)');
    ctx.fillStyle = vig;
    ctx.fillRect(0, 0, w, h);
  }

  // =========================================================================
  // 🐾 STYLE 1: BLAZE EARS 2.0 (Dynamic Cyber Feline)
  // =========================================================================
  _drawBlazeEars(ctx, center, rMin, rMax, scale, freqs, bass) {
    const N = freqs.length;
    const trebleEnergy = freqs.slice(Math.floor(N * 0.65)).reduce((a, b) => a + b, 0) / (N * 0.35);
    const midEnergy = freqs.slice(Math.floor(N * 0.2), Math.floor(N * 0.65)).reduce((a, b) => a + b, 0) / (N * 0.45);

    // Dynamic twitch mechanics
    if (trebleEnergy > 0.45 && Math.random() < 0.35) {
      if (Math.random() < 0.5) {
        this.earTwitchLeft = Math.min(1.0, this.earTwitchLeft + 0.65);
      } else {
        this.earTwitchRight = Math.min(1.0, this.earTwitchRight + 0.65);
      }
    }

    this.earTwitchLeft *= 0.84;
    this.earTwitchRight *= 0.84;
    this.earFlare = (this.earFlare * 0.82) + (bass * 0.18);

    const leftPeak = 128.0 + (this.earTwitchLeft * 5.0) - (this.earFlare * 3.5);
    const rightPeak = 52.0 - (this.earTwitchRight * 5.0) + (this.earFlare * 3.5);

    const earBoost = 1.0 + (bass * 0.75) + (midEnergy * 0.35);
    const pointsOuter = [];
    const rib1 = [];
    const rib2 = [];

    for (let i = 0; i < N; i++) {
      const deg = (i / N) * 360.0;
      let envelope = 0.0;

      if (deg >= 0.0 && deg <= 180.0) {
        const dR = Math.abs((deg - rightPeak + 180) % 360 - 180);
        const earR = Math.exp(-Math.pow(dR / 20.5, 2));

        const dL = Math.abs((deg - leftPeak + 180) % 360 - 180);
        const earL = Math.exp(-Math.pow(dL / 20.5, 2));

        const dC = Math.abs((deg - 90.0 + 180) % 360 - 180);
        const saddle = 0.32 * Math.exp(-Math.pow(dC / 17.0, 2));

        let taper = 1.0;
        if (deg < 28.0) taper = Math.max(0.0, deg / 28.0);
        else if (deg > 152.0) taper = Math.max(0.0, (180.0 - deg) / 28.0);

        envelope = Math.max(0.0, ((earR + earL) * 1.45 - saddle) * taper);
      }

      const fVal = freqs[i];
      const earHeight = envelope * (95.0 * scale * earBoost);
      const audioWave = Math.pow(fVal, 0.82) * (70.0 * scale) * Math.max(0.25, envelope);
      const lowerBreath = (deg > 180.0 && deg < 360.0)
        ? (bass * 6.0 * scale) * (1.0 + 0.3 * Math.sin((deg * Math.PI) / 180 + this.timePhase * 2))
        : 0.0;

      const totalR = rMin + earHeight + audioWave + lowerBreath;
      const rad = (deg * Math.PI) / 180.0;

      const ox = center.x + totalR * Math.cos(rad);
      const oy = center.y - totalR * Math.sin(rad);
      pointsOuter.push({ x: ox, y: oy });

      // Inner acoustic ribs
      if (envelope > 0.35 && deg >= 0.0 && deg <= 180.0) {
        const r1 = rMin + (earHeight * 0.58) + (fVal * 25.0 * scale);
        rib1.push({ x: center.x + r1 * Math.cos(rad), y: center.y - r1 * Math.sin(rad) });

        const r2 = rMin + (earHeight * 0.28) + (fVal * 14.0 * scale);
        rib2.push({ x: center.x + r2 * Math.cos(rad), y: center.y - r2 * Math.sin(rad) });
      }
    }

    // Emit tip sparks
    if ((trebleEnergy > 0.45 || bass > 0.65) && this.particles.length < 260) {
      for (const peakDeg of [rightPeak, leftPeak]) {
        const pRad = (peakDeg * Math.PI) / 180.0;
        const tipR = rMin + (95.0 * scale * earBoost) + (trebleEnergy * 40.0 * scale);
        const tx = center.x + tipR * Math.cos(pRad);
        const ty = center.y - tipR * Math.sin(pRad);
        if (Math.random() < 0.6) {
          const ang = -pRad + (Math.random() * 0.8 - 0.4);
          const spd = (4.0 + Math.random() * 5.5) * scale;
          this.particles.push(new Particle(tx, ty, ang, spd, this.currentTheme.earRim || '#ffd700', 18 + Math.floor(Math.random() * 18), 3.0 * scale));
        }
      }
    }

    // 1. Silhouette Body Fill
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(pointsOuter[0].x, pointsOuter[0].y);
    for (let i = 1; i < pointsOuter.length; i++) {
      ctx.lineTo(pointsOuter[i].x, pointsOuter[i].y);
    }
    ctx.closePath();

    const bodyGrad = ctx.createLinearGradient(center.x, center.y - rMax * 1.1, center.x, center.y + rMin);
    bodyGrad.addColorStop(0.0, 'rgba(28, 16, 38, 0.95)');
    bodyGrad.addColorStop(0.5, 'rgba(12, 8, 20, 0.96)');
    bodyGrad.addColorStop(1.0, 'rgba(4, 4, 10, 0.85)');
    ctx.fillStyle = bodyGrad;
    ctx.fill();
    ctx.restore();

    // 2. Inner Neon Acoustic Ribs
    ctx.save();
    if (rib1.length > 4) {
      ctx.beginPath();
      ctx.moveTo(rib1[0].x, rib1[0].y);
      for (let j = 1; j < rib1.length; j++) ctx.lineTo(rib1[j].x, rib1[j].y);
      ctx.strokeStyle = this.currentTheme.earGlow;
      ctx.lineWidth = 2.2 * scale;
      ctx.lineCap = 'round';
      ctx.stroke();
    }
    if (rib2.length > 4) {
      ctx.beginPath();
      ctx.moveTo(rib2[0].x, rib2[0].y);
      for (let j = 1; j < rib2.length; j++) ctx.lineTo(rib2[j].x, rib2[j].y);
      ctx.strokeStyle = this.currentTheme.earRim;
      ctx.lineWidth = 1.8 * scale;
      ctx.lineCap = 'round';
      ctx.stroke();
    }
    ctx.restore();

    // 3. Multi-layer Glowing Neon Rim
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(pointsOuter[0].x, pointsOuter[0].y);
    for (let i = 1; i < pointsOuter.length; i++) {
      ctx.lineTo(pointsOuter[i].x, pointsOuter[i].y);
    }
    ctx.closePath();

    // Glow bloom
    ctx.strokeStyle = this.currentTheme.earGlow;
    ctx.lineWidth = 16.0 * scale;
    ctx.globalAlpha = 0.28;
    ctx.lineJoin = 'round';
    ctx.stroke();

    ctx.lineWidth = 6.0 * scale;
    ctx.globalAlpha = 0.65;
    ctx.stroke();

    // Sharp outer neon line
    ctx.strokeStyle = this.currentTheme.earRim || '#ffffff';
    ctx.lineWidth = 3.6 * scale;
    ctx.globalAlpha = 1.0;
    ctx.stroke();
    ctx.restore();
  }

  // =========================================================================
  // 🔥 STYLE 2: BLAZE FIRE SPIKES (Solar Flare)
  // =========================================================================
  _drawBlazeFireSpikes(ctx, center, rMin, rMax, scale, freqs, bass) {
    const numSpikes = 180;
    const step = Math.floor(freqs.length / numSpikes);

    ctx.save();
    for (let i = 0; i < numSpikes; i++) {
      const f = freqs[Math.min(freqs.length - 1, i * step)];
      const angle = (i / numSpikes) * 2 * Math.PI;
      const flutter = Math.sin(i * 0.45 + this.timePhase * 6.0) * (12.0 * scale);
      const flameLen = Math.pow(f, 0.75) * (rMax - rMin) * 1.35 * (1.0 + bass * 0.6) + flutter;
      const rOut = rMin + Math.max(0.0, flameLen);

      const x1 = center.x + rMin * Math.cos(angle);
      const y1 = center.y + rMin * Math.sin(angle);
      const x2 = center.x + rOut * Math.cos(angle);
      const y2 = center.y + rOut * Math.sin(angle);

      // Outer wide glow ray
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.strokeStyle = this.currentTheme.particle;
      ctx.lineWidth = 7.0 * scale;
      ctx.globalAlpha = 0.25;
      ctx.stroke();

      // Sharp flame needle
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.strokeStyle = this.currentTheme.coreCenter;
      ctx.lineWidth = 2.8 * scale;
      ctx.globalAlpha = 0.95;
      ctx.stroke();

      // Flaming tip bead on loud transients
      if (f > 0.45) {
        ctx.beginPath();
        ctx.arc(x2, y2, (3.5 + f * 4.0) * scale, 0, Math.PI * 2);
        ctx.fillStyle = this.currentTheme.ring;
        ctx.globalAlpha = 1.0;
        ctx.fill();
      }
    }
    ctx.restore();
  }

  // =========================================================================
  // ⚡ STYLE 3: TRAP NATION BASS RING
  // =========================================================================
  _drawTrapNationBassRing(ctx, center, rMin, rMax, scale, freqs, bass) {
    const numBars = 160;
    const step = Math.floor(freqs.length / numBars);

    ctx.save();
    for (let i = 0; i < numBars; i++) {
      const f = freqs[Math.min(freqs.length - 1, i * step)];
      const angle = (i / numBars) * 2 * Math.PI;
      const rOut = rMin + Math.pow(f, 0.8) * (rMax - rMin) * (1.0 + bass * 0.45);

      const x1 = center.x + rMin * Math.cos(angle);
      const y1 = center.y + rMin * Math.sin(angle);
      const x2 = center.x + rOut * Math.cos(angle);
      const y2 = center.y + rOut * Math.sin(angle);

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.strokeStyle = this.currentTheme.particle;
      ctx.lineWidth = 3.2 * scale;
      ctx.lineCap = 'round';
      ctx.globalAlpha = 0.95;
      ctx.stroke();
    }
    ctx.restore();
  }

  // =========================================================================
  // 🐱 STYLE 4: MONSTERCAT DUAL SPECTRUM ARC
  // =========================================================================
  _drawMonstercatStyle(ctx, center, rMin, rMax, scale, freqs, bass) {
    const halfN = Math.floor(freqs.length / 2);

    ctx.save();
    for (let i = 0; i < halfN; i++) {
      const f = freqs[i];
      const thL = Math.PI / 2 + (i / halfN) * (Math.PI / 2);
      const thR = Math.PI / 2 - (i / halfN) * (Math.PI / 2);
      const h = Math.pow(f, 0.85) * (rMax - rMin) * (1.15 + bass * 0.35);

      for (const th of [thL, thR]) {
        const x1 = center.x + rMin * Math.cos(th);
        const y1 = center.y - rMin * Math.sin(th);
        const x2 = center.x + (rMin + h) * Math.cos(th);
        const y2 = center.y - (rMin + h) * Math.sin(th);

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.strokeStyle = this.currentTheme.earGlow;
        ctx.lineWidth = 3.6 * scale;
        ctx.lineCap = 'round';
        ctx.stroke();
      }
    }
    ctx.restore();
  }

  // =========================================================================
  // 🌆 STYLE 5: HORIZON DOUBLE MIRROR (Cyber Skyline)
  // =========================================================================
  _drawHorizonDoubleMirror(ctx, center, w, h, scale, freqs, bass) {
    const numBars = 120;
    const step = Math.floor(freqs.length / numBars);
    const barW = (w * 0.92) / numBars;
    const startX = w * 0.04;
    const midY = h * 0.52;
    const maxH = h * 0.38;

    ctx.save();
    // Baseline glow
    ctx.beginPath();
    ctx.moveTo(startX, midY);
    ctx.lineTo(w - startX, midY);
    ctx.strokeStyle = this.currentTheme.ring;
    ctx.lineWidth = 2.5 * scale;
    ctx.stroke();

    for (let i = 0; i < numBars; i++) {
      const f = freqs[Math.min(freqs.length - 1, i * step)];
      const barH = Math.pow(f, 0.85) * maxH * (1.0 + bass * 0.4);
      const bx = startX + i * barW;

      // Upper Skyline Bar
      const grad = ctx.createLinearGradient(0, midY - barH, 0, midY);
      grad.addColorStop(0, this.currentTheme.coreCenter);
      grad.addColorStop(1, this.currentTheme.particle);
      ctx.fillStyle = grad;
      ctx.fillRect(bx, midY - barH, barW * 0.78, barH);

      // Lower Reflection Floor
      ctx.fillStyle = this.currentTheme.particle;
      ctx.globalAlpha = 0.28;
      ctx.fillRect(bx, midY + 2, barW * 0.78, barH * 0.65);
      ctx.globalAlpha = 1.0;

      // Floating peak beacon
      if (f > 0.4) {
        ctx.beginPath();
        ctx.arc(bx + (barW * 0.78) / 2.0, midY - barH - 4.0 * scale, 2.5 * scale, 0, Math.PI * 2);
        ctx.fillStyle = this.currentTheme.ring;
        ctx.fill();
      }
    }
    ctx.restore();
  }

  // =========================================================================
  // 🌀 STYLE 6: VORTEX WORMHOLE (3D Audio Tunnel)
  // =========================================================================
  _drawVortexWormhole(ctx, center, rMin, rMax, scale, freqs, bass) {
    const numRings = 9;
    ctx.save();

    for (let ringI = 0; ringI < numRings; ringI++) {
      const depth = (ringI + 1) / numRings;
      const ringR = rMin * depth * 2.1 + (bass * 35.0 * scale * depth);
      const rot = this.rotationAngle * (ringI % 2 === 0 ? 1 : -1) * (1.0 + depth);

      const numPts = 64;
      const step = Math.floor(freqs.length / numPts);
      const pts = [];

      for (let p = 0; p < numPts; p++) {
        const f = freqs[Math.min(freqs.length - 1, p * step)];
        const ang = (p / numPts) * 2 * Math.PI + (rot * Math.PI) / 180;
        const deform = Math.pow(f, 0.9) * (45.0 * scale * depth);
        const currR = ringR + deform;
        pts.push({
          x: center.x + currR * Math.cos(ang),
          y: center.y + currR * Math.sin(ang)
        });
      }

      if (pts.length > 2) {
        ctx.beginPath();
        ctx.moveTo(pts[0].x, pts[0].y);
        for (let j = 1; j < pts.length; j++) ctx.lineTo(pts[j].x, pts[j].y);
        ctx.closePath();
        ctx.strokeStyle = this.currentTheme.particle;
        ctx.lineWidth = (2.0 + depth * 2.5) * scale;
        ctx.globalAlpha = depth * 0.9;
        ctx.stroke();
      }
    }
    ctx.restore();
  }

  // =========================================================================
  // 🛡️ STYLE 7: HEXAGON CYBER SHIELD (Matrix Pulse)
  // =========================================================================
  _drawHexagonCyberShield(ctx, center, rMin, rMax, scale, freqs, bass) {
    const hexSides = 6;
    const hexPts = [];
    const hexR = rMin * 1.35 + (bass * 28.0 * scale);

    for (let s = 0; s < hexSides; s++) {
      const ang = ((60 * s + this.rotationAngle * 0.5) * Math.PI) / 180.0;
      hexPts.push({
        x: center.x + hexR * Math.cos(ang),
        y: center.y + hexR * Math.sin(ang)
      });
    }

    ctx.save();
    // Draw Hex Hull
    ctx.beginPath();
    ctx.moveTo(hexPts[0].x, hexPts[0].y);
    for (let s = 1; s < hexSides; s++) ctx.lineTo(hexPts[s].x, hexPts[s].y);
    ctx.closePath();
    ctx.strokeStyle = this.currentTheme.ring;
    ctx.lineWidth = 3.5 * scale;
    ctx.stroke();

    // Edge Equalizers
    const step = Math.floor(freqs.length / hexSides);
    for (let s = 0; s < hexSides; s++) {
      const p1 = hexPts[s];
      const p2 = hexPts[(s + 1) % hexSides];
      const subBars = 16;

      for (let b = 0; b < subBars; b++) {
        const t = (b + 0.5) / subBars;
        const bx = p1.x + t * (p2.x - p1.x);
        const by = p1.y + t * (p2.y - p1.y);

        const f = freqs[Math.min(freqs.length - 1, s * step + b * 2)];
        const dx = p2.x - p1.x;
        const dy = p2.y - p1.y;
        const dist = Math.hypot(dx, dy) + 1e-5;
        const nx = -dy / dist;
        const ny = dx / dist;

        const burstLen = Math.pow(f, 0.85) * (70.0 * scale) * (1.0 + bass * 0.5);
        const ex = bx + nx * burstLen;
        const ey = by + ny * burstLen;

        ctx.beginPath();
        ctx.moveTo(bx, by);
        ctx.lineTo(ex, ey);
        ctx.strokeStyle = this.currentTheme.particle;
        ctx.lineWidth = 2.8 * scale;
        ctx.lineCap = 'round';
        ctx.stroke();
      }
    }
    ctx.restore();
  }

  // =========================================================================
  // ⚡ STYLE 8: OSCILLOSCOPE LASER (Lightning Wave)
  // =========================================================================
  _drawOscilloscopeLaser(ctx, center, rMin, rMax, scale, freqs, bass) {
    const N = freqs.length;
    const radOffset = (this.rotationAngle * Math.PI) / 180.0;
    const pts = [];

    for (let i = 0; i < N; i++) {
      const th = (i / N) * 2 * Math.PI;
      const osc = Math.sin(th * 12.0 + this.timePhase * 4.0) * (freqs[i] * 55.0 * scale);
      const r = rMin + osc + (freqs[i] * (rMax - rMin) * 0.75);
      pts.push({
        x: center.x + r * Math.cos(th + radOffset),
        y: center.y + r * Math.sin(th + radOffset)
      });
    }

    if (pts.length > 2) {
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(pts[0].x, pts[0].y);
      for (let j = 1; j < pts.length; j++) ctx.lineTo(pts[j].x, pts[j].y);
      ctx.closePath();

      // Outer Laser Bloom
      ctx.strokeStyle = this.currentTheme.particle;
      ctx.lineWidth = 14.0 * scale;
      ctx.globalAlpha = 0.35;
      ctx.lineJoin = 'round';
      ctx.stroke();

      // Sharp Core
      ctx.strokeStyle = this.currentTheme.ring;
      ctx.lineWidth = 3.0 * scale;
      ctx.globalAlpha = 1.0;
      ctx.stroke();
      ctx.restore();
    }
  }

  // =========================================================================
  // 🌊 STYLE 9: SMOOTH WAVEFORM 360
  // =========================================================================
  _drawSmoothWaveform(ctx, center, rMin, rMax, scale, freqs) {
    const N = freqs.length;
    const radOffset = (this.rotationAngle * Math.PI) / 180.0;
    const pts = [];

    for (let i = 0; i < N; i++) {
      const th = (i / N) * 2 * Math.PI;
      const r = rMin + (freqs[i] * (rMax - rMin));
      pts.push({
        x: center.x + r * Math.cos(th + radOffset),
        y: center.y + r * Math.sin(th + radOffset)
      });
    }

    if (pts.length > 2) {
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(pts[0].x, pts[0].y);
      for (let j = 1; j < pts.length; j++) ctx.lineTo(pts[j].x, pts[j].y);
      ctx.closePath();

      ctx.strokeStyle = this.currentTheme.particle;
      ctx.lineWidth = 9.0 * scale;
      ctx.globalAlpha = 0.3;
      ctx.stroke();

      ctx.lineWidth = 3.2 * scale;
      ctx.globalAlpha = 1.0;
      ctx.stroke();
      ctx.restore();
    }
  }

  // =========================================================================
  // 📊 STYLE 10: RADIAL EQUALIZER BARS
  // =========================================================================
  _drawRadialBars(ctx, center, rMin, rMax, scale, freqs) {
    const numBars = 180;
    const step = Math.floor(freqs.length / numBars);

    ctx.save();
    for (let i = 0; i < numBars; i++) {
      const f = freqs[Math.min(freqs.length - 1, i * step)];
      const angle = (i / numBars) * 2 * Math.PI;
      const rOut = rMin + f * (rMax - rMin);

      const x1 = center.x + rMin * Math.cos(angle);
      const y1 = center.y + rMin * Math.sin(angle);
      const x2 = center.x + rOut * Math.cos(angle);
      const y2 = center.y + rOut * Math.sin(angle);

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.strokeStyle = this.currentTheme.particle;
      ctx.lineWidth = 2.8 * scale;
      ctx.lineCap = 'round';
      ctx.stroke();
    }
    ctx.restore();
  }

  // =========================================================================
  // 🌟 CENTER BADGE & BLAZE BRANDING
  // =========================================================================
  _drawCenterBadge(ctx, center, rMin, scale, bass) {
    ctx.save();
    // 1. Center backdrop disc
    ctx.beginPath();
    ctx.arc(center.x, center.y, rMin, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(8, 8, 16, 0.88)';
    ctx.fill();

    // 2. Custom logo or BLAZE brand crest
    if (this.showLogo) {
      if (this.customLogoImage && this.customLogoImage.complete) {
        const logoSize = rMin * 1.4;
        ctx.drawImage(
          this.customLogoImage,
          center.x - logoSize / 2,
          center.y - logoSize / 2,
          logoSize,
          logoSize
        );
      } else {
        this._drawBlazeCrest(ctx, center, rMin, scale, bass);
      }
    }

    // 3. Glowing Center Ring Outline
    ctx.beginPath();
    ctx.arc(center.x, center.y, rMin, 0, Math.PI * 2);
    ctx.strokeStyle = this.currentTheme.ring;
    ctx.lineWidth = 4.2 * scale;
    ctx.stroke();

    ctx.lineWidth = 10.0 * scale;
    ctx.globalAlpha = 0.35;
    ctx.stroke();
    ctx.restore();
  }

  _drawBlazeCrest(ctx, center, rMin, scale, bass) {
    ctx.save();
    // Pulsating halo
    const coreR = rMin * (0.72 + bass * 0.12);
    const radGlow = ctx.createRadialGradient(center.x, center.y, 5, center.x, center.y, coreR * 1.25);
    radGlow.addColorStop(0.0, this.currentTheme.coreCenter);
    radGlow.addColorStop(0.7, 'rgba(0,0,0,0)');
    ctx.fillStyle = radGlow;
    ctx.globalAlpha = 0.85;
    ctx.beginPath();
    ctx.arc(center.x, center.y, coreR * 1.25, 0, Math.PI * 2);
    ctx.fill();

    // Cyber Flame Crest
    const flameSize = 28.0 * scale * (1.0 + bass * 0.18);
    const cx = center.x;
    const cy = center.y - 14.0 * scale;

    ctx.beginPath();
    ctx.moveTo(cx, cy - flameSize);
    ctx.bezierCurveTo(cx + flameSize * 0.85, cy - flameSize * 0.3, cx + flameSize * 0.75, cy + flameSize * 0.65, cx, cy + flameSize * 0.85);
    ctx.bezierCurveTo(cx - flameSize * 0.75, cy + flameSize * 0.65, cx - flameSize * 0.85, cy - flameSize * 0.3, cx, cy - flameSize);
    ctx.closePath();

    const flameGrad = ctx.createLinearGradient(cx, cy - flameSize, cx, cy + flameSize);
    flameGrad.addColorStop(0.0, this.currentTheme.earRim || '#ffc832');
    flameGrad.addColorStop(1.0, this.currentTheme.earGlow || '#ff3700');
    ctx.fillStyle = flameGrad;
    ctx.globalAlpha = 1.0;
    ctx.fill();

    // Inner White Flame Core
    const innerSize = flameSize * 0.48;
    ctx.beginPath();
    ctx.moveTo(cx, cy - innerSize * 0.7);
    ctx.bezierCurveTo(cx + innerSize * 0.7, cy, cx + innerSize * 0.5, cy + innerSize * 0.6, cx, cy + innerSize * 0.75);
    ctx.bezierCurveTo(cx - innerSize * 0.5, cy + innerSize * 0.6, cx - innerSize * 0.7, cy, cx, cy - innerSize * 0.7);
    ctx.closePath();
    ctx.fillStyle = '#ffffff';
    ctx.fill();

    // Typography "BLAZE"
    ctx.fillStyle = this.currentTheme.ring || '#ffffff';
    ctx.font = `900 ${Math.floor(22 * scale)}px Orbitron, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('BLAZE', center.x, center.y + 30.0 * scale);

    // Subtext "AUDIO ENGINE"
    ctx.fillStyle = 'rgba(200, 205, 225, 0.85)';
    ctx.font = `700 ${Math.floor(8.5 * scale)}px Rajdhani, sans-serif`;
    ctx.fillText('AUDIO ENGINE', center.x, center.y + 46.0 * scale);

    ctx.restore();
  }

  _updateHudMetrics(isActive, bassEnergy, rms) {
    if (!this.showHud) return;

    const dot = document.getElementById('hud-status-dot');
    const badgeText = document.getElementById('hud-status-text');
    if (dot && badgeText) {
      if (isActive) {
        dot.classList.add('active');
        badgeText.textContent = 'BLAZE ACTIVE';
      } else {
        dot.classList.remove('active');
        badgeText.textContent = 'LISTENING...';
      }
    }

    const trackEl = document.getElementById('hud-track');
    if (trackEl) trackEl.textContent = this.audioEngine.trackName;

    const bassBar = document.getElementById('hud-bass-meter');
    if (bassBar) {
      bassBar.style.width = `${Math.min(100, Math.round(bassEnergy * 100))}%`;
    }

    const rmsEl = document.getElementById('hud-rms');
    if (rmsEl) rmsEl.textContent = rms.toFixed(4);
  }
}

// Initialize application on DOM ready
window.addEventListener('DOMContentLoaded', () => {
  window.blazeApp = new BlazeVisualizerApp();
});
