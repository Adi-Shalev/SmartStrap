/**
 * Smart Strap — Night Session (tinnitus demo)
 * ────────────────────────────────────────────
 * A pre-sleep session that pairs soft sound with wrist vibration, personalised
 * to the patient's notch. Built as a demo for clinical discussion, not as a
 * validated protocol.
 *
 *   NightSessionEngine  builds the sound layer (Web Audio) and the vibration
 *                       schedule, both timed from the AudioContext clock so the
 *                       two stay in sync.
 *   ScreenHapticOutput  shows each vibration pulse on screen. A device output
 *                       (ESP32 over USB) can replace it later: anything with a
 *                       pulse(intensity, durationMs) method works.
 *   NightUI             the setup / running / finished screens.
 */

(function () {
    'use strict';

    // Hard ceiling for the sound layer, whatever the volume slider says.
    // Damaged ears: keep it soft. Tune with the clinical team.
    const MAX_MASTER_GAIN = 0.25;

    const PACE_START_SEC = 5;    // 12 pulses / min at the start
    const PACE_END_SEC   = 10;   // 6 pulses / min (slow breathing) at the end
    const PULSE_MS       = 400;
    const TONE_MS        = 350;
    const SCHEDULE_AHEAD = 0.5;  // seconds of events scheduled in advance

    // ─── Haptic outputs ─────────────────────────────────────────────────────

    class ScreenHapticOutput {
        constructor(el) { this.el = el; }

        pulse(intensity, durationMs) {
            if (!this.el) return;
            this.el.style.setProperty('--pulse-strength', intensity.toFixed(2));
            this.el.classList.remove('pulsing');
            void this.el.offsetWidth; // restart the CSS animation
            this.el.style.animationDuration = `${durationMs}ms`;
            this.el.classList.add('pulsing');
            if (navigator.vibrate) navigator.vibrate(durationMs);
        }
    }

    // ─── Engine ─────────────────────────────────────────────────────────────

    class NightSessionEngine {
        /**
         * @param {object} opts
         *   notchHz, widthHz      patient's notch (from Device_Settings)
         *   mode                  'both' | 'sound' | 'vibration'
         *   sound                 'soft-noise' | 'notch-noise' | 'edge-tones'
         *   durationSec
         *   volume                0..1 (scaled by MAX_MASTER_GAIN)
         *   vibration             0..1 (already capped by the clinician's setting)
         *   haptics               object with pulse(intensity, durationMs)
         *   onTick(state)         called ~4×/s for the UI
         *   onPulse()             called on every vibration pulse
         *   onEnd(summary)
         */
        constructor(opts) {
            this.o = opts;
            this.ctx = null;
            this.timer = null;
            this.pending = [];
            this.pulses = 0;
            this.running = false;
        }

        get usesSound()     { return this.o.mode !== 'vibration'; }
        get usesVibration() { return this.o.mode !== 'sound'; }

        // Edges of the notch, where residual hearing is still present.
        get edges() {
            const half = Math.max(this.o.widthHz, 200) / 2;
            return [Math.max(this.o.notchHz - half, 250), Math.min(this.o.notchHz + half, 12000)];
        }

        // Pulse period slows from PACE_START to PACE_END over the first 2/3.
        periodAt(t) {
            const ramp = this.o.durationSec * (2 / 3);
            const k = Math.min(t / ramp, 1);
            return PACE_START_SEC + (PACE_END_SEC - PACE_START_SEC) * k;
        }

        // Fade-out envelope: the last 5 min, or the last 25% for short sessions.
        fadeLength() { return Math.min(300, this.o.durationSec * 0.25); }

        fadeAt(t) {
            const fade = this.fadeLength();
            const remaining = this.o.durationSec - t;
            return remaining >= fade ? 1 : Math.max(remaining / fade, 0);
        }

        async start() {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
            if (this.ctx.state === 'suspended') await this.ctx.resume();

            const now = this.ctx.currentTime;
            this.t0 = now + 0.1;
            this.nextPulse = this.t0 + 1;  // first pulse after one second
            this.edgeIndex = 0;

            this.master = this.ctx.createGain();
            const limiter = this.ctx.createDynamicsCompressor();
            limiter.threshold.value = -12;
            limiter.ratio.value = 12;
            this.master.connect(limiter).connect(this.ctx.destination);

            // Fade in over 10 s, hold, then fade out at the end.
            const g = this.o.volume * MAX_MASTER_GAIN;
            const end = this.t0 + this.o.durationSec;
            this.master.gain.setValueAtTime(0, now);
            this.master.gain.linearRampToValueAtTime(g, this.t0 + Math.min(10, this.o.durationSec / 4));
            this.master.gain.setValueAtTime(g, end - this.fadeLength());
            this.master.gain.linearRampToValueAtTime(0, end);

            if (this.usesSound && this.o.sound !== 'edge-tones') this.buildNoiseBed(end);

            this.running = true;
            this.timer = setInterval(() => this.tick(), 100);
            this.tick();
        }

        buildNoiseBed(end) {
            const ctx = this.ctx;
            const src = ctx.createBufferSource();
            src.buffer = this.o.sound === 'soft-noise' ? this.pinkNoise(10) : this.whiteNoise(10);
            src.loop = true;

            let node = src;
            if (this.o.sound === 'soft-noise') {
                const lp = ctx.createBiquadFilter();
                lp.type = 'lowpass';
                lp.frequency.value = 6000;
                node = node.connect(lp);
            } else {
                // Band of noise around the notch, wide enough to reach both edges.
                const bp = ctx.createBiquadFilter();
                bp.type = 'bandpass';
                bp.frequency.value = this.o.notchHz;
                bp.Q.value = Math.min(Math.max(this.o.notchHz / (2 * this.o.widthHz), 0.7), 8);
                node = node.connect(bp);
            }

            // Gentle swell that follows the pulse rhythm (set per pulse in tick()).
            this.swell = ctx.createGain();
            this.swell.gain.value = 0.75;
            node.connect(this.swell).connect(this.master);

            src.start(this.t0);
            src.stop(end + 0.5);
            this.noiseSrc = src;
        }

        whiteNoise(seconds) {
            const n = this.ctx.sampleRate * seconds;
            const buf = this.ctx.createBuffer(1, n, this.ctx.sampleRate);
            const d = buf.getChannelData(0);
            for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * 0.5;
            return buf;
        }

        // Paul Kellet's pink-noise filter: softer, less hissy than white noise.
        pinkNoise(seconds) {
            const n = this.ctx.sampleRate * seconds;
            const buf = this.ctx.createBuffer(1, n, this.ctx.sampleRate);
            const d = buf.getChannelData(0);
            let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
            for (let i = 0; i < n; i++) {
                const w = Math.random() * 2 - 1;
                b0 = 0.99886 * b0 + w * 0.0555179;
                b1 = 0.99332 * b1 + w * 0.0750759;
                b2 = 0.96900 * b2 + w * 0.1538520;
                b3 = 0.86650 * b3 + w * 0.3104856;
                b4 = 0.55000 * b4 + w * 0.5329522;
                b5 = -0.7616 * b5 - w * 0.0168980;
                d[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + w * 0.5362) * 0.11;
                b6 = w * 0.115926;
            }
            return buf;
        }

        // Short, smooth tone at one notch edge (alternating low / high).
        scheduleTone(at) {
            const freq = this.edges[this.edgeIndex++ % 2];
            const osc = this.ctx.createOscillator();
            const env = this.ctx.createGain();
            osc.frequency.value = freq;
            const dur = TONE_MS / 1000;
            env.gain.setValueAtTime(0, at);
            env.gain.linearRampToValueAtTime(0.6, at + 0.06);
            env.gain.setValueAtTime(0.6, at + dur - 0.12);
            env.gain.linearRampToValueAtTime(0, at + dur);
            osc.connect(env).connect(this.master);
            osc.start(at);
            osc.stop(at + dur + 0.05);
        }

        tick() {
            if (!this.running) return;
            const now = this.ctx.currentTime;
            const elapsed = Math.max(now - this.t0, 0);

            if (elapsed >= this.o.durationSec) {
                this.finish(true);
                return;
            }

            // Schedule every pulse that falls inside the look-ahead window.
            while (this.nextPulse < now + SCHEDULE_AHEAD &&
                   this.nextPulse - this.t0 < this.o.durationSec - 0.5) {
                const at = this.nextPulse;
                const t = at - this.t0;
                const period = this.periodAt(t);
                const fade = this.fadeAt(t);

                if (this.usesSound) {
                    if (this.o.sound === 'edge-tones') {
                        this.scheduleTone(at);
                    } else if (this.swell) {
                        // Swell up on the pulse, ease down over the rest of the cycle.
                        this.swell.gain.setTargetAtTime(1.0, at - 0.3, 0.15);
                        this.swell.gain.setTargetAtTime(0.6, at + 0.4, period / 4);
                    }
                }

                if (this.usesVibration) {
                    const intensity = this.o.vibration * fade;
                    const delayMs = Math.max((at - now) * 1000, 0);
                    const id = setTimeout(() => {
                        this.pending = this.pending.filter(p => p !== id);
                        if (!this.running) return;
                        this.o.haptics.pulse(intensity, PULSE_MS);
                        this.pulses++;
                        if (this.o.onPulse) this.o.onPulse();
                    }, delayMs);
                    this.pending.push(id);
                }

                this.nextPulse += period;
            }

            if (this.o.onTick) {
                this.o.onTick({
                    elapsed,
                    remaining: this.o.durationSec - elapsed,
                    perMinute: 60 / this.periodAt(elapsed),
                    fading: this.fadeAt(elapsed) < 1,
                });
            }
        }

        stop() { this.finish(false); }

        finish(completed) {
            if (!this.running) return;
            this.running = false;
            clearInterval(this.timer);
            this.pending.forEach(clearTimeout);
            this.pending = [];

            const elapsed = Math.min(Math.max(this.ctx.currentTime - this.t0, 0), this.o.durationSec);
            const ctx = this.ctx;
            // Short ramp so a manual stop doesn't click.
            this.master.gain.cancelScheduledValues(ctx.currentTime);
            this.master.gain.setTargetAtTime(0, ctx.currentTime, 0.1);
            setTimeout(() => ctx.close(), 600);

            if (this.o.onEnd) this.o.onEnd({ completed, elapsed, pulses: this.pulses });
        }
    }

    // ─── UI ─────────────────────────────────────────────────────────────────

    const NightUI = {
        engine: null,
        wakeLock: null,
        settings: { mode: 'both', sound: 'soft-noise', minutes: 2 },

        el(id) { return document.getElementById(id); },

        init() {
            this.bindSegments('night-mode-control', 'mode', () => this.syncModeFields());
            this.bindSegments('night-duration-control', 'minutes');
            this.el('night-sound-select').addEventListener('change', e => { this.settings.sound = e.target.value; });
            this.el('night-volume').addEventListener('input', () => this.syncSliderLabels());
            this.el('night-vibration').addEventListener('input', () => this.syncSliderLabels());
            this.el('btn-night-start').addEventListener('click', () => this.start());
            this.el('btn-night-stop').addEventListener('click', () => this.engine && this.engine.stop());
            this.el('btn-night-again').addEventListener('click', () => this.showPanel('setup'));
            this.el('btn-night-back').addEventListener('click', () => {
                this.stop();
                window.app.showView('view-patient');
            });
        },

        bindSegments(controlId, key, after) {
            const control = this.el(controlId);
            control.querySelectorAll('.segment').forEach(btn => {
                btn.addEventListener('click', () => {
                    control.querySelectorAll('.segment').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    const v = btn.dataset.value;
                    this.settings[key] = key === 'minutes' ? parseFloat(v) : v;
                    if (after) after();
                });
            });
        },

        /** Called when the patient opens the Night Session screen. */
        open(user) {
            this.user = user;
            const notch = (user && user.notch) || 4000;
            const width = (user && user.width) || 500;
            const cap = (user && user.device_settings && user.device_settings.Vibration_Intensity) || 70;
            this.profile = { notch, width, cap };

            this.el('night-notch-label').textContent = `${notch} Hz · width ${width} Hz`;
            const vib = this.el('night-vibration');
            vib.max = cap;
            if (parseFloat(vib.value) > cap) vib.value = cap;
            this.el('night-vibration-cap').textContent = `Your clinician's limit: ${cap}%`;

            this.syncModeFields();
            this.syncSliderLabels();
            this.showPanel('setup');
        },

        syncModeFields() {
            const mode = this.settings.mode;
            this.el('night-sound-group').classList.toggle('hidden', mode === 'vibration');
            this.el('night-volume-group').classList.toggle('hidden', mode === 'vibration');
            this.el('night-vibration-group').classList.toggle('hidden', mode === 'sound');
        },

        syncSliderLabels() {
            this.el('night-volume-value').textContent = `${this.el('night-volume').value}%`;
            this.el('night-vibration-value').textContent = `${this.el('night-vibration').value}%`;
        },

        showPanel(which) {
            ['setup', 'running', 'done'].forEach(p => {
                this.el(`night-${p}`).classList.toggle('hidden', p !== which);
            });
            document.body.classList.toggle('night-running', which === 'running');
        },

        async start() {
            const s = this.settings;
            const orb = this.el('night-orb');
            const modeLabels = { both: 'Sound + vibration', sound: 'Sound only', vibration: 'Vibration only' };
            const soundLabels = { 'soft-noise': 'soft noise', 'notch-noise': 'notch-band noise', 'edge-tones': 'edge tones' };

            this.el('night-running-mode').textContent =
                s.mode === 'vibration' ? modeLabels.vibration : `${modeLabels[s.mode]} · ${soundLabels[s.sound]}`;
            this.el('night-pulse-count').textContent = '0';

            this.engine = new NightSessionEngine({
                notchHz: this.profile.notch,
                widthHz: this.profile.width,
                mode: s.mode,
                sound: s.sound,
                durationSec: s.minutes * 60,
                volume: this.el('night-volume').value / 100,
                vibration: this.el('night-vibration').value / 100,
                haptics: new ScreenHapticOutput(orb),
                onTick: st => this.renderTick(st),
                onPulse: () => { this.el('night-pulse-count').textContent = this.engine.pulses; },
                onEnd: summary => this.onEnd(summary),
            });

            this.showPanel('running');
            this.requestWakeLock();
            try {
                await this.engine.start();
            } catch (e) {
                console.error('Night session failed to start:', e);
                this.showPanel('setup');
                this.releaseWakeLock();
            }
        },

        renderTick(st) {
            const r = Math.ceil(st.remaining);
            this.el('night-remaining').textContent =
                `${Math.floor(r / 60)}:${String(r % 60).padStart(2, '0')}`;
            this.el('night-pace').textContent = st.fading
                ? 'Fading out…'
                : `${st.perMinute.toFixed(1)} pulses / min`;
        },

        async onEnd(summary) {
            this.releaseWakeLock();
            const mins = Math.floor(summary.elapsed / 60);
            const secs = Math.round(summary.elapsed % 60);
            this.el('night-done-title').textContent = summary.completed ? 'Session complete' : 'Session stopped';
            this.el('night-done-duration').textContent = `${mins}:${String(secs).padStart(2, '0')}`;
            this.el('night-done-pulses').textContent = summary.pulses;
            this.showPanel('done');

            if (this.user && this.user.id) {
                try {
                    await API.logNightSession(this.user.id, {
                        mode: this.settings.mode,
                        sound: this.settings.mode === 'vibration' ? null : this.settings.sound,
                        planned_minutes: this.settings.minutes,
                        duration_seconds: Math.round(summary.elapsed),
                        pulses: summary.pulses,
                        completed: summary.completed,
                    });
                } catch (e) {
                    console.error('Failed to log night session:', e);
                }
            }
        },

        /** Stop silently (logout / leaving the screen). */
        stop() {
            if (this.engine && this.engine.running) this.engine.stop();
            this.showPanel('setup');
        },

        // Keep the screen (and the timers) awake while the session runs.
        async requestWakeLock() {
            try {
                if ('wakeLock' in navigator) this.wakeLock = await navigator.wakeLock.request('screen');
            } catch (e) { /* not supported or denied: the session still runs */ }
        },

        releaseWakeLock() {
            if (this.wakeLock) { this.wakeLock.release().catch(() => {}); this.wakeLock = null; }
        },
    };

    window.NightSessionEngine = NightSessionEngine;
    window.NightUI = NightUI;
    document.addEventListener('DOMContentLoaded', () => NightUI.init());
})();
