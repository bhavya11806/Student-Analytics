// Interactive Chart.js Initializers for Dashboards & Analytics
document.addEventListener("DOMContentLoaded", function () {
  // 1. Monthly Attendance Line Chart
  const monthlyCanvas = document.getElementById("monthlyAttendanceChart");
  if (monthlyCanvas) {
    fetch("/analytics/api/monthly-trends")
      .then(res => res.json())
      .then(data => {
        const labels = data.map(d => d.month);
        const values = data.map(d => d.percentage);

        new Chart(monthlyCanvas, {
          type: "line",
          data: {
            labels: labels,
            datasets: [{
              label: "Average Attendance (%)",
              data: values,
              borderColor: "#2563eb",
              backgroundColor: "rgba(37, 99, 235, 0.1)",
              borderWidth: 2.5,
              fill: true,
              tension: 0.35,
              pointBackgroundColor: "#1d4ed8",
              pointRadius: 4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                min: 0,
                max: 100,
                ticks: { callback: v => v + "%" },
                grid: { color: "#f1f5f9" }
              },
              x: { grid: { display: false } }
            },
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: { label: ctx => `Attendance: ${ctx.parsed.y}%` }
              }
            }
          }
        });
      });
  }

  // 2. Academic Risk Distribution Doughnut Chart
  const riskCanvas = document.getElementById("riskDistributionChart");
  if (riskCanvas) {
    fetch("/analytics/api/risk-distribution")
      .then(res => res.json())
      .then(data => {
        const labels = ["Good", "Attendance Risk", "Academic Risk", "High Risk", "Moderate"];
        const counts = [
          data["GOOD"] || 0,
          data["ATTENDANCE RISK"] || 0,
          data["ACADEMIC RISK"] || 0,
          data["HIGH RISK"] || 0,
          data["MODERATE PROGRESS"] || 0
        ];

        new Chart(riskCanvas, {
          type: "doughnut",
          data: {
            labels: labels,
            datasets: [{
              data: counts,
              backgroundColor: [
                "#16a34a", // Good - Green
                "#f59e0b", // Attendance Risk - Amber
                "#ef4444", // Academic Risk - Red
                "#1e293b", // High Risk - Dark Slate
                "#6366f1"  // Moderate - Indigo
              ],
              borderWidth: 2,
              borderColor: "#ffffff"
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: "bottom",
                labels: { boxWidth: 12, padding: 12 }
              }
            },
            cutout: "65%"
          }
        });
      });
  }

  // 3. Department Comparison Bar Chart
  const deptCanvas = document.getElementById("deptComparisonChart");
  if (deptCanvas) {
    fetch("/analytics/api/department-comparison")
      .then(res => res.json())
      .then(data => {
        const labels = data.map(d => d.code || d.name);
        const values = data.map(d => d.percentage);

        new Chart(deptCanvas, {
          type: "bar",
          data: {
            labels: labels,
            datasets: [{
              label: "Department Attendance (%)",
              data: values,
              backgroundColor: "#4f46e5",
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                min: 0,
                max: 100,
                ticks: { callback: v => v + "%" },
                grid: { color: "#f1f5f9" }
              },
              x: { grid: { display: false } }
            },
            plugins: {
              legend: { display: false }
            }
          }
        });
      });
  }
});
