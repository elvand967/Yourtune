// ==========================================================================
// apps/core/static/core/js/mobile-menu.js
// Улучшения UX для мобильного меню (checkbox hack)
// ==========================================================================

(function () {
  'use strict';

  const menuToggle = document.getElementById('menu-toggle');
  const mobileMenu = document.getElementById('mobile-menu');
  const mobileClose = mobileMenu?.querySelector('.topbar__mobile-close');
  const mobileOverlay = mobileMenu?.querySelector('.topbar__mobile-overlay');
  const body = document.body;

  if (!menuToggle || !mobileMenu) return;


  // ========================================================================
  // 1. Блокировка скролла body при открытом меню
  // ========================================================================

  menuToggle.addEventListener('change', function () {
    if (this.checked) {
      body.style.overflow = 'hidden';
      mobileMenu.setAttribute('aria-hidden', 'false');
    } else {
      body.style.overflow = '';
      mobileMenu.setAttribute('aria-hidden', 'true');
    }
  });


  // ========================================================================
  // 2. Закрытие по клику на overlay
  // ========================================================================

  mobileOverlay?.addEventListener('click', function () {
    menuToggle.checked = false;
  });


  // ========================================================================
  // 3. Закрытие по кнопке "Закрыть" (дублирует label, но для надёжности)
  // ========================================================================

  mobileClose?.addEventListener('click', function () {
    menuToggle.checked = false;
  });


  // ========================================================================
  // 4. Закрытие по ESC
  // ========================================================================

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && menuToggle.checked) {
      menuToggle.checked = false;
    }
  });

})();