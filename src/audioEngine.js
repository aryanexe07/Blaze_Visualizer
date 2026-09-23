/**
 * Web Audio Engine for Real-time FFT Analysis, Bass Kick Detection & Multi-source Audio
 */

export class AudioEngine {
  constructor(numBins = 360) {
    this.numBins = numBins;
    this.audioCtx = null;
    this.analyser = null;
    this.sourceNode = null;
    this.audioElement = new Audio();
    this.audioElement.crossOrigin = "anonymous";
    this.audioElement.loop = true;

    this.mediaStream = null;
    this.synthInterval = null;
    this.sourceMode = "NONE"; // "FILE", "SYSTEM", "MIC", "SYNTH_DEMO", "NONE"
    
    // Frequency buffers
    this.fftSize = 2048;
    this.freqData = new Uint8Array(this.fftSize / 2);
    this.timeData = new Uint8Array(this.fftSize);
    this.smoothedBins = new Float32Array(this.numBins);
    
    // Dynamic values
    this.bassEnergy = 0.0;
    this.smoothedBass = 0.0;
    this.rmsVolume = 0.0;
    this.isPlaying = false;
    this.maxObserved = 0.01;
    this.smoothing = 0.32;
    
    this.trackName = "No Audio Loaded";
    this.onTrackEnded = null;
    this.onProgressUpdate = null;

    this._setupAudioElementListeners();
  }

  _initContext() {
    if (!this.audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      this.audioCtx = new AudioContextClass();
      this.analyser = this.audioCtx.createAnalyser();
      this.analyser.fftSize = this.fftSize;
      this.analyser.smoothingTimeConstant = 0.75;
    }
    if (this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
  }

  _setupAudioElementListeners() {
    this.audioElement.addEventListener('timeupdate', () => {
      if (this.onProgressUpdate && this.audioElement.duration) {
        this.onProgressUpdate(this.audioElement.currentTime, this.audioElement.duration);
      }
    });

    this.audioElement.addEventListener('ended', () => {
      if (this.onTrackEnded) this.onTrackEnded();
    });
  }

  _disconnectCurrentSource() {
    if (this.synthInterval) {
      clearInterval(this.synthInterval);
      this.synthInterval = null;
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(t => t.stop());
      this.mediaStream = null;
    }
    if (this.audioElement) {
      this.audioElement.pause();
    }
    if (this.sourceNode) {
      try {
        this.sourceNode.disconnect();
      } catch (e) {
        // ignore
      }
      this.sourceNode = null;
    }
  }

  /**
   * Loads and plays a user audio file (Blob / File / URL)
   */
  async loadAudioFile(file) {
    this._initContext();
    this._disconnectCurrentSource();

    const url = typeof file === 'string' ? file : URL.createObjectURL(file);
    this.trackName = typeof file === 'string' ? file.split('/').pop() : file.name;
    
    this.audioElement.src = url;
    
    if (!this.fileSourceNode) {
      this.fileSourceNode = this.audioCtx.createMediaElementSource(this.audioElement);
    }
    this.sourceNode = this.fileSourceNode;
    this.sourceNode.connect(this.analyser);
    this.analyser.connect(this.audioCtx.destination);

    this.sourceMode = "FILE";
    await this.audioElement.play();
    this.isPlaying = true;
    return this.trackName;
  }

  /**
   * Captures Live System / Tab Audio via DisplayMedia
   */
  async startSystemAudio() {
    this._initContext();
    this._disconnectCurrentSource();

    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: {
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false
        }
      });

      // Stop video track since we only visualize audio
      const audioTracks = stream.getAudioTracks();
      if (audioTracks.length === 0) {
        stream.getTracks().forEach(t => t.stop());
        throw new Error("No audio track selected! Please check 'Share audio' when choosing a screen/tab.");
      }
      stream.getVideoTracks().forEach(t => t.stop());

      this.mediaStream = stream;
      this.sourceNode = this.audioCtx.createMediaStreamSource(new MediaStream(audioTracks));
      this.sourceNode.connect(this.analyser);
      // Do not connect to destination to prevent echo

      this.sourceMode = "SYSTEM";
      this.trackName = "Live System Audio (Loopback)";
      this.isPlaying = true;

      // Handle user stopping share
      audioTracks[0].addEventListener('ended', () => {
        this.sourceMode = "NONE";
        this.isPlaying = false;
        this.trackName = "Stream Ended";
      });

      return true;
    } catch (err) {
      console.warn("System audio capture error:", err);
      throw err;
    }
  }

  /**
   * Captures Live Microphone input
   */
  async startMicrophone() {
    this._initContext();
    this._disconnectCurrentSource();

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false
        }
      });

      this.mediaStream = stream;
      this.sourceNode = this.audioCtx.createMediaStreamSource(stream);
      this.sourceNode.connect(this.analyser);

      this.sourceMode = "MIC";
      this.trackName = "Live Microphone Input";
      this.isPlaying = true;
      return true;
    } catch (err) {
      console.warn("Microphone access error:", err);
      throw err;
    }
  }

  /**
   * Plays built-in punchy EDM Synthesizer Demo Beat
   */
  startDemoBeat() {
    this._initContext();
    this._disconnectCurrentSource();

    const bpm = 128;
    const stepTime = (60 / bpm) / 4; // 16th note
    let step = 0;

    const synthDest = this.audioCtx.createGain();
    synthDest.gain.value = 0.85;
    synthDest.connect(this.analyser);
    this.analyser.connect(this.audioCtx.destination);

    const bassNotes = [36.71, 36.71, 41.20, 43.65, 36.71, 32.70, 36.71, 49.00]; // D1, D1, E1, F1...

    const playKick = (time) => {
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(140, time);
      osc.frequency.exponentialRampToValueAtTime(38, time + 0.08);
      osc.frequency.exponentialRampToValueAtTime(20, time + 0.28);
      
      gain.gain.setValueAtTime(1.0, time);
      gain.gain.exponentialRampToValueAtTime(0.001, time + 0.32);
      
      osc.connect(gain);
      gain.connect(synthDest);
      osc.start(time);
      osc.stop(time + 0.35);
    };

    const playBass = (time, freq) => {
      const osc = this.audioCtx.createOscillator();
      const filter = this.audioCtx.createBiquadFilter();
      const gain = this.audioCtx.createGain();
      
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(freq, time);
      
      filter.type = "lowpass";
      filter.frequency.setValueAtTime(600, time);
      filter.frequency.exponentialRampToValueAtTime(120, time + 0.18);
      
      gain.gain.setValueAtTime(0.7, time);
      gain.gain.exponentialRampToValueAtTime(0.01, time + 0.2);
      
      osc.connect(filter);
      filter.connect(gain);
      gain.connect(synthDest);
      
      osc.start(time);
      osc.stop(time + 0.22);
    };

    const playHiHat = (time, isOpen = false) => {
      const bufferSize = this.audioCtx.sampleRate * (isOpen ? 0.15 : 0.04);
      const buffer = this.audioCtx.createBuffer(1, bufferSize, this.audioCtx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = Math.random() * 2 - 1;
      }
      const noise = this.audioCtx.createBufferSource();
      noise.buffer = buffer;
      const filter = this.audioCtx.createBiquadFilter();
      filter.type = "highpass";
      filter.frequency.value = 7500;
      const gain = this.audioCtx.createGain();
      gain.gain.setValueAtTime(isOpen ? 0.35 : 0.2, time);
      gain.gain.exponentialRampToValueAtTime(0.001, time + (isOpen ? 0.14 : 0.035));
      noise.connect(filter);
      filter.connect(gain);
      gain.connect(synthDest);
      noise.start(time);
    };

    this.synthInterval = setInterval(() => {
      const now = this.audioCtx.currentTime;
      // Kick on 0, 4, 8, 12 (4-on-the-floor)
      if (step % 4 === 0) {
        playKick(now);
      }
      // Offbeat Hi-hat on 2, 6, 10, 14
      if (step % 4 === 2) {
        playHiHat(now, true);
      } else {
        playHiHat(now, false);
      }
      // Bassline
      const noteIdx = Math.floor(step / 2) % bassNotes.length;
      playBass(now, bassNotes[noteIdx]);

      step = (step + 1) % 16;
    }, stepTime * 1000);

    this.sourceMode = "SYNTH_DEMO";
    this.trackName = "Punchy EDM Demo Beat (128 BPM)";
    this.isPlaying = true;
  }

  togglePlayPause() {
    if (this.sourceMode === "FILE") {
      if (this.audioElement.paused) {
        this.audioElement.play();
        this.isPlaying = true;
      } else {
        this.audioElement.pause();
        this.isPlaying = false;
      }
      return this.isPlaying;
    }
    return this.isPlaying;
  }

  seek(percentage) {
    if (this.sourceMode === "FILE" && this.audioElement.duration) {
      this.audioElement.currentTime = percentage * this.audioElement.duration;
    }
  }

  setVolume(val) {
    this.audioElement.volume = Math.max(0, Math.min(1, val));
  }

  /**
   * Processes current audio frame: extracts 360 frequency bins and bass energy
   */
  processFrame() {
    if (!this.analyser) {
      return {
        freqs: this.smoothedBins,
        bassEnergy: 0,
        rms: 0,
        isActive: false
      };
    }

    this.analyser.getByteFrequencyData(this.freqData);
    this.analyser.getByteTimeDomainData(this.timeData);

    // 1. RMS volume
    let sumSquares = 0;
    for (let i = 0; i < this.timeData.length; i++) {
      const norm = (this.timeData[i] - 128) / 128;
      sumSquares += norm * norm;
    }
    const rms = Math.sqrt(sumSquares / this.timeData.length);
    this.rmsVolume = rms;
    const isActive = rms > 0.005;

    if (!isActive) {
      for (let i = 0; i < this.numBins; i++) {
        this.smoothedBins[i] *= 0.88;
      }
      this.smoothedBass *= 0.85;
      return {
        freqs: this.smoothedBins,
        bassEnergy: this.smoothedBass,
        rms: this.rmsVolume,
        isActive: false
      };
    }

    // 2. Sub-Bass Energy (20Hz to 160Hz)
    const sampleRate = this.audioCtx.sampleRate;
    const binWidth = sampleRate / this.fftSize;
    const bassMinBin = Math.floor(20 / binWidth);
    const bassMaxBin = Math.min(this.freqData.length - 1, Math.ceil(160 / binWidth));
    
    let bassSum = 0;
    let bassCount = 0;
    for (let i = bassMinBin; i <= bassMaxBin; i++) {
      bassSum += this.freqData[i];
      bassCount++;
    }
    const rawBass = bassCount > 0 ? (bassSum / bassCount) / 255 : 0;

    // 3. Logarithmic frequency mapping to 360 radial bins
    const minFreq = 25.0;
    const maxFreq = Math.min(16000.0, sampleRate / 2);
    const logMin = Math.log10(minFreq);
    const logMax = Math.log10(maxFreq);

    const binned = new Float32Array(this.numBins);
    let peak = 0.001;

    for (let i = 0; i < this.numBins; i++) {
      const fStart = Math.pow(10, logMin + (i / this.numBins) * (logMax - logMin));
      const fEnd = Math.pow(10, logMin + ((i + 1) / this.numBins) * (logMax - logMin));
      const binStart = Math.max(0, Math.floor(fStart / binWidth));
      const binEnd = Math.min(this.freqData.length - 1, Math.ceil(fEnd / binWidth));

      let binSum = 0;
      let count = 0;
      for (let b = binStart; b <= binEnd; b++) {
        binSum += this.freqData[b];
        count++;
      }
      const val = count > 0 ? (binSum / count) / 255.0 : 0;
      const weight = 1.0 + (i / this.numBins) * 1.5; // High frequency compensation
      binned[i] = val * weight;
      if (binned[i] > peak) peak = binned[i];
    }

    // 4. Dynamic Auto-Gain Normalization
    if (peak > this.maxObserved) {
      this.maxObserved = peak;
    } else {
      this.maxObserved = Math.max(0.1, this.maxObserved * 0.996);
    }

    // 5. Temporal Smoothing
    for (let i = 0; i < this.numBins; i++) {
      const norm = Math.min(1.0, binned[i] / (this.maxObserved + 0.01));
      this.smoothedBins[i] = (this.smoothing * norm) + ((1.0 - this.smoothing) * this.smoothedBins[i]);
    }

    const normBass = Math.min(1.0, rawBass / (this.maxObserved + 0.01));
    this.smoothedBass = (0.45 * normBass) + (0.55 * this.smoothedBass);

    return {
      freqs: this.smoothedBins,
      bassEnergy: this.smoothedBass,
      rms: this.rmsVolume,
      isActive: true
    };
  }
}
