'use strict';

/* ══════════════════════════════════════════════════════════
   LUMIERE — Main Application Script
   GSAP · Lenis · Custom Cursor · Magnetic · Tilt
   Services / Reviews / Booking API integration
══════════════════════════════════════════════════════════ */

gsap.registerPlugin(ScrollTrigger);

document.body.style.overflow = 'hidden';

/* ─── PRELOADER ─── */
window.addEventListener('load', () => {
  setTimeout(() => {
    gsap.to('#preloader', {
      yPercent: -100,
      duration: 1,
      ease: 'power4.inOut',
      onComplete: () => {
        const pl = document.getElementById('preloader');
        if (pl) { pl.style.pointerEvents = 'none'; pl.style.visibility = 'hidden'; }
        document.body.style.overflow = '';
        if (window.LumiereThree) window.LumiereThree.init();
      }
    });
  }, 1800);
});

/* ─── LENIS SMOOTH SCROLL ─── */
const lenis = new Lenis({
  duration: 1.2,
  easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smoothTouch: false
});
gsap.ticker.add(time => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);
lenis.on('scroll', ScrollTrigger.update);

document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const href = a.getAttribute('href');
    if (href && href.length > 1) {
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        lenis.scrollTo(target, { duration: 1.4 });
      }
    }
  });
});

/* ─── PROGRESS BAR ─── */
gsap.to('#progressBar', {
  scaleX: 1, ease: 'none',
  scrollTrigger: { trigger: 'body', start: 'top top', end: 'bottom bottom', scrub: true }
});

/* ─── HERO ENTRANCE ─── */
const heroTl = gsap.timeline({ delay: 2 });
heroTl
  .fromTo('.hero-badge',       { opacity: 0, y: -16 }, { opacity: 1, y: 0, duration: .8 })
  .fromTo('.hero-title .line', { opacity: 0, y: 120 }, { opacity: 1, y: 0, duration: 1.2, stagger: .12, ease: 'power4.out' }, '-=.4')
  .fromTo('.hero-sub',         { opacity: 0, y: 20  }, { opacity: 1, y: 0, duration: .8 }, '-=.6')
  .fromTo('.hero-ctas > *',    { opacity: 0, y: 16  }, { opacity: 1, y: 0, duration: .6, stagger: .1 }, '-=.4')
  .fromTo('.hero-meta',        { opacity: 0 }, { opacity: 1, duration: .6 }, '-=.3')
  .fromTo('.scroll-hint',      { opacity: 0 }, { opacity: 1, duration: .5 }, '-=.2');

/* ─── SECTION TITLE CLIP REVEAL ─── */
gsap.utils.toArray('.section-title').forEach(el => {
  gsap.fromTo(el,
    { 'clip-path': 'inset(0 0 100% 0)' },
    { 'clip-path': 'inset(0 0 0% 0)', duration: 1.1, ease: 'power4.out',
      scrollTrigger: { trigger: el, start: 'top 85%' }
    }
  );
});

gsap.utils.toArray('.eyebrow').forEach(el => {
  gsap.fromTo(el,
    { opacity: 0, y: 14 },
    { opacity: 1, y: 0, duration: .7, scrollTrigger: { trigger: el, start: 'top 90%' } }
  );
});

/* ─── REUSABLE CARD REVEAL ─── */
function revealCards(selector, trigger, opts = {}) {
  gsap.fromTo(selector,
    { opacity: 0, y: 60 },
    {
      opacity: 1, y: 0,
      duration: opts.duration || .9,
      stagger: opts.stagger || .12,
      ease: 'power3.out',
      scrollTrigger: { trigger: trigger, start: opts.start || 'top 78%' }
    }
  );
}

revealCards('.gal-item', '.gallery-grid', { stagger: .1 });
revealCards('.review-card', '.reviews-track', { stagger: .12 });

/* ─── ABOUT ─── */
gsap.fromTo('.about-visual',
  { opacity: 0, x: -60 },
  { opacity: 1, x: 0, duration: 1.1, ease: 'power3.out',
    scrollTrigger: { trigger: '#about', start: 'top 65%' }
  }
);
gsap.fromTo('.about-content > *',
  { opacity: 0, y: 30 },
  { opacity: 1, y: 0, duration: .8, stagger: .1, ease: 'power3.out',
    scrollTrigger: { trigger: '#about', start: 'top 60%' }
  }
);

/* ─── CONTACT ─── */
gsap.fromTo('.contact-info',
  { opacity: 0, x: -40 },
  { opacity: 1, x: 0, duration: 1, ease: 'power3.out',
    scrollTrigger: { trigger: '.contact-grid', start: 'top 70%' }
  }
);
gsap.fromTo('.map-wrap',
  { opacity: 0, x: 40 },
  { opacity: 1, x: 0, duration: 1, ease: 'power3.out',
    scrollTrigger: { trigger: '.contact-grid', start: 'top 70%' }
  }
);

/* ─── MARQUEE ─── */
gsap.to('.marquee-track', { xPercent: -50, ease: 'none', duration: 30, repeat: -1 });

/* ─── CUSTOM CURSOR ─── */
const cursorDot  = document.getElementById('cursorDot');
const cursorRing = document.getElementById('cursorRing');
let cMx = 0, cMy = 0, cRx = 0, cRy = 0;

document.addEventListener('mousemove', e => {
  cMx = e.clientX; cMy = e.clientY;
  if (cursorDot) {
    cursorDot.style.left = cMx + 'px';
    cursorDot.style.top  = cMy + 'px';
  }
});

(function animCursor() {
  cRx += (cMx - cRx) * 0.12;
  cRy += (cMy - cRy) * 0.12;
  if (cursorRing) {
    cursorRing.style.left = cRx + 'px';
    cursorRing.style.top  = cRy + 'px';
  }
  requestAnimationFrame(animCursor);
})();

/* ─── NAVBAR ─── */
const navbar    = document.getElementById('navbar');
const scrollBtn = document.getElementById('scrollTop');

window.addEventListener('scroll', () => {
  const y = window.scrollY;
  if (navbar)    navbar.classList.toggle('scrolled', y > 50);
  if (scrollBtn) scrollBtn.classList.toggle('visible', y > 500);
}, { passive: true });

/* ─── HAMBURGER ─── */
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('navLinks');
if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    navLinks.classList.toggle('open');
  });
  navLinks.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      hamburger.classList.remove('open');
      navLinks.classList.remove('open');
    });
  });
}

if (scrollBtn) {
  scrollBtn.addEventListener('click', () => lenis.scrollTo(0, { duration: 1.4 }));
}

/* ─── ACTIVE NAV ─── */
const navAnchors = document.querySelectorAll('.nav-links a');
const sideDots   = document.querySelectorAll('.sn-dot');
const sections   = document.querySelectorAll('section[id]');

const sectionObs = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    const id = entry.target.id;
    navAnchors.forEach(a => a.classList.toggle('active-link', a.getAttribute('href') === '#' + id));
    sideDots.forEach(d   => d.classList.toggle('active', d.getAttribute('href') === '#' + id));
  });
}, { rootMargin: '-40% 0px -55% 0px' });
sections.forEach(s => sectionObs.observe(s));

/* ─── 3D TILT for cards ─── */
function applyTilt(selectors, max = 6) {
  document.querySelectorAll(selectors).forEach(card => {
    card.addEventListener('mousemove', e => {
      const r  = card.getBoundingClientRect();
      const dx = (e.clientX - (r.left + r.width  / 2)) / (r.width  / 2);
      const dy = (e.clientY - (r.top  + r.height / 2)) / (r.height / 2);
      card.style.transform   = `perspective(900px) rotateX(${-dy * max}deg) rotateY(${dx * max}deg) translateY(-4px)`;
      card.style.transition  = 'transform 0.12s linear';
    });
    card.addEventListener('mouseleave', () => {
      card.style.transition = 'transform 0.55s cubic-bezier(.25,.1,.25,1)';
      card.style.transform  = 'perspective(900px) rotateX(0) rotateY(0) translateY(0)';
    });
  });
}

/* ─── MAGNETIC BUTTONS ─── */
function applyMagnetic() {
  document.querySelectorAll('.magnetic').forEach(btn => {
    if (btn.dataset.magnetic === 'on') return;
    btn.dataset.magnetic = 'on';
    btn.addEventListener('mousemove', e => {
      const r  = btn.getBoundingClientRect();
      const dx = e.clientX - (r.left + r.width  / 2);
      const dy = e.clientY - (r.top  + r.height / 2);
      btn.style.transform  = `translate(${dx * 0.2}px, ${dy * 0.2}px)`;
      btn.style.transition = 'transform 0.12s linear';
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.transform  = '';
      btn.style.transition = 'transform 0.5s cubic-bezier(.25,.1,.25,1)';
    });
  });
}

/* ─── API HELPER ─── */
async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

/* ─── SERVICES LOAD ─── */
async function loadServices() {
  const grid = document.getElementById('servicesGrid');
  const select = document.getElementById('bkService');
  if (!grid) return;
  try {
    const services = await api('/api/services');
    grid.innerHTML = services.map((s, i) => `
      <article class="svc-card">
        <div class="svc-num">— ${String(i + 1).padStart(2, '0')}</div>
        <h3>${s.name}</h3>
        <p>${serviceDesc(s.id)}</p>
        <div class="svc-meta">
          <span>${s.duration} min · from <strong>$${s.price}</strong></span>
          <a href="#book" class="svc-cta" data-service="${s.name}">Book →</a>
        </div>
      </article>
    `).join('');

    if (select) {
      select.innerHTML = `<option value="" disabled selected>Choose a service</option>` +
        services.map(s => `<option value="${s.name}">${s.name} — $${s.price}</option>`).join('');
    }

    gsap.fromTo('.svc-card',
      { opacity: 0, y: 50 },
      { opacity: 1, y: 0, duration: .8, stagger: .1, ease: 'power3.out',
        scrollTrigger: { trigger: '#services .services-grid', start: 'top 78%' }
      }
    );
    applyTilt('.svc-card', 4);

    document.querySelectorAll('.svc-cta').forEach(link => {
      link.addEventListener('click', e => {
        const svc = link.dataset.service;
        if (svc && select) {
          setTimeout(() => { select.value = svc; }, 600);
        }
      });
    });
  } catch (e) {
    grid.innerHTML = '<p style="color:var(--muted);text-align:center;grid-column:1/-1">Unable to load services.</p>';
  }
}

function serviceDesc(id) {
  const map = {
    cut:     'A considered shape, with line and texture tuned to your hair. Includes consultation and finish.',
    color:   'Single-process, balayage, and tone. Slow, intentional placement for a lived-in, refined result.',
    silk:    'Smooth, mirror-finish silk press. Wash, blow-dry, and silk press with heat-protective care.',
    keratin: 'A months-long smoothing treatment. Reduces frizz and drying time, deepens shine.',
    blowout: 'Our signature blowout — soft volume and movement that holds beautifully for days.',
    treat:   'A deep, restorative treatment for stressed hair. Bond repair, hydration, and finish.'
  };
  return map[id] || 'A considered service, intentionally delivered.';
}

/* ─── REVIEWS LOAD ─── */
let reviewState = { cards: [], current: 0, interval: null };

function getReviewsPerView() {
  return window.innerWidth <= 768 ? 1 : window.innerWidth <= 1100 ? 2 : 3;
}

function renderReviewCard(r) {
  const initials = (r.name || '?').split(' ').map(s => s[0]).join('').slice(0, 2).toUpperCase();
  const stars = '★'.repeat(r.rating || 5);
  return `
    <article class="review-card">
      <div class="rc-quote">“</div>
      <p class="rc-text">${escapeHtml(r.text)}</p>
      <div class="rc-footer">
        <div class="rc-avatar">${initials}</div>
        <div class="rc-info">
          <strong>${escapeHtml(r.name)}</strong>
          <span>${escapeHtml(r.service || 'Guest')} · ${formatDate(r.date)}</span>
        </div>
        <div class="rc-stars">${stars}</div>
      </div>
    </article>
  `;
}

function escapeHtml(str) {
  return String(str || '').replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

function formatDate(d) {
  if (!d) return 'recent';
  try {
    const dt = new Date(d);
    return dt.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  } catch { return d; }
}

async function loadReviews() {
  const track = document.getElementById('reviewsTrack');
  if (!track) return;
  try {
    const reviews = await api('/api/reviews');
    track.innerHTML = reviews.map(renderReviewCard).join('');
    reviewState.cards = Array.from(track.children);
    reviewState.current = 0;
    buildReviewDots();
    gsap.fromTo('.review-card',
      { opacity: 0, y: 40 },
      { opacity: 1, y: 0, duration: .8, stagger: .12, ease: 'power3.out',
        scrollTrigger: { trigger: '.reviews-slider', start: 'top 78%' }
      }
    );
    startAutoReview();
  } catch (e) {
    track.innerHTML = '<p style="color:var(--muted);text-align:center;flex:1">No reviews yet.</p>';
  }
}

function buildReviewDots() {
  const dotsWrap = document.getElementById('rDots');
  if (!dotsWrap) return;
  dotsWrap.innerHTML = '';
  const total = Math.ceil(reviewState.cards.length / getReviewsPerView());
  for (let i = 0; i < total; i++) {
    const btn = document.createElement('button');
    btn.className = 'sd-dot' + (i === reviewState.current ? ' active' : '');
    btn.addEventListener('click', () => gotoReview(i));
    dotsWrap.appendChild(btn);
  }
}

function gotoReview(i) {
  const track = document.getElementById('reviewsTrack');
  if (!track) return;
  const spv = getReviewsPerView();
  const max = Math.max(0, Math.ceil(reviewState.cards.length / spv) - 1);
  reviewState.current = Math.max(0, Math.min(i, max));
  const w = reviewState.cards[0] ? reviewState.cards[0].offsetWidth + 24 : 0;
  track.style.transform = `translateX(-${reviewState.current * spv * w}px)`;
  document.querySelectorAll('#rDots .sd-dot').forEach((d, k) => {
    d.classList.toggle('active', k === reviewState.current);
  });
}

function startAutoReview() {
  if (reviewState.interval) clearInterval(reviewState.interval);
  reviewState.interval = setInterval(() => {
    const total = Math.ceil(reviewState.cards.length / getReviewsPerView());
    gotoReview(reviewState.current + 1 >= total ? 0 : reviewState.current + 1);
  }, 5500);
}

document.getElementById('rNext')?.addEventListener('click', () => {
  const total = Math.ceil(reviewState.cards.length / getReviewsPerView());
  gotoReview(reviewState.current + 1 >= total ? 0 : reviewState.current + 1);
  startAutoReview();
});
document.getElementById('rPrev')?.addEventListener('click', () => {
  const total = Math.ceil(reviewState.cards.length / getReviewsPerView());
  gotoReview(reviewState.current - 1 < 0 ? total - 1 : reviewState.current - 1);
  startAutoReview();
});

window.addEventListener('resize', () => { reviewState.current = 0; buildReviewDots(); gotoReview(0); });

/* ─── STATS ─── */
async function loadStats() {
  try {
    const stats = await api('/api/stats');
    const scoreEl = document.getElementById('orScore');
    const countEl = document.getElementById('orCount');
    if (scoreEl) scoreEl.textContent = (stats.averageRating || 5).toFixed(1);
    if (countEl) countEl.textContent = stats.reviewCount;

    document.querySelectorAll('[data-stat]').forEach(el => {
      const key = el.dataset.stat;
      const v = stats[key];
      if (typeof v === 'number') {
        animateNumber(el, v);
      } else {
        el.textContent = v;
      }
    });
  } catch (e) {
    /* silent */
  }
}

function animateNumber(el, target) {
  const isFloat = !Number.isInteger(target);
  const dur = 1200;
  const start = performance.now();
  function frame(now) {
    const p = Math.min(1, (now - start) / dur);
    const eased = 1 - Math.pow(1 - p, 3);
    const cur = target * eased;
    el.textContent = isFloat ? cur.toFixed(1) : Math.round(cur);
    if (p < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

/* ─── REVIEW FORM ─── */
const reviewForm = document.getElementById('reviewForm');
const rvSuccess  = document.getElementById('rvSuccess');
const ratingWrap = document.getElementById('ratingStars');

if (ratingWrap) {
  const stars = ratingWrap.querySelectorAll('span');
  const setStars = v => {
    stars.forEach(s => s.classList.toggle('active', +s.dataset.v <= v));
    ratingWrap.dataset.value = v;
  };
  setStars(5);
  stars.forEach(s => {
    s.addEventListener('mouseenter', () => {
      stars.forEach(x => x.classList.toggle('hover', +x.dataset.v <= +s.dataset.v));
    });
    s.addEventListener('mouseleave', () => stars.forEach(x => x.classList.remove('hover')));
    s.addEventListener('click', () => setStars(+s.dataset.v));
  });
}

if (reviewForm) {
  reviewForm.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = reviewForm.querySelector('button[type="submit"]');
    const span = btn?.querySelector('span');
    const prev = span ? span.textContent : '';
    if (span) span.textContent = 'Sending…';
    if (btn) btn.disabled = true;
    try {
      const payload = {
        name: document.getElementById('rvName').value,
        service: document.getElementById('rvService').value,
        rating: parseInt(ratingWrap.dataset.value, 10) || 5,
        text: document.getElementById('rvText').value
      };
      await api('/api/reviews', { method: 'POST', body: JSON.stringify(payload) });
      if (rvSuccess) rvSuccess.classList.add('show');
      reviewForm.reset();
      if (ratingWrap) {
        ratingWrap.querySelectorAll('span').forEach(s =>
          s.classList.toggle('active', +s.dataset.v <= 5)
        );
        ratingWrap.dataset.value = 5;
      }
      setTimeout(() => rvSuccess?.classList.remove('show'), 5000);
      await loadReviews();
      await loadStats();
    } catch (err) {
      alert('Could not submit review. Please try again.');
    } finally {
      if (span) span.textContent = prev;
      if (btn) btn.disabled = false;
    }
  });
}

/* ─── BOOKING FORM ─── */
const bookForm = document.getElementById('bookForm');
const bkSuccess = document.getElementById('bkSuccess');
const bkError  = document.getElementById('bkError');

(function setMinDate() {
  const today = new Date().toISOString().slice(0, 10);
  const dt = document.getElementById('bkDate');
  if (dt) dt.min = today;
})();

if (bookForm) {
  bookForm.addEventListener('submit', async e => {
    e.preventDefault();
    bkError?.classList.remove('show');
    const btn = bookForm.querySelector('button[type="submit"]');
    const span = btn?.querySelector('span');
    const prev = span ? span.textContent : '';
    if (span) span.textContent = 'Confirming…';
    if (btn) btn.disabled = true;
    try {
      const payload = {
        name:    document.getElementById('bkName').value,
        email:   document.getElementById('bkEmail').value,
        phone:   document.getElementById('bkPhone').value,
        service: document.getElementById('bkService').value,
        date:    document.getElementById('bkDate').value,
        time:    document.getElementById('bkTime').value,
        notes:   document.getElementById('bkNotes').value
      };
      const result = await api('/api/bookings', { method: 'POST', body: JSON.stringify(payload) });
      if (!result.ok) throw new Error(result.error || 'Booking failed');
      if (bkSuccess) bkSuccess.classList.add('show');
      bookForm.reset();
      setTimeout(() => bkSuccess?.classList.remove('show'), 7000);
    } catch (err) {
      if (bkError) {
        bkError.textContent = 'Could not confirm booking. Please check the fields and try again.';
        bkError.classList.add('show');
      }
    } finally {
      if (span) span.textContent = prev;
      if (btn) btn.disabled = false;
    }
  });
}

/* ─── CONTACT FORM ─── */
const contactForm = document.getElementById('contactForm');
const cfSuccess   = document.getElementById('cfSuccess');

if (contactForm) {
  contactForm.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = contactForm.querySelector('button[type="submit"]');
    const span = btn?.querySelector('span');
    const prev = span ? span.textContent : '';
    if (span) span.textContent = 'Sending…';
    if (btn) btn.disabled = true;
    try {
      const payload = {
        name:    document.getElementById('cfName').value,
        email:   document.getElementById('cfEmail').value,
        message: document.getElementById('cfMsg').value
      };
      await api('/api/contacts', { method: 'POST', body: JSON.stringify(payload) });
      if (cfSuccess) cfSuccess.classList.add('show');
      contactForm.reset();
      setTimeout(() => cfSuccess?.classList.remove('show'), 6000);
    } catch (err) {
      alert('Message could not be sent. Please try again.');
    } finally {
      if (span) span.textContent = prev;
      if (btn) btn.disabled = false;
    }
  });
}

/* ─── GALLERY TILT ─── */
applyTilt('.gal-item', 5);

/* ─── INIT API LOADERS ─── */
(async function init() {
  await Promise.all([loadServices(), loadReviews(), loadStats()]);
  applyMagnetic();
})();

/* Reapply magnetic after dynamic content */
const mo = new MutationObserver(() => applyMagnetic());
mo.observe(document.body, { childList: true, subtree: true });
