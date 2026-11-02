// Pixel scenes: the sky, the Home still-life, and original research companions.
// Each scene paints whole art pixels into an ImageData at art resolution, and
// CSS scales its canvas up without smoothing. One requestAnimationFrame loop
// advances every visible scene at its own low frame rate, stops a scene while
// it is off-screen or the tab is hidden, and paints a single still frame while
// motion is reduced or held (window.siteMotion, from app.js). Without
// JavaScript the page keeps the static SVG sky and the GIF still-life, so
// nothing here carries content.
(() => {
  'use strict';
  const motion = window.siteMotion;
  if (!motion || !('IntersectionObserver' in window) || !('ResizeObserver' in window)) return;
  const root = document.documentElement;
  const darkMedia = window.matchMedia('(prefers-color-scheme: dark)');
  const isDark = () => root.dataset.theme === 'dark' || (!root.dataset.theme && darkMedia.matches);

  // ---- Pixel helpers ----------------------------------------------------------
  const LITTLE = new Uint8Array(new Uint32Array([1]).buffer)[0] === 1;
  const color = (hex) => {
    const n = parseInt(hex.slice(1), 16);
    const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
    return (LITTLE ? (255 << 24) | (b << 16) | (g << 8) | r : (r << 24) | (g << 16) | (b << 8) | 255) >>> 0;
  };
  const colors = palette => Object.fromEntries(Object.entries(palette).map(([key, hex]) => [key, color(hex)]));
  // 4×4 ordered dither thresholds in (0, 1): every fade is a pattern, never a blend.
  const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map(v => (v + 0.5) / 16);
  const bayer = (x, y) => BAYER[((y & 3) << 2) | (x & 3)];
  // Repeatable noise in [0, 1) for a pair of integers: the same sky on every visit.
  const hash = (a, b = 0) => {
    let h = Math.imul(a | 0, 0x27d4eb2d) ^ Math.imul((b | 0) + 0x3c6ef372, 0x165667b1);
    h = Math.imul(h ^ (h >>> 15), 0x85ebca6b);
    h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35);
    return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
  };
  const mod = (a, n) => ((a % n) + n) % n;
  // The Konami-code celebration shares one wall clock across every visible scene.
  // It never changes content or navigation and becomes a still tableau under reduced motion.
  const PARTY_SECONDS = 9;
  let partyAt = null, partyTimer = 0;
  const partyTime = () => {
    if (partyAt === null) return null;
    const elapsed = (performance.now() - partyAt) / 1000;
    return elapsed >= 0 && elapsed < PARTY_SECONDS ? elapsed : null;
  };
  // Sprites are rows of '#' (paint) and '.' (leave).
  const sprite = rows => rows.map(row => [...row].map(cell => cell === '#'));
  const BIRD = [sprite(['#...#', '.#.#.', '..#..']), sprite(['.....', '##.##', '..#..'])];
  // A star's brightness now: 0 dim, 1 as drawn, 2 bright, 3 bright with a cross.
  const twinkle = (seed, t) => {
    const u = mod(t / (3 + 5 * hash(seed, 1)) + hash(seed, 2), 1);
    if (u < 0.04 || (u >= 0.08 && u < 0.11)) return 2;
    if (u < 0.08) return hash(seed, 3) < 0.4 ? 3 : 2;
    return u > 0.55 && u < 0.64 ? 0 : 1;
  };

  // ---- The sky behind the top of every page ------------------------------------
  // Frame units are those of assets/sky-day.svg and assets/sky-night.svg: a
  // 1440 × 640 frame centered on the page (960 × 427 on phones), drawn out to
  // -560 and 2000 so the hills taper off on wide screens; four units make one art
  // pixel. The first frame repeats the SVG, so the canvas takes over without a
  // jump; the bands behind it stay the page's own CSS gradient.
  const SKY = {
    clouds: [
      { speed: 6, rects: [[88, 40, 48, 16], [56, 56, 112, 16], [40, 72, 152, 16]] },
      { speed: 5, rects: [[1236, 92, 64, 16], [1204, 108, 144, 16], [1180, 124, 192, 16]] },
      { speed: 8, rects: [[624, 232, 40, 16], [592, 248, 112, 16]] },
      { speed: 7, rects: [[860, 176, 56, 16], [828, 192, 128, 16], [812, 208, 168, 16]] },
      { speed: 5, rects: [[-184, 136, 48, 16], [-216, 152, 112, 16]] },
      { speed: 6, rects: [[1556, 52, 56, 16], [1524, 68, 128, 16], [1508, 84, 160, 16]] },
    ],
    // Stepped ranges: [layer, base line, [from, to, top] columns], far layer first.
    hills: [
      ['far', 520, [[-192, -112, 512], [-112, -48, 504], [-48, 0, 496], [0, 32, 488], [32, 64, 464], [64, 112, 440], [112, 160, 416],
        [160, 192, 440], [192, 224, 464], [224, 272, 488]]],
      ['far', 552, [[1152, 1184, 520], [1184, 1216, 488], [1216, 1264, 456], [1264, 1296, 432], [1296, 1328, 456], [1328, 1360, 480],
        [1360, 1408, 496], [1408, 1440, 520], [1440, 1488, 528], [1488, 1552, 536], [1552, 1632, 544]]],
      ['near', 584, [[-64, 0, 576], [0, 32, 568], [32, 64, 552], [64, 128, 536], [128, 192, 520], [192, 240, 536], [240, 288, 552], [288, 384, 568]]],
      ['near', 584, [[1152, 1216, 568], [1216, 1296, 552], [1296, 1360, 536], [1360, 1392, 552], [1392, 1440, 568], [1440, 1504, 576]]],
    ],
    moon: [[120, 40, 24, 8], [112, 48, 40, 24], [120, 72, 24, 8]],
    stars: [[44, 120], [224, 52], [1232, 76], [1332, 36], [1176, 208], [1372, 276], [64, 224],
      [108, 176], [148, 316], [20, 356], [1300, 168], [1348, 332], [1412, 92],
      [-92, 64], [-236, 148], [-388, 40], [-472, 212], [-160, 300], [-520, 340],
      [1508, 140], [1596, 236], [1740, 104], [1868, 244], [1652, 324], [1960, 36]],
  };
  const SKY_COLORS = {
    day: { cloud: '#fcf8ef', far: '#e1e3d6', near: '#d8ddd3', bird: '#7a8986' },
    night: { moon: '#d8c6ac', star: '#8490ac', dim: '#4e5878', bright: '#c6cde0', glint: '#f0eadb',
      far: '#293049', near: '#232940', meteor: '#f0eadb' },
  };
  const BIRDS_EVERY = 41;    // seconds per slot; most slots send a small flock across
  const METEORS_EVERY = 21;  // seconds per slot; about half have a shooting star

  function createSky(host, canvas) {
    const narrow = window.matchMedia('(max-width: 600px)');
    let W = 0, H = 0, ox = 0, dark = false, P = null, base = null, stars = [], lanes = [];
    const clouds = SKY.clouds.map(({ speed, rects }) => {
      const from = Math.min(...rects.map(r => r[0])), to = Math.max(...rects.map(r => r[0] + r[2]));
      return { speed, rects, x: from / 4, w: (to - from) / 4 };
    });
    const rect = (out, x, y, w, h, c) => {
      const x0 = Math.max(0, x), x1 = Math.min(W, x + w), y1 = Math.min(H, y + h);
      if (x1 <= x0) return;
      for (let row = Math.max(0, y); row < y1; row++) out.fill(c, row * W + x0, row * W + x1);
    };
    const dot = (out, x, y, c) => { if (x >= 0 && x < W && y >= 0 && y < H) out[y * W + x] = c; };

    function layout() {
      if (!W || !P) return;
      base = new Uint32Array(W * H);
      for (const [layer, line, columns] of SKY.hills) {
        for (const [from, to, top] of columns) rect(base, ox + from / 4, top / 4, (to - from) / 4, (line - top) / 4, P[layer]);
      }
      if (dark) for (const [x, y, w, h] of SKY.moon) rect(base, ox + x / 4, y / 4, w / 4, h / 4, P.moon);
      stars = SKY.stars.map(([x, y], i) => ({ x: ox + x / 4, y: y / 4, seed: i }));
      // Past the drawn sky (very wide screens) a sparse field of stars carries on.
      for (let col = 0; col < W; col++) {
        const fx = col - ox;
        if (fx >= -140 && fx < 500) continue;
        for (let row = 2; row < 96; row++) if (hash(fx, row) < 0.0004) stars.push({ x: col, y: row, seed: 5000 + fx * 97 + row });
      }
    }

    // A few birds cross the sky now and then, flapping in two frames.
    function birds(out, t) {
      const slot = Math.floor(t / BIRDS_EVERY);
      for (let s = Math.max(0, slot - 2); s <= slot; s++) {
        if (hash(s, 21) > 0.7) continue;
        const dt = t - s * BIRDS_EVERY - 4 - hash(s, 22) * (BIRDS_EVERY - 8);
        const travel = Math.floor(dt * 12);
        if (dt < 0 || travel > W + 40) continue;
        const rightward = hash(s, 23) < 0.6;
        const row = 8 + Math.floor(hash(s, 24) * 40);
        const flock = hash(s, 25) < 0.5 ? 3 : 2;
        for (let b = 0; b < flock; b++) {
          const x = rightward ? travel - 8 - b * 9 : W + 3 - travel + b * 9;
          const y = row + [0, 3, -2][b] + (Math.floor(dt * 1.5 + b) % 2);
          BIRD[Math.floor(dt * 4 + b * 0.5) % 2].forEach((cells, j) => cells.forEach((on, i) => { if (on) dot(out, x + i, y + j, P.bird); }));
        }
      }
    }

    // Now and then a shooting star, preferring the open sky beside the page.
    function meteors(out, t) {
      const slot = Math.floor(t / METEORS_EVERY);
      for (let s = Math.max(0, slot - 1); s <= slot; s++) {
        if (hash(s, 31) > 0.55) continue;
        const step = Math.floor((t - s * METEORS_EVERY - 2 - hash(s, 32) * (METEORS_EVERY - 5)) * 18);
        if (step < 0 || step > 13) continue;
        const [from, to] = lanes.length ? lanes[Math.floor(hash(s, 33) * lanes.length)] : [0, W];
        const dir = hash(s, 35) < 0.5 ? -1 : 1;
        const x0 = from + Math.floor(hash(s, 34) * (to - from)) - dir * 8;
        const y0 = 3 + Math.floor(hash(s, 36) * 36);
        const fade = step > 9 ? (13 - step) / 4 : 1;
        for (let i = 0; i < 6; i++) {
          const p = Math.min(step, 9) - i;
          if (p < 0) continue;
          for (let k = 0; k < 2; k++) {
            const x = x0 + dir * (p * 2 + k), y = y0 + p;
            if (i === 0 && step <= 9) dot(out, x, y, P.meteor);
            else if (bayer(x, y) < (1 - i / 6) * fade) dot(out, x, y, i < 2 ? P.meteor : P.star);
          }
        }
      }
    }

    // A short flock or meteor parade for the secret celebration. The still mode
    // uses one arranged frame rather than playing the sequence.
    function skyParty(out, elapsed, still) {
      if (dark) {
        for (let m = 0; m < 5; m++) {
          const local = still ? 1 : elapsed - m * 0.32;
          if (local < 0 || local > 2.2) continue;
          const step = still ? 7 : Math.floor(local * 10);
          const x0 = Math.floor((m + 1) * W / 6), y0 = 5 + (m % 3) * 13;
          for (let i = 0; i < 6; i++) {
            const p = step - i;
            if (p < 0) continue;
            for (let k = 0; k < 2; k++) {
              const x = x0 - p * 2 - k, y = y0 + p;
              if (i === 0) dot(out, x, y, P.meteor);
              else if (bayer(x, y) < 1 - i / 6) dot(out, x, y, i < 2 ? P.meteor : P.star);
            }
          }
        }
      } else {
        const travel = still ? Math.floor(W * 0.55) : Math.floor(elapsed * 24);
        for (let b = 0; b < 7; b++) {
          const x = travel - b * 12, y = 10 + (b % 3) * 11;
          BIRD[(still ? b : Math.floor(elapsed * 6) + b) % 2].forEach((cells, j) => cells.forEach((on, i) => {
            if (on) dot(out, x + i, y + j, P.bird);
          }));
        }
      }
    }

    return {
      fps: 12,
      still: 0,
      fit() {
        const scale = narrow.matches ? 2 / 3 : 1;
        const px = 4 * scale;                       // CSS pixels per art pixel
        const width = host.clientWidth;
        if (!width) return null;
        const frameLeft = (width - 1440 * scale) / 2;
        ox = Math.ceil(frameLeft / px);              // the frame's first column
        const left = frameLeft - ox * px;            // in (-px, 0]
        W = Math.ceil((width - left) / px);
        H = 160;
        Object.assign(canvas.style, { left: `${left}px`, width: `${W * px}px`, height: `${H * px}px` });
        const shell = document.querySelector('.site-shell')?.getBoundingClientRect();
        lanes = shell ? [[0, Math.floor((shell.left - left) / px)], [Math.ceil((shell.right - left) / px), W]]
          .filter(([from, to]) => to - from >= 6) : [];
        layout();
        return [W, H];
      },
      theme() {
        dark = isDark();
        P = colors(SKY_COLORS[dark ? 'night' : 'day']);
        layout();
      },
      render(t, out, still) {
        out.set(base);
        const celebration = partyTime();
        if (dark) {
          for (const star of stars) {
            const level = still ? 1 : twinkle(star.seed, t);
            dot(out, star.x, star.y, [P.dim, P.star, P.bright, P.glint][level]);
            if (level === 3) {
              dot(out, star.x - 1, star.y, P.star); dot(out, star.x + 1, star.y, P.star);
              dot(out, star.x, star.y - 1, P.star); dot(out, star.x, star.y + 1, P.star);
            }
          }
          if (!still) meteors(out, t);
          if (celebration !== null) skyParty(out, celebration, still);
          return;
        }
        for (const cloud of clouds) {
          // Clouds drift right in whole art pixels and wrap around the page.
          const start = ox + cloud.x;
          const lo = Math.min(-cloud.w, start), span = Math.max(W, start + cloud.w) - lo;
          const dx = lo + mod(start - lo + Math.floor(cloud.speed * t / 4), span) - start;
          for (const [x, y, w, h] of cloud.rects) rect(out, ox + x / 4 + dx, y / 4, w / 4, h / 4, P.cloud);
        }
        if (!still) birds(out, t);
        if (celebration !== null) skyParty(out, celebration, still);
      },
      shown() { root.classList.add('sky-live'); },
    };
  }

  // ---- The Home still-life ------------------------------------------------------
  // Overlays drawn in the GIF's own pixels (512 × 341) and two-pixel art cells:
  // by day clouds and the odd bird pass behind the window glass, steam rises from
  // the coffee and dust glints in the sunbeams; by night the stars twinkle,
  // a shooting star sometimes crosses the window, and the steam is fainter. The
  // cat's tail stays the GIF's own. A still frame paints the whole picture into
  // the canvas and hides the GIF underneath.
  const CORNER = {
    size: [512, 341],
    glass: [340, 0, 472, 230],   // box searched for window glass
    beams: [108, 40, 307, 310],  // box searched for sunlit wall
    cup: [388, 192],             // foot of the left wisp, just above the rim
    // Cloud sprites in art cells; the last row is the shaded underside.
    clouds: [
      { x: 350, y: 24, speed: 1.2, cells: sprite(['.....###..........', '...#######.####...', '..##############..', '.################.', '..##############..']) },
      { x: 420, y: 84, speed: 0.8, cells: sprite(['...###......', '.#######.##.', '############', '.##########.']) },
    ],
    stars: [[432, 59], [367, 87], [388, 144], [441, 163]],
    // The four-point star's core and inner arms.
    sparkle: [[414, 112, 2, 2], [414, 111, 2, 1], [412, 112, 2, 2], [416, 112, 2, 2], [414, 114, 2, 2]],
  };
  const CORNER_COLORS = {
    day: { cloud: '#f7faff', shade: '#d6e3f7', bird: '#56637a', steam: '#ffffff', wisp: '#eef3fb', mote: '#fffaf0', catInk: '#574852' },
    night: { steam: '#8f96b8', wisp: '#5f678c', star: '#fff1d6', arm: '#66635a', dim: '#66635a', core: '#b98f79',
      meteor: '#fff1d6', tail: '#d8b394', fade: '#66635a', catInk: '#372f3c' },
  };
  const CORNER_BIRD_EVERY = 27;
  const CORNER_METEOR_EVERY = 17;

  function createCorner(figure) {
    const img = figure.querySelector('img');
    const [W, H] = CORNER.size;
    const scratch = document.createElement('canvas');
    scratch.width = W;
    scratch.height = H;
    const sctx = scratch.getContext('2d', { willReadFrequently: true });
    let base = null, glass = null, beam = null, night = false, pending = false, P = null, glassColor = 0;
    let helloAt = null, helloTimer = 0;

    const inside = (x, y) => x >= 0 && x < W && y >= 0 && y < H;
    // One art cell (2 × 2 pixels), optionally only where a mask is set.
    const cell = (out, x, y, c, mask) => {
      for (let j = 0; j < 2; j++) for (let i = 0; i < 2; i++) {
        const px = x + i, py = y + j;
        if (inside(px, py) && (!mask || mask[py * W + px])) out[py * W + px] = c;
      }
    };
    const block = (out, x, y, w, h, c) => {
      for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) if (inside(x + i, y + j)) out[(y + j) * W + x + i] = c;
    };

    function capture() {
      if (!img.complete || !img.naturalWidth) return false;
      sctx.clearRect(0, 0, W, H);
      sctx.drawImage(img, 0, 0, W, H);
      const pixels = sctx.getImageData(0, 0, W, H);
      const d = pixels.data;
      base = new Uint32Array(pixels.data.buffer.slice(0));
      night = /night/.test(img.currentSrc || img.src);
      glass = new Uint8Array(W * H);
      beam = new Uint8Array(W * H);
      const [gx0, gy0, gx1, gy1] = CORNER.glass;
      for (let y = gy0; y < gy1; y++) for (let x = gx0; x < gx1; x++) {
        const i = y * W + x, r = d[i * 4], b = d[i * 4 + 2];
        glass[i] = night ? (b > r + 30 && b < 120 && r < 50) : (b > r + 25 && b > 200);
      }
      if (!night) {
        const [bx0, by0, bx1, by1] = CORNER.beams;
        for (let y = by0; y < by1; y++) for (let x = bx0; x < bx1; x++) {
          const i = y * W + x, r = d[i * 4], b = d[i * 4 + 2];
          beam[i] = r > b + 8 && r > 200;
        }
      }
      // The night glass colour, to dim a star against.
      glassColor = base[30 * W + 400];
      P = colors(CORNER_COLORS[night ? 'night' : 'day']);
      pending = night !== isDark();
      return true;
    }

    function windowClouds(out, t) {
      for (const cloud of CORNER.clouds) {
        const width = cloud.cells[0].length * 2;
        const x = 330 - width + mod(cloud.x - 330 + width + Math.floor(cloud.speed * t) * 2, 142 + width);
        cloud.cells.forEach((row, j) => row.forEach((on, i) => {
          if (on) cell(out, x + i * 2, cloud.y + j * 2, j === cloud.cells.length - 1 ? P.shade : P.cloud, glass);
        }));
      }
    }

    function windowBird(out, t) {
      const slot = Math.floor(t / CORNER_BIRD_EVERY);
      if (slot > 0 && hash(slot, 51) > 0.65) return;   // the first slot always has one
      const dt = t - slot * CORNER_BIRD_EVERY - 3 - hash(slot, 52) * (CORNER_BIRD_EVERY - 12);
      const steps = Math.floor(dt * 10);
      if (dt < 0 || steps > 72) return;
      const x = hash(slot, 53) < 0.5 ? 472 - steps * 2 : 330 + steps * 2;
      const y = 20 + Math.floor(hash(slot, 54) * 40) * 2 + (Math.floor(dt * 2) % 2) * 2;
      BIRD[Math.floor(dt * 4) % 2].forEach((row, j) => row.forEach((on, i) => { if (on) cell(out, x + i * 2, y + j * 2, P.bird, glass); }));
    }

    // Wisps of steam rise from the cup as short wavy strokes, one cell wide, and
    // thin out into a dither as they climb.
    function steam(out, t) {
      const [cx, cy] = CORNER.cup;
      const rows = 22, stroke = 9;
      for (let w = 0; w < 3; w++) {
        const u = mod(t / 2.6 + w / 3, 1);
        const top = Math.floor(u * (rows + stroke));
        for (let j = Math.max(0, top - stroke); j <= Math.min(rows - 1, top); j++) {
          const sway = Math.round(Math.sin(j / 3.2 + w * 2.1 + t * 0.8) * Math.min(1.6, j / 5));
          const x = cx + w * 6 + sway * 2, y = cy - j * 2;
          const thin = j < rows * 0.55 ? 1 : 1 - (j - rows * 0.55) / (rows * 0.45);
          if (bayer(x >> 1, y >> 1) < thin) cell(out, x, y, j < 9 ? P.steam : P.wisp);
        }
      }
    }

    // Dust drifts up through the sunlight and glints only where the light falls.
    function motes(out, t) {
      for (let m = 0; m < 10; m++) {
        const u = mod(t / (10 + hash(m, 41) * 9) + hash(m, 42), 1);
        if (mod(t * (0.5 + hash(m, 44)) + hash(m, 45), 1) > 0.75) continue;
        const x = 112 + Math.floor(hash(m, 43) * 96) * 2 + Math.round(Math.sin(t * 0.6 + m * 1.7)) * 2;
        cell(out, x, 300 - Math.floor(u * 120) * 2, P.mote, beam);
      }
    }

    function windowStars(out, t, still) {
      CORNER.stars.forEach(([x, y], i) => {
        const level = still ? 1 : twinkle(90 + i, t);
        if (level === 1) return;
        block(out, x, y, 2, 2, level === 0 ? P.dim : P.star);
        if (level === 3) for (const [dx, dy] of [[-2, 0], [2, 0], [0, -2], [0, 2]]) block(out, x + dx, y + dy, 2, 2, P.arm);
      });
      // The four-point star breathes slowly: brighter, as drawn, then faint.
      const level = still ? 1 : twinkle(99, t * 0.6);
      if (level === 1) return;
      CORNER.sparkle.forEach(([x, y, w, h], i) => {
        const core = i === 0;
        block(out, x, y, w, h, level === 0 ? (core ? P.core : glassColor) : (core ? P.star : P.tail));
      });
    }

    function windowMeteor(out, t) {
      const slot = Math.floor(t / CORNER_METEOR_EVERY);
      if (slot > 0 && hash(slot, 61) > 0.5) return;
      const step = Math.floor((t - slot * CORNER_METEOR_EVERY - 2 - hash(slot, 62) * (CORNER_METEOR_EVERY - 5)) * 14);
      if (step < 0 || step > 13) return;
      const x0 = 452 - Math.floor(hash(slot, 63) * 20) * 2, y0 = 12 + Math.floor(hash(slot, 64) * 30) * 2;
      const fade = step > 9 ? (13 - step) / 4 : 1;
      for (let i = 0; i < 6; i++) {
        const p = Math.min(step, 9) - i;
        if (p < 0) continue;
        for (let k = 0; k < 2; k++) {
          const x = x0 - (p * 2 + k) * 2, y = y0 + p * 2;
          if (i === 0 && step <= 9) cell(out, x, y, P.meteor, glass);
          else if (bayer(x >> 1, y >> 1) < (1 - i / 6) * fade) cell(out, x, y, i < 2 ? P.tail : P.fade, glass);
        }
      }
    }

    // The cat normally faces away, so a greeting reveals one eye and a tiny
    // smile rather than redrawing the original sprite. It reads as a quick look
    // back; the GIF's own tail animation continues underneath the canvas.
    function catGreeting(out, elapsed, still) {
      if (elapsed === null || elapsed > 2.4) return;
      const blink = !still && elapsed >= 0.3 && elapsed < 0.55;
      if (blink) block(out, 352, 181, 4, 2, P.catInk);
      else block(out, 352, 180, 3, 3, P.catInk);
      if (still || elapsed >= 0.55) {
        block(out, 353, 189, 2, 2, P.catInk);
        block(out, 355, 191, 2, 2, P.catInk);
      }
      if (night && (still || elapsed < 1.4)) {
        block(out, 430, 57, 2, 6, P.star);
        block(out, 428, 59, 6, 2, P.star);
      }
    }

    function cornerParty(out, elapsed, still) {
      if (night) {
        for (let m = 0; m < 3; m++) {
          const local = still ? 1 : elapsed - m * 0.4;
          if (local < 0 || local > 1.8) continue;
          const step = still ? 6 : Math.floor(local * 9);
          for (let i = 0; i < 5; i++) {
            const p = step - i;
            if (p >= 0) cell(out, 444 - p * 4 - m * 22, 20 + m * 30 + p * 2, i < 2 ? P.meteor : P.tail, glass);
          }
        }
      } else {
        const travel = still ? 36 : Math.floor(elapsed * 24);
        for (let b = 0; b < 3; b++) {
          const x = 336 + travel - b * 16, y = 28 + b * 22;
          BIRD[(still ? b : Math.floor(elapsed * 6) + b) % 2].forEach((row, j) => row.forEach((on, i) => {
            if (on) cell(out, x + i * 2, y + j * 2, P.bird, glass);
          }));
        }
      }
    }

    const scene = {
      fps: 10,
      still: 6,
      async load() {
        if (!img.complete || !img.naturalWidth) {
          await new Promise((resolve, reject) => {
            img.addEventListener('load', resolve, { once: true });
            img.addEventListener('error', reject, { once: true });
          });
        }
        await img.decode?.().catch(() => {});
        if (!capture()) throw new Error('The still-life did not load.');
        // A theme switch swaps the GIF: take its pixels again once it arrives.
        img.addEventListener('load', () => {
          try { if (capture()) scene.redraw?.(); } catch (_) { /* keep the last frame */ }
        });
        // Fetch the other theme's picture while idle, so a switch is instant.
        const idle = window.requestIdleCallback || (callback => setTimeout(callback, 1500));
        idle(() => [figure.querySelector('source')?.getAttribute('srcset'), img.getAttribute('src')]
          .filter(Boolean).forEach((url) => { new Image().src = url; }));
      },
      fit: () => CORNER.size,
      hello() {
        helloAt = performance.now();
        scene.redraw?.();
        clearTimeout(helloTimer);
        helloTimer = setTimeout(() => scene.redraw?.(), 2450);
      },
      theme() { pending = Boolean(base) && night !== isDark(); },
      setStill(still) { figure.classList.toggle('is-still', still && Boolean(base)); },
      render(t, out, still) {
        if (still && base) out.set(base); else out.fill(0);
        if (!base || pending) return;
        if (night) {
          windowStars(out, t, still);
          if (!still) windowMeteor(out, t);
        } else {
          windowClouds(out, t);
          if (!still) windowBird(out, t);
          motes(out, t);
        }
        steam(out, t);
        const celebration = partyTime();
        const greeting = helloAt === null ? null : (performance.now() - helloAt) / 1000;
        catGreeting(out, celebration !== null ? celebration : greeting, still);
        if (celebration !== null) cornerParty(out, celebration, still);
      },
    };
    return scene;
  }

  // ---- Original research companions ------------------------------------------------
  // Compact 32 × 32 code-drawn scenes replace inline SVG fallbacks. Each card has
  // a quiet, repeating pixel loop: a layered shield, a three-way conversation,
  // and a compact book with a turning page. No character artwork or sprite
  // atlas is downloaded.
  const MINI_COLORS = {
    day: { outline: '#29434a', body: '#fff7e8', shade: '#bdd3c7', face: '#203d43', eye: '#bdd3c7', accent: '#a64a35' },
    night: { outline: '#8791aa', body: '#f0eadb', shade: '#8791aa', face: '#181d30', eye: '#e7b3a4', accent: '#e7b3a4' },
  };

  function createMiniScene(host, mode) {
    let P = null, artPalette = {}, reactAt = null;
    // The inline SVG is both the unscripted artwork and the live scene's source.
    const artwork = [...host.querySelectorAll('svg rect[data-tone]')].map(rect => ({
      x: Number(rect.getAttribute('x')), y: Number(rect.getAttribute('y')),
      w: Number(rect.getAttribute('width')), h: Number(rect.getAttribute('height')),
      tone: rect.dataset.tone, part: rect.dataset.part,
    }));
    const card = host.closest('a');
    const block = (out, x, y, w, h, c) => {
      for (let row = Math.max(0, y); row < Math.min(32, y + h); row++) {
        for (let col = Math.max(0, x); col < Math.min(32, x + w); col++) out[row * 32 + col] = c;
      }
    };
    const check = (out, x, y, c) => {
      block(out, x, y + 2, 2, 2, c); block(out, x + 2, y + 4, 2, 2, c);
      block(out, x + 4, y + 2, 2, 2, c); block(out, x + 6, y, 2, 4, c);
    };
    function shield(out, frame, still) {
      // A single art-pixel lift, held for half the two-second loop.
      const dy = !still && frame % 16 >= 8 ? -1 : 0;
      for (const r of artwork) block(out, r.x, r.y + dy, r.w, r.h, artPalette[r.tone]);
    }

    function sentinel(out, pose, frame) {
      const sleep = pose === 'sleep', dy = sleep ? 1 : 0;
      const leftUp = pose === 'celebrate', rightUp = pose === 'wave' || pose === 'celebrate';
      // Arms sit behind the stepped body and move only between discrete poses.
      if (leftUp) {
        block(out, 3, 7, 3, 10, P.outline); block(out, 1, 3, 3, 7, P.outline);
        block(out, 4, 8, 2, 8, P.body); block(out, 2, 4, 2, 6, P.body);
        block(out, 0, 2, 4, 3, P.outline);
      } else if (pose === 'confused') {
        block(out, 1, 15, 5, 3, P.outline); block(out, 2, 16, 4, 1, P.body);
      } else {
        block(out, 3, 13, 3, 9, P.outline); block(out, 4, 14, 2, 7, P.shade);
      }
      if (rightUp) {
        block(out, 25, 8, 3, 10, P.outline); block(out, 27, 4, 3, 7, P.outline);
        block(out, 26, 9, 2, 8, P.body); block(out, 28, 5, 2, 6, P.body);
        block(out, 27, 3 + (frame % 2), 4, 3, P.outline);
      } else {
        block(out, 26, 13, 3, 9, P.outline); block(out, 27, 14, 2, 7, P.shade);
      }
      block(out, 15, 1 + dy, 2, 5, P.outline); block(out, 14, dy, 4, 2, P.accent);
      block(out, 7, 6 + dy, 18, 2, P.outline); block(out, 5, 8 + dy, 22, 15, P.outline);
      block(out, 7, 23 + dy, 18, 3, P.outline); block(out, 8, 8 + dy, 16, 2, P.body);
      block(out, 7, 10 + dy, 18, 11, P.body); block(out, 9, 21 + dy, 14, 2, P.shade);
      block(out, 10, 26 + dy, 12, 2, P.outline); block(out, 11, 26 + dy, 10, 1, P.shade);
      block(out, 8, 10 + dy, 16, 8, P.face);
      if (sleep || pose === 'blink') {
        block(out, 11, 14 + dy, 3, 1, P.eye); block(out, 19, 14 + dy, 3, 1, P.eye);
      } else if (pose === 'confused') {
        block(out, 11, 13, 3, 2, P.eye); block(out, 19, 14, 3, 1, P.eye);
      } else {
        block(out, 11, 13 + dy, 3, 2, P.eye); block(out, 19, 13 + dy, 3, 2, P.eye);
      }
      block(out, 14, 21 + dy, 4, 2, pose === 'check' ? P.face : P.accent);
      if (pose === 'scan') block(out, 9 + (frame % 14), 11, 1, 6, P.accent);
      if (pose === 'check') check(out, 23, 0, P.outline);
      if (pose === 'confused') {
        block(out, 28, 1, 3, 2, P.accent); block(out, 30, 3, 2, 3, P.accent);
        block(out, 28, 6, 2, 2, P.accent); block(out, 28, 10, 2, 2, P.accent);
      }
    }

    function dialogue(out, frame, reacting, still) {
      // The three bubbles take turns lifting one art pixel; a hover or focus
      // lifts all three together. The still frame matches the SVG fallback.
      const active = still ? -1 : Math.floor((frame % 18) / 6);
      const parts = ['bubble-a', 'bubble-b', 'bubble-c'];
      for (const r of artwork) {
        const lifted = reacting || parts.indexOf(r.part) === active;
        block(out, r.x, r.y - (lifted ? 1 : 0), r.w, r.h, artPalette[r.tone]);
      }
    }

    function storybook(out, frame, still) {
      // Briefly lift the cover one pixel and expose a pale leaf beneath it.
      // The book then rests closed; no spin, shimmer or extra effects.
      const phase = frame % 24;
      const lifted = !still && phase >= 12 && phase < 18;
      for (const r of artwork) {
        const dy = lifted && r.part === 'cover' ? -1 : 0;
        block(out, r.x, r.y + dy, r.w, r.h, artPalette[r.tone]);
      }
      if (lifted) {
        block(out, 10, 21, phase < 15 ? 15 : 12, 1, artPalette.paper);
        block(out, 10, 22, 15, 1, artPalette['paper-shade']);
      }
    }

    const scene = {
      fps: 12,
      still: 0,
      fit: () => [32, 32],
      theme() {
        P = colors(MINI_COLORS[isDark() ? 'night' : 'day']);
        const style = getComputedStyle(host);
        artPalette = Object.fromEntries([...new Set(artwork.map(r => r.tone))]
          .map(tone => [tone, color(style.getPropertyValue(`--art-${tone}`).trim())]));
      },
      shown() { host.classList.add('scene-live'); },
      render(t, out, still) {
        out.fill(0);
        const celebration = partyTime();
        const elapsed = reactAt === null ? Infinity : (performance.now() - reactAt) / 1000;
        const stillReaction = Boolean(card && (card.matches(':hover') || card.contains(document.activeElement)));
        const reacting = still ? stillReaction : elapsed < 1.6;
        const frame = still ? 0 : Math.floor(t * 8);
        if (mode === 'cameo') {
          sentinel(out, 'celebrate', frame);
          return;
        }
        if (mode === 'interest-safety') {
          shield(out, frame, still);
          return;
        }
        if (mode === 'interest-inclusivity') {
          dialogue(out, frame, reacting || celebration !== null, still);
          return;
        }
        if (mode === 'interest-creativity') {
          storybook(out, frame, still);
          return;
        }
        let pose;
        if (celebration !== null) pose = 'celebrate';
        else if (reacting) pose = still ? 'check' : elapsed < 0.45 ? 'wave' : elapsed < 1.05 ? 'scan' : 'check';
        else if (mode === 'sentinel-404') pose = 'confused';
        else if (isDark()) pose = 'sleep';
        else {
          const slot = Math.floor(t / 9), blinkAt = 2 + hash(slot, 82) * 5;
          pose = t - slot * 9 > blinkAt && t - slot * 9 < blinkAt + 0.25 ? 'blink' : 'idle';
        }
        sentinel(out, pose, frame);
      },
    };
    if (card) {
      const react = () => { reactAt = performance.now(); scene.redraw?.(); };
      const still = () => { if (motion.reduced) scene.redraw?.(); };
      card.addEventListener('pointerenter', react);
      card.addEventListener('focusin', react);
      card.addEventListener('pointerleave', still);
      card.addEventListener('focusout', still);
    }
    return scene;
  }

  // ---- One loop for every scene ---------------------------------------------------
  const items = [];
  let raf = 0;

  function draw(item) {
    if (!item.data) return;
    const still = motion.reduced;
    item.scene.render(still ? item.scene.still : item.t, item.data, still);
    item.ctx.putImageData(item.image, 0, 0);
  }

  function fit(item) {
    const size = item.scene.fit();
    if (!size) return false;
    const [w, h] = size;
    if (w !== item.w || h !== item.h) {
      Object.assign(item, { w, h });
      item.canvas.width = w;
      item.canvas.height = h;
      item.image = item.ctx.createImageData(w, h);
      item.data = new Uint32Array(item.image.data.buffer);
    }
    item.frame = -1;
    return true;
  }

  function loop(now) {
    raf = 0;
    let any = false;
    for (const item of items) {
      if (!item.running) continue;
      any = true;
      if (item.last !== null) item.t += Math.min(0.1, (now - item.last) / 1000);
      item.last = now;
      const frame = Math.floor(item.t * item.scene.fps);
      if (frame !== item.frame) { item.frame = frame; draw(item); }
    }
    if (any) raf = requestAnimationFrame(loop);
  }

  function sync() {
    const still = motion.reduced;
    let any = false;
    for (const item of items) {
      if (!item.ready) continue;
      const run = !still && item.visible && !document.hidden;
      if (run !== item.running) { item.running = run; item.last = null; }
      const mode = still ? 'still' : run ? 'live' : 'paused';
      if (mode !== item.mode) {
        item.mode = mode;
        item.scene.setStill?.(still);
        if (mode !== 'live') draw(item);
      }
      any = any || run;
    }
    if (any && !raf) raf = requestAnimationFrame(loop);
    else if (!any && raf) { cancelAnimationFrame(raf); raf = 0; }
  }

  const io = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      const item = items.find(it => it.node === entry.target);
      if (item) item.visible = entry.isIntersecting;
    }
    sync();
  });
  let resizing = 0;
  const ro = new ResizeObserver(() => {
    cancelAnimationFrame(resizing);
    resizing = requestAnimationFrame(() => {
      items.forEach((item) => { if (item.ready && fit(item)) draw(item); });
      sync();
    });
  });

  function add(node, canvas, scene) {
    canvas.setAttribute('aria-hidden', 'true');
    const item = { node, canvas, ctx: canvas.getContext('2d'), scene, t: 0, last: null, frame: -1,
      visible: false, running: false, mode: null, ready: false, w: 0, h: 0, image: null, data: null };
    items.push(item);
    scene.redraw = () => { if (item.ready) { item.scene.setStill?.(motion.reduced); draw(item); } };
    Promise.resolve(scene.load?.()).then(() => {
      item.ready = true;
      scene.theme();
      if (!fit(item)) return;
      scene.setStill?.(motion.reduced);
      draw(item);
      scene.shown?.();
      io.observe(node);
      ro.observe(node);
      sync();
    }).catch(() => {
      // Fall back to the static sky or the GIF, whichever the scene replaced.
      canvas.remove();
      node.classList.remove('is-still', 'scene-live');
      items.splice(items.indexOf(item), 1);
    });
    return item;
  }

  // Palettes follow the theme, whether chosen on the page or by the system.
  const retheme = () => items.forEach((item) => { if (item.ready) { item.scene.theme(); draw(item); } });
  new MutationObserver(retheme).observe(root, { attributes: true, attributeFilter: ['data-theme'] });
  darkMedia.addEventListener?.('change', () => { if (!root.dataset.theme) retheme(); });
  document.addEventListener('visibilitychange', sync);
  motion.subscribe(sync);

  const skyHost = document.createElement('div');
  skyHost.className = 'pixel-sky';
  skyHost.setAttribute('aria-hidden', 'true');
  const skyCanvas = document.createElement('canvas');
  skyHost.append(skyCanvas);
  document.body.prepend(skyHost);
  add(skyHost, skyCanvas, createSky(skyHost, skyCanvas));

  const corner = document.querySelector('[data-scene="reading-corner"]');
  if (corner?.querySelector('img')) {
    const scene = createCorner(corner);
    const picture = corner.querySelector('.study-picture');
    const hello = document.createElement('button');
    hello.className = 'cat-hello';
    hello.type = 'button';
    hello.setAttribute('aria-label', 'Say hello to the cat');
    hello.title = 'Say hello to the cat';
    corner.insertBefore(hello, picture);
    hello.append(picture);
    hello.addEventListener('click', () => scene.hello());
    const canvas = document.createElement('canvas');
    canvas.className = 'scene-canvas';
    corner.append(canvas);
    add(corner, canvas, scene);
  }

  document.querySelectorAll('.interest-scene[data-scene],.not-found-companion[data-scene]').forEach((host) => {
    const canvas = document.createElement('canvas');
    canvas.className = 'scene-canvas';
    host.append(canvas);
    add(host, canvas, createMiniScene(host, host.dataset.scene));
  });

  // A single framed cameo travels to the Copy BibTeX button only after success.
  if (document.querySelector('.copy-citation')) {
    const host = document.createElement('div');
    host.className = 'companion-cameo';
    host.hidden = true;
    host.setAttribute('aria-hidden', 'true');
    const canvas = document.createElement('canvas');
    canvas.className = 'scene-canvas';
    host.append(canvas);
    document.body.append(host);
    const item = add(host, canvas, createMiniScene(host, 'cameo'));
    let timer = 0;
    document.addEventListener('site:celebrate', (event) => {
      const anchor = event.detail?.anchor;
      if (!anchor || !item.ready) return;
      const rect = anchor.getBoundingClientRect();
      const headerBottom = document.querySelector('.site-header')?.getBoundingClientRect().bottom || 0;
      const left = Math.max(8, Math.min(window.innerWidth - 76, rect.left + rect.width / 2 - 34));
      let top = rect.top - 78;
      if (top < headerBottom + 8) top = rect.bottom + 10;
      top = Math.max(8, Math.min(window.innerHeight - 78, top));
      Object.assign(host.style, { left: `${Math.round(left)}px`, top: `${Math.round(top)}px` });
      host.hidden = false;
      item.visible = true; item.t = 0; item.last = null; item.frame = -1;
      fit(item); draw(item); sync();
      clearTimeout(timer);
      timer = setTimeout(() => { host.hidden = true; item.visible = false; sync(); }, 1800);
    });
  }

  function startParty() {
    partyAt = performance.now();
    items.forEach((item) => { if (item.ready) draw(item); });
    sync();
    clearTimeout(partyTimer);
    partyTimer = setTimeout(() => {
      partyAt = null;
      items.forEach((item) => { if (item.ready) draw(item); });
    }, PARTY_SECONDS * 1000);
  }
  const konami = ['arrowup', 'arrowup', 'arrowdown', 'arrowdown', 'arrowleft', 'arrowright', 'arrowleft', 'arrowright', 'b', 'a'];
  let entered = [];
  document.addEventListener('keydown', (event) => {
    if (event.ctrlKey || event.metaKey || event.altKey || event.target.closest?.('input,textarea,select,[contenteditable]')) return;
    entered.push(event.key.toLowerCase());
    entered = entered.slice(-konami.length);
    if (entered.every((key, index) => key === konami[index])) {
      entered = [];
      startParty();
    }
  });
})();
