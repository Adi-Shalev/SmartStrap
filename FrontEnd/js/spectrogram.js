/**
 * Smart Strap - Spectrogram Visualizer
 * Analyzes an AudioContext node and draws a frequency visualizer on a canvas.
 */

class Spectrogram {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.audioCtx = null;
        this.analyser = null;
        this.source = null;
        this.animationId = null;
        
        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        if (!this.canvas) return;
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
    }

    connect(audioElement) {
        if (!this.audioCtx) {
            this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        
        if (!this.analyser) {
            this.analyser = this.audioCtx.createAnalyser();
            this.analyser.fftSize = 512;
            this.analyser.smoothingTimeConstant = 0.8;
            
            // Connect element to analyser
            this.source = this.audioCtx.createMediaElementSource(audioElement);
            this.source.connect(this.analyser);
            this.analyser.connect(this.audioCtx.destination);
        }
    }

    start() {
        if (!this.analyser) return;
        this.draw();
    }

    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        // Clear canvas
        if (this.ctx) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
    }

    draw() {
        this.animationId = requestAnimationFrame(() => this.draw());

        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        this.analyser.getByteFrequencyData(dataArray);

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        const barWidth = (this.canvas.width / bufferLength) * 2.5;
        let barHeight;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            barHeight = dataArray[i];

            // 4kHz emphasis roughly in the middle bins
            let is4k = (i > bufferLength * 0.15 && i < bufferLength * 0.25);
            
            if (is4k && barHeight > 100) {
                this.ctx.fillStyle = `rgba(196, 80, 62, ${barHeight / 255})`; // Red accent for 4k
            } else {
                this.ctx.fillStyle = `rgba(13, 138, 150, ${barHeight / 255})`; // Teal primary
            }

            this.ctx.fillRect(x, this.canvas.height - (barHeight / 2), barWidth, barHeight / 2);
            x += barWidth + 1;
        }
    }
}

window.Spectrogram = Spectrogram;
