// apps/core/static/core/js/theme-switcher.js

(function() {
  'use strict';

  const THEMES = ['light', 'dark', 'cream'];
  const STORAGE_KEY = 'yourtune_theme';

  const LABELS = {
    light: '☀️',
    dark: '🌙',
    cream: '🎨',
  };

  function getStoredTheme() {
    return localStorage.getItem(STORAGE_KEY) || 'light';
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    updateThemeLabel(theme);  // ← Обновлённая функция
  }

  // ← ЗАМЕНИТЕ ЭТУ ФУНКЦИЮ
  function updateThemeLabel(theme) {
    const label = document.getElementById('theme-label');
    if (label) {
      label.textContent = LABELS[theme] || LABELS.light;
    }
  }

  function cycleTheme() {
    const current = getStoredTheme();
    const currentIndex = THEMES.indexOf(current);
    const nextIndex = (currentIndex + 1) % THEMES.length;
    return THEMES[nextIndex];
  }

  function init() {
    // Устанавливаем сохранённую тему
    const storedTheme = getStoredTheme();
    setTheme(storedTheme);

    // Добавляем обработчик
    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
      toggle.addEventListener('click', function() {
        const nextTheme = cycleTheme();
        setTheme(nextTheme);
      });
    }

    // Кнопка "Наверх" в футере
    const backToTop = document.getElementById('backToTop');
    if (backToTop) {
      window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
          backToTop.classList.add('is-active');
        } else {
          backToTop.classList.remove('is-active');
        }
      });

      backToTop.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }
  }

  // Инициализация после загрузки DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Глобальный API
  window.YourTuneTheme = {
    getTheme: getStoredTheme,
    setTheme: setTheme,
    cycleTheme: cycleTheme,
  };
})();