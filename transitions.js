/* ═══════════════════════════════════════════════════════════════
   GSAP Page Transitions  ·  anna-senselova / mapa spomienok
   ───────────────────────────────────────────────────────────────
   Overlay (#pg-transition) štartuje opacity:1 → zakrýva obsah.
   PAGE IN  : GSAP fade-out (odhalí stránku)
   PAGE OUT : klik na interný odkaz → GSAP fade-in → navigate
   BFCACHE  : pageshow event → okamžité skrytie overlay
═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  var OV = document.getElementById('pg-transition');
  if (!OV || typeof gsap === 'undefined') {
    if (OV) OV.style.display = 'none';
    return;
  }

  /* ── PAGE IN — odhalenie obsahu ─────────────────────────── */
  gsap.to(OV, {
    opacity: 0,
    duration: 0.55,
    ease: 'power2.out',
    delay: 0.04,
    onComplete: function () {
      OV.style.pointerEvents = 'none';
      OV.style.visibility    = 'hidden';
    }
  });

  /* ── PAGE OUT — zachytenie interných odkazov ────────────── */
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href]');
    if (!a) return;

    var href = a.getAttribute('href');
    if (!href) return;

    /* preskočiť: externé, hash, mailto, tel, _blank, download, modifier keys */
    if (
      href.startsWith('http')   ||
      href.startsWith('//')     ||
      href.startsWith('#')      ||
      href.startsWith('mailto:') ||
      href.startsWith('tel:')   ||
      a.target   === '_blank'   ||
      a.hasAttribute('download') ||
      e.metaKey || e.ctrlKey || e.shiftKey || e.altKey
    ) return;

    e.preventDefault();
    var dest = href;

    OV.style.visibility    = 'visible';
    OV.style.pointerEvents = 'all';

    gsap.fromTo(OV,
      { opacity: 0 },
      {
        opacity: 1,
        duration: 0.3,
        ease: 'power2.in',
        onComplete: function () {
          window.location.href = dest;
        }
      }
    );
  });

  /* ── BFCACHE — back/forward tlačidlá ────────────────────── */
  window.addEventListener('pageshow', function (e) {
    if (e.persisted) {
      gsap.set(OV, { opacity: 0 });
      OV.style.pointerEvents = 'none';
      OV.style.visibility    = 'hidden';
    }
  });

}());
