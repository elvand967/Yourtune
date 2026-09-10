// apps/core/static/core/js/theme-switcher.js

(() => {
  const STORAGE_KEY = 'theme';
  const THEMES = ['light', 'dark', 'cream'];

  const root = document.documentElement;
  const toggle = document.getElementById('themeToggle');
  const label = document.getElementById('themeToggleLabel');

  if (!root || !toggle) return;

  const themeLabels = {
    light: 'Светлая',
    dark: 'Тёмная',
    cream: 'Кремовая',
  };

  const getSystemTheme = () => {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  };

  const getInitialTheme = () => {
    const savedTheme = localStorage.getItem(STORAGE_KEY);
    return THEMES.includes(savedTheme) ? savedTheme : getSystemTheme();
  };

  const applyTheme = (theme, persist = true) => {
    const nextTheme = THEMES.includes(theme) ? theme : 'light';
    root.setAttribute('data-theme', nextTheme);

    if (persist) {
      localStorage.setItem(STORAGE_KEY, nextTheme);
    }

    if (label) {
      label.textContent = themeLabels[nextTheme] || nextTheme;
    }

    toggle.setAttribute('aria-label', `Переключить тему. Сейчас: ${themeLabels[nextTheme]}`);
    toggle.setAttribute('aria-pressed', nextTheme !== 'light');
  };

  applyTheme(getInitialTheme(), false);

  toggle.addEventListener('click', () => {
    const current = root.getAttribute('data-theme') || getInitialTheme();
    const index = THEMES.indexOf(current);
    const next = THEMES[(index + 1) % THEMES.length];
    applyTheme(next, true);
  });
})();