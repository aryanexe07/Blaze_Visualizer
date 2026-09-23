/**
 * 🔥 BLAZE Audio Visualizer — Preset Themes & Visualizer Styles
 */

export const THEMES = [
  {
    id: "blaze-inferno",
    name: "Blaze Inferno",
    bg: "#160a06",
    coreCenter: "#ff3c00",
    coreHalo: "rgba(255, 140, 0, 0.4)",
    earGlow: "#ff3700",
    earRim: "#ffbe28",
    gradient: [
      { stop: 0.0, color: "#ff3700" },
      { stop: 0.3, color: "#ffa000" },
      { stop: 0.6, color: "#ff0046" },
      { stop: 0.85, color: "#ffc832" },
      { stop: 1.0, color: "#ff3700" }
    ],
    ring: "#ffebd2",
    maxbar: "rgba(255, 180, 0, 0.8)",
    particle: "#ff7800"
  },
  {
    id: "uk-rave",
    name: "UK Rave / Acid Underground",
    bg: "#0a0816",
    coreCenter: "#39ff14",
    coreHalo: "rgba(190, 0, 255, 0.38)",
    earGlow: "#39ff14",
    earRim: "#faff00",
    gradient: [
      { stop: 0.0, color: "#39ff14" },
      { stop: 0.25, color: "#faff00" },
      { stop: 0.5, color: "#dc00ff" },
      { stop: 0.75, color: "#00f0ff" },
      { stop: 1.0, color: "#39ff14" }
    ],
    ring: "#ffffff",
    maxbar: "rgba(57, 255, 20, 0.8)",
    particle: "#39ff14"
  },
  {
    id: "monochrome-noir",
    name: "Monochrome Noir (B&W)",
    bg: "#08080a",
    coreCenter: "#ffffff",
    coreHalo: "rgba(200, 200, 210, 0.35)",
    earGlow: "#ffffff",
    earRim: "#e6ebf5",
    gradient: [
      { stop: 0.0, color: "#ffffff" },
      { stop: 0.3, color: "#8c919b" },
      { stop: 0.6, color: "#e1e6f0" },
      { stop: 0.85, color: "#5a5f69" },
      { stop: 1.0, color: "#ffffff" }
    ],
    ring: "#ffffff",
    maxbar: "rgba(255, 255, 255, 0.85)",
    particle: "#f0f0fa"
  },
  {
    id: "cyberpunk-overdrive",
    name: "Cyberpunk Overdrive",
    bg: "#0e0a18",
    coreCenter: "#00f0ff",
    coreHalo: "rgba(255, 0, 127, 0.38)",
    earGlow: "#ff007f",
    earRim: "#00f0ff",
    gradient: [
      { stop: 0.0, color: "#ff007f" },
      { stop: 0.25, color: "#9d00ff" },
      { stop: 0.5, color: "#00f0ff" },
      { stop: 0.75, color: "#ff007f" },
      { stop: 1.0, color: "#ff007f" }
    ],
    ring: "#ffffff",
    maxbar: "rgba(0, 240, 255, 0.75)",
    particle: "#ff007f"
  },
  {
    id: "tokyo-neon",
    name: "Tokyo Neon",
    bg: "#120a1c",
    coreCenter: "#ff50ff",
    coreHalo: "rgba(160, 30, 240, 0.38)",
    earGlow: "#ff28a0",
    earRim: "#ffb4ff",
    gradient: [
      { stop: 0.0, color: "#ff28a0" },
      { stop: 0.35, color: "#8c1eff" },
      { stop: 0.7, color: "#ffb4ff" },
      { stop: 1.0, color: "#ff28a0" }
    ],
    ring: "#fff0ff",
    maxbar: "rgba(255, 120, 255, 0.75)",
    particle: "#ff46c8"
  },
  {
    id: "matrix-emerald",
    name: "Matrix Emerald",
    bg: "#08140e",
    coreCenter: "#00ffaa",
    coreHalo: "rgba(0, 180, 80, 0.38)",
    earGlow: "#00ffaa",
    earRim: "#82ffd2",
    gradient: [
      { stop: 0.0, color: "#00ffaa" },
      { stop: 0.35, color: "#00beff" },
      { stop: 0.7, color: "#3cff64" },
      { stop: 1.0, color: "#00ffaa" }
    ],
    ring: "#ebfff5",
    maxbar: "rgba(0, 255, 170, 0.75)",
    particle: "#00ffaa"
  },
  {
    id: "deep-abyss",
    name: "Deep Abyss (Bioluminescent)",
    bg: "#060c18",
    coreCenter: "#00e5ff",
    coreHalo: "rgba(0, 110, 255, 0.35)",
    earGlow: "#00f5d4",
    earRim: "#0082ff",
    gradient: [
      { stop: 0.0, color: "#00f5d4" },
      { stop: 0.35, color: "#008cff" },
      { stop: 0.7, color: "#7846ff" },
      { stop: 1.0, color: "#00f5d4" }
    ],
    ring: "#e6f8ff",
    maxbar: "rgba(0, 229, 255, 0.75)",
    particle: "#00f5d4"
  },
  {
    id: "sunset-horizon",
    name: "Sunset Horizon",
    bg: "#160c12",
    coreCenter: "#ffb703",
    coreHalo: "rgba(251, 133, 0, 0.38)",
    earGlow: "#ff006e",
    earRim: "#ffb703",
    gradient: [
      { stop: 0.0, color: "#ff006e" },
      { stop: 0.33, color: "#fb8500" },
      { stop: 0.66, color: "#8338ec" },
      { stop: 1.0, color: "#ff006e" }
    ],
    ring: "#fff5eb",
    maxbar: "rgba(255, 183, 3, 0.75)",
    particle: "#fb8500"
  },
  {
    id: "ghost-void",
    name: "Ghost Void / Amethyst",
    bg: "#100a1a",
    coreCenter: "#be78ff",
    coreHalo: "rgba(130, 40, 220, 0.35)",
    earGlow: "#d8b4fe",
    earRim: "#ffffff",
    gradient: [
      { stop: 0.0, color: "#d8b4fe" },
      { stop: 0.35, color: "#823cf0" },
      { stop: 0.7, color: "#f5ebff" },
      { stop: 1.0, color: "#d8b4fe" }
    ],
    ring: "#f5f0ff",
    maxbar: "rgba(216, 180, 254, 0.75)",
    particle: "#d8b4fe"
  },
  {
    id: "blood-moon",
    name: "Blood Moon / Crimson",
    bg: "#180608",
    coreCenter: "#ff1744",
    coreHalo: "rgba(180, 0, 30, 0.38)",
    earGlow: "#ff1744",
    earRim: "#ff9100",
    gradient: [
      { stop: 0.0, color: "#ff1744" },
      { stop: 0.35, color: "#ff6e00" },
      { stop: 0.7, color: "#8c0019" },
      { stop: 1.0, color: "#ff1744" }
    ],
    ring: "#ffe6e6",
    maxbar: "rgba(255, 23, 68, 0.8)",
    particle: "#ff1744"
  }
];

export const VISUALIZER_STYLES = [
  { id: "blaze-ears", name: "Blaze Ears 2.0 (Cyber Feline)" },
  { id: "blaze-spikes", name: "Blaze Fire Spikes (Solar Flare)" },
  { id: "bass-ring", name: "Bass Pulse Ring (Trap Nation)" },
  { id: "dual-spectrum", name: "Dual Spectrum Arc (Monstercat)" },
  { id: "horizon-mirror", name: "Horizon Double Mirror (Cyber Skyline)" },
  { id: "vortex-tunnel", name: "Vortex Wormhole (3D Audio Tunnel)" },
  { id: "hexagon-shield", name: "Hexagon Cyber Shield (Matrix Pulse)" },
  { id: "laser-oscilloscope", name: "Oscilloscope Laser (Lightning Wave)" },
  { id: "smooth-wave", name: "Smooth Waveform 360" },
  { id: "radial-bars", name: "Radial Equalizer Bars" }
];

export const SHAKE_LEVELS = [
  { id: "heavy", name: "Heavy (Bass Vibrate)", multiplier: 1.0 },
  { id: "intense", name: "Intense (Earthquake)", multiplier: 1.6 },
  { id: "subtle", name: "Subtle", multiplier: 0.5 },
  { id: "off", name: "Off", multiplier: 0.0 }
];
