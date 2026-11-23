(() => {
  let mode = "auto";
  try {
    mode = localStorage.getItem("homepage-theme") || "auto";
  } catch {}

  function applyTheme() {
    const hour = new Date().getHours();
    const theme = mode === "auto"
      ? (hour >= 7 && hour < 19 ? "light" : "dark")
      : mode;
    document.documentElement.dataset.theme = theme;
    document.querySelector('meta[name="theme-color"]').content =
      theme === "dark" ? "#171c22" : "#ffffff";
    document.querySelectorAll("[data-theme-mode]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.themeMode === mode));
    });
  }

  applyTheme();

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-theme-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        mode = button.dataset.themeMode;
        try {
          localStorage.setItem("homepage-theme", mode);
        } catch {}
        applyTheme();
      });
    });
    applyTheme();
  });

  setInterval(() => {
    if (mode === "auto") applyTheme();
  }, 60_000);

  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) applyTheme();
  });
})();
