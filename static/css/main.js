document.addEventListener("DOMContentLoaded", () => {
  /* ---------- Sidebar toggle ---------- */
  const menuToggle = document.getElementById("menuToggle");
  const sidebar = document.getElementById("sidebar");
  const backdrop = document.getElementById("sidebarBackdrop");

  const closeSidebar = () => {
    sidebar?.classList.remove("open");
    backdrop?.classList.remove("show");
  };

  menuToggle?.addEventListener("click", () => {
    sidebar?.classList.toggle("open");
    backdrop?.classList.toggle("show");
  });
  backdrop?.addEventListener("click", closeSidebar);

  /* ---------- Flash dismiss ---------- */
  document.querySelectorAll(".flash-close").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.target.closest(".flash")?.remove();
    });
  });

  /* Auto-dismiss flashes after 4s */
  setTimeout(() => {
    document.querySelectorAll(".flash").forEach((f) => {
      f.style.transition = "opacity .4s, transform .4s";
      f.style.opacity = "0";
      f.style.transform = "translateY(-6px)";
      setTimeout(() => f.remove(), 400);
    });
  }, 4000);

  /* ---------- Confirm on destructive actions ---------- */
  document.querySelectorAll("[data-confirm]").forEach((el) => {
    el.addEventListener("click", (e) => {
      if (!window.confirm(el.dataset.confirm || "Are you sure?")) {
        e.preventDefault();
      }
    });
  });

  /* ---------- Auto-submit filters on change ---------- */
  const filterForm = document.getElementById("filterForm");
  if (filterForm) {
    filterForm.querySelectorAll("select").forEach((sel) => {
      sel.addEventListener("change", () => filterForm.submit());
    });
  }
});