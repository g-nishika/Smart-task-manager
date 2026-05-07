document.addEventListener('DOMContentLoaded', () => {
  initSidebarToggle();
  initThemeToggle();
  initPasswordToggle();
  initTaskSearch();
  initCharts();
  initToasts();
});

function initSidebarToggle() {
  const toggle = document.getElementById('toggleSidebar');
  const sidebar = document.querySelector('.sidebar');
  if (!toggle || !sidebar) return;
  toggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
  });
}

function initThemeToggle() {
  const toggle = document.getElementById('darkModeToggle');
  if (!toggle) return;
  const saved = localStorage.getItem('ttm-theme');
  if (saved === 'dark') {
    document.body.classList.add('dark-mode');
  }
  toggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('ttm-theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
  });
}

function initPasswordToggle() {
  document.querySelectorAll('.password-toggle').forEach(button => {
    button.addEventListener('click', () => {
      const input = document.querySelector(button.dataset.target);
      if (!input) return;
      const visible = input.type === 'text';
      input.type = visible ? 'password' : 'text';
      button.innerHTML = visible ? '<i class="bi bi-eye"></i>' : '<i class="bi bi-eye-slash"></i>';
    });
  });
}

function initTaskSearch() {
  const search = document.getElementById('task-search');
  if (!search) return;
  search.addEventListener('input', () => {
    const query = search.value.toLowerCase();
    document.querySelectorAll('#tasks-table tbody tr').forEach(row => {
      row.style.display = row.innerText.toLowerCase().includes(query) ? '' : 'none';
    });
  });
}

function confirmDelete() {
  return window.confirm('Are you sure you want to delete this item? This action cannot be undone.');
}

function initCharts() {
  if (typeof Chart === 'undefined') return;
  const chartData = window.dashboardData || {};
  const statusCanvas = document.getElementById('statusChart');
  if (statusCanvas) {
    new Chart(statusCanvas, {
      type: 'doughnut',
      data: {
        labels: chartData.statusLabels,
        datasets: [{
          data: chartData.statusValues,
          backgroundColor: ['#7c3aed', '#2563eb', '#16a34a'],
          borderWidth: 0,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: '#475569' },
          },
        },
      },
    });
  }

  const progressCanvas = document.getElementById('progressChart');
  if (progressCanvas) {
    new Chart(progressCanvas, {
      type: 'bar',
      data: {
        labels: chartData.progressLabels,
        datasets: [{
          label: 'Tasks',
          data: chartData.progressValues,
          backgroundColor: ['#3b82f6', '#8b5cf6', '#22c55e'],
          borderRadius: 12,
          borderSkipped: false,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: '#475569' },
          },
          y: {
            grid: { color: 'rgba(148, 163, 184, 0.18)' },
            ticks: { color: '#475569', stepSize: 1 },
          },
        },
      },
    });
  }
}

function initToasts() {
  document.querySelectorAll('.toast').forEach(toastEl => {
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
  });
}
