"""
Player Module for loading and playing local audio files.
Uses scipy.io.wavfile / soundfile and sounddevice for seamless playback while streaming into the visualizer.
"""

import os
import threading
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wavfile

# Optional soundfile import
try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    sf = None
    HAS_SOUNDFILE = False

class AudioFilePlayer:
    def __init__(self, audio_engine):
        self.audio_engine = audio_engine
        self.file_path = None
        self.data = None
        self.sample_rate = 44100
        self.position = 0
        self.is_playing = False
        self.is_paused = False
        self.playback_stream = None
        self.lock = threading.Lock()

    def load(self, file_path):
        """Loads an audio file into memory."""
        self.stop()
        self.file_path = file_path
        
        try:
            if HAS_SOUNDFILE:
                data, sr = sf.read(file_path, dtype='float32')
            else:
                # Load with scipy.io.wavfile
                sr, raw_data = wavfile.read(file_path)
                # Normalize integer formats to float32 (-1.0 to 1.0)
                if raw_data.dtype == np.int16:
                    data = (raw_data / 32768.0).astype(np.float32)
                elif raw_data.dtype == np.int32:
                    data = (raw_data / 2147483648.0).astype(np.float32)
                elif raw_data.dtype == np.uint8:
                    data = ((raw_data - 128) / 128.0).astype(np.float32)
                else:
                    data = raw_data.astype(np.float32)

            self.data = data
            self.sample_rate = sr
            self.position = 0
            print(f"[Player] Loaded '{os.path.basename(file_path)}' ({sr}Hz, {len(data)/sr:.2f}s)")
            return True
        except Exception as e:
            print(f"[Player] Error loading file: {e}")
            return False

    def play(self):
        """Starts playback."""
        if self.data is None:
            print("[Player] No audio file loaded.")
            return False
            
        self.is_playing = True
        self.is_paused = False
        
        # Open output stream
        channels = self.data.shape[1] if self.data.ndim > 1 else 1
        self.playback_stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=channels,
            callback=self._stream_callback
        )
        self.playback_stream.start()
        return True

    def _stream_callback(self, outdata, frames, time_info, status):
        """Callback to feed audio output and concurrently feed audio_engine."""
        with self.lock:
            if not self.is_playing or self.is_paused:
                outdata.fill(0)
                return

            remaining = len(self.data) - self.position
            chunk_size = min(frames, remaining)
            
            if chunk_size <= 0:
                outdata.fill(0)
                self.is_playing = False
                raise sd.CallbackStop()

            chunk = self.data[self.position:self.position + chunk_size]
            if chunk.ndim == 1 and outdata.shape[1] > 1:
                outdata[:chunk_size] = np.column_stack([chunk, chunk])
            else:
                outdata[:chunk_size] = chunk if chunk.ndim > 1 else chunk.reshape(-1, 1)

            if chunk_size < frames:
                outdata[chunk_size:].fill(0)
                self.is_playing = False

            self.position += chunk_size

            # Feed to visualizer audio engine directly
            mono_chunk = np.mean(chunk, axis=1) if chunk.ndim > 1 else chunk
            with self.audio_engine.lock:
                shift = len(mono_chunk)
                if shift < self.audio_engine.fft_size:
                    self.audio_engine.buffer = np.roll(self.audio_engine.buffer, -shift)
                    self.audio_engine.buffer[-shift:] = mono_chunk
                else:
                    self.audio_engine.buffer = mono_chunk[-self.audio_engine.fft_size:]

    def pause_toggle(self):
        """Toggle pause state."""
        self.is_paused = not self.is_paused
        return self.is_paused

    def stop(self):
        """Stops playback."""
        self.is_playing = False
        self.is_paused = False
        if self.playback_stream is not None:
            try:
                self.playback_stream.stop()
                self.playback_stream.close()
            except Exception:
                pass
            self.playback_stream = None
        self.position = 0
