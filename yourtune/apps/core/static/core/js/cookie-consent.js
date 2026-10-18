// =========================================================
// apps/core/static/core/js/cookie-consent.js
// =========================================================
// Cookie-баннер YourTune.
//
// Гостю показывается информационное уведомление.
// Авторизованному пользователю — баннер с настройками cookie.
//
// Анимация:
// - .cookie-banner.is-visible — плавное появление снизу;
// - .cookie-banner.is-hidden — плавное скрытие вниз.
// =========================================================

const BANNER = document.getElementById("cookie-banner");
const GUEST_NOTICE = document.getElementById("cookie-guest-notice");
const USER_CONSENT = document.getElementById("cookie-user-consent");
const SETTINGS = document.getElementById("cookie-settings");
const ANALYTICS_CHECKBOX = document.getElementById("cookie-analytics");

const STORAGE_KEY = "yourtune_cookie_consent";
const GUEST_NOTICE_KEY = "yourtune_cookie_guest_notice";
const POLICY_VERSION = "1.0";
const CONSENT_API_URL = "/core/api/cookie-consent/";
const BANNER_ANIMATION_DURATION = 350;

const IS_AUTHENTICATED =
  document.body.dataset.isAuthenticated === "true";


// =========================================================
// Вспомогательные функции
// =========================================================

function getCookie(name) {
  const cookies = document.cookie.split("; ");

  for (const cookie of cookies) {
    const [cookieName, cookieValue] = cookie.split("=");

    if (cookieName === name) {
      return decodeURIComponent(cookieValue);
    }
  }

  return null;
}


function getConsent() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);

    if (!raw) {
      return null;
    }

    const consent = JSON.parse(raw);

    if (consent.policy_version !== POLICY_VERSION) {
      return null;
    }

    return consent;
  } catch (error) {
    return null;
  }
}


// =========================================================
// Управление видимостью баннера
// =========================================================

function showBanner() {
  if (!BANNER) {
    return;
  }

  BANNER.hidden = false;
  BANNER.classList.remove("is-hidden");
  BANNER.classList.add("is-visible");
}


function hideBanner() {
  if (!BANNER) {
    return;
  }

  BANNER.classList.remove("is-visible");
  BANNER.classList.add("is-hidden");

  // Скрываем баннер из доступности после завершения анимации.
  setTimeout(() => {
    if (BANNER.classList.contains("is-hidden")) {
      BANNER.hidden = true;
    }
  }, BANNER_ANIMATION_DURATION);
}


function hideBannerImmediately() {
  if (!BANNER) {
    return;
  }

  BANNER.hidden = true;
  BANNER.classList.remove("is-visible");
  BANNER.classList.add("is-hidden");
}


function showGuestNotice() {
  if (!GUEST_NOTICE || !USER_CONSENT || !SETTINGS) {
    return;
  }

  GUEST_NOTICE.hidden = false;
  USER_CONSENT.hidden = true;
  SETTINGS.hidden = true;

  showBanner();
}


function showUserConsent() {
  if (!GUEST_NOTICE || !USER_CONSENT || !SETTINGS) {
    return;
  }

  GUEST_NOTICE.hidden = true;
  USER_CONSENT.hidden = false;
  SETTINGS.hidden = true;

  showBanner();
}


// =========================================================
// Сохранение согласия
// =========================================================

function saveConsent(consent) {
  const consentData = {
    necessary: true,
    analytics: Boolean(consent.analytics),
    marketing: Boolean(consent.marketing),
    policy_version: POLICY_VERSION,
    source: consent.source || "settings",
    updated_at: new Date().toISOString()
  };

  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify(consentData)
  );

  sendConsentToServer(consentData);
  applyConsent(consentData);
  hideBanner();
}


function sendConsentToServer(consent) {
  const csrfToken = getCookie("csrftoken");

  if (!csrfToken) {
    return;
  }

  fetch(CONSENT_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken
    },
    body: JSON.stringify({
      necessary: consent.necessary,
      analytics: consent.analytics,
      marketing: consent.marketing,
      policy_version: consent.policy_version,
      source: consent.source
    })
  }).catch((error) => {
    console.warn(
      "Не удалось сохранить cookie-согласие на сервере.",
      error
    );
  });
}


// =========================================================
// Применение согласия
// =========================================================

function applyConsent(consent) {
  const analyticsAllowed = Boolean(consent.analytics);
  const marketingAllowed = Boolean(consent.marketing);

  if (typeof window.gtag === "function") {
    window.gtag("consent", "update", {
      analytics_storage: analyticsAllowed ? "granted" : "denied",
      ad_storage: marketingAllowed ? "granted" : "denied",
      ad_user_data: marketingAllowed ? "granted" : "denied",
      ad_personalization: marketingAllowed ? "granted" : "denied"
    });
  }

  if (analyticsAllowed) {
    initAnalytics();
  }
}


function initAnalytics() {
  if (window.yourtuneAnalyticsInitialized) {
    return;
  }

  window.yourtuneAnalyticsInitialized = true;

  // Замените 00000000 на номер вашего счётчика Яндекс Метрики.
  const COUNTER_ID = 00000000;

  const script = document.createElement("script");
  script.async = true;
  script.src = "https://mc.yandex.ru/metrika/tag.js";
  document.head.appendChild(script);

  window.ym = window.ym || function () {
    (window.ym.q = window.ym.q || []).push(arguments);
  };

  window.ym.l = window.ym.l || new Date().getMilliseconds();

  window.ym(COUNTER_ID, "init", {
    clickmap: true,
    trackLinks: true,
    accurateTrackBounce: true
  });
}


// =========================================================
// Инициализация
// =========================================================

document.addEventListener("DOMContentLoaded", () => {
  if (!BANNER || !GUEST_NOTICE || !USER_CONSENT) {
    return;
  }

  const savedConsent = getConsent();

  if (IS_AUTHENTICATED) {
    if (savedConsent) {
      applyConsent(savedConsent);
      hideBannerImmediately();
    } else {
      showUserConsent();
    }
  } else {
    const guestNoticeClosed = sessionStorage.getItem(
      GUEST_NOTICE_KEY
    );

    if (!guestNoticeClosed) {
      showGuestNotice();
    } else {
      hideBannerImmediately();
    }
  }

  const acceptAllButton = document.getElementById(
    "cookie-accept-all"
  );

  const acceptNecessaryButton = document.getElementById(
    "cookie-accept-necessary"
  );

  const openSettingsButton = document.getElementById(
    "cookie-open-settings"
  );

  const saveSettingsButton = document.getElementById(
    "cookie-save-settings"
  );

  const closeGuestNoticeButton = document.getElementById(
    "cookie-guest-close"
  );

  if (acceptAllButton) {
    acceptAllButton.addEventListener("click", () => {
      saveConsent({
        analytics: true,
        marketing: true,
        source: "banner"
      });
    });
  }

  if (acceptNecessaryButton) {
    acceptNecessaryButton.addEventListener("click", () => {
      saveConsent({
        analytics: false,
        marketing: false,
        source: "banner"
      });
    });
  }

  if (openSettingsButton && SETTINGS) {
    openSettingsButton.addEventListener("click", () => {
      SETTINGS.hidden = !SETTINGS.hidden;
    });
  }

  if (saveSettingsButton && ANALYTICS_CHECKBOX) {
    saveSettingsButton.addEventListener("click", () => {
      saveConsent({
        analytics: ANALYTICS_CHECKBOX.checked,
        marketing: false,
        source: "settings"
      });
    });
  }

  if (closeGuestNoticeButton) {
    closeGuestNoticeButton.addEventListener("click", () => {
      sessionStorage.setItem(
        GUEST_NOTICE_KEY,
        "closed"
      );

      hideBanner();
    });
  }
});