
// apps/core/static/core/js/theme-switcher.js
// Переключатель цветовых тем для YourTune

(function() {
  'use strict';

  const themeToggle = document.getElementById('theme-toggle');
  const themeToggleMobile = document.getElementById('theme-toggle-mobile');
  const html = document.documentElement;

  // Эмодзи для тем
  const themeIcons = {
    light: '☀️',
    dark: '🌙',
    cream: '🎨'
  };

  // Установите тему по умолчанию
  let currentTheme = localStorage.getItem('theme') || 'dark';
  html.setAttribute('data-theme', currentTheme);

  /**
   * Обновление иконки
   */
  function updateIcon() {
    const theme = html.getAttribute('data-theme');
    const icon = themeIcons[theme] || '🌙';

    // Обновляем иконку в обеих кнопках
    const iconElements = document.querySelectorAll('.topbar__toggle-icon');
    iconElements.forEach(function(el) {
      el.textContent = icon;
    });
  }

  /**
   * Переключение темы
   */
  function toggleTheme() {
    const currentTheme = html.getAttribute('data-theme');

    // Переключение: dark → light → cream → dark
    let newTheme;
    if (currentTheme === 'dark') {
      newTheme = 'light';
    } else if (currentTheme === 'light') {
      newTheme = 'cream';
    } else {
      newTheme = 'dark';
    }

    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    updateIcon();
  }

  // Инициализация иконки
  updateIcon();

  // Навешиваем обработчики событий
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }

  if (themeToggleMobile) {
    themeToggleMobile.addEventListener('click', toggleTheme);
  }
})();