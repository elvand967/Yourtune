// apps/core/static/core/js/fast_nav.js

function setupFastScroll() {
    const navFixed = document.querySelector('.fast-scroll-nav-fixed');
    const header = document.querySelector('header.main-header');
    const footer = document.querySelector('footer.site-footer');
    if (!navFixed || !header || !footer) return;

    const upBtn = navFixed.querySelector('.fast-scroll-btn.up');
    const downBtn = navFixed.querySelector('.fast-scroll-btn.down');

    let headerVisible = false;
    let footerVisible = false;

    // 1. Управление видимостью панели и кнопок (влево/вправо/скрытие)
    const updateStates = () => {
        if (headerVisible && footerVisible) {
            navFixed.classList.add('is-hidden');
        } else {
            navFixed.classList.remove('is-hidden');
            upBtn.classList.toggle('is-btn-hidden', headerVisible);
            downBtn.classList.toggle('is-btn-hidden', footerVisible);
        }
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.target === header) headerVisible = entry.isIntersecting;
            if (entry.target === footer) footerVisible = entry.isIntersecting;
        });
        updateStates();
    }, { root: null, threshold: 0 });

    observer.observe(header);
    observer.observe(footer);

    // 2. ЭФФЕКТ "УПОРА" В ФУТЕР (Динамический расчет координат)
    const handleFooterSticky = () => {
        const footerRect = footer.getBoundingClientRect();
        const windowHeight = window.innerHeight;

        // Если верхняя граница футера пересекла нижнюю границу экрана
        if (footerRect.top < windowHeight) {
            // Переключаем панель в абсолютное положение относительно документа
            navFixed.style.position = 'absolute';
            // Высчитываем точную точку остановки с учетом прокрутки окна
            navFixed.style.top = `${window.pageYOffset + footerRect.top}px`;
            navFixed.style.bottom = 'auto';
        } else {
            // Возвращаем фиксированное положение, когда футер ушел вниз
            navFixed.style.position = 'fixed';
            navFixed.style.top = 'auto';
            navFixed.style.bottom = '0';
        }
    };

    // Слушаем скролл и ресайз только для корректировки "прилипания"
    window.addEventListener('scroll', handleFooterSticky, { passive: true });
    window.addEventListener('resize', handleFooterSticky);
    // Первичный запуск на случай, если страница загрузилась сразу внизу
    handleFooterSticky();

    // 3. Логика кликов
    if (upBtn) {
        upBtn.onclick = () => header.scrollIntoView({ behavior: 'smooth' });
    }
    if (downBtn) {
        downBtn.onclick = () => footer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

document.addEventListener('DOMContentLoaded', setupFastScroll);
