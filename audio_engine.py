"""
Audio Engine for Real-Time Circular Audio Visualizer
Handles:
- Native Windows WASAPI Loopback capture (recording laptop speakers / headphones output directly)
- Zero-dropout circular buffer streaming
- Real-time FFT analysis, logarithmic frequency binning, and temporal smoothing
- Bass energy & kick beat transient detection
"""

import sys
import threading
import time
import numpy as np

# Try importing soundcard for native WASAPI loopback support
try:
    import soundcard as sc
    SOUNDCARD_AVAILABLE = True
except ImportError:
    SOUNDCARD_AVAILABLE = False

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False


class AudioEngine:
    def __init__(self, fft_size=2048, sample_rate=48000, num_bins=360, smoothing=0.30):
        self.fft_size = fft_size
        self.sample_rate = sample_rate
        self.num_bins = num_bins
        self.smoothing = smoothing
        
        # Audio buffers
        self.buffer = np.zeros(self.fft_size, dtype=np.float32)
        self.lock = threading.Lock()
        
        # Output metrics
        self.smoothed_freqs = np.zeros(self.num_bins, dtype=np.float32)
        self.bass_energy = 0.0
        self.smoothed_bass = 0.0
        self.rms_volume = 0.0
        self.is_playing = False
        
        # Dynamic Auto-gain
        self.max_observed = 1e-3
        
        # Device & Thread state
        self.device_id = None
        self.device_name = "Default System Audio"
        self.is_loopback = True
        self.is_running = False
        self.capture_thread = None
        self.sd_stream = None

    @staticmethod
    def get_audio_devices():
        """Returns list of all available loopback and input audio devices, prioritizing system loopback."""
        devices = []
        seen_ids = set()

        # 1. Use soundcard for native WASAPI Loopback devices
        if SOUNDCARD_AVAILABLE:
            try:
                def_spk = sc.default_speaker()
                if def_spk:
                    dev_id = f"sc_loop_{def_spk.name}"
                    devices.append({
                        'id': dev_id,
                        'name': f"[System Audio] {def_spk.name} (Loopback)",
                        'type': 'soundcard',
                        'sc_name': def_spk.name,
                        'is_loopback': True,
                        'priority': 0
                    })
                    seen_ids.add(dev_id)

                all_mics = sc.all_microphones(include_loopback=True)
                for mic in all_mics:
                    dev_id = f"sc_{'loop' if mic.isloopback else 'mic'}_{mic.name}"
                    if dev_id not in seen_ids:
                        seen_ids.add(dev_id)
                        prefix = "[System Audio]" if mic.isloopback else "[Mic/Input]"
                        devices.append({
                            'id': dev_id,
                            'name': f"{prefix} {mic.name}",
                            'type': 'soundcard',
                            'sc_name': mic.name,
                            'is_loopback': mic.isloopback,
                            'priority': 1 if mic.isloopback else 4
                        })
            except Exception as e:
                print(f"[AudioEngine] soundcard query exception: {e}")

        # 2. Add sounddevice inputs as fallback
        if SOUNDDEVICE_AVAILABLE:
            try:
                sd_devs = sd.query_devices()
                for idx, dev in enumerate(sd_devs):
                    if dev.get('max_input_channels', 0) > 0:
                        name = dev.get('name', '')
                        dev_id = f"sd_{idx}"
                        if "Stereo Mix" in name:
                            devices.append({
                                'id': dev_id,
                                'name': f"[Stereo Mix] {name}",
                                'type': 'sounddevice',
                                'sd_index': idx,
                                'is_loopback': False,
                                'priority': 2
                            })
                        else:
                            devices.append({
                                'id': dev_id,
                                'name': f"[SoundDevice] {name}",
                                'type': 'sounddevice',
                                'sd_index': idx,
                                'is_loopback': False,
                                'priority': 5
                            })
            except Exception as e:
                print(f"[AudioEngine] sounddevice query exception: {e}")

        devices.sort(key=lambda x: x.get('priority', 99))
        return devices

    def find_best_default_device(self):
        """Finds the optimal capture device, defaulting to the laptop's active speaker/headphones loopback."""
        devs = self.get_audio_devices()
        if devs:
            return devs[0]
        return None

    def start(self, device_id=None, device_info=None):
        """Starts real-time audio capture stream on selected device or default laptop output."""
        self.stop()
        
        target = device_info
        if target is None:
            if device_id is not None:
                for d in self.get_audio_devices():
                    if d['id'] == device_id or str(d.get('sd_index')) == str(device_id):
                        target = d
                        break
            if target is None:
                target = self.find_best_default_device()

        if target is None:
            print("[AudioEngine] No audio capture devices found.")
            return False

        self.device_id = target.get('id')
        self.device_name = target.get('name', 'Default Audio')
        self.is_loopback = target.get('is_loopback', True)

        # Launch appropriate backend
        if target.get('type') == 'soundcard' and SOUNDCARD_AVAILABLE:
            success = self._start_soundcard_stream(target)
            if success:
                print(f"[AudioEngine] Successfully listening to PC System Audio on: {self.device_name} ({self.sample_rate}Hz)")
                return True

        # Fallback to sounddevice
        if SOUNDDEVICE_AVAILABLE:
            success = self._start_sounddevice_stream(target)
            if success:
                print(f"[AudioEngine] Connected via sounddevice on: {self.device_name}")
                return True

        print(f"[AudioEngine] Failed to connect to {self.device_name}")
        return False

    def _start_soundcard_stream(self, dev_info):
        """Starts native WASAPI Loopback / soundcard recording thread."""
        try:
            sc_name = dev_info.get('sc_name')
            is_loop = dev_info.get('is_loopback', True)
            
            mic = None
            if sc_name:
                try:
                    mic = sc.get_microphone(id=sc_name, include_loopback=True)
                except Exception:
                    pass

            if mic is None:
                if is_loop:
                    spk = sc.default_speaker()
                    mic = sc.get_microphone(id=spk.name, include_loopback=True) if spk else None
                else:
                    mic = sc.default_microphone()

            if mic is None:
                return False

            self.sample_rate = 48000
            self.is_running = True
            
            self.capture_thread = threading.Thread(
                target=self._soundcard_worker,
                args=(mic,),
                daemon=True,
                name="BlazeAudioLoopbackThread"
            )
            self.capture_thread.start()
            return True
        except Exception as e:
            print(f"[AudioEngine] soundcard stream init error: {e}")
            self.is_running = False
            return False

    def _soundcard_worker(self, mic):
        """Worker loop continuously reading loopback audio frames from Windows audio session."""
        block_size = self.fft_size // 4
        try:
            with mic.recorder(samplerate=self.sample_rate, channels=2, blocksize=block_size) as rec:
                while self.is_running:
                    data = rec.record(numframes=block_size)
                    if not self.is_running:
                        break
                    if data is not None and len(data) > 0:
                        # Convert stereo to mono
                        mono = np.mean(data, axis=1, dtype=np.float32) if data.ndim > 1 else data.astype(np.float32)
                        with self.lock:
                            shift = len(mono)
                            if shift < self.fft_size:
                                self.buffer = np.roll(self.buffer, -shift)
                                self.buffer[-shift:] = mono
                            else:
                                self.buffer = mono[-self.fft_size:]
        except Exception as e:
            if self.is_running:
                print(f"[AudioEngine] soundcard worker loop error: {e}")

    def _start_sounddevice_stream(self, dev_info):
        """Starts fallback sounddevice InputStream."""
        try:
            idx = dev_info.get('sd_index')
            if idx is None:
                dev = sd.query_devices(kind='input')
                idx = dev.get('index') if dev else None

            dev_data = sd.query_devices(idx) if idx is not None else None
            self.sample_rate = int(dev_data.get('default_samplerate', 44100)) if dev_data else 44100
            channels = min(2, max(1, int(dev_data.get('max_input_channels', 2)))) if dev_data else 2

            self.sd_stream = sd.InputStream(
                device=idx,
                channels=channels,
                samplerate=self.sample_rate,
                blocksize=self.fft_size // 4,
                callback=self._sd_audio_callback
            )
            self.sd_stream.start()
            return True
        except Exception as e:
            print(f"[AudioEngine] sounddevice init error: {e}")
            self.sd_stream = None
            return False

    def _sd_audio_callback(self, indata, frames, time_info, status):
        """sounddevice stream callback."""
        mono = np.mean(indata, axis=1) if indata.ndim > 1 else indata.flatten()
        with self.lock:
            shift = len(mono)
            if shift < self.fft_size:
                self.buffer = np.roll(self.buffer, -shift)
                self.buffer[-shift:] = mono
            else:
                self.buffer = mono[-self.fft_size:]

    def process_frame(self):
        """
        Processes audio buffer:
        - Computes Hanning-windowed FFT
        - Extracts 360 frequency bins with logarithmic distribution
        - Detects Bass/Kick energy & RMS volume
        """
        with self.lock:
            samples = np.copy(self.buffer)
            
        # 1. RMS Volume Calculation
        rms = float(np.sqrt(np.mean(samples ** 2)) + 1e-9)
        self.rms_volume = rms
        self.is_playing = bool(rms > 0.001)

        if not self.is_playing:
            self.smoothed_freqs *= 0.88
            self.smoothed_bass *= 0.88
            return self.smoothed_freqs, self.smoothed_bass, self.rms_volume, False

        # 2. Windowed FFT
        window = np.hanning(len(samples))
        windowed = samples * window
        fft_complex = np.fft.rfft(windowed)
        magnitudes = np.abs(fft_complex)
        
        freqs = np.fft.rfftfreq(len(samples), 1.0 / self.sample_rate)

        # 3. Bass Energy (20Hz - 160Hz)
        bass_mask = (freqs >= 20) & (freqs <= 160)
        raw_bass = float(np.mean(magnitudes[bass_mask])) if np.any(bass_mask) else 0.0

        # 4. Map FFT spectrum to 360 radial bins (Logarithmic scale)
        min_freq = 25.0
        max_freq = min(16000.0, self.sample_rate / 2.0)
        log_edges = np.logspace(np.log10(min_freq), np.log10(max_freq), self.num_bins + 1)
        
        binned_values = np.zeros(self.num_bins, dtype=np.float32)
        for i in range(self.num_bins):
            f_start = log_edges[i]
            f_end = log_edges[i + 1]
            bin_mask = (freqs >= f_start) & (freqs < f_end)
            if np.any(bin_mask):
                weight = 1.0 + (i / self.num_bins) * 1.5
                binned_values[i] = np.mean(magnitudes[bin_mask]) * weight
            else:
                idx = np.searchsorted(freqs, (f_start + f_end) / 2)
                idx = min(idx, len(magnitudes) - 1)
                binned_values[i] = magnitudes[idx]

        # 5. Dynamic Auto-Gain Normalization
        current_peak = float(np.max(binned_values))
        if current_peak > self.max_observed:
            self.max_observed = current_peak
        else:
            self.max_observed = max(1e-3, self.max_observed * 0.997)
            
        normalized_bins = np.clip(binned_values / (self.max_observed + 1e-5), 0.0, 1.0)
        
        # 6. Temporal Smoothing
        self.smoothed_freqs = (self.smoothing * normalized_bins) + ((1.0 - self.smoothing) * self.smoothed_freqs)
        
        norm_bass = np.clip(raw_bass / (self.max_observed + 1e-5), 0.0, 1.0)
        self.smoothed_bass = (0.45 * norm_bass) + (0.55 * self.smoothed_bass)
        
        return self.smoothed_freqs, self.smoothed_bass, self.rms_volume, True

    def stop(self):
        """Stops the audio stream."""
        self.is_running = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=0.3)
        self.capture_thread = None

        if self.sd_stream is not None:
            try:
                self.sd_stream.stop()
                self.sd_stream.close()
            except Exception:
                pass
            self.sd_stream = None
