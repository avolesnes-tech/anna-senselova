(function () {
  'use strict';
  var KEY = 'mapa_cookie_consent';

  function grant() {
    if (typeof gtag === 'function') {
      gtag('consent', 'update', { analytics_storage: 'granted' });
    }
  }

  function setConsent(val) {
    try { localStorage.setItem(KEY, val); } catch(e) {}
    if (val === 'granted') grant();
  }

  function hideBanner() {
    var b = document.getElementById('cookie-banner');
    if (!b) return;
    b.classList.remove('cookie-banner--visible');
    setTimeout(function () { b && b.parentNode && b.parentNode.removeChild(b); }, 420);
  }

  function showBanner() {
    var b = document.createElement('div');
    b.id = 'cookie-banner';
    b.setAttribute('role', 'dialog');
    b.setAttribute('aria-label', 'Súhlas s cookies');
    b.innerHTML =
      '<div class="cookie-inner">' +
        '<p class="cookie-text">Táto stránka používa cookies na analýzu návštevnosti (Google Analytics). ' +
        'Dáta spracúvame anonymne a nevyužívame ich na reklamu.</p>' +
        '<div class="cookie-btns">' +
          '<button class="cookie-btn cookie-btn--accept" id="cookie-accept">Súhlasím</button>' +
          '<button class="cookie-btn cookie-btn--decline" id="cookie-decline">Odmietnuť</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(b);

    document.getElementById('cookie-accept').addEventListener('click', function () {
      setConsent('granted'); hideBanner();
    });
    document.getElementById('cookie-decline').addEventListener('click', function () {
      setConsent('denied'); hideBanner();
    });

    setTimeout(function () { b.classList.add('cookie-banner--visible'); }, 700);
  }

  // Restore previously granted consent immediately (before page interaction)
  try {
    if (localStorage.getItem(KEY) === 'granted') grant();
  } catch(e) {}

  // Show banner only if no decision yet
  try {
    if (!localStorage.getItem(KEY)) {
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', showBanner);
      } else {
        showBanner();
      }
    }
  } catch(e) {}
})();
