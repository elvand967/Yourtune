// ==========================================================================
// apps/core/static/core/js/mobile-menu.js
// Мобильное меню (бургер) для YourTune
// ==========================================================================
//
// Назначение:
//   - Открытие/закрытие мобильного меню по кнопке бургера
//   - Анимация иконки бургера
//   - Блокировка прокрутки фона при открытом меню
//   - Закрытие по клику на overlay, крестик или пункт меню
//   - Закрытие по клавише Escape
//   - Синхронизация переключателя тем между десктопной и мобильной версией
//
// ==========================================================================

(function() {
  'use strict';

  // ==========================================================================
  // Инициализация
  // ==========================================================================

  function init() {
    // Находим элементы
    const burger = document.querySelector('.topbar__burger');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileClose = document.querySelector('.topbar__mobile-close');
    const mobileOverlay = document.querySelector('.topbar__mobile-overlay');
    const mobileItems = document.querySelectorAll('.topbar__mobile-item');
    const themeToggleMobile = document.getElementById('theme-toggle-mobile');
    const themeToggleDesktop = document.getElementById('theme-toggle');

    // Если нет бургера или меню — выходим
    if (!burger || !mobileMenu) return;

    // ==========================================================================
    // Обработчики событий
    // ==========================================================================

    // Открытие/закрытие по клику на бургер
    burger.addEventListener('click', function() {
      const isOpen = mobileMenu.classList.contains('is-open');

      if (isOpen) {
        closeMenu();
      } else {
        openMenu();
      }
    });

    // Закрытие по крестику
    if (mobileClose) {
      mobileClose.addEventListener('click', closeMenu);
    }

    // Закрытие по клику на затемнение
    if (mobileOverlay) {
      mobileOverlay.addEventListener('click', closeMenu);
    }

    // Закрытие по клику на пункт меню
    mobileItems.forEach(function(item) {
      item.addEventListener('click', closeMenu);
    });

    // Закрытие по клавише Escape
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && mobileMenu.classList.contains('is-open')) {
        closeMenu();
      }
    });

    // Синхронизация переключателя тем
    if (themeToggleMobile && themeToggleDesktop) {
      themeToggleMobile.addEventListener('click', function() {
        // Кликаем по десктопному переключателю
        themeToggleDesktop.click();
        // Закрываем меню
        closeMenu();
      });
    }

    // ==========================================================================
    // Функции
    // ==========================================================================

    function openMenu() {
      // Показываем меню
      mobileMenu.classList.add('is-open');
      mobileMenu.setAttribute('aria-hidden', 'false');

      // Обновляем состояние бургера
      burger.setAttribute('aria-expanded', 'true');
      burger.setAttribute('aria-label', 'Закрыть меню');

      // Блокируем прокрутку страницы
      document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
      // Скрываем меню
      mobileMenu.classList.remove('is-open');
      mobileMenu.setAttribute('aria-hidden', 'true');

      // Возвращаем состояние бургера
      burger.setAttribute('aria-expanded', 'false');
      burger.setAttribute('aria-label', 'Открыть меню');

      // Возвращаем прокрутку
      document.body.style.overflow = '';
    }
  }

  // ==========================================================================
  // Запуск после загрузки DOM
  // ==========================================================================

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    // DOM уже загружен
    init();
  }

})();