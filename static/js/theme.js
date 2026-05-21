(function () {
  const key = "fitforge-theme";
  const root = document.documentElement;
  const toggle = document.getElementById("themeToggle");

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    localStorage.setItem(key, theme);
    if (toggle) {
      toggle.innerHTML = theme === "light"
        ? '<i class="fa-solid fa-sun"></i>'
        : '<i class="fa-solid fa-moon"></i>';
    }
    if (window.FitForgeChartDefaults) {
      window.FitForgeChartDefaults();
    }
  }

  applyTheme(localStorage.getItem(key) || "dark");

  if (toggle) {
    toggle.addEventListener("click", function () {
      const next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      applyTheme(next);
    });
  }
})();
