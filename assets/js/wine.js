/* Dasabami wine pages: reveals, nav hide, language menu, copy email. */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const EMAIL = 'zazabery@gmail.com';

  /* reveal on scroll */
  $$('.specs [data-reveal], .wp-cards [data-reveal], .wp-others [data-reveal], .wp-said-grid [data-reveal]').forEach(el => {
    if (!el.style.getPropertyValue('--delay')) el.style.setProperty('--delay', `${Math.min([...el.parentNode.children].indexOf(el), 4) * 90}ms`);
  });
  if (reduce || !('IntersectionObserver' in window)) {
    $$('[data-reveal]').forEach(el => el.classList.add('is-in'));
  } else {
    const obs = new IntersectionObserver(entries => {
      entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('is-in'); obs.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    $$('[data-reveal]').forEach(el => obs.observe(el));
  }

  /* hide the nav while scrolling down */
  const nav = $('#nav');
  let lastY = scrollY, ticking = false;
  addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const y = scrollY;
      nav.classList.toggle('is-hidden', y > lastY && y > 200);
      nav.classList.toggle('is-scrolled', y > 8);
      lastY = y; ticking = false;
    });
  }, { passive: true });

  /* language menu: close on outside click or Escape */
  const lang = $('#lang');
  if (lang) {
    document.addEventListener('click', e => { if (lang.open && !lang.contains(e.target)) lang.open = false; });
    addEventListener('keydown', e => { if (e.key === 'Escape' && lang.open) { lang.open = false; lang.querySelector('summary').focus(); } });
  }

  /* copy email */
  const toastEl = $('#toast');
  let t;
  const toast = msg => {
    toastEl.textContent = msg; toastEl.classList.add('is-on');
    clearTimeout(t); t = setTimeout(() => toastEl.classList.remove('is-on'), 2200);
  };
  const copy = $('#copy-email');
  copy && copy.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(EMAIL); toast(copy.dataset.copied); }
    catch (_) { toast(copy.dataset.failed); }
  });
})();
