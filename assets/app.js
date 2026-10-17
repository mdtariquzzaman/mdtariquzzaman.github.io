(() => {
  const root = document.documentElement;
  root.classList.add('js');

  // One switch for decorative motion: it follows the system's reduced-motion
  // preference, the header's motion button holds every animation still (and the
  // site remembers it), and pressing it again plays them for this visit.
  const motionMedia = window.matchMedia('(prefers-reduced-motion: reduce)');
  const motionListeners = new Set();
  let motionHeld = false;
  let motionPlayed = false;
  try { motionHeld = localStorage.getItem('tariq-motion') === 'held'; } catch (_) { /* storage unavailable */ }
  const siteMotion = {
    get reduced() { return motionHeld || (motionMedia.matches && !motionPlayed); },
    play() {
      motionHeld = false;
      motionPlayed = true;
      try { localStorage.removeItem('tariq-motion'); } catch (_) {}
      motionChanged();
    },
    hold() {
      motionHeld = true;
      try { localStorage.setItem('tariq-motion', 'held'); } catch (_) {}
      motionChanged();
    },
    subscribe(listener) { motionListeners.add(listener); },
  };
  const motionChanged = () => {
    root.dataset.motion = siteMotion.reduced ? 'still' : 'live';
    motionListeners.forEach(listener => listener());
  };
  // A change to the system setting takes precedence over this visit's choice.
  motionMedia.addEventListener?.('change', () => { motionPlayed = false; motionChanged(); });
  root.dataset.motion = siteMotion.reduced ? 'still' : 'live';
  window.siteMotion = siteMotion;

  const motionButtons = [...document.querySelectorAll('.motion-toggle')];
  const updateMotionLabel = () => {
    const still = siteMotion.reduced;
    motionButtons.forEach((button) => {
      button.setAttribute('aria-pressed', String(still));
      button.title = still ? 'Play animations' : 'Pause animations';
    });
  };
  motionButtons.forEach(button => button.addEventListener('click', () => {
    if (siteMotion.reduced) siteMotion.play(); else siteMotion.hold();
  }));
  siteMotion.subscribe(updateMotionLabel);
  updateMotionLabel();

  const themeButtons = [...document.querySelectorAll('.theme-toggle')];
  const menuButton = document.querySelector('.nav-burger');
  const nav = document.querySelector('.site-header nav');
  const siteHeader = document.querySelector('.site-header');
  const measureHeader = () => {
    if (siteHeader) root.style.setProperty('--header-h', `${siteHeader.offsetHeight}px`);
  };
  if (siteHeader) new ResizeObserver(measureHeader).observe(siteHeader);
  measureHeader();

  try {
    const savedTheme = localStorage.getItem('tariq-theme');
    if (savedTheme === 'dark' || savedTheme === 'light') root.dataset.theme = savedTheme;
  } catch (_) { /* Reading controls still work when storage is unavailable. */ }

  if (themeButtons.length) {
    const SUN = '<svg class="icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M10 1h4v3h-4zM10 20h4v3h-4zM1 10h3v4H1zM20 10h3v4h-3zM4 4h3v3H4zM17 4h3v3h-3zM4 17h3v3H4zM17 17h3v3h-3zM8 6h8v2H8zM6 8h2v8H6zM16 8h2v8h-2zM8 16h8v2H8z"/></svg>';
    const MOON = '<svg class="icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 2h6v2H8zM6 4h4v2H6zM4 6h4v2H4zM2 8h4v8H2zM4 16h4v2H4zM6 18h12v2H6zM8 20h8v2H8zM10 4h2v6h-2zM12 10h2v2h-2zM14 12h6v2h-6zM18 14h4v2h-4zM16 16h4v2h-4z"/></svg>';
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const effectiveDark = () => root.dataset.theme === 'dark' || (!root.dataset.theme && media.matches);
    const updateThemeLabel = () => {
      const dark = effectiveDark();
      themeButtons.forEach(themeButton => {
        themeButton.innerHTML = dark ? `${SUN}<span>Day</span>` : `${MOON}<span>Night</span>`;
        themeButton.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
        themeButton.title = dark ? 'Switch to light theme' : 'Switch to dark theme';
      });
      document.querySelectorAll('meta[name="theme-color"]').forEach(meta => {
        meta.content = dark ? '#181d30' : '#f2e9d8';
      });
      const studySource = document.querySelector('.study-picture source');
      if (studySource) studySource.media = dark ? 'all' : 'not all';
    };
    // The Home picture changes with the theme: wait briefly for the new one, so
    // the dissolve reveals it rather than the old picture.
    const studyPictureReady = () => {
      const image = document.querySelector('.study-picture img');
      if (!image) return undefined;
      return new Promise((resolve) => {
        const done = () => {
          clearTimeout(timer);
          image.removeEventListener('load', done);
          image.removeEventListener('error', done);
          resolve();
        };
        const timer = setTimeout(done, 400);
        image.addEventListener('load', done);
        image.addEventListener('error', done);
      });
    };
    media.addEventListener?.('change', () => { if (!root.dataset.theme) updateThemeLabel(); });
    updateThemeLabel();
    themeButtons.forEach(themeButton => themeButton.addEventListener('click', () => {
      const next = effectiveDark() ? 'light' : 'dark';
      const swap = () => {
        root.dataset.theme = next;
        try { localStorage.setItem('tariq-theme', next); } catch (_) {}
        updateThemeLabel();
        return studyPictureReady();
      };
      // The new palette dissolves in through a pixel dither (interactions.css);
      // the pixel scenes repaint inside the update, so they dissolve with it.
      if (document.startViewTransition && !siteMotion.reduced) document.startViewTransition(swap);
      else swap();
    }));
  }

  // Reading progress: a bar fills along the header's title strip in whole
  // four-pixel steps, like a loading gauge.
  const titleStrip = document.querySelector('.header-title-strip');
  if (titleStrip) {
    const gauge = document.createElement('span');
    gauge.className = 'read-progress';
    gauge.setAttribute('aria-hidden', 'true');
    const gaugeFill = document.createElement('span');
    gauge.append(gaugeFill);
    titleStrip.append(gauge);
    let gaugePending = false;
    const paintGauge = () => {
      gaugePending = false;
      const room = document.documentElement.scrollHeight - window.innerHeight;
      const done = room > 0 ? Math.min(1, Math.max(0, window.scrollY / room)) : 0;
      gaugeFill.style.width = `${Math.round(done * titleStrip.clientWidth / 4) * 4}px`;
    };
    const scheduleGauge = () => {
      if (!gaugePending) { gaugePending = true; requestAnimationFrame(paintGauge); }
    };
    window.addEventListener('scroll', scheduleGauge, { passive: true });
    window.addEventListener('resize', scheduleGauge);
    new ResizeObserver(scheduleGauge).observe(document.body);
    paintGauge();
  }

  // Back to top pops up at the bottom right once the page has scrolled down, and
  // tucks away again near the top (interactions.css).
  const backToTop = document.querySelector('.back-to-top');
  if (backToTop) {
    let backPending = false;
    const syncBackToTop = () => {
      backPending = false;
      backToTop.classList.toggle('is-shown', window.scrollY > 160);
    };
    window.addEventListener('scroll', () => {
      if (!backPending) { backPending = true; requestAnimationFrame(syncBackToTop); }
    }, { passive: true });
    syncBackToTop();
  }

  // Accepted seals catch the light once, the first time each scrolls into view.
  const seals = document.querySelectorAll('.accepted-venue');
  if (seals.length && 'IntersectionObserver' in window) {
    const shine = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        shine.unobserve(entry.target);
        if (!siteMotion.reduced) entry.target.classList.add('is-glinting');
      });
    }, { rootMargin: `-${(siteHeader?.offsetHeight || 0) + 12}px 0px -8% 0px`, threshold: 0.9 });
    seals.forEach(seal => shine.observe(seal));
  }

  if (menuButton && nav) {
    const closeMenu = () => {
      nav.classList.remove('is-open');
      menuButton.setAttribute('aria-expanded', 'false');
      menuButton.setAttribute('aria-label', 'Open menu');
    };
    menuButton.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      menuButton.setAttribute('aria-expanded', String(open));
      menuButton.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && nav.classList.contains('is-open')) {
        closeMenu();
        menuButton.focus();
      }
    });
    nav.addEventListener('click', (event) => {
      if (event.target.closest('a')) closeMenu();
    });
  }
  // Subtle tap feedback on touch: brief press state for buttons, topic chips,
  // and favorite cards, so taps feel responsive on phones/tablets. The main
  // page tabs stay still while navigating between documents.
  // Skipped while motion is reduced or held.
  if (window.matchMedia('(hover: none)').matches) {
    const pressable = 'a.btn, button.btn, .page-contents a, .personal-topics a, .topic-grid a, .interest-grid > a';
    let pressed = null;
    const press = (target) => {
      if (siteMotion.reduced) return;
      const el = target?.closest ? target.closest(pressable) : target?.parentElement?.closest?.(pressable);
      const hit = el || (target?.nodeType === 3 ? target.parentElement?.closest?.(pressable) : null);
      if (hit && hit !== pressed) {
        release();
        pressed = hit;
        pressed.style.transform = 'translateY(2px)';
        pressed.style.transition = 'none';
      }
    };
    const release = () => {
      if (pressed) { pressed.style.transform = ''; pressed.style.transition = ''; pressed = null; }
    };
    document.addEventListener('touchstart', (e) => press(e.target), { passive: true });
    document.addEventListener('touchend', release, { passive: true });
    document.addEventListener('touchcancel', release, { passive: true });
  }
  const contents = document.querySelector('.page-contents');
  if (contents) {
    const links = [...contents.querySelectorAll('a[href^="#"]')];
    const sections = links.map(link => document.getElementById(link.hash.slice(1)));
    const headings = sections.map(section => section?.querySelector(':scope > h2'));
    const header = document.querySelector('.site-header');
    const currentPlaque = document.createElement('p');
    currentPlaque.className = 'contents-current';
    const currentContent = document.createElement('span');
    currentContent.className = 'contents-current-content';
    currentPlaque.append(currentContent);
    contents.prepend(currentPlaque);
    let scheduled = false;
    let lastActive = -1;
    let mobileMode = false;
    let plaqueVisible = false;
    let hashCorrectionPending = Boolean(location.hash);
    const reduceMotion = () => siteMotion.reduced;
    const syncMode = () => {
      const mobile = window.innerWidth <= 600;
      if (mobile === mobileMode) return mobile;
      mobileMode = mobile;
      plaqueVisible = false;
      delete contents.dataset.contentsVisible;
      currentPlaque.classList.remove('is-changing');
      if (mobile) {
        contents.dataset.contentsEnhanced = 'true';
        contents.setAttribute('aria-label', 'Current section');
        contents.setAttribute('aria-hidden', 'true');
        lastActive = -1;
      } else {
        delete contents.dataset.contentsEnhanced;
        contents.setAttribute('aria-label', contents.getAttribute('data-desktop-label') || 'On this page');
        contents.removeAttribute('aria-hidden');
        root.style.setProperty('--contents-height', '0px');
      }
      return mobile;
    };
    contents.setAttribute('data-desktop-label', contents.getAttribute('aria-label') || 'On this page');
    syncMode();
    const renderCurrent = (index) => {
      const link = links[index];
      if (!link) return;
      const icon = link.querySelector('svg');
      const label = document.createElement('span');
      label.textContent = link.textContent.trim();
      currentContent.replaceChildren(...(icon ? [icon.cloneNode(true), label] : [label]));
      currentPlaque.dataset.section = link.hash.slice(1);
    };
    const correctHashTarget = () => {
      if (!hashCorrectionPending || !mobileMode) return;
      hashCorrectionPending = false;
      const target = document.getElementById(location.hash.slice(1));
      if (!target) return;
      const section = target.closest('section');
      const heading = section?.querySelector(':scope > h2');
      // A section link exposes its own heading; content links leave room for the plaque.
      const atHeading = target === section || target === heading ||
        (heading && target.getBoundingClientRect().top <= heading.getBoundingClientRect().bottom);
      const plaqueHeight = atHeading ? 0 : currentPlaque.offsetHeight;
      const desiredTop = (header?.offsetHeight || 0) + plaqueHeight + 20;
      const delta = target.getBoundingClientRect().top - desiredTop;
      if (Math.abs(delta) > 1) window.scrollBy({top: delta, behavior: 'instant'});
    };
    const updateSection = () => {
      scheduled = false;
      const mobile = syncMode();
      correctHashTarget();
      const headerBottom = header ? header.getBoundingClientRect().bottom : 0;
      const threshold = mobile ? headerBottom : headerBottom + 45;
      let active = mobile ? -1 : 0;
      sections.forEach((section, index) => {
        if (section && section.getBoundingClientRect().top <= threshold) active = index;
      });
      if (!mobile && window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 3) active = links.length - 1;
      links.forEach((link, index) => {
        if (index === active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
      if (mobile) {
        const heading = headings[active];
        const nextHeading = headings[active + 1];
        const nextHeadingNearPlaque = nextHeading &&
          nextHeading.getBoundingClientRect().top < headerBottom + currentPlaque.offsetHeight + 12;
        const visible = Boolean(heading && heading.getBoundingClientRect().bottom <= headerBottom && !nextHeadingNearPlaque);
        const reveal = visible && (!plaqueVisible || active !== lastActive);
        if (active !== lastActive && active >= 0) renderCurrent(active);
        contents.toggleAttribute('data-contents-visible', visible);
        contents.setAttribute('aria-hidden', String(!visible));
        if (!visible) currentPlaque.classList.remove('is-changing');
        else if (reveal && !reduceMotion()) {
          currentPlaque.classList.remove('is-changing');
          void currentPlaque.offsetWidth;
          currentPlaque.classList.add('is-changing');
        }
        plaqueVisible = visible;
        root.style.setProperty('--contents-height', `${visible ? currentPlaque.offsetHeight : 0}px`);
      }
      lastActive = active;
    };
    const schedule = () => {
      if (!scheduled) { scheduled = true; requestAnimationFrame(updateSection); }
    };
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', () => { syncMode(); schedule(); });
    window.addEventListener('load', () => { hashCorrectionPending = Boolean(location.hash); schedule(); });
    window.addEventListener('pageshow', schedule);
    window.addEventListener('hashchange', () => { hashCorrectionPending = Boolean(location.hash); schedule(); });
    new ResizeObserver(schedule).observe(contents);
    if (header) new ResizeObserver(schedule).observe(header);
    updateSection();
  }
  // Publication drawers: the link-row buttons open the <details> below them, whose own
  // summaries are hidden once JavaScript runs. A hash link to a drawer opens it.
  const toggles = [...document.querySelectorAll('.drawer-toggle')];
  const syncToggles = (drawer) => {
    toggles.filter(t => t.getAttribute('aria-controls') === drawer.id).forEach((t) => {
      t.setAttribute('aria-expanded', String(drawer.open));
      if (t.hasAttribute('aria-label')) t.setAttribute('aria-label', drawer.open ? 'Hide BibTeX' : 'Show BibTeX');
    });
  };
  toggles.forEach((toggle) => {
    const drawer = document.getElementById(toggle.getAttribute('aria-controls'));
    if (!drawer) return;
    toggle.closest('[hidden]')?.removeAttribute('hidden');
    toggle.removeAttribute('hidden');
    toggle.addEventListener('click', () => { drawer.open = !drawer.open; });
    drawer.addEventListener('toggle', () => {
      syncToggles(drawer);
      // Fetch every figure once the drawer opens, so later slides are ready before a swipe reaches them.
      if (drawer.open) drawer.querySelectorAll('img[loading="lazy"]').forEach((img) => { img.loading = 'eager'; });
    });
  });
  document.querySelectorAll('.btn-split[hidden]').forEach(split => split.removeAttribute('hidden'));

  // Figure carousels: a scroll-snap track that also swipes without JavaScript; buttons,
  // dots, and arrow keys step through it, and the counter follows the scroll position.
  document.querySelectorAll('.figure-carousel:not(.is-single)').forEach((carousel) => {
    const track = carousel.querySelector('.carousel-track');
    const slides = [...track.children];
    const controls = carousel.querySelector('.carousel-controls');
    const dots = [...carousel.querySelectorAll('.carousel-dot')];
    const status = carousel.querySelector('.carousel-status');
    const [prev, next] = carousel.querySelectorAll('.carousel-step');
    controls.hidden = false;
    let current = 0;
    let heading = null; // The slide a smooth scroll is on its way to, so quick repeat presses keep counting.
    const sizeTrack = () => {
      const height = slides[current].getBoundingClientRect().height;
      const scrollbar = track.offsetHeight - track.clientHeight;
      if (height > 0) track.style.height = `${Math.ceil(height) + scrollbar}px`;
    };
    const show = (index) => {
      heading = Math.max(0, Math.min(slides.length - 1, index));
      const target = slides[heading];
      track.scrollTo({ left: target.offsetLeft, behavior: reduceMotion() ? 'auto' : 'smooth' });
    };
    const update = () => {
      current = Math.round(track.scrollLeft / Math.max(1, track.clientWidth));
      current = Math.max(0, Math.min(slides.length - 1, current));
      if (current === heading) heading = null;
      dots.forEach((dot, i) => dot.setAttribute('aria-current', String(i === current)));
      // Off-screen slides leave the tab order and the accessibility tree.
      slides.forEach((slide, i) => { slide.inert = i !== current; });
      sizeTrack();
      status.textContent = `${current + 1} / ${slides.length}`;
      prev.disabled = current === 0;
      next.disabled = current === slides.length - 1;
    };
    let pending = false;
    track.addEventListener('scroll', () => {
      if (!pending) { pending = true; requestAnimationFrame(() => { pending = false; update(); }); }
    }, { passive: true });
    const from = () => heading ?? current;
    prev.addEventListener('click', () => show(from() - 1));
    next.addEventListener('click', () => show(from() + 1));
    dots.forEach((dot, i) => dot.addEventListener('click', () => show(i)));
    track.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        event.preventDefault();
        show(from() + (event.key === 'ArrowRight' ? 1 : -1));
      }
    });
    // Remeasure after a drawer opens, images load, fonts settle, or the layout changes.
    const slideResize = new ResizeObserver(sizeTrack);
    slides.forEach(slide => slideResize.observe(slide));
    update();
  });
  function reduceMotion() { return siteMotion.reduced; }

  const openFromHash = () => {
    const target = location.hash && document.getElementById(location.hash.slice(1));
    if (target && target.matches('details.pub-drawer')) target.open = true;
  };
  window.addEventListener('hashchange', openFromHash);
  openFromHash();

  document.querySelectorAll('.copy-citation').forEach((button) => {
    if (button.dataset.copyBound) return;
    button.dataset.copyBound = 'true';
    button.addEventListener('click', async () => {
      const target = document.getElementById(button.dataset.copyTarget);
      if (!target) return;
      const text = target.textContent;
      try {
        await navigator.clipboard.writeText(text);
        const label = button.querySelector('.copy-label') || button;
        label.textContent = 'Copied BibTeX';
        button.classList.add('is-copied');
        window.setTimeout(() => { label.textContent = 'Copy BibTeX'; button.classList.remove('is-copied'); }, 1600);
      } catch (_) {
        target.focus();
      }
    });
  });

})();
