// Dashboard Interactions & Helpers
document.addEventListener("DOMContentLoaded", function () {
  // Sidebar Toggle
  const toggleBtn = document.getElementById("sidebarToggle");
  const sidebar = document.getElementById("appSidebar");

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", function () {
      if (window.innerWidth <= 992) {
        sidebar.classList.toggle("show");
      } else {
        sidebar.classList.toggle("collapsed");
      }
    });
  }

  // Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert.alert-dismissible");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 5000);
  });

  // Select all / Mark all present shortcut for Attendance marking
  const markAllPresentBtn = document.getElementById("markAllPresentBtn");
  if (markAllPresentBtn) {
    markAllPresentBtn.addEventListener("click", function () {
      const presentRadios = document.querySelectorAll('input[type="radio"][value="Present"]');
      presentRadios.forEach(function (radio) {
        radio.checked = true;
      });
    });
  }

  const markAllAbsentBtn = document.getElementById("markAllAbsentBtn");
  if (markAllAbsentBtn) {
    markAllAbsentBtn.addEventListener("click", function () {
      const absentRadios = document.querySelectorAll('input[type="radio"][value="Absent"]');
      absentRadios.forEach(function (radio) {
        radio.checked = true;
      });
    });
  }

  // Quick Notification Read Mark
  const notifItems = document.querySelectorAll(".mark-read-btn");
  notifItems.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const notifId = this.dataset.id;
      fetch(`/api/notifications/mark-read/${notifId}`, { method: "POST" })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            const card = document.getElementById(`notif-item-${notifId}`);
            if (card) {
              card.classList.remove("border-primary", "bg-light");
              this.remove();
            }
          }
        });
    });
  });
});
