/**
 * apps/core/static/core/js/fast_nav.js
 * YourTune — быстрый навигатор
 *
 * Поддерживает:
 * - плавную прокрутку к секциям страницы;
 * - возврат наверх;
 * - подсветку активной секции;
 * - доступность клавиатурой;
 * - автоматическую инициализацию мобильной панели;
 *
 * Ожидаемая HTML-структура:
 *
 * <nav class="fast-nav" aria-label="Быстрая навигация">
 *     <a href="#topics" class="fast-nav__item">
 *         <span class="fast-nav__icon">▦</span>
 *         <span class="fast-nav__label">Темы</span>
 *     </a>
 *
 *     <a href="#featured" class="fast-nav__item">
 *         <span class="fast-nav__icon">★</span>
 *         <span class="fast-nav__label">Подборки</span>
 *     </a>
 *
 *     <a href="#daily" class="fast-nav__item">
 *         <span class="fast-nav__icon">▶</span>
 *         <span class="fast-nav__label">День</span>
 *     </a>
 *
 *     <a href="#blog" class="fast-nav__item">
 *         <span class="fast-nav__icon">◎</span>
 *         <span class="fast-nav__label">Статьи</span>
 *     </a>
 *
 *     <button type="button" class="fast-nav__item fast-nav__item--top">
 *         <span class="fast-nav__icon">↑</span>
 *         <span class="fast-nav__label">Вверх</span>
 *     </button>
 * </nav>
 */

(function () {
    "use strict";

    const SELECTORS = {
        navigation: ".fast-nav",
        navigationItem: ".fast-nav__item",
        anchor: 'a[href^="#"]',
        topButton: ".fast-nav__item--top",
        section: "main [id]",
    };

    const CLASSES = {
        active: "is-active",
        visible: "is-visible",
    };

    const CONFIG = {
        scrollOffset: 80,
        topButtonThreshold: 360,
        activeSectionThreshold: 0.35,
        smoothScrollBehavior: "smooth",
    };

    function getNavigation() {
        return document.querySelector(SELECTORS.navigation);
    }

    function getNavigationItems() {
        const navigation = getNavigation();

        if (!navigation) {
            return [];
        }

        return Array.from(
            navigation.querySelectorAll(SELECTORS.navigationItem)
        );
    }

    function getTargetFromLink(link) {
        const href = link.getAttribute("href");

        if (!href || href === "#") {
            return null;
        }

        try {
            return document.querySelector(href);
        } catch (error) {
            console.warn("YourTune fast navigation: invalid selector", href);
            return null;
        }
    }

    function scrollToElement(element) {
        if (!element) {
            return;
        }

        const elementTop =
            element.getBoundingClientRect().top + window.scrollY;

        const targetPosition = Math.max(
            elementTop - CONFIG.scrollOffset,
            0
        );

        window.scrollTo({
            top: targetPosition,
            behavior: CONFIG.smoothScrollBehavior,
        });
    }

    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: CONFIG.smoothScrollBehavior,
        });
    }

    function updateTopButton() {
        const topButton = document.querySelector(SELECTORS.topButton);

        if (!topButton) {
            return;
        }

        const isVisible = window.scrollY >= CONFIG.topButtonThreshold;

        topButton.classList.toggle(CLASSES.visible, isVisible);
        topButton.setAttribute("aria-hidden", String(!isVisible));
    }

    function setActiveItem(targetId) {
        const items = getNavigationItems();

        items.forEach((item) => {
            const href = item.getAttribute("href");
            const isActive = href === `#${targetId}`;

            item.classList.toggle(CLASSES.active, isActive);

            if (isActive) {
                item.setAttribute("aria-current", "location");
            } else {
                item.removeAttribute("aria-current");
            }
        });
    }

    function getSections() {
        return Array.from(
            document.querySelectorAll(SELECTORS.section)
        ).filter((section) => {
            return section.id && section.offsetParent !== null;
        });
    }

    function updateActiveSection() {
        const sections = getSections();

        if (!sections.length) {
            return;
        }

        const referenceLine =
            window.scrollY +
            window.innerHeight * CONFIG.activeSectionThreshold;

        let activeSection = sections[0];

        sections.forEach((section) => {
            const sectionTop =
                section.getBoundingClientRect().top + window.scrollY;

            if (sectionTop <= referenceLine) {
                activeSection = section;
            }
        });

        setActiveItem(activeSection.id);
    }

    function handleAnchorClick(event) {
        const link = event.currentTarget;
        const target = getTargetFromLink(link);

        if (!target) {
            return;
        }

        event.preventDefault();

        scrollToElement(target);

        if (window.history && window.history.pushState) {
            window.history.pushState(
                null,
                "",
                `#${target.id}`
            );
        }
    }

    function handleTopButtonClick(event) {
        event.preventDefault();
        scrollToTop();

        if (window.history && window.history.pushState) {
            window.history.pushState(
                null,
                "",
                window.location.pathname +
                    window.location.search
            );
        }
    }

    function handleHashOnLoad() {
        const hash = window.location.hash;

        if (!hash) {
            return;
        }

        const target = getTargetFromLink({
            getAttribute: function () {
                return hash;
            },
        });

        if (!target) {
            return;
        }

        window.requestAnimationFrame(function () {
            scrollToElement(target);
        });
    }

    function applyReducedMotionPreference() {
        const prefersReducedMotion = window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        ).matches;

        if (prefersReducedMotion) {
            document.documentElement.classList.add(
                "prefers-reduced-motion"
            );
        }
    }

    function bindEvents() {
        const navigation = getNavigation();

        if (!navigation) {
            return;
        }

        const anchorLinks = navigation.querySelectorAll(
            SELECTORS.anchor
        );

        anchorLinks.forEach((link) => {
            link.addEventListener("click", handleAnchorClick);
        });

        const topButton = navigation.querySelector(
            SELECTORS.topButton
        );

        if (topButton) {
            topButton.addEventListener(
                "click",
                handleTopButtonClick
            );
        }

        let ticking = false;

        window.addEventListener(
            "scroll",
            function () {
                if (ticking) {
                    return;
                }

                window.requestAnimationFrame(function () {
                    updateTopButton();
                    updateActiveSection();
                    ticking = false;
                });

                ticking = true;
            },
            { passive: true }
        );

        window.addEventListener("resize", function () {
            updateActiveSection();
        });
    }

    function init() {
        applyReducedMotionPreference();
        bindEvents();
        updateTopButton();
        updateActiveSection();
        handleHashOnLoad();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();