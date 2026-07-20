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
                loadAdminDashboard();
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

    // ─── Admin Dashboard Logic ────────────────────────────────────────────────

    async function loadAdminDashboard() {
        try {
            // 1. Fetch Stats
            const stats = await API.getAdminStats();
            if (stats) {
                document.getElementById('kpi-users').textContent = stats.total_users;
                document.getElementById('kpi-users-desc').textContent = `${stats.patients} Patients, ${stats.doctors} Doctors, 1 Admin`;
                document.getElementById('kpi-data').textContent = (stats.data_points > 1000) ? (stats.data_points/1000).toFixed(1) + 'k' : stats.data_points;
                document.getElementById('kpi-load').textContent = stats.db_load;
            }

            // 2. Fetch Doctors for the dropdown
            const doctors = await API.getAllDoctors();
            const doctorSelect = document.getElementById('pat-doctor');
            if (doctorSelect) {
                doctorSelect.innerHTML = '<option value="" disabled selected>Select a Doctor</option>';
                doctors.forEach(doc => {
                    const opt = document.createElement('option');
                    opt.value = doc.Doctor_ID;
                    opt.textContent = `Dr. ${doc.First_Name} ${doc.Last_Name} (${doc.Email})`;
                    doctorSelect.appendChild(opt);
                });
            }

            // 3. Fetch Logs
            const logs = await API.getAdminLogs();
            const logsContainer = document.getElementById('admin-logs');
            if (logsContainer) {
                logsContainer.innerHTML = '';
                if (logs.length === 0) {
                    logsContainer.innerHTML = '<div>No recent activity.</div>';
                } else {
                    logs.forEach(log => {
                        const div = document.createElement('div');
                        const time = new Date(log.Timestamp).toLocaleTimeString();
                        div.innerHTML = `<span style="color:#94a3b8">[${time}]</span> <span style="color:#0d8a96">[${log.Event_Type}]</span> ${log.Action_Description || ''}`;
                        logsContainer.appendChild(div);
                    });
                }
            }

            // 4. Render Chart
            renderAdminChart();

        } catch (err) {
            console.error('Failed to load dashboard data:', err);
            showToast('Error loading dashboard data', true);
        }
    }

    // ─── Chart Rendering (Doctor Analytics Dashboard) ───────
    let performanceChart = null;

    async function renderAdminChart() {
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

        let labels = [];
        let hitsData = [];
        let missesData = [];

        try {
            const trends = await API.getAdminPerformance();
            if (trends && trends.length > 0) {
                trends.forEach(t => {
                    labels.push(t.Date);
                    hitsData.push(t.Total_Hits);
                    missesData.push(t.Total_Misses);
                });
            } else {
                labels = ['No Data'];
                hitsData = [0];
                missesData = [0];
            }
        } catch(e) {
            labels = ['Error'];
            hitsData = [0];
            missesData = [0];
        }

        performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Total Hits',
                        data: hitsData,
                        borderColor: colors.green,
                        backgroundColor: 'rgba(47, 143, 107, 0.1)',
                        borderWidth: 3,
                        tension: 0.3,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Total Misses',
                        data: missesData,
                        borderColor: colors.red,
                        backgroundColor: 'rgba(196, 80, 62, 0.1)',
                        borderWidth: 3,
                        tension: 0.3,
                        fill: true,
                        yAxisID: 'y'
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
                    x: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: colors.textMuted }
                    }
                }
            }
        });
    }

    // ─── Registration Handlers ────────────────────────────────────────────────

    const docForm = document.getElementById('admin-add-doctor-form');
    if (docForm) {
        docForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('doc-email').value;
            const pass = document.getElementById('doc-password').value;
            try {
                await API.registerDoctor(email, pass);
                showToast(`Doctor registered: ${email}`);
                docForm.reset();
                document.getElementById('modal-add-doctor').classList.add('hidden');
                loadAdminDashboard(); // refresh
            } catch (err) {
                showToast(err.message, true);
            }
        });
    }

    const patForm = document.getElementById('admin-add-patient-form');
    if (patForm) {
        patForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fName = document.getElementById('pat-first-name').value;
            const lName = document.getElementById('pat-last-name').value;
            const email = document.getElementById('pat-email').value;
            const phone = document.getElementById('pat-phone').value;
            const testDate = document.getElementById('pat-test-date').value;
            const docId = document.getElementById('pat-doctor').value;
            const pass = document.getElementById('pat-password').value;
            try {
                await API.registerPatient(email, pass, docId, fName, lName, phone, testDate);
                showToast(`Patient registered: ${email}`);
                patForm.reset();
                document.getElementById('modal-add-patient').classList.add('hidden');
                loadAdminDashboard(); // refresh
            } catch (err) {
                showToast(err.message, true);
            }
        });
    }
});
