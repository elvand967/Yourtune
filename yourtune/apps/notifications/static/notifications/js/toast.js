// apps/core/static/core/js/toast.js

(() => {
    "use strict";

    // =========================================================================
    // Настройки
    // =========================================================================

    const DEFAULT_DURATION = 5000;
    const ERROR_DURATION = 8000;
    const EXIT_ANIMATION_MS = 220;

    const SELECTORS = {
        root: "[data-toast-root]",
        toast: "[data-toast]",
        close: "[data-toast-close]",
        progress: ".toast__progress",
    };

    const ICONS = {
        success: "✓",
        info: "i",
        warning: "!",
        error: "✕",
    };

    const TEXT = {
        close: "Закрыть уведомление",
        open: "Открыть",
    };

    // =========================================================================
    // Toast engine
    // =========================================================================

    class ToastEngine {
        constructor(root) {
            this.root = root;

            this.bindExistingToasts();
            this.bindExternalEvents();
        }

        // ------------------------------------------------------------------
        // Серверные toast из Django messages
        // ------------------------------------------------------------------

        bindExistingToasts() {
            this.root
                .querySelectorAll(SELECTORS.toast)
                .forEach((toast) => this.initToast(toast));
        }

        initToast(toast) {
            if (toast.dataset.toastInitialized === "true") {
                return;
            }

            toast.dataset.toastInitialized = "true";
            toast.dataset.state = "visible";

            const level = toast.dataset.toastLevel || "info";
            const duration =
                level === "error" ? ERROR_DURATION : DEFAULT_DURATION;

            let timer = null;
            let remaining = duration;
            let startedAt = Date.now();

            const hide = () => {
                if (toast.dataset.state === "closing") {
                    return;
                }

                toast.dataset.state = "closing";
                toast.classList.add("is-closing");

                window.setTimeout(() => {
                    toast.remove();

                    if (!this.root.querySelector(SELECTORS.toast)) {
                        this.root.remove();
                    }
                }, EXIT_ANIMATION_MS);
            };

            const pause = () => {
                if (!timer || toast.dataset.state === "closing") {
                    return;
                }

                window.clearTimeout(timer);
                timer = null;

                remaining -= Date.now() - startedAt;

                const progress = toast.querySelector(SELECTORS.progress);

                if (progress) {
                    progress.style.animationPlayState = "paused";
                }
            };

            const resume = () => {
                if (timer || toast.dataset.state === "closing") {
                    return;
                }

                startedAt = Date.now();
                timer = window.setTimeout(hide, Math.max(remaining, 0));

                const progress = toast.querySelector(SELECTORS.progress);

                if (progress) {
                    progress.style.animationPlayState = "running";
                }
            };

            const closeButton = toast.querySelector(SELECTORS.close);

            if (closeButton) {
                closeButton.addEventListener("click", hide);
            }

            toast.addEventListener("mouseenter", pause);
            toast.addEventListener("mouseleave", resume);
            toast.addEventListener("focusin", pause);
            toast.addEventListener("focusout", resume);

            timer = window.setTimeout(hide, duration);
        }

        // ------------------------------------------------------------------
        // Создание toast из JavaScript
        // ------------------------------------------------------------------

        create({
            title = "",
            message = "",
            level = "info",
            url = "",
            duration = null,
        } = {}) {
            const toast = document.createElement("div");

            const safeLevel = Object.prototype.hasOwnProperty.call(
                ICONS,
                level
            )
                ? level
                : "info";

            toast.className = `toast toast--${safeLevel}`;
            toast.dataset.toast = "";
            toast.dataset.toastLevel = safeLevel;
            toast.setAttribute("role", "status");

            const icon = document.createElement("div");
            icon.className = "toast__icon";
            icon.setAttribute("aria-hidden", "true");
            icon.textContent = ICONS[safeLevel];

            const body = document.createElement("div");
            body.className = "toast__body";

            if (title) {
                const titleElement = document.createElement("strong");
                titleElement.textContent = title;
                body.append(titleElement);
            }

            if (message) {
                if (title) {
                    body.append(" ");
                }

                body.append(message);
            }

            if (url) {
                const link = document.createElement("a");
                link.className = "toast__link";
                link.href = url;
                link.textContent = TEXT.open;

                body.append(document.createElement("br"), link);
            }

            const closeButton = document.createElement("button");
            closeButton.type = "button";
            closeButton.className = "toast__close";
            closeButton.dataset.toastClose = "";
            closeButton.setAttribute("aria-label", TEXT.close);
            closeButton.textContent = "×";

            const progress = document.createElement("div");
            progress.className = "toast__progress";
            progress.setAttribute("aria-hidden", "true");

            if (duration) {
                progress.style.animationDuration = `${duration}ms`;
            }

            toast.append(icon, body, closeButton, progress);
            this.root.append(toast);

            this.initToast(toast);

            return toast;
        }

        // ------------------------------------------------------------------
        // Интеграция с внешними событиями
        // ------------------------------------------------------------------

        bindExternalEvents() {
            document.body.addEventListener(
                "yourtune:toast",
                (event) => {
                    const detail = event.detail || {};

                    this.create({
                        title: detail.title || "",
                        message: detail.message || "",
                        level: detail.level || "info",
                        url: detail.url || "",
                        duration: detail.duration || null,
                    });
                },
                { passive: true }
            );
        }
    }

    // =========================================================================
    // Инициализация
    // =========================================================================

    const root = document.querySelector(SELECTORS.root);

    if (root) {
        window.YourtuneToast = new ToastEngine(root);
    }
})();