/**
 * Smart Strap - Main Application Logic
 * Handles Routing, State, and UI Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    
    // --- State ---
    let currentUser = null;
    let currentRole = 'patient'; // Default selected role on login screen

    // --- DOM Elements ---
    const topNav = document.getElementById('top-nav');
    const navUserRole = document.getElementById('nav-user-role');
    const navUserName = document.getElementById('nav-user-name');
    const btnLogout = document.getElementById('btn-logout');
    
    const views = document.querySelectorAll('.view');
    const loginForm = document.getElementById('login-form');
    const roleSegments = document.querySelectorAll('.segment');

    // --- Routing & View Management ---
    function showView(viewId) {
        views.forEach(v => {
            v.classList.remove('active');
        });
        document.getElementById(viewId).classList.add('active');
    }

    function updateNav() {
        if (currentUser) {
            topNav.classList.remove('hidden');
            navUserRole.textContent = currentUser.role;
            navUserName.textContent = currentUser.name;
        } else {
            topNav.classList.add('hidden');
        }
    }

    // --- Login Logic ---
    
    // Role Selector
    roleSegments.forEach(segment => {
        segment.addEventListener('click', (e) => {
            roleSegments.forEach(s => s.classList.remove('active'));
            e.target.classList.add('active');
            currentRole = e.target.getAttribute('data-role');
            
            // Helpful auto-fill for demo purposes
            document.getElementById('login-email').value = `${currentRole}@demo.com`;
            document.getElementById('login-password').value = 'password';
        });
    });

    // Auto-fill initial for demo
    document.getElementById('login-email').value = 'patient@demo.com';
    document.getElementById('login-password').value = 'password';

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const btn = loginForm.querySelector('button');
        
        btn.textContent = 'Authenticating...';
        btn.disabled = true;

        try {
            const user = await API.login(email, password, currentRole);
            currentUser = user;
            updateNav();
            
            // Route to appropriate dashboard
            showView(`view-${user.role}`);
            
            showToast(`Welcome back, ${user.name}`);
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btn.textContent = 'Access Portal';
            btn.disabled = false;
        }
    });

    // Logout
    btnLogout.addEventListener('click', () => {
        currentUser = null;
        updateNav();
        showView('view-login');
        showToast('Logged out successfully');
    });

    // --- Toast Notifications ---
    function showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => toast.classList.add('toast-visible'));

        // Auto-dismiss after 3.5 s
        setTimeout(() => {
            toast.classList.remove('toast-visible');
            toast.addEventListener('transitionend', () => toast.remove(), { once: true });
        }, 3500);
    }

    // --- Sub-View Navigation ---
    window.app = {
        showView: showView,
        showSubView: (subViewId) => {
            showView(`view-${subViewId}`);
            if (subViewId === 'patient-profile') renderAudiogramChart();
            if (subViewId === 'patient-stats') renderStatsCharts();
            if (subViewId === 'doctor-patient-detail') renderDoctorPatientChart();
        }
    };

    // --- Chart.js Rendering ---
    let audiogramChart, trendChart, accuracyChart;

    function renderAudiogramChart() {
        const ctx = document.getElementById('audiogram-chart');
        if (!ctx) return;
        if (audiogramChart) audiogramChart.destroy();
        
        Chart.defaults.color = '#94a3b8';
        
        audiogramChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['125', '250', '500', '1000', '2000', '4000', '8000'],
                datasets: [{
                    label: 'Hearing Threshold (dB HL)',
                    data: [10, 15, 10, 20, 30, 65, 35], // Simulate a 4kHz notch
                    borderColor: '#0ea5e9',
                    backgroundColor: 'rgba(14, 165, 233, 0.1)',
                    borderWidth: 3,
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#10b981',
                    pointRadius: 6
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        reverse: true, // Audiograms go down
                        min: -10,
                        max: 120,
                        title: { display: true, text: 'Hearing Level (dB)' }
                    },
                    x: {
                        title: { display: true, text: 'Frequency (Hz)' }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#f8fafc' } }
                }
            }
        });
    }

    function renderStatsCharts() {
        const ctxTrend = document.getElementById('feedback-trend-chart');
        const ctxAcc = document.getElementById('training-accuracy-chart');
        
        if (trendChart) trendChart.destroy();
        if (accuracyChart) accuracyChart.destroy();
        
        Chart.defaults.color = '#94a3b8';

        trendChart = new Chart(ctxTrend, {
            type: 'line',
            data: {
                labels: ['May 1', 'May 15', 'Jun 1', 'Jun 15'],
                datasets: [{
                    label: 'Tinnitus Relief Score',
                    data: [3, 5, 6, 8],
                    borderColor: '#10b981',
                    tension: 0.2
                }]
            },
            options: { scales: { y: { min: 1, max: 10 } } }
        });

        accuracyChart = new Chart(ctxAcc, {
            type: 'bar',
            data: {
                labels: ['Session 1', 'Session 2', 'Session 3', 'Session 4'],
                datasets: [{
                    label: 'Accuracy %',
                    data: [65, 72, 85, 94],
                    backgroundColor: '#0ea5e9',
                    borderRadius: 4
                }]
            },
            options: { scales: { y: { min: 0, max: 100 } } }
        });
    }

    let doctorPatientChart;
    function renderDoctorPatientChart() {
        const ctx = document.getElementById('doctor-patient-chart');
        if (!ctx) return;
        if (doctorPatientChart) doctorPatientChart.destroy();
        
        Chart.defaults.color = '#94a3b8';
        
        doctorPatientChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Patient Relief Score (Yossi Cohen)',
                    data: [3, 4, 6, 8],
                    borderColor: '#10b981',
                    tension: 0.2,
                    fill: false
                }]
            },
            options: { scales: { y: { min: 1, max: 10 } } }
        });
    }

    // --- Patient Feedback Flow ---
    const feedbackForm = document.getElementById('patient-feedback-form');
    const feedbackSlider = document.getElementById('feedback-score');
    const feedbackScoreDisplay = document.getElementById('feedback-score-display');
    const feedbackContainer = document.getElementById('feedback-form-container');
    const feedbackLocked = document.getElementById('feedback-locked-container');

    if (feedbackSlider) {
        feedbackSlider.addEventListener('input', (e) => {
            feedbackScoreDisplay.textContent = `${e.target.value} / 10`;
        });
    }

    if (feedbackForm) {
        feedbackForm.addEventListener('submit', (e) => {
            e.preventDefault();
            // Simulate 14-day lock
            showToast('Feedback submitted successfully!');
            feedbackContainer.classList.add('hidden');
            feedbackLocked.classList.remove('hidden');
        });
    }

    // --- Web Audio API & Haptic Game Simulation ---
    const modeSegments = document.querySelectorAll('.mode-selector .segment');
    const trainingContainer = document.getElementById('training-container');
    const hapticWindow = document.getElementById('haptic-window');
    const btnPlayGame = document.getElementById('btn-play-game');
    const btnUserTap = document.getElementById('btn-user-tap');
    
    const scoreHits = document.getElementById('game-hits');
    const scoreMisses = document.getElementById('game-misses');
    const scoreAccuracy = document.getElementById('game-accuracy');
    
    let isPlaying = false;
    let audioContext, oscillator, gainNode;
    let gameLoop;
    let hapticActive = false;
    
    let hits = 0;
    let misses = 0;

    modeSegments.forEach(seg => {
        seg.addEventListener('click', (e) => {
            modeSegments.forEach(s => s.classList.remove('active'));
            e.target.classList.add('active');
            if (e.target.dataset.mode === 'training') {
                trainingContainer.classList.remove('hidden');
            } else {
                trainingContainer.classList.add('hidden');
            }
        });
    });

    if (btnPlayGame) {
        btnPlayGame.addEventListener('click', () => {
            if (isPlaying) return stopGame();
            startGame();
        });
    }

    function startGame() {
        isPlaying = true;
        btnPlayGame.textContent = '⏹ Stop Track';
        btnPlayGame.classList.replace('btn-primary', 'btn-outline');
        
        hits = 0; misses = 0;
        updateScore();

        // Simulate Web Audio API for PoC
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        oscillator = audioContext.createOscillator();
        gainNode = audioContext.createGain();
        
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(4000, audioContext.currentTime); // 4kHz focus
        
        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        oscillator.start();

        // Game Loop: randomly trigger a 4kHz "notch" event
        gameLoop = setInterval(() => {
            if (Math.random() > 0.7) {
                triggerHapticEvent();
            }
        }, 2000);
    }

    function stopGame() {
        isPlaying = false;
        btnPlayGame.textContent = '▶ Play Track';
        btnPlayGame.classList.replace('btn-outline', 'btn-primary');
        clearInterval(gameLoop);
        if (oscillator) oscillator.stop();
        hapticWindow.classList.remove('haptic-active');
        hapticActive = false;
    }

    function triggerHapticEvent() {
        if (hapticActive) return;
        hapticActive = true;
        
        // Visual flash (the glow)
        hapticWindow.classList.add('haptic-active');
        
        // Audio blip
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.5);

        // Wait for user interaction
        let interacted = false;
        
        const tapHandler = () => {
            interacted = true;
            hits++;
            updateScore();
            btnUserTap.removeEventListener('click', tapHandler);
            
            // Visual feedback for successful tap
            btnUserTap.style.backgroundColor = 'var(--accent-emerald)';
            setTimeout(() => btnUserTap.style.backgroundColor = '', 200);
        };
        
        btnUserTap.addEventListener('click', tapHandler);

        setTimeout(() => {
            hapticWindow.classList.remove('haptic-active');
            hapticActive = false;
            btnUserTap.removeEventListener('click', tapHandler);
            if (!interacted) {
                misses++;
                updateScore();
            }
        }, 800); // 800ms window to click
    }

    function updateScore() {
        scoreHits.textContent = hits;
        scoreMisses.textContent = misses;
        const total = hits + misses;
        const acc = total === 0 ? 0 : Math.round((hits / total) * 100);
        scoreAccuracy.textContent = acc + '%';
    }

    // --- Admin Flow ---
    const adminAddForm = document.getElementById('admin-add-user-form');
    if (adminAddForm) {
        adminAddForm.addEventListener('submit', (e) => {
            e.preventDefault();
            showToast('Clinical staff member registered successfully!');
            adminAddForm.reset();
        });
    }
});
