/**
 * Smart Strap - Admin Portal Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const views = document.querySelectorAll('.view');
    const nav = document.getElementById('top-nav');
    const navUserName = document.getElementById('nav-user-name');
    const loginForm = document.getElementById('login-form');
    const btnLogout = document.getElementById('btn-logout');

    let currentUser = null;

    // View Management
    function showView(viewId) {
        views.forEach(v => v.classList.remove('active'));
        const target = document.getElementById(viewId);
        if (target) target.classList.add('active');
    }

    // Navigation State
    function updateNav() {
        if (currentUser) {
            nav.classList.remove('hidden');
            navUserName.textContent = currentUser.name;
        } else {
            nav.classList.add('hidden');
        }
    }

    // Login Handler
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;
            const btn = loginForm.querySelector('.btn-login');
            const originalText = btn.innerHTML;

            btn.innerHTML = 'Authorizing…';
            btn.style.opacity = '0.7';
            btn.disabled = true;

            try {
                // Must be an admin role
                const user = await API.login(email, password, 'admin');
                currentUser = user;
                updateNav();
                showView('view-admin');
                renderAdminChart();
                showToast(`Authorized as ${user.name}`);
            } catch (err) {
                showToast(err.message || 'Access denied.', true);
                btn.innerHTML = originalText;
                btn.style.opacity = '1';
                btn.disabled = false;
            }
        });
    }

    // Logout Handler
    if (btnLogout) {
        btnLogout.addEventListener('click', () => {
            currentUser = null;
            updateNav();
            showView('view-login');
            
            // Reset button state
            const btn = loginForm.querySelector('.btn-login');
            if(btn) {
                btn.innerHTML = 'Authorize <span class="ms">shield</span>';
                btn.style.opacity = '1';
                btn.disabled = false;
            }
        });
    }

    // Toast Notification System
    function showToast(message, isError = false) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = 'toast';
        if (isError) toast.classList.add('error');

        const icon = document.createElement('span');
        icon.className = 'ms';
        icon.textContent = isError ? 'error' : 'check_circle';

        const text = document.createElement('span');
        text.textContent = message;

        toast.appendChild(icon);
        toast.appendChild(text);
        container.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // ─── Chart Rendering (Doctor Analytics Dashboard) ───────
    let performanceChart = null;

    function renderAdminChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;
        if (performanceChart) performanceChart.destroy();

        // Earthy Pulse Theme Colors
        const colors = {
            teal: '#0d8a96',
            green: '#2f8f6b',
            red: '#c4503e',
            textMuted: '#a99f8e',
            textSecondary: '#6f6a60',
            grid: '#e7ded2'
        };

        Chart.defaults.color = colors.textMuted;
        Chart.defaults.font.family = "'Inter', sans-serif";

        const dummyLabels = ['Session 1', 'Session 2', 'Session 3', 'Session 4', 'Session 5'];

        performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dummyLabels,
                datasets: [
                    {
                        label: 'Hits',
                        data: [25, 32, 38, 45, 52],
                        borderColor: colors.green,
                        backgroundColor: 'rgba(47, 143, 107, 0.1)',
                        borderWidth: 3,
                        tension: 0.3,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Misses',
                        data: [15, 12, 9, 6, 4],
                        borderColor: colors.red,
                        backgroundColor: 'rgba(196, 80, 62, 0.1)',
                        borderWidth: 3,
                        tension: 0.3,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Avg Reaction Time (ms)',
                        data: [850, 780, 620, 510, 430],
                        borderColor: colors.teal,
                        backgroundColor: colors.teal,
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 4,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: colors.textSecondary, usePointStyle: true, padding: 20 }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { display: true, text: 'Haptic Events Count', color: colors.textSecondary },
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: colors.textMuted }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: 'Reaction Time (ms)', color: colors.textSecondary },
                        grid: { drawOnChartArea: false },
                        ticks: { color: colors.textMuted }
                    },
                    x: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: colors.textMuted }
                    }
                }
            }
        });
    }
});
