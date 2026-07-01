/**
 * Smart Strap — Main Application Logic
 * ─────────────────────────────────────
 * Earthy Pulse Design · Handles Routing, State, and UI Interactions
 */

document.addEventListener('DOMContentLoaded', () => {

    // ─── State ──────────────────────────────────────────────
    let currentUser = null;
    let currentRole = 'patient'; // Default selected role on login screen

    // ─── DOM Elements ───────────────────────────────────────
    const topNav       = document.getElementById('top-nav');
    const navUserRole  = document.getElementById('nav-user-role');
    const navUserName  = document.getElementById('nav-user-name');
    const navHome      = document.getElementById('nav-home');
    const btnLogout    = document.getElementById('btn-logout');

    const views        = document.querySelectorAll('.view');
    const loginForm    = document.getElementById('login-form');
    const roleTabs     = document.querySelectorAll('.role-tab');

    // ─── Routing & View Management ──────────────────────────
    function showView(viewId) {
        views.forEach(v => v.classList.remove('active'));
        const target = document.getElementById(viewId);
        if (target) target.classList.add('active');

        // Toggle nav visibility (hidden on login)
        if (viewId === 'view-login') {
            topNav.classList.add('hidden');
        }
    }

    function updateNav() {
        if (currentUser) {
            topNav.classList.remove('hidden');
            navUserRole.textContent = currentUser.role === 'doctor' ? 'CLINICIAN' : currentUser.role.toUpperCase();
            navUserName.textContent = currentUser.name;
        } else {
            topNav.classList.add('hidden');
        }
    }

    // Nav brand → home
    if (navHome) {
        navHome.addEventListener('click', () => {
            if (currentUser) showView(`view-${currentUser.role}`);
        });
    }

    // ─── Login Logic ────────────────────────────────────────

    // Real credentials per role for quick demo access
    const demoCredentials = {
        patient: { email: 'yossi.c@email.com', password: 'p_yossi1' },
        doctor:  { email: 'moshe.cohen@hospital.com', password: 'hash_moshe123' },
    };

    // Role tab selector
    roleTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            roleTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentRole = tab.getAttribute('data-role');

            // Auto-fill with real credentials for quick login
            const creds = demoCredentials[currentRole];
            if (creds) {
                document.getElementById('login-email').value = creds.email;
                document.getElementById('login-password').value = creds.password;
            }
        });
    });

    // Auto-fill initial (patient)
    document.getElementById('login-email').value = demoCredentials.patient.email;
    document.getElementById('login-password').value = demoCredentials.patient.password;

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email    = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const btn      = loginForm.querySelector('.btn-login');
        const btnText  = btn.innerHTML;

        btn.innerHTML = 'Authenticating…';
        btn.style.opacity = '0.7';
        btn.disabled = true;

        try {
            const user = await API.login(email, password, currentRole);
            currentUser = user;
            updateNav();

            // Update patient greeting if patient
            if (user.role === 'patient') {
                const greetEl = document.getElementById('patient-greeting');
                if (greetEl) greetEl.textContent = `Hi, ${user.name.split(' ')[0]}`;
            }

            // Route to appropriate dashboard
            showView(`view-${user.role}`);
            showToast(`Welcome back, ${user.name}`);
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btn.innerHTML = btnText;
            btn.style.opacity = '1';
            btn.disabled = false;
        }
    });

    // Logout
    btnLogout.addEventListener('click', () => {
        stopGame();
        currentUser = null;
        updateNav();
        showView('view-login');
        showToast('Logged out successfully');
    });

    // ─── Toast Notifications ────────────────────────────────
    function showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        // Add icon
        const icon = type === 'success' ? 'check_circle' : 'error';
        toast.innerHTML = `<span class="ms" style="font-size:18px;">${icon}</span>${message}`;
        container.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => toast.classList.add('toast-visible'));

        // Auto-dismiss after 3.5s
        setTimeout(() => {
            toast.classList.remove('toast-visible');
            toast.addEventListener('transitionend', () => toast.remove(), { once: true });
        }, 3500);
    }

    // ─── Sub-View Navigation ────────────────────────────────
    window.app = {
        showView: showView,
        showSubView: (subViewId) => {
            showView(`view-${subViewId}`);
            if (subViewId === 'patient-profile')        renderAudiogramChart();
            if (subViewId === 'patient-stats')          renderStatsCharts();
            if (subViewId === 'doctor-patient-detail')  renderDoctorPatientChart();
        }
    };

    // ─── Chart.js — Warm Palette Theme ──────────────────────
    // Shared config for the warm design system
    const chartColors = {
        teal:       '#0d8a96',
        green:      '#2f8f6b',
        red:        '#c4503e',
        textMuted:  '#a99f8e',
        textSecondary: '#6f6a60',
        grid:       '#e7ded2',
        gridLight:  '#f1ebe1',
        cardBg:     '#fffdf9'
    };

    function warmChartDefaults() {
        Chart.defaults.color = chartColors.textMuted;
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        Chart.defaults.plugins.legend.labels.padding = 16;
    }

    let audiogramChart, trendChart, accuracyChart, doctorPatientChart;

    function renderAudiogramChart() {
        const ctx = document.getElementById('audiogram-chart');
        if (!ctx) return;
        if (audiogramChart) audiogramChart.destroy();
        warmChartDefaults();

        audiogramChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['125', '250', '500', '1k', '2k', '4k', '8k'],
                datasets: [{
                    label: 'Hearing Threshold (dB HL)',
                    data: [10, 15, 10, 20, 30, 65, 35],
                    borderColor: chartColors.teal,
                    backgroundColor: 'rgba(13, 138, 150, 0.08)',
                    borderWidth: 3,
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: (ctx) => ctx.dataIndex === 5 ? chartColors.red : chartColors.teal,
                    pointBorderColor: (ctx) => ctx.dataIndex === 5 ? chartColors.red : chartColors.teal,
                    pointRadius: (ctx) => ctx.dataIndex === 5 ? 7 : 5
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { labels: { color: chartColors.textSecondary } }
                },
                scales: {
                    y: {
                        reverse: true,
                        min: -10,
                        max: 120,
                        title: { display: true, text: 'Hearing Level (dB)', color: chartColors.textSecondary },
                        grid: { color: chartColors.gridLight },
                        ticks: { color: chartColors.textMuted }
                    },
                    x: {
                        title: { display: true, text: 'Frequency (Hz)', color: chartColors.textSecondary },
                        grid: { color: chartColors.gridLight },
                        ticks: { color: chartColors.textMuted }
                    }
                }
            }
        });
    }

    async function renderStatsCharts() {
        const ctxTrend = document.getElementById('feedback-trend-chart');
        const ctxAcc   = document.getElementById('training-accuracy-chart');

        if (trendChart) trendChart.destroy();
        if (accuracyChart) accuracyChart.destroy();
        warmChartDefaults();

        // Fetch training history
        let accLabels = ['No Data'];
        let accData = [0];
        
        if (currentUser && currentUser.id) {
            const history = await API.getTrainingHistory(currentUser.id);
            if (history && history.length > 0) {
                // Show last 5 sessions
                const recent = history.slice(-5);
                accLabels = recent.map((h, i) => `Sess ${i+1}`);
                accData = recent.map(h => h.Final_Accuracy_Score || 0);
                
                // Update KPI values in the DOM
                const lastSession = recent[recent.length - 1];
                const bestSession = Math.max(...history.map(h => h.Final_Accuracy_Score || 0));
                
                const scoreEls = document.querySelectorAll('#view-patient-stats .kpi-value');
                if (scoreEls.length >= 3) {
                    scoreEls[0].textContent = `${lastSession.Final_Accuracy_Score}%`; // Current score
                    scoreEls[1].textContent = `${bestSession}%`; // Best accuracy
                    scoreEls[2].textContent = history.length; // Sessions
                }
            }
        }

        trendChart = new Chart(ctxTrend, {
            type: 'line',
            data: {
                labels: ['May 1', 'May 15', 'Jun 1', 'Jun 15'],
                datasets: [{
                    label: 'Hearing Perception Score',
                    data: [3, 5, 6, 8],
                    borderColor: chartColors.green,
                    backgroundColor: 'rgba(47, 143, 107, 0.08)',
                    borderWidth: 3,
                    tension: 0.2,
                    fill: true,
                    pointBackgroundColor: chartColors.green,
                    pointRadius: 5
                }]
            },
            options: {
                plugins: { legend: { labels: { color: chartColors.textSecondary } } },
                scales: {
                    y: {
                        min: 1, max: 10,
                        grid: { color: chartColors.gridLight },
                        ticks: { color: chartColors.textMuted }
                    },
                    x: {
                        grid: { color: chartColors.gridLight },
                        ticks: { color: chartColors.textMuted }
                    }
                }
            }
        });

        accuracyChart = new Chart(ctxAcc, {
            type: 'bar',
            data: {
                labels: accLabels,
                datasets: [{
                    label: 'Accuracy %',
                    data: accData,
                    backgroundColor: 'rgba(13, 138, 150, 0.85)',
                    borderRadius: 5
                }]
            },
            options: {
                plugins: { legend: { labels: { color: chartColors.textSecondary } } },
                scales: {
                    y: {
                        min: 0, max: 100,
                        grid: { color: chartColors.gridLight },
                        ticks: { color: chartColors.textMuted }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: chartColors.textMuted }
                    }
                }
            }
        });
    }

    function renderDoctorPatientChart() {
        const ctx = document.getElementById('doctor-patient-chart');
        if (!ctx) return;
        if (doctorPatientChart) doctorPatientChart.destroy();
        warmChartDefaults();

        doctorPatientChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Patient Perception Score',
                    data: [3, 4, 6, 8],
                    borderColor: chartColors.teal,
                    backgroundColor: 'rgba(13, 138, 150, 0.08)',
                    borderWidth: 3,
                    tension: 0.2,
                    fill: true,
                    pointBackgroundColor: chartColors.teal,
                    pointRadius: 5
                }]
            },
            options: {
                plugins: { legend: { labels: { color: chartColors.textSecondary } } },
                scales: {
                    y: {
                        min: 1, max: 10,
                        grid: { color: chartColors.gridLight },
                        ticks: { color: chartColors.textMuted }
                    },
                    x: {
                        grid: { color: chartColors.gridLight },
                        ticks: { color: chartColors.textMuted }
                    }
                }
            }
        });
    }

    // ─── Patient Feedback Flow ──────────────────────────────
    const feedbackForm          = document.getElementById('patient-feedback-form');
    const feedbackSlider        = document.getElementById('feedback-score');
    const feedbackScoreDisplay  = document.getElementById('feedback-score-display');
    const feedbackContainer     = document.getElementById('feedback-form-container');
    const feedbackLocked        = document.getElementById('feedback-locked-container');

    if (feedbackSlider) {
        feedbackSlider.addEventListener('input', (e) => {
            feedbackScoreDisplay.textContent = `${e.target.value} / 10`;
        });
    }

    if (feedbackForm) {
        feedbackForm.addEventListener('submit', (e) => {
            e.preventDefault();
            showToast('Feedback submitted successfully!');
            feedbackContainer.classList.add('hidden');
            feedbackLocked.classList.remove('hidden');
        });
    }

    // ─── Web Audio API & Haptic Game Simulation ─────────────
    const modeSegments       = document.querySelectorAll('.mode-selector .segment');
    const trainingContainer  = document.getElementById('training-container');
    const simpleModeContainer = document.getElementById('simple-mode-container');
    const hapticWindow       = document.getElementById('haptic-window');
    const btnPlayGame        = document.getElementById('btn-play-game');
    const playLabel          = document.getElementById('play-label');
    const btnUserTap         = document.getElementById('btn-user-tap');
    const pulseRingAnim      = document.getElementById('pulse-ring-anim');
    const pulseDot           = document.getElementById('pulse-dot');

    const scoreHits          = document.getElementById('game-hits');
    const scoreMisses        = document.getElementById('game-misses');
    const scoreAccuracy      = document.getElementById('game-accuracy');

    let isPlaying   = false;
    let audioContext = null;
    let gameLoop     = null;
    let hapticActive = false;
    let hapticTimer  = null;
    let hits         = 0;
    let misses       = 0;
    
    let availableSongs = [];
    let currentAudioElement = null;
    let songPeaks = [];
    let nextPeakIndex = 0;
    
    // Initialize spectrogram if available
    let spectrogram = null;
    if (window.Spectrogram) {
        spectrogram = new window.Spectrogram('spectrogram-canvas');
    }

    // Mode metadata for simple modes
    const modeMeta = {
        normal:  { icon: 'graphic_eq', title: 'Normal mode',  desc: 'The strap continuously translates your missing frequencies into haptics as you go about your day.' },
        discreet: { icon: 'vibration',  title: 'Discreet mode', desc: 'Gentler, lower-key vibrations for meetings and quiet settings — the strap stays socially invisible.' }
    };

    modeSegments.forEach(seg => {
        seg.addEventListener('click', async (e) => {
            modeSegments.forEach(s => s.classList.remove('active'));
            e.target.classList.add('active');
            const mode = e.target.dataset.mode;

            if (mode === 'training') {
                trainingContainer.classList.remove('hidden');
                simpleModeContainer.classList.add('hidden');
                
                try {
                    await loadSongsTable();
                } catch (e) {
                    console.error('Failed to load songs:', e);
                }
            } else {
                stopGame();
                trainingContainer.classList.add('hidden');
                simpleModeContainer.classList.remove('hidden');

                // Update simple mode content
                const meta = modeMeta[mode] || modeMeta.normal;
                document.getElementById('mode-icon').textContent = meta.icon;
                document.getElementById('mode-title').textContent = meta.title;
                document.getElementById('mode-desc').textContent = meta.desc;
            }
        });
    });

    if (btnPlayGame) {
        btnPlayGame.addEventListener('click', () => {
            if (isPlaying) return stopGame();
            startGame();
        });
    }

    let currentSessionId = null;

    async function startGame() {
        if (availableSongs.length === 0) return;
        
        const selector = document.getElementById('song-selector');
        if (!selector || selector.value === "") return;
        
        const selectedSong = availableSongs[selector.value];
        songPeaks = selectedSong.peaks || [];
        nextPeakIndex = 0;

        // Start API session
        try {
            currentSessionId = await API.startTrainingSession(currentUser.id, selectedSong.Song_ID);
        } catch (e) {
            console.error("Failed to start session:", e);
            showToast("Failed to start training session in database.");
        }

        isPlaying = true;
        const playIcon = btnPlayGame.querySelector('.ms');
        playIcon.textContent = 'stop';
        playLabel.textContent = 'Stop track';
        hits = 0; misses = 0;
        updateScore();

        if (currentAudioElement) {
            currentAudioElement.pause();
            currentAudioElement.currentTime = 0;
        }

        const fileName = selectedSong.File_Path.split('/').pop().split('\\').pop();
        currentAudioElement = new Audio(`${API._baseUrl.replace('/api', '')}/api/audio/${fileName}`);
        currentAudioElement.crossOrigin = "anonymous";
        currentAudioElement.play();

        if (spectrogram) {
            spectrogram.connect(currentAudioElement);
            spectrogram.start();
        }

        gameLoop = setInterval(() => {
            if (!currentAudioElement || currentAudioElement.paused) return;
            
            const currentTimeMs = currentAudioElement.currentTime * 1000;
            
            if (nextPeakIndex < songPeaks.length) {
                const peak = songPeaks[nextPeakIndex];
                if (currentTimeMs >= peak.time_ms && currentTimeMs < peak.time_ms + 500) {
                    triggerHapticEvent();
                    nextPeakIndex++;
                } else if (currentTimeMs > peak.time_ms + 500) {
                    nextPeakIndex++;
                }
            }
            
            if (currentAudioElement.ended) {
                stopGame();
            }
        }, 50);
    }

    async function stopGame() {
        if (!isPlaying && !hapticActive) return;
        isPlaying = false;

        const playIcon = btnPlayGame ? btnPlayGame.querySelector('.ms') : null;
        if (playIcon) playIcon.textContent = 'play_arrow';
        if (playLabel) playLabel.textContent = 'Play track';

        clearInterval(gameLoop);
        clearTimeout(hapticTimer);

        let finalDuration = 0;
        if (currentAudioElement) {
            finalDuration = currentAudioElement.currentTime;
            currentAudioElement.pause();
            currentAudioElement.currentTime = 0;
        }

        // Reset visuals
        if (pulseDot) pulseDot.classList.remove('active');
        if (pulseRingAnim) pulseRingAnim.classList.remove('visible');
        if (pulseRingAnim) pulseRingAnim.classList.remove('visible');
        if (btnUserTap) btnUserTap.classList.remove('haptic-active');
        hapticActive = false;
        
        if (spectrogram) {
            spectrogram.stop();
        }

        // Stop API session
        const total = hits + misses;
        const acc = total === 0 ? 0 : Math.round((hits / total) * 100);
        
        if (currentSessionId) {
            try {
                await API.stopTrainingSession(currentUser.id, currentSessionId, {
                    duration_seconds: finalDuration,
                    total_events: total,
                    hits: hits,
                    misses: misses,
                    false_positives: 0,
                    accuracy: acc
                });
            } catch (e) {
                console.error("Failed to stop session:", e);
            }
        }

        // Show Conclusion Modal
        const modal = document.getElementById('conclusion-modal');
        if (modal) {
            document.getElementById('modal-hits').textContent = hits;
            document.getElementById('modal-misses').textContent = misses;
            document.getElementById('modal-acc').textContent = acc + '%';
            modal.classList.remove('hidden');
        }
    }

    function triggerHapticEvent() {
        if (hapticActive) return;
        hapticActive = true;
        let tapped = false;

        // Visual: pulse ring + dot glow + tap button highlight
        if (pulseDot) pulseDot.classList.add('active');
        if (pulseRingAnim) pulseRingAnim.classList.add('visible');
        if (btnUserTap) btnUserTap.classList.add('haptic-active');

        // Wait for user tap
        const tapHandler = () => {
            if (tapped) return;
            tapped = true;
            hits++;
            updateScore();
            btnUserTap.removeEventListener('click', tapHandler);
            clearTimeout(hapticTimer);

            // Success flash
            if (pulseDot) pulseDot.classList.remove('active');
            if (pulseRingAnim) pulseRingAnim.classList.remove('visible');
            if (btnUserTap) btnUserTap.classList.remove('haptic-active');
            hapticActive = false;
        };

        btnUserTap.addEventListener('click', tapHandler);

        // Timeout — miss
        hapticTimer = setTimeout(() => {
            if (pulseDot) pulseDot.classList.remove('active');
            if (pulseRingAnim) pulseRingAnim.classList.remove('visible');
            if (btnUserTap) btnUserTap.classList.remove('haptic-active');
            btnUserTap.removeEventListener('click', tapHandler);
            hapticActive = false;
            if (!tapped) {
                misses++;
                updateScore();
            }
        }, 1000);
    }

    function updateScore() {
        scoreHits.textContent = hits;
        scoreMisses.textContent = misses;
        const total = hits + misses;
        const acc = total === 0 ? 0 : Math.round((hits / total) * 100);
        scoreAccuracy.textContent = acc;
    }

    // Modal buttons
    const btnViewProgress = document.getElementById('btn-view-progress');
    if (btnViewProgress) {
        btnViewProgress.addEventListener('click', () => {
            document.getElementById('conclusion-modal').classList.add('hidden');
            app.showSubView('patient-stats');
        });
    }

    // ─── Admin Flow ─────────────────────────────────────────
    const adminAddForm = document.getElementById('admin-add-user-form');
    if (adminAddForm) {
        adminAddForm.addEventListener('submit', (e) => {
            e.preventDefault();
            showToast('Clinical staff member registered successfully!');
            adminAddForm.reset();
        });
    }

    // ─── Doctor Config Form ─────────────────────────────────
    const doctorConfigForm = document.getElementById('doctor-config-form');
    if (doctorConfigForm) {
        doctorConfigForm.addEventListener('submit', (e) => {
            e.preventDefault();
            showToast('Configuration saved successfully!');
        });
    }

    // ─── CSV Download Logic ─────────────────────────────────
    const btnDownloadCsv = document.getElementById('btn-download-csv');
    if (btnDownloadCsv) {
        btnDownloadCsv.addEventListener('click', () => {
            if (availableSongs.length === 0) {
                showToast('No songs to download.', 'error');
                return;
            }
            
            const headers = ['Song_ID', 'Title', 'Artist', 'Duration_Seconds', 'Total_Peaks', 'Created_At'];
            const rows = availableSongs.map(song => {
                return [
                    song.Song_ID,
                    `"${song.Title}"`,
                    `"${song.Artist}"`,
                    song.Duration_Seconds,
                    song.peaks ? song.peaks.length : 0,
                    `"${song.Created_At || ''}"`
                ].join(',');
            });
            
            const csvContent = headers.join(',') + '\n' + rows.join('\n');
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            
            const link = document.createElement('a');
            link.setAttribute('href', url);
            link.setAttribute('download', 'training_tracks_library.csv');
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showToast('CSV downloaded successfully!');
        });
    }

    // ─── Custom Audio Upload Logic ──────────────────────────
    const fileInput = document.getElementById('audio-upload');
    if (fileInput) {
        fileInput.addEventListener('change', async (e) => {
            if (!e.target.files.length) return;
            const file = e.target.files[0];
            
            showToast(`Uploading ${file.name}...`);
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const res = await fetch(`${API._baseUrl}/audio/upload`, {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.success) {
                    showToast('Track processed and added to library!');
                    loadSongsTable(); // Reload dropdown and table
                } else {
                    showToast(data.error || 'Upload failed', 'error');
                }
            } catch (err) {
                console.error(err);
                showToast('Failed to upload track', 'error');
            }
            // Reset input
            fileInput.value = '';
        });
    }

    // Helper to reload songs
    async function loadSongsTable() {
        try {
            const allSongs = await API.getSongs();
            availableSongs = allSongs.filter(s => s.File_Path);
            const selector = document.getElementById('song-selector');
            if (selector) {
                const currentVal = selector.value;
                selector.innerHTML = '';
                availableSongs.forEach((song, idx) => {
                    const option = document.createElement('option');
                    option.value = idx;
                    option.textContent = `${song.Title} (${song.Duration_Seconds}s)`;
                    option.style.background = '#2a2a2a';
                    option.style.color = '#ffffff';
                    selector.appendChild(option);
                });
                if (currentVal && parseInt(currentVal) < availableSongs.length) {
                    selector.value = currentVal;
                }
            }
            
            const tableBody = document.getElementById('songs-table-body');
            if (tableBody) {
                tableBody.innerHTML = '';
                availableSongs.forEach(song => {
                    const row = document.createElement('div');
                    row.className = 'patient-table-row';
                    row.style.gridTemplateColumns = '2fr 1fr 1fr';
                    row.innerHTML = `
                        <span>${song.Title}</span>
                        <span class="value-mono">${song.Duration_Seconds}s</span>
                        <span style="color:var(--text-secondary);">${song.peaks ? song.peaks.length : 0} peaks</span>
                    `;
                    tableBody.appendChild(row);
                });
            }
        } catch (e) {
            console.error('Failed to load songs:', e);
        }
    }

    // ─── Hearing Loss Simulator (Doctor View) ───────────────
    const btnSimPlay = document.getElementById('btn-sim-play');
    const simPlayIcon = document.getElementById('sim-play-icon');
    const simPlayLabel = document.getElementById('sim-play-label');
    const simSongSelector = document.getElementById('sim-song-selector');
    
    // EQ Sliders and Value Displays
    const eqBands = [
        { freq: 250, slider: document.getElementById('eq-250'), valDisplay: document.getElementById('val-250') },
        { freq: 500, slider: document.getElementById('eq-500'), valDisplay: document.getElementById('val-500') },
        { freq: 1000, slider: document.getElementById('eq-1000'), valDisplay: document.getElementById('val-1000') },
        { freq: 2000, slider: document.getElementById('eq-2000'), valDisplay: document.getElementById('val-2000') },
        { freq: 4000, slider: document.getElementById('eq-4000'), valDisplay: document.getElementById('val-4000') }
    ];

    let simAudioCtx = null;
    let simAudioElement = null;
    let simSource = null;
    let eqFilters = [];
    let simIsPlaying = false;
    let simSongsLoaded = false;
    let simAllSongs = [];

    async function loadSimulatorSongs() {
        if (simSongsLoaded || !simSongSelector) return;
        try {
            const allSongs = await API.getSongs();
            simAllSongs = allSongs.filter(s => s.File_Path);
            simSongSelector.innerHTML = '';
            simAllSongs.forEach((song, idx) => {
                const option = document.createElement('option');
                option.value = idx;
                option.textContent = `${song.Title} (${song.Duration_Seconds}s)`;
                option.style.background = '#2a2a2a';
                option.style.color = '#ffffff';
                simSongSelector.appendChild(option);
            });
            // Try to default to vocal_sibilance if available, else first track
            const defaultIdx = simAllSongs.findIndex(s => s.File_Path.includes('vocal_sibilance'));
            if (defaultIdx !== -1) {
                simSongSelector.selectedIndex = defaultIdx;
            }
            simSongsLoaded = true;
        } catch (e) {
            console.error('Failed to load songs for simulator:', e);
            simSongSelector.innerHTML = '<option disabled>Failed to load tracks</option>';
        }
    }

    function initSimulator() {
        if (simAudioCtx) return;
        simAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
        
        simAudioElement = new Audio();
        simAudioElement.crossOrigin = "anonymous";
        simAudioElement.loop = true;

        simSource = simAudioCtx.createMediaElementSource(simAudioElement);
        
        // Build the 5-band EQ chain
        let prevNode = simSource;
        eqFilters = [];
        
        eqBands.forEach(band => {
            const filter = simAudioCtx.createBiquadFilter();
            filter.type = "peaking";
            filter.frequency.value = band.freq;
            filter.Q.value = 1.0; // Standard octave width
            filter.gain.value = band.slider ? parseFloat(band.slider.value) : 0;
            
            prevNode.connect(filter);
            prevNode = filter;
            eqFilters.push(filter);
        });
        
        // Connect the last filter to the destination (speakers)
        prevNode.connect(simAudioCtx.destination);
    }

    // Bind slider inputs to the BiquadFilters
    eqBands.forEach((band, index) => {
        if (band.slider) {
            band.slider.addEventListener('input', (e) => {
                const gainVal = parseFloat(e.target.value);
                // Update UI text
                if (band.valDisplay) {
                    band.valDisplay.textContent = gainVal > 0 ? `+${gainVal} dB` : `${gainVal} dB`;
                    // Color code negative values for clinical emphasis
                    band.valDisplay.style.color = gainVal < -10 ? 'var(--accent-amber)' : 'var(--text-muted)';
                }
                
                // Update Audio Filter in real-time
                if (simAudioCtx && eqFilters[index]) {
                    eqFilters[index].gain.setTargetAtTime(gainVal, simAudioCtx.currentTime, 0.05);
                }
            });
        }
    });

    // Load songs when someone clicks the View button for the first time
    document.addEventListener('click', (e) => {
        if (e.target.closest('.btn-view')) {
            loadSimulatorSongs();
        }
    });

    if (simSongSelector) {
        simSongSelector.addEventListener('change', () => {
            if (simIsPlaying && simAudioElement) {
                const selectedIdx = simSongSelector.value;
                const song = simAllSongs[selectedIdx];
                simAudioElement.src = `${API._baseUrl}/audio/${song.File_Path.split('/').pop()}`;
                simAudioElement.play();
            }
        });
    }

    if (btnSimPlay) {
        btnSimPlay.addEventListener('click', () => {
            if (!simSongsLoaded) {
                showToast('Please wait for tracks to load', 'error');
                return;
            }
            
            initSimulator();
            
            if (simAudioCtx.state === 'suspended') {
                simAudioCtx.resume();
            }

            if (simIsPlaying) {
                simAudioElement.pause();
                simIsPlaying = false;
                if(simPlayIcon) simPlayIcon.textContent = 'play_arrow';
                if(simPlayLabel) simPlayLabel.textContent = 'Play';
            } else {
                const selectedIdx = simSongSelector.value;
                const song = simAllSongs[selectedIdx];
                const filename = song.File_Path.includes('/') ? song.File_Path.split('/').pop() : song.File_Path;
                simAudioElement.src = `${API._baseUrl}/audio/${filename}`;
                
                simAudioElement.play();
                simIsPlaying = true;
                if(simPlayIcon) simPlayIcon.textContent = 'pause';
                if(simPlayLabel) simPlayLabel.textContent = 'Pause';
            }
        });
    }
});
