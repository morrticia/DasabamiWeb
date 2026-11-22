/* Dasabami — interactions & motion. Vanilla, no dependencies. */
(() => {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const T = window.DASABAMI_I18N || {};
  const BASE = T.base || '';
  const tx = (group, key, fallback) => (T[group] && T[group][key]) || fallback;
  const easeInOut = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

  /* ------------------------------------------------------------------
     Knowledge: the single source the wine sheet and the guide draw on
     ------------------------------------------------------------------ */
  const EMAIL = 'zazabery@gmail.com';
  const WINES = {
    'rkatsiteli-2019': { name: 'Rkatsiteli', vintage: '2019', geo: 'რქაწითელი', style: 'Amber wine', img: 'rkatsiteli-2019',
      text: 'Georgia’s great white grape, fermented on its skins in qvevri until it turns amber. From the 70-year-old family vineyard.',
      facts: { Grape: 'Rkatsiteli', Vessel: 'Qvevri', Vines: 'About 70 years old', Label: 'Painted art label' } },
    'khikhvi-2018': { name: 'Khikhvi', vintage: '2018', geo: 'ხიხვი', style: 'Amber wine', img: 'khikhvi-2018',
      text: 'The rare Kakhetian white, grown here on younger vines planted around 2009. Hamburg’s Skin Contact filed the 2018 under high-energy, vibrant and deep.',
      facts: { Grape: 'Khikhvi', Vessel: 'Qvevri', Style: 'Skin contact' } },
    'tavkveri-2019': { name: 'Tavkveri', vintage: '2019', geo: 'თავკვერი', style: 'Red wine', img: 'tavkveri-2019',
      text: 'Kartli’s native red. A short time on skins, then months resting in qvevri. Recent vintages run to just a couple of hundred bottles.',
      facts: { Grape: 'Tavkveri', Vessel: 'Qvevri', Vines: 'About 70 years old' } },
    'mtsvane-2017': { name: 'Mtsvane', vintage: '2017', geo: 'მწვანე', style: 'Amber wine', img: 'mtsvane-2017',
      text: 'An amber white from Mtsvane, fermented on its skins in qvevri. Recent vintages spend about six months on skins.',
      facts: { Grape: 'Mtsvane', Vessel: 'Qvevri', Style: 'Amber white' } },
    'tavkveri-2017': { name: 'Tavkveri', vintage: '2017', geo: 'თავკვერი', style: 'Red wine', img: 'tavkveri-2017',
      text: 'A dry red made with skin-contact fermentation in qvevri.',
      facts: { Grape: 'Tavkveri', Vessel: 'Qvevri', Style: 'Dry red' } },
    'rkatsiteli-2016': { name: 'Rkatsiteli', vintage: '2016', geo: 'რქაწითელი', style: 'Amber wine', img: 'rkatsiteli-2016',
      text: 'Amber Rkatsiteli that travelled to London, where it was poured at Proper Natural Wine.',
      facts: { Grape: 'Rkatsiteli', Vessel: 'Qvevri', 'Poured at': 'Proper Natural Wine, London' } },
    'tavkveri-2018': { name: 'Tavkveri', vintage: '2018', geo: 'თავკვერი', style: 'Red wine', img: 'tavkveri-2018',
      text: 'Tavkveri from the 2018 harvest, fermented in qvevri.',
      facts: { Grape: 'Tavkveri', Vessel: 'Qvevri' } },
    'field-blend': { name: 'Field Blend', vintage: 'NV', geo: 'ჯიშების ნაზავი', style: 'Blend', img: 'field-blend',
      text: 'A blend of grapes from the family hectare. For a current blend, look for the Rkatsiteli–Mtsvane (80/20).',
      facts: { Grapes: 'Various', Vessel: 'Qvevri' } }
  };

  /* ------------------------------------------------------------------
     Hero — frame expands to full-bleed as you scroll
     ------------------------------------------------------------------ */
  const hero = $('.hero');
  const heroSticky = $('.hero-sticky');
  const heroCopy = $('.hero-copy');
  function layoutHero() {
    if (!heroSticky) return;
    const h = heroSticky.clientHeight;
    const top0 = heroCopy.offsetTop + heroCopy.offsetHeight + Math.max(20, h * 0.035);
    const h0 = Math.max(h - top0 - Math.max(16, h * 0.04), h * 0.26);
    heroSticky.style.setProperty('--top0', top0 + 'px');
    heroSticky.style.setProperty('--h0', h0 + 'px');
  }
  layoutHero();
  addEventListener('resize', layoutHero);
  if (document.fonts) document.fonts.ready.then(layoutHero);
  function updateHero() {
    if (!hero || !heroSticky) return;
    const r = hero.getBoundingClientRect();
    const total = Math.max(1, r.height - innerHeight);
    const p = clamp(-r.top / total);
    const e = easeInOut(clamp((p - 0.04) / 0.6));
    heroSticky.style.setProperty('--p', p.toFixed(4));
    heroSticky.style.setProperty('--e', e.toFixed(4));
  }

  /* parallax for full-width photo band */
  const parallax = $$('[data-parallax]');
  function updateParallax() {
    if (reduce) return;
    parallax.forEach(img => {
      const r = img.parentElement.getBoundingClientRect();
      if (r.bottom < 0 || r.top > innerHeight) return;
      const off = (r.top + r.height / 2 - innerHeight / 2) * -0.08;
      img.style.setProperty('--py', off.toFixed(1) + 'px');
    });
  }

  /* ------------------------------------------------------------------
     Nav — hide on scroll down, show on scroll up, active section
     ------------------------------------------------------------------ */
  const nav = $('#nav');
  const dock = $('#dock');
  let lastY = scrollY;
  function updateNav() {
    const y = scrollY;
    const down = y > lastY && y > 200;
    nav.classList.toggle('is-hidden', down && !document.body.classList.contains('guide-open'));
    lastY = y;
    dock.classList.toggle('is-shown', y > innerHeight * 0.9);
  }
  const links = $$('.nav-links a');
  const sectionObs = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        links.forEach(a => a.classList.toggle('is-active', a.getAttribute('href') === '#' + en.target.id));
      }
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  ['story', 'wines', 'qvevri', 'press', 'find'].forEach(id => { const el = document.getElementById(id); if (el) sectionObs.observe(el); });

  /* ------------------------------------------------------------------
     Reveal on scroll (with stagger)
     ------------------------------------------------------------------ */
  $$('[data-stagger]').forEach(group => {
    $$('[data-reveal]', group).forEach((el, i) => el.style.setProperty('--delay', `${i * 90}ms`));
  });
  $$('.rail [data-reveal]').forEach((el, i) => el.style.setProperty('--delay', `${Math.min(i, 4) * 90}ms`));
  $$('.gallery [data-reveal]').forEach((el, i) => el.style.setProperty('--delay', `${(i % 3) * 90}ms`));
  const revealObs = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add('is-in'); revealObs.unobserve(en.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  $$('[data-reveal]').forEach(el => revealObs.observe(el));

  /* ------------------------------------------------------------------
     Manifesto — words light up with scroll
     ------------------------------------------------------------------ */
  const manifesto = $('[data-words]');
  let words = [];
  if (manifesto) {
    const frag = document.createDocumentFragment();
    manifesto.childNodes.forEach(node => {
      const accent = node.nodeType === 1 && node.classList.contains('accent');
      const text = node.textContent;
      text.split(/(\s+)/).forEach(part => {
        if (!part) return;
        if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
        const s = document.createElement('span');
        s.className = 'w' + (accent ? ' accent' : '');
        s.textContent = part;
        frag.appendChild(s);
      });
    });
    manifesto.textContent = '';
    manifesto.appendChild(frag);
    words = $$('.w', manifesto);
  }
  function updateManifesto() {
    if (!words.length) return;
    const r = manifesto.getBoundingClientRect();
    const start = innerHeight * 0.85, end = innerHeight * 0.25;
    const p = clamp((start - r.top) / (start - end + r.height * 0.6));
    const n = Math.round(p * words.length);
    words.forEach((w, i) => w.classList.toggle('on', i < n));
  }

  /* ------------------------------------------------------------------
     Counters
     ------------------------------------------------------------------ */
  const countObs = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      const el = en.target; countObs.unobserve(el);
      const target = +el.dataset.count; const sep = el.hasAttribute('data-sep');
      const fmt = v => (sep ? v.toLocaleString('en-US') : String(v));
      if (reduce) { el.textContent = fmt(target); return; }
      const from = target > 1000 && !sep ? target - 60 : 0;
      const dur = 1600; const t0 = performance.now();
      const tick = now => {
        const t = clamp((now - t0) / dur);
        const v = Math.round(from + (target - from) * (1 - Math.pow(1 - t, 4)));
        el.textContent = fmt(v);
        if (t < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.6 });
  $$('[data-count]').forEach(el => countObs.observe(el));

  /* ------------------------------------------------------------------
     Wines — filter pill, rail nav, tilt + glare, detail sheet
     ------------------------------------------------------------------ */
  const rail = $('#rail');
  const filterBtns = $$('.filters button');
  const pill = $('.filters .pill');
  function movePill(btn) {
    if (!pill || !btn) return;
    pill.style.width = btn.offsetWidth + 'px';
    pill.style.transform = `translateX(${btn.offsetLeft}px)`;
  }
  function setFilter(kind) {
    filterBtns.forEach(b => {
      const on = b.dataset.filter === kind;
      b.setAttribute('aria-pressed', on);
      if (on) movePill(b);
    });
    let first = null;
    $$('.wine', rail).forEach(card => {
      const show = kind === 'all' || card.dataset.style === kind;
      card.classList.toggle('is-dim', !show);
      if (show && !first) first = card;
    });
    if (first) {
      // order matching wines first so they're in view
      const cards = $$('.wine', rail);
      cards.sort((a, b) => (a.classList.contains('is-dim') - b.classList.contains('is-dim')));
      cards.forEach(c => rail.appendChild(c));
      rail.scrollTo({ left: 0, behavior: reduce ? 'auto' : 'smooth' });
    }
  }
  filterBtns.forEach(b => b.addEventListener('click', () => setFilter(b.dataset.filter)));
  requestAnimationFrame(() => movePill($('.filters [aria-pressed="true"]')));
  addEventListener('resize', () => movePill($('.filters [aria-pressed="true"]')));

  $$('[data-rail]').forEach(btn => {
    const target = document.getElementById(btn.dataset.target || 'rail');
    if (!target) return;
    const dir = btn.dataset.rail === 'next' ? 1 : -1;
    btn.addEventListener('click', () => target.scrollBy({ left: dir * Math.min(target.clientWidth * 0.8, 760), behavior: 'smooth' }));
    const sync = () => {
      btn.disabled = dir < 0 ? target.scrollLeft < 8 : target.scrollLeft + target.clientWidth > target.scrollWidth - 8;
    };
    target.addEventListener('scroll', sync, { passive: true });
    addEventListener('resize', sync);
    sync();
  });

  if (!reduce && matchMedia('(hover: hover)').matches) {
    $$('.wine').forEach(card => {
      card.addEventListener('pointermove', e => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        card.style.transform = `perspective(1000px) rotateY(${(x - 0.5) * 10}deg) rotateX(${(0.5 - y) * 10}deg) translateY(-6px)`;
        card.style.setProperty('--gx', `${x * 100}%`);
        card.style.setProperty('--gy', `${y * 100}%`);
      });
      card.addEventListener('pointerleave', () => { card.style.transform = ''; });
    });
  }

  // drag-to-scroll on desktop
  let drag = null;
  rail.addEventListener('pointerdown', e => { if (e.pointerType !== 'mouse') return; drag = { x: e.clientX, left: rail.scrollLeft, moved: false }; });
  addEventListener('pointermove', e => { if (!drag) return; const dx = e.clientX - drag.x; if (Math.abs(dx) > 5) drag.moved = true; rail.scrollLeft = drag.left - dx; });
  addEventListener('pointerup', () => { setTimeout(() => { drag = null; }, 0); });

  const sheet = $('#sheet');
  let lastFocus = null;
  function openWine(id) {
    const w = WINES[id]; if (!w) return;
    $('#sheet-img').src = `${BASE}assets/img/${w.img}-lg.webp`;
    $('#sheet-img').alt = `Dasabami ${w.name} ${w.vintage}`;
    $('#sheet-style').textContent = tx('styles', w.style, w.style);
    $('#sheet-title').textContent = `${tx('grapes', w.name, w.name)} ${w.vintage}`;
    $('#sheet-geo').textContent = tx('geo', w.name, w.geo);
    $('#sheet-text').textContent = tx('wines', id, w.text);
    $('#sheet-facts').innerHTML = Object.entries(w.facts).map(([k, v]) => `<dt>${tx('labels', k, k)}</dt><dd>${tx('values', v, v)}</dd>`).join('');
    $('#sheet-ask').onclick = () => { closeSheet(); openGuide(tellMe(w)); };
    $('#sheet-mail').href = `mailto:${EMAIL}?subject=${encodeURIComponent(`Dasabami ${w.name} ${w.vintage}`)}`;
    lastFocus = document.activeElement;
    sheet.classList.add('is-open'); sheet.setAttribute('aria-hidden', 'false');
    setTimeout(() => $('.sheet-body .x').focus(), 50);
  }
  function closeSheet() {
    sheet.classList.remove('is-open'); sheet.setAttribute('aria-hidden', 'true');
    if (lastFocus) lastFocus.focus({ preventScroll: true });
  }
  $$('.wine').forEach(card => card.addEventListener('click', e => { if (drag && drag.moved) { e.preventDefault(); return; } openWine(card.dataset.wine); }));
  $$('[data-close-sheet]').forEach(b => b.addEventListener('click', closeSheet));

  /* ------------------------------------------------------------------
     Qvevri process — active step + progress line + image swap
     ------------------------------------------------------------------ */
  const steps = $$('.step');
  const stepImgs = $$('[data-step-img]');
  const stepsWrap = $('#steps');
  function updateSteps() {
    if (!steps.length) return;
    const mid = innerHeight * 0.5;
    let active = 0;
    steps.forEach((s, i) => { if (s.getBoundingClientRect().top < mid) active = i; });
    steps.forEach((s, i) => s.classList.toggle('is-active', i <= active));
    stepImgs.forEach((img, i) => img.classList.toggle('is-on', i === active));
    const r = stepsWrap.getBoundingClientRect();
    stepsWrap.style.setProperty('--sp', clamp((mid - r.top) / r.height).toFixed(3));
  }

  /* ------------------------------------------------------------------
     Press — auto-advancing quotes with progress bars
     ------------------------------------------------------------------ */
  const quotes = $$('#quotes .quote');
  const qImgs = $$('.quote-media img');
  const bars = $$('#qcontrols .bar');
  const qCredit = $('#qcredit');
  const stage = $('.quote-stage');
  let qi = 0, qInView = false;
  function showQuote(i) {
    qi = (i + quotes.length) % quotes.length;
    quotes.forEach((q, k) => q.classList.toggle('is-on', k === qi));
    qImgs.forEach((im, k) => im.classList.toggle('is-on', k === qi));
    bars.forEach((b, k) => { b.classList.toggle('is-on', k === qi); b.setAttribute('aria-current', k === qi ? 'true' : 'false'); });
    qCredit.textContent = quotes[qi].dataset.credit || '';
  }
  bars.forEach((b, i) => b.addEventListener('click', () => showQuote(i)));
  new IntersectionObserver(([en]) => { qInView = en.isIntersecting; }, { threshold: 0.35 }).observe(stage);

  // swipe: touch, mouse drag and trackpad
  let sx = null, sy = null, dragged = false;
  stage.addEventListener('pointerdown', e => {
    if (e.target.closest('a, button')) return;
    sx = e.clientX; sy = e.clientY; dragged = false;
    stage.classList.add('is-dragging');
  });
  addEventListener('pointerup', e => {
    if (sx === null) return;
    const dx = e.clientX - sx, dy = e.clientY - sy;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) { showQuote(qi + (dx < 0 ? 1 : -1)); dragged = true; }
    sx = sy = null; stage.classList.remove('is-dragging');
  });
  addEventListener('pointercancel', () => { sx = sy = null; stage.classList.remove('is-dragging'); });
  stage.addEventListener('click', e => { if (dragged) { e.preventDefault(); e.stopPropagation(); dragged = false; } }, true);
  let wheelLock = 0;
  stage.addEventListener('wheel', e => {
    if (Math.abs(e.deltaX) < 24 || Math.abs(e.deltaX) < Math.abs(e.deltaY)) return;
    e.preventDefault();
    const now = performance.now();
    if (now - wheelLock < 650) return;
    wheelLock = now;
    showQuote(qi + (e.deltaX > 0 ? 1 : -1));
  }, { passive: false });
  showQuote(0);

  /* ------------------------------------------------------------------
     Gallery lightbox
     ------------------------------------------------------------------ */
  const lb = $('#lightbox');
  function openLB(src, cap) {
    $('#lb-img').src = src; $('#lb-img').alt = cap; $('#lb-cap').textContent = cap;
    lastFocus = document.activeElement;
    lb.classList.add('is-open'); lb.setAttribute('aria-hidden', 'false');
    setTimeout(() => $('[data-close-lb]').focus(), 50);
  }
  function closeLB() { lb.classList.remove('is-open'); lb.setAttribute('aria-hidden', 'true'); if (lastFocus) lastFocus.focus({ preventScroll: true }); }
  $$('.shot').forEach(s => s.addEventListener('click', () => openLB(s.dataset.full, s.querySelector('figcaption').textContent)));
  lb.addEventListener('click', e => { if (e.target === lb || e.target.closest('[data-close-lb]')) closeLB(); });

  /* ------------------------------------------------------------------
     Event countdown — Amber Georgia Berlin, 28 Nov 2026
     ------------------------------------------------------------------ */
  const EVENT = new Date('2026-11-28T12:00:00+01:00');
  function updateCountdown() {
    const ms = EVENT - Date.now();
    const cd = $('#countdown');
    if (ms <= 0) {
      const ended = ms < -12 * 3600e3;
      $('#event-badge').textContent = ended ? tx('badge', 'recently', 'Recently') : tx('badge', 'today', 'Today');
      if (cd) cd.style.display = 'none';
      return;
    }
    const d = Math.floor(ms / 864e5), h = Math.floor(ms / 36e5) % 24, m = Math.floor(ms / 6e4) % 60;
    $('[data-cd="d"]').textContent = d;
    $('[data-cd="h"]').textContent = String(h).padStart(2, '0');
    $('[data-cd="m"]').textContent = String(m).padStart(2, '0');
  }
  updateCountdown(); setInterval(updateCountdown, 30000);

  /* ------------------------------------------------------------------
     End of page: keep scrolling to continue to the next site
     ------------------------------------------------------------------ */
  const nextSite = $('#next-site');
  let userScrolled = false, going = false;
  const loadedAt = performance.now();
  ['wheel', 'touchmove', 'keydown'].forEach(ev => addEventListener(ev, () => { userScrolled = true; }, { passive: true }));
  function updateNext() {
    if (!nextSite || reduce) return;
    const r = nextSite.getBoundingClientRect();
    const np = clamp(-r.top / Math.max(1, r.height - innerHeight));
    nextSite.style.setProperty('--np', np.toFixed(4));
    if (np > 0.985 && !going && userScrolled && performance.now() - loadedAt > 1500) {
      going = true;
      nextSite.classList.add('is-going');
      $('#next-hint').textContent = (T.opening || 'Opening {name}…').replace('{name}', nextSite.dataset.nextName);
      setTimeout(() => {
        const stillThere = nextSite.getBoundingClientRect().bottom <= innerHeight + 4;
        if (stillThere) location.href = nextSite.dataset.nextUrl;
        else { going = false; nextSite.classList.remove('is-going'); $('#next-hint').textContent = T.keepScrolling || 'Keep scrolling'; }
      }, 700);
    }
  }

  /* ------------------------------------------------------------------
     Scroll loop
     ------------------------------------------------------------------ */
  let ticking = false;
  function onScroll() {
    if (ticking) return; ticking = true;
    requestAnimationFrame(() => { updateHero(); updateNav(); updateManifesto(); updateSteps(); updateParallax(); updateNext(); ticking = false; });
  }
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', onScroll);
  onScroll();

  /* ------------------------------------------------------------------
     Contact: copy address
     ------------------------------------------------------------------ */
  const toastEl = $('#toast');
  let toastT;
  function toast(msg) {
    toastEl.textContent = msg; toastEl.classList.add('is-on');
    clearTimeout(toastT); toastT = setTimeout(() => toastEl.classList.remove('is-on'), 2200);
  }
  const copyBtn = $('#copy-email');
  if (copyBtn) copyBtn.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(EMAIL); toast((T.copied || 'Copied') + ' ' + EMAIL); }
    catch (_) { toast(EMAIL); }
  });

  /* ==================================================================
     Cellar guide — an on-page agent. It answers from the site's own
     knowledge and acts on the page: scrolls, filters, opens wines.
     ================================================================== */
  const guide = $('#guide');
  const log = $('#guide-log');
  const input = $('#guide-input');
  const suggestEl = $('#guide-suggest');
  let greeted = false;

  const go = (sel, opts = {}) => () => new Promise(res => {
    const el = $(sel); if (!el) return res();
    const top = el.getBoundingClientRect().top + scrollY - (opts.offset ?? 90);
    scrollTo({ top, behavior: reduce ? 'auto' : 'smooth' });
    setTimeout(() => { if (opts.spot) { const t = $(opts.spot); t && (t.classList.remove('spotlight'), void t.offsetWidth, t.classList.add('spotlight')); } res(); }, reduce ? 50 : 900);
  });

  const INTENTS = [
    { id: 'contact', re: /contact|e-?mail|mail|reach|write|phone|call|message|gmail/i,
      say: () => `<p>Write to Zaza directly at <a href="mailto:zazabery@gmail.com"><b>zazabery@gmail.com</b></a>, or message <a href="https://www.instagram.com/dasabami/" target="_blank" rel="noopener">@dasabami</a> on Instagram. Importers, shops, press and questions about a bottle are all welcome.</p>`,
      act: [{ label: 'Opening contact', run: go('#contact', { offset: 60 }) }],
      next: ['Where can I buy it?', 'Show me the amber wines'] },
    { id: 'amber', re: /\bamber|orange|skin.?contact|white|rkats|mtsvane|khikhvi\b/i,
      say: () => `<p>Three of the four grapes become <b>amber wines</b>: Rkatsiteli, Mtsvane and Khikhvi. They ferment on their skins in qvevri, from 3 months (Rkatsiteli 2022) up to 12 (Khikhvi 2021).</p><p>I’ve filtered the wines to amber for you.</p>`,
      act: [{ label: 'Filtering wines: Amber', run: () => { setFilter('amber'); return go('#wines', { offset: 100 })(); } }],
      next: ['Which is the rarest?', 'How is qvevri wine made?'] },
    { id: 'red', re: /\bred|tavkveri|saperavi\b/i,
      say: () => `<p><b>Tavkveri</b> is the red, a native Kartli grape. The 2020 had 45 days on skins and 9 months in qvevri, and only 180 bottles were made.</p><p>Dasabami doesn’t make a Saperavi.</p>`,
      act: [{ label: 'Filtering wines: Red', run: () => { setFilter('red'); return go('#wines', { offset: 100 })(); } }],
      next: ['Show me the amber wines', 'Where can I buy it?'] },
    { id: 'rare', re: /\brare|rarest|smallest|limited|how many bottles|production\b/i,
      say: () => `<p>Everything is small: from a 70-year-old vineyard, at most <b>~3,000 bottles a year</b> across all wines. The rarest recent release is <b>Tavkveri 2020</b>, at 180 bottles. Khikhvi 2022 made 300.</p>`,
      act: [{ label: 'Opening the tech sheets', run: go('.techsheet', { offset: 120, spot: '.techsheet' }) }],
      next: ['Tell me about Tavkveri', 'Where can I buy it?'] },
    { id: 'wines', re: /\bwines?\b|bottles?|range|portfolio|cuv[ée]e|what (do|does) (you|they) make/i,
      say: () => `<p>Dasabami makes wine from four indigenous grapes: <b>Rkatsiteli, Mtsvane, Khikhvi</b> (amber) and <b>Tavkveri</b> (red), plus a Rkatsiteli–Mtsvane blend. All are fermented in qvevri with wild yeasts, and none are fined or filtered.</p>`,
      act: [{ label: 'Scrolling to the wines', run: () => { setFilter('all'); return go('#wines', { offset: 100 })(); } }],
      next: ['Show me the amber wines', 'Which is the rarest?'] },
    { id: 'qvevri', re: /qvevri|kvevri|clay|how.*(made|make)|process|method|ferment/i,
      say: () => `<p>A <b>qvevri</b> is a large clay vessel buried in the earth, the traditional Georgian way to make wine. Grapes go in with their skins and ferment on ambient yeasts. The family qvevri is more than a century old.</p>`,
      act: [{ label: 'Walking through the process', run: go('#qvevri', { offset: 100 }) }],
      next: ['Is it organic?', 'Show me the amber wines'] },
    { id: 'organic', re: /organic|natural|sulfit|sulphit|so2|additive|vegan|filter/i,
      say: () => `<p>The vineyard is farmed <b>organically</b>, and the importer’s tech sheets list <b>no added SO₂</b>, ambient yeast, and no fining or filtering. Dasabami is a member of Georgia’s <a href="https://nwa.ge/en/profiles/about/295/dasabami" target="_blank" rel="noopener">Natural Wine Association</a>.</p>`,
      act: [{ label: 'Showing step 4: Bottled as it is', run: go('.step:last-child', { offset: 200 }) }],
      next: ['How is qvevri wine made?', 'Who is the winemaker?'] },
    { id: 'zaza', re: /zaza|winemaker|who|family|darsavelidze|story|history|founder|father/i,
      say: () => `<p><b>Zaza Darsavelidze</b> runs Dasabami, the family cellar his father founded in Tamarisi. The whole family makes the wine together, and Zaza first bottled it in 2012. You can write to him at <a href="mailto:zazabery@gmail.com">zazabery@gmail.com</a>.</p>`,
      act: [{ label: 'Opening the family story', run: go('#story', { offset: 100 }) }],
      next: ['Where is the vineyard?', 'What do critics say?'] },
    { id: 'where', re: /where.*(vineyard|located|from)|location|tamarisi|kartli|region|map|village/i,
      say: () => `<p>The vineyard is in <b>Tamarisi</b>, Marneuli Municipality, in <b>Kvemo Kartli</b> (Lower Kartli), south of Tbilisi and east of the Khrami River. It is about one hectare, and about 70 years old.</p>`,
      act: [{ label: 'Scrolling to the vines', run: go('#qvevri', { offset: 100 }) }],
      next: ['Can I visit?', 'Where can I buy it?'] },
    { id: 'buy', re: /buy|shop|stock|purchase|order|price|import|usa|us\b|london|tbilisi|where can/i,
      say: () => `<p>In <b>Tbilisi</b>, try 27 Wine Cellar &amp; Shop and Sulico Wine Bar at 27 Zandukeli St (the shop stocks the Rkatsiteli–Mtsvane 2025 and Rkatsiteli 2014), or Dadi Wine Bar at 4 Dadiani St, by Freedom Square. In the <b>US</b>, the importer is <a href="https://www.roniselects.com/georgia-producers/dasabami" target="_blank" rel="noopener">Roni Selects</a>. Online listings (Berlin, London, New York) were all sold out when we last checked.</p><p>For current bottles, email <a href="mailto:zazabery@gmail.com">zazabery@gmail.com</a> or message <a href="https://www.instagram.com/dasabami/" target="_blank" rel="noopener">@dasabami</a>.</p>`,
      act: [{ label: 'Showing online listings', run: go('.listings-head', { offset: 100 }) }],
      next: ['When is the next event?', 'Can I visit?'] },
    { id: 'event', re: /event|berlin|amber georgia|fair|festival|tasting|next/i,
      say: () => { const d = Math.ceil((EVENT - Date.now()) / 864e5); return d > 0 ? `<p>Next up: <b>Amber Georgia in Berlin</b> on 28 November 2026, ${d} day${d === 1 ? '' : 's'} from now. Dasabami is on the winemaker line-up.</p>` : `<p>Dasabami poured at <b>Amber Georgia in Berlin</b> on 28 November 2026. Follow <a href="https://www.instagram.com/dasabami/" target="_blank" rel="noopener">@dasabami</a> for the next one.</p>`; },
      act: [{ label: 'Opening the event', run: go('#find', { offset: 100, spot: '#event' }) }],
      next: ['Where can I buy it?', 'What do critics say?'] },
    { id: 'visit', re: /visit|tour|come|trip|travel|book/i,
      say: () => `<p>Dasabami is a small family cellar in Tamarisi, south of Tbilisi. If you’d like to visit, write first: <a href="mailto:zazabery@gmail.com">zazabery@gmail.com</a> or <a href="https://www.instagram.com/dasabami/" target="_blank" rel="noopener">Instagram</a>.</p>`,
      act: [], next: ['Where is the vineyard?', 'Where can I buy it?'] },
    { id: 'press', re: /press|critic|review|quote|said|rating|vivino|book|capalbo|media/i,
      say: () => `<p>Dasabami appears in Carla Capalbo’s book <i>Tasting Georgia</i> and in Culinary Backstreets. US importer Roni Selects counts Zaza among the founders of Georgia’s natural wine movement. On Vivino it averages <b>3.8 from 222 ratings</b>, with Khikhvi rated highest.</p>`,
      act: [{ label: 'Opening the press', run: go('#press', { offset: 40 }) }],
      next: ['Tell me about Khikhvi', 'Who is the winemaker?'] },
    { id: 'pair', re: /pair|food|eat|dish|cheese|dinner|meal/i,
      say: () => `<p>A general rule for qvevri wines: amber wines like Rkatsiteli and Khikhvi have grip and texture that suit Georgian food such as walnut dishes, khachapuri and grilled vegetables, plus aged cheeses. One reviewer called the 2010 Rkatsiteli superb with cheese. Tavkveri is lighter-bodied and suits grilled meat and mushrooms.</p>`,
      act: [], next: ['Show me the amber wines', 'Tell me about Tavkveri'] },
    { id: 'name', re: /name|mean|dasabami|დასაბამი/i,
      say: () => `<p><b>Dasabami</b> (დასაბამი) means “the beginning” in Georgian.</p>`,
      act: [], next: ['Who is the winemaker?', 'How is qvevri wine made?'] }
  ];

  const WINE_INTENT = { re: /tell me about (\w+)|about (rkatsiteli|mtsvane|khikhvi|tavkveri)/i };

  // "Tell me about X" in the page language (T.tellMe has a {name} placeholder; T.grapes localizes X)
  function tellMe(w) {
    return T.tellMe ? T.tellMe.replace('{name}', tx('grapes', w.name, w.name)) : `Tell me about ${w.name}`;
  }

  function findIntent(q) {
    const m = q.match(WINE_INTENT.re);
    let id = null;
    if (m) {
      const grape = (m[1] || m[2] || '').toLowerCase();
      id = Object.keys(WINES).find(k => k.startsWith(grape)) || null;
    }
    if (!id && T.tellMe) id = Object.keys(WINES).find(k => q === tellMe(WINES[k])) || null;
    if (id) {
      const w = WINES[id];
      return { say: () => `<p><b>${tx('grapes', w.name, w.name)}</b> (${tx('geo', w.name, w.geo)}) · ${tx('styles', w.style, w.style)}</p><p>${tx('wines', id, w.text)}</p>`,
        act: [{ label: T.goingThere || `Opening ${w.name} ${w.vintage}`, run: () => go('#wines', { offset: 100 })().then(() => { const c = $(`.wine[data-wine="${id}"]`); if (c) { setFilter('all'); c.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' }); c.classList.remove('is-flash'); void c.offsetWidth; c.classList.add('is-flash'); } }) }],
        next: T.suggestions || ['Which is the rarest?', 'Where can I buy it?'] };
    }
    if (T.intents) {
      const lq = q.toLowerCase();
      for (const [id, def] of Object.entries(T.intents)) {
        if ((def.kw || []).some(k => lq.includes(k.toLowerCase()))) {
          const base = INTENTS.find(i => i.id === id);
          const answer = def.answer || (T.faq && T.faq[def.faq]) || '';
          return {
            say: () => `<p>${answer}</p>`,
            act: base && base.act ? base.act.map(a => ({ label: T.goingThere || a.label, run: a.run })) : [],
            next: T.suggestions || []
          };
        }
      }
    }
    return INTENTS.find(i => i.re.test(q)) || null;
  }

  function addMsg(role, html) {
    const el = document.createElement('div');
    el.className = `msg ${role}`;
    el.innerHTML = role === 'bot' ? `<span class="orb" aria-hidden="true"></span><div class="body">${html}</div>` : html;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return el;
  }
  function setSuggest(list) {
    suggestEl.innerHTML = '';
    list.forEach(t => {
      const b = document.createElement('button'); b.type = 'button'; b.textContent = t;
      b.addEventListener('click', () => ask(t));
      suggestEl.appendChild(b);
    });
  }
  const wait = ms => new Promise(r => setTimeout(r, reduce ? 0 : ms));

  async function typeInto(body, html) {
    // reveal paragraph by paragraph, word by word
    const tmp = document.createElement('div'); tmp.innerHTML = html;
    body.innerHTML = '';
    for (const node of [...tmp.childNodes]) {
      const clone = node.cloneNode(true);
      body.appendChild(clone);
      if (reduce) continue;
      const walker = document.createTreeWalker(clone, NodeFilter.SHOW_TEXT);
      const texts = []; while (walker.nextNode()) texts.push(walker.currentNode);
      const full = texts.map(t => t.textContent);
      texts.forEach(t => { t.textContent = ''; });
      for (let i = 0; i < texts.length; i++) {
        const parts = full[i].split(/(\s+)/);
        for (const p of parts) { texts[i].textContent += p; if (p.trim()) { log.scrollTop = log.scrollHeight; await wait(14); } }
      }
    }
  }

  let busy = false;
  async function ask(q) {
    q = q.trim(); if (!q || busy) return;
    busy = true; input.value = ''; setSuggest([]);
    addMsg('user', q.replace(/[<>&]/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[c])));
    const bot = addMsg('bot', '<span class="typing"><i></i><i></i><i></i></span>');
    const body = $('.body', bot);
    await wait(550 + Math.random() * 350);
    const intent = findIntent(q);
    if (!intent) {
      await typeInto(body, `<p>${T.fallback || 'I can help with the wines, how they’re made, the family, where to buy, and upcoming events. Try one of these:'}</p>`);
      setSuggest(T.suggestions || ['Show me the amber wines', 'How is qvevri wine made?', 'Where can I buy it?', 'Who is the winemaker?']);
      busy = false; return;
    }
    await typeInto(body, intent.say());
    for (const a of intent.act || []) {
      const chip = document.createElement('div');
      chip.className = 'action-chip'; chip.innerHTML = `<span class="spin"></span>${a.label}`;
      body.appendChild(chip); log.scrollTop = log.scrollHeight;
      await wait(350);
      if (matchMedia('(max-width: 720px)').matches) closeGuide(true);
      await a.run();
      chip.classList.add('done');
    }
    setSuggest(intent.next || []);
    busy = false;
  }

  function openGuide(prefill) {
    lastFocus = document.activeElement;
    guide.classList.add('is-open'); guide.setAttribute('aria-hidden', 'false');
    document.body.classList.add('guide-open');
    if (!greeted) {
      greeted = true;
      const b = addMsg('bot', '');
      typeInto($('.body', b), `<p>${T.greeting || 'Gamarjoba! I’m the Dasabami cellar guide. Ask me about the wines, the qvevri, the family, or where to find a bottle, and I’ll take you to the right part of the page.'}</p>`)
        .then(() => { if (!prefill) setSuggest(T.suggestions || ['Show me the amber wines', 'How is qvevri wine made?', 'Where can I buy it?', 'How do I contact Zaza?']); });
    }
    setTimeout(() => input.focus({ preventScroll: true }), 120);
    if (prefill) setTimeout(() => ask(prefill), greeted ? 200 : 1600);
  }
  function closeGuide(keepFocus) {
    guide.classList.remove('is-open'); guide.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('guide-open');
    if (!keepFocus && lastFocus) lastFocus.focus({ preventScroll: true });
  }
  $$('[data-open-guide]').forEach(b => b.addEventListener('click', () => openGuide()));
  $$('[data-close-guide]').forEach(b => b.addEventListener('click', () => closeGuide()));
  $('#guide-form').addEventListener('submit', e => { e.preventDefault(); ask(input.value); });

  addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); guide.classList.contains('is-open') ? closeGuide() : openGuide(); }
    else if (e.key === '/' && !/input|textarea/i.test(document.activeElement.tagName) && !guide.classList.contains('is-open')) { e.preventDefault(); openGuide(); }
    else if (e.key === 'Escape') {
      if (lb.classList.contains('is-open')) closeLB();
      else if (sheet.classList.contains('is-open')) closeSheet();
      else if (guide.classList.contains('is-open')) closeGuide();
    }
    else if (stage && qInView && (e.key === 'ArrowRight' || e.key === 'ArrowLeft') && !guide.classList.contains('is-open') && document.activeElement.closest && document.activeElement.closest('.press')) {
      showQuote(qi + (e.key === 'ArrowRight' ? 1 : -1));
    }
  });

})();
