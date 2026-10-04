(() => {
  const root = document.documentElement;
  root.classList.add('js');
  const themeButton = document.querySelector('.theme-toggle');
  const menuButton = document.querySelector('.nav-burger');
  const nav = document.querySelector('.site-header nav');

  try {
    const savedTheme = localStorage.getItem('tariq-theme');
    if (savedTheme === 'dark' || savedTheme === 'light') root.dataset.theme = savedTheme;
  } catch (_) { /* Reading controls still work when storage is unavailable. */ }

  if (themeButton) {
    const SUN = '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.8v2.4M12 18.8v2.4M4.2 4.2l1.7 1.7M18.1 18.1l1.7 1.7M2.8 12h2.4M18.8 12h2.4M4.2 19.8l1.7-1.7M18.1 5.9l1.7-1.7"/></svg>';
    const MOON = '<svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" aria-hidden="true"><path d="M20.6 14.5A8.6 8.6 0 0 1 9.5 3.4a.7.7 0 0 0-.9-.9A10 10 0 1 0 21.5 15.4a.7.7 0 0 0-.9-.9Z"/></svg>';
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const effectiveDark = () => root.dataset.theme === 'dark' || (!root.dataset.theme && media.matches);
    const updateThemeLabel = () => {
      const dark = effectiveDark();
      themeButton.innerHTML = dark ? SUN : MOON;
      themeButton.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
      themeButton.title = dark ? 'Switch to light theme' : 'Switch to dark theme';
    };
    media.addEventListener?.('change', () => { if (!root.dataset.theme) updateThemeLabel(); });
    updateThemeLabel();
    themeButton.addEventListener('click', () => {
      root.dataset.theme = effectiveDark() ? 'light' : 'dark';
      try { localStorage.setItem('tariq-theme', root.dataset.theme); } catch (_) {}
      updateThemeLabel();
    });
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
  // Subtle tap feedback on touch: brief press state for nav links, buttons,
  // topic chips, and favorite cards, so taps feel responsive on phones/tablets.
  // Skipped when reduced motion is preferred.
  if (window.matchMedia('(hover: none)').matches && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const pressable = 'a.btn, button.btn, .site-header nav a, .page-contents a, .personal-topics a, .topic-grid a, .interest-grid > a';
    let pressed = null;
    const press = (target) => {
      const el = target?.closest ? target.closest(pressable) : target?.parentElement?.closest?.(pressable);
      const hit = el || (target?.nodeType === 3 ? target.parentElement?.closest?.(pressable) : null);
      if (hit && hit !== pressed) {
        release();
        pressed = hit;
        pressed.style.transform = 'scale(.97)';
        pressed.style.transition = 'transform .15s ease';
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
    const header = document.querySelector('.site-header');
    let scheduled = false;
    let lastActive = -1;
    const updateContentsEdges = () => {
      const horizontal = window.innerWidth <= 600 && contents.scrollWidth > contents.clientWidth;
      contents.toggleAttribute('data-overflow-start', horizontal && contents.scrollLeft > 1);
      contents.toggleAttribute('data-overflow-end', horizontal && contents.scrollLeft + contents.clientWidth < contents.scrollWidth - 1);
    };
    const updateSection = () => {
      scheduled = false;
      const stickyHeight = getComputedStyle(contents).position === 'sticky' && window.innerWidth <= 600 ? contents.offsetHeight : 0;
      root.style.setProperty('--contents-height', `${stickyHeight}px`);
      const threshold = header.getBoundingClientRect().bottom + stickyHeight + 45;
      let active = 0;
      sections.forEach((section, index) => {
        if (section && section.getBoundingClientRect().top <= threshold) active = index;
      });
      if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 3) active = links.length - 1;
      links.forEach((link, index) => {
        if (index === active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
      // On phones the paper-page contents is one swipeable row; keep the active link in view.
      if (active !== lastActive && contents.scrollWidth > contents.clientWidth) {
        contents.scrollLeft += links[active].getBoundingClientRect().left - contents.getBoundingClientRect().left - 16;
      }
      lastActive = active;
      updateContentsEdges();
    };
    const schedule = () => {
      if (!scheduled) { scheduled = true; requestAnimationFrame(updateSection); }
    };
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);
    window.addEventListener('load', schedule);
    contents.addEventListener('scroll', updateContentsEdges, { passive: true });
    new ResizeObserver(schedule).observe(contents);
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
    update();
  });
  function reduceMotion() { return window.matchMedia('(prefers-reduced-motion: reduce)').matches; }

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
