// apps/core/static/core/js/footer_animations.js

(function () {
    "use strict";

    const SELECTORS = {
        footer: ".site-footer",
        reveal: ".footer-reveal",
        links: ".footer-link",
        backToTop: ".footer-back-to-top",
    };

    const CLASSES = {
        visible: "is-visible",
        active: "is-active",
        reducedMotion: "prefers-reduced-motion",
    };

    const CONFIG = {
        revealThreshold: 0.15,
        revealRootMargin: "0px 0px -40px 0px",
        topButtonThreshold: 360,
        defaultAnimationDelay: 0,
        linkAnimationStep: 70,
    };

    let prefersReducedMotion = false;
    let reducedMotionQuery = null;
    let revealObserver = null;

    function getFooter() {
        return document.querySelector(SELECTORS.footer);
    }

    function getRevealElements() {
        const footer = getFooter();

        if (!footer) {
            return [];
        }

        return Array.from(
            footer.querySelectorAll(SELECTORS.reveal)
        );
    }

    function getFooterLinks() {
        const footer = getFooter();

        if (!footer) {
            return [];
        }

        return Array.from(
            footer.querySelectorAll(SELECTORS.links)
        );
    }

    function getBackToTopButton() {
        return document.querySelector(SELECTORS.backToTop);
    }

    function detectReducedMotion() {
        reducedMotionQuery = window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        );

        prefersReducedMotion = reducedMotionQuery.matches;

        document.documentElement.classList.toggle(
            CLASSES.reducedMotion,
            prefersReducedMotion
        );

        if (typeof reducedMotionQuery.addEventListener === "function") {
            reducedMotionQuery.addEventListener(
                "change",
                handleReducedMotionChange
            );
        } else if (
            typeof reducedMotionQuery.addListener === "function"
        ) {
            reducedMotionQuery.addListener(
                handleReducedMotionChange
            );
        }
    }

    function handleReducedMotionChange(event) {
        prefersReducedMotion = event.matches;

        document.documentElement.classList.toggle(
            CLASSES.reducedMotion,
            prefersReducedMotion
        );

        if (prefersReducedMotion) {
            showAllAnimatedElements();
            disconnectRevealObserver();
        } else {
            prepareRevealElements();
            prepareFooterLinks();
            createRevealObserver();
        }
    }

    function disconnectRevealObserver() {
        if (!revealObserver) {
            return;
        }

        revealObserver.disconnect();
        revealObserver = null;
    }

    function showAllAnimatedElements() {
        const elements = [
            ...getRevealElements(),
            ...getFooterLinks(),
        ];

        elements.forEach((element) => {
            element.classList.add(CLASSES.visible);
            element.style.removeProperty("transition-delay");
        });
    }

    function setAnimationDelay(element, delay) {
        if (prefersReducedMotion) {
            element.style.removeProperty("transition-delay");
            return;
        }

        const customDelay = Number(
            element.dataset.animationDelay
        );

        const finalDelay = Number.isFinite(customDelay)
            ? customDelay
            : delay;

        element.style.transitionDelay = `${finalDelay}ms`;
    }

    function prepareRevealElements() {
        const elements = getRevealElements();

        elements.forEach((element, index) => {
            setAnimationDelay(
                element,
                index * CONFIG.linkAnimationStep
            );

            if (prefersReducedMotion) {
                element.classList.add(CLASSES.visible);
            }
        });
    }

    function prepareFooterLinks() {
        const links = getFooterLinks();

        links.forEach((link, index) => {
            setAnimationDelay(
                link,
                index * CONFIG.linkAnimationStep
            );

            if (prefersReducedMotion) {
                link.classList.add(CLASSES.visible);
            }
        });
    }

    function createRevealObserver() {
        const elements = [
            ...getRevealElements(),
            ...getFooterLinks(),
        ];

        if (!elements.length || prefersReducedMotion) {
            return;
        }

        if (!("IntersectionObserver" in window)) {
            showAllAnimatedElements();
            return;
        }

        disconnectRevealObserver();

        revealObserver = new IntersectionObserver(
            function (entries, observer) {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) {
                        return;
                    }

                    entry.target.classList.add(CLASSES.visible);
                    observer.unobserve(entry.target);
                });
            },
            {
                threshold: CONFIG.revealThreshold,
                rootMargin: CONFIG.revealRootMargin,
            }
        );

        elements.forEach((element) => {
            revealObserver.observe(element);
        });
    }

    function updateBackToTopButton() {
        const button = getBackToTopButton();

        if (!button) {
            return;
        }

        const shouldShow =
            window.scrollY >= CONFIG.topButtonThreshold;

        button.classList.toggle(
            CLASSES.active,
            shouldShow
        );

        button.setAttribute(
            "aria-hidden",
            String(!shouldShow)
        );

        button.tabIndex = shouldShow ? 0 : -1;
    }

    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: prefersReducedMotion
                ? "auto"
                : "smooth",
        });
    }

    function bindBackToTop() {
        const button = getBackToTopButton();

        if (!button) {
            return;
        }

        button.addEventListener(
            "click",
            function (event) {
                event.preventDefault();
                scrollToTop();

                if (
                    window.history &&
                    typeof window.history.replaceState ===
                        "function"
                ) {
                    window.history.replaceState(
                        null,
                        "",
                        window.location.pathname +
                            window.location.search
                    );
                }
            }
        );
    }

    function bindFooterLinks() {
        const links = getFooterLinks();

        links.forEach((link) => {
            link.addEventListener(
                "click",
                function () {
                    link.classList.add(CLASSES.active);
                }
            );

            link.addEventListener(
                "blur",
                function () {
                    link.classList.remove(CLASSES.active);
                }
            );
        });
    }

    function bindScrollEvents() {
        let ticking = false;

        window.addEventListener(
            "scroll",
            function () {
                if (ticking) {
                    return;
                }

                window.requestAnimationFrame(function () {
                    updateBackToTopButton();
                    ticking = false;
                });

                ticking = true;
            },
            {
                passive: true,
            }
        );

        updateBackToTopButton();
    }

    function init() {
        const footer = getFooter();

        if (!footer) {
            return;
        }

        detectReducedMotion();

        prepareRevealElements();
        prepareFooterLinks();

        if (prefersReducedMotion) {
            showAllAnimatedElements();
        } else {
            createRevealObserver();
        }

        bindBackToTop();
        bindFooterLinks();
        bindScrollEvents();
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            init
        );
    } else {
        init();
    }
})();