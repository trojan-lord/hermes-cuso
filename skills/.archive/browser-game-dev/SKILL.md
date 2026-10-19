---
name: browser-game-dev
description: Build single-file HTML5 browser games with Canvas2D. Covers game loop architecture, touch controls, collision, procedural sprites, and the test-fix cycle.
version: 1.0.0
author: Hermes Agent
tags: [html, canvas, game, browser, touch, single-file, procedural]
related_skills: [claude-design, static-site-dev]
---

# Browser Game Development

Build complete, playable single-file HTML5 browser games using Canvas2D.

Use this skill when the task involves:
- Creating browser-based games (platformers, action, puzzle, etc.)
- Adding touch/mobile controls to a canvas game
- Building game loops, collision systems, or sprite rendering
- Iterating on game features (enemies, bosses, combos, etc.)
- Deploying a game via GitHub Pages or local HTTP server

Do NOT use this skill for:
- Design artifacts (landing pages, prototypes) — use `claude-design`
- Multi-file game projects with build tools — use `software-development/*`
- Non-game interactive apps — use `claude-design`

## Architecture: Single-File Canvas2D Game

```
┌─────────────────────────────────────┐
│ HTML                                │
│  ├─ <style> (all CSS inline)        │
│  ├─ <canvas> (game viewport)        │
│  ├─ <div> overlays (title/win/lose) │
│  ├─ <div> touch layer (controls)    │
│  └─ <script> (all game logic)       │
└─────────────────────────────────────┘
```

### Fixed Timestep Game Loop

Always use a fixed timestep accumulator with `requestAnimationFrame`. Never use variable-dt.

```js
var last = performance.now(), acc = 0, STEP = 1000/60;
function frame(now) {
  acc += now - last; last = now;
  if (acc > 200) acc = 200;  // spiral of death guard
  while (acc >= STEP) { update(); acc -= STEP; }
  draw();
  requestAnimationFrame(frame);
}
```

### State Machine

```
title → play → pause (toggle)
            ↘ win → (restart) → play
            ↘ lose → (restart) → play
```

Use a `gState` variable. Only call `update()` when `gState === 'play'`.

## CRITICAL: Touch Controls Architecture

This is the #1 source of bugs in mobile browser games. Get it wrong and the game is unplayable on tablets/phones.

### The Problem

Canvas `touchstart` events with `preventDefault()` swallow ALL touch input. If your d-pad buttons are children of the canvas, or if the canvas sits on top of them, taps never reach the buttons.

### The Solution: Separate DOM Overlay

Touch controls MUST be in a separate `<div>` overlay, NOT inside the canvas:

```html
<div id="wrap">
  <canvas id="game" width="800" height="480"></canvas>
  <!-- Touch layer: ABOVE canvas in z-index, separate DOM tree -->
  <div id="touchLayer" style="position:absolute;inset:0;z-index:20;pointer-events:none;display:none">
    <div id="bL" class="tb">◀</div>      <!-- left -->
    <div id="bR" class="tb">▶</div>      <!-- right -->
    <div id="bJ" class="tb">JUMP</div>   <!-- jump -->
    <div id="bA" class="tb">ATK</div>    <!-- attack -->
    <div id="bS" class="tb">SP</div>     <!-- special -->
    <div id="bP" class="tb">❚❚</div>     <!-- pause -->
  </div>
</div>
```

```css
/* Show only on touch devices */
@media(hover:none) and (pointer:coarse) {
  #touchLayer { display: block; }
}

.tb {
  position: absolute;
  pointer-events: auto;  /* CRITICAL: parent is pointer-events:none */
  border-radius: 10px;
  touch-action: manipulation;  /* prevents zoom/double-tap delay */
  -webkit-user-select: none;
  user-select: none;
}
```

### Multi-Touch Input Handling

Each button gets independent touch handlers. DO NOT use a single touch listener on the wrapper.

```js
function bindTouch(id, key, onFn) {
  var el = document.getElementById(id);
  if (!el) return;
  function onStart(e) {
    e.preventDefault();
    e.stopPropagation();
    tch[key] = true;
    el.classList.add('on');
    if (onFn) onFn();  // fire action on press (jump, attack)
  }
  function onEnd(e) {
    e.preventDefault();
    e.stopPropagation();
    tch[key] = false;
    el.classList.remove('on');
  }
  el.addEventListener('touchstart', onStart, {passive: false});
  el.addEventListener('touchend', onEnd, {passive: false});
  el.addEventListener('touchcancel', onEnd);
  el.addEventListener('mousedown', onStart);  // desktop fallback
  el.addEventListener('mouseup', onEnd);
  el.addEventListener('mouseleave', onEnd);
}
```

Input state object (read by game update):
```js
var tch = {left: false, right: false, jump: false, attack: false, special: false};

function isLeft() { return keys['a'] || keys['arrowleft'] || tch.left; }
function isRight() { return keys['d'] || keys['arrowright'] || tch.right; }
```

### Touch Button Sizing

Minimum 20% screen width for movement buttons. On a 800px canvas scaled to iPad:
- D-pad buttons: 22% width, 28% height
- Action buttons: 22% width, 22% height
- Pause button: 40px × 36px (smaller, top-right)

### Touch Layer CSS Requirements

```css
#wrap {
  position: relative;
  overflow: hidden;
  width: min(800px, 100vw);
  aspect-ratio: 800/480;
}

#touchLayer {
  position: absolute;
  inset: 0;
  z-index: 20;     /* ABOVE canvas (z-index 0) and overlays (z-index 30 only when visible) */
  pointer-events: none;  /* lets clicks pass through to canvas */
  display: none;
}

.tb {
  pointer-events: auto;  /* each button captures its own touches */
}
```

## JS Validation Pattern

Before opening in a browser, always validate syntax:

```bash
# 1. Extract script from HTML
python3 -c "
import re
with open('index.html') as f: content = f.read()
m = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
if m:
    with open('/tmp/game_check.js', 'w') as f: f.write(m.group(1))
    print(f'Script: {len(m.group(1))} chars')
"

# 2. Check syntax
node --check /tmp/game_check.js 2>&1 && echo "SYNTAX OK"
```

**NEVER write minified single-line JS.** When debugging syntax errors, minified code is nearly impossible to trace. Always use readable multi-line code with proper indentation.

If you find yourself searching for an "Unexpected token" error in minified code, STOP and rewrite the affected section with proper line breaks. It's faster than debugging minified code.

## Procedural Pixel Art

For games that need characters/sprites without external assets, draw everything with Canvas2D primitives:

```js
// Character sprite composed from rectangles and arcs
function drawPlayer(p, x, y) {
  // Shadow
  ctx.fillStyle = 'rgba(0,0,0,.25)';
  ctx.beginPath(); ctx.ellipse(x+p.w/2, GROUND, p.w*0.7, 4, 0, 0, 7); ctx.fill();
  // Body
  ctx.fillStyle = '#e8e8e0'; ctx.fillRect(x+4, y+10, p.w-8, 16);
  // Head
  ctx.fillStyle = '#d4c4a0'; ctx.beginPath(); ctx.arc(x+p.w/2, y+6, 8, 0, 7); ctx.fill();
  // Hair
  ctx.fillStyle = '#c0392b';
  ctx.beginPath(); ctx.arc(x+p.w/2, y+2, 9, Math.PI, 0); ctx.fill();
}
```

### Procedural Audio (WebAudio)

Generate all sounds with oscillators and noise buffers. No external audio files.

```js
var Snd = (function() {
  var ac = null, master = null, muted = false;
  function ens() {
    if (ac) return;
    try {
      var A = window.AudioContext || window.webkitAudioContext;
      ac = new A();
      master = ac.createGain();
      master.gain.value = 0.35;
      master.connect(ac.destination);
    } catch(e) { ac = null; }
  }
  function tone(f, d, o) {
    if (!ac || muted) return;
    var t = ac.currentTime;
    var osc = ac.createOscillator();
    var g = ac.createGain();
    osc.type = o.type || 'square';
    osc.frequency.setValueAtTime(f, t);
    if (o.s) osc.frequency.exponentialRampToValueAtTime(Math.max(20, o.s), t + d);
    g.gain.setValueAtTime(0.001, t);
    g.gain.exponentialRampToValueAtTime(o.g || 0.12, t + 0.01);
    g.gain.exponentialRampToValueAtTime(0.001, t + d);
    osc.connect(g); g.connect(master);
    osc.start(t); osc.stop(t + d + 0.02);
  }
  // Add noise() for slash/hit sounds
  return { init: ens, jump: function() { tone(440, 0.1, {type:'square',g:0.1,s:880}); }, /* ... */ };
})();
```

## Game Feel Techniques

- **Hit freeze**: 2-3 frame pause on attack impact (set `hitFreeze` counter, return early from update)
- **Screen shake**: `shake` variable, translate canvas by random offset, decay by 0.85 per frame
- **Floating damage numbers**: `floaters[]` array, draw with alpha fading
- **Particles**: `particles[]` with position, velocity, gravity, color, lifetime
- **Combo counter**: increment on hit, decay timer, score multiplier at thresholds

## Enemy Spawning Algorithms

### CRITICAL: Don't Spawn Relative to Player Near World Edge

Spawning enemies at `player.x + randomOffset * direction` causes all enemies to stack on the same clamp point when the player is near the world edge.

**BROKEN** (all enemies stack at x=50):
```js
// Player at x=120, offset=300-900, 50% go negative → clamped to 50
var x = player.x + rnd(300,900) * (Math.random()<0.5?1:-1);
enemies.push(mkEnemy(type, clamp(x, 50, WW-100)));
// Result: 45% of enemies end up at x=50, stacked on top of each other
```

**FIXED** (enemies spread ahead of player):
```js
// Always spawn in front of the player, spread across a range
var spawnRight = player.x < WW * 0.4;
var baseX = spawnRight
  ? Math.max(player.x + rnd(300,600), W * 0.6)
  : player.x - rnd(300,600);
baseX = clamp(baseX, 50, WW-100);

for (var i = 0; i < n; i++) {
  var type = pickEnemyType(wave);
  var x = baseX + i * rnd(40,80) + rnd(-20,20);  // spread apart
  enemies.push(mkEnemy(type, clamp(x, 50, WW-100)));
}
```

**Same bug in boss spawning:**
```js
// BROKEN: boss can spawn behind player → walks offscreen or stacks
boss = mkBoss(player.x + rnd(300,500) * (Math.random()<0.5?1:-1));

// FIXED: always spawn ahead
var dir = player.x > WW * 0.5 ? -1 : 1;
boss = mkBoss(clamp(player.x + dir * rnd(200,400), 200, WW-200));
```

### Spawn Spread Pattern

For n enemies, offset each by `i * spacing + jitter`:
- Spacing: 40-80px (prevents overlap)
- Jitter: ±20px (looks natural)
- This ensures visual separation even with similar enemy types

See `references/spawn-algorithms.md` for more patterns.

## Iterative Development Pattern

1. **Build minimum playable** — move, jump, attack, one enemy type, one wave
2. **Verify in desktop browser first** — check JS loads, game renders, controls work
3. **Push to GitHub Pages** — user tests on target device (iPad)
4. **User reports what's broken** — usually touch controls, then missing features
5. **Fix critical bugs first** — touch/input issues are always P0
6. **Add features in priority order** — boss fights, enemy variety, pickups, HUD
7. **Repeat from step 2**

### BEFORE Deploy: Verify Locally

Every time. No exceptions. The user is playing on their iPad — if it doesn't work, they'll tell you, and "bullshit" is the polite version.

Checklist before `git push`:
1. JS syntax: `node --check` (extract script from HTML first)
2. Browser: open localhost, click start, move, attack, verify enemies spawn
3. Console: check for zero errors after 5+ seconds of gameplay
4. Touch layer: verify all 6 buttons exist and are positioned correctly

### GitHub Pages Deployment

```bash
cd ~/project-name
git add -A && git commit -m "feat: description"
git push
# Pages auto-deploys from main branch
# Live at: https://trojan-lord.github.io/<repo-name>/
```

**Build not triggering?** GitHub Pages sometimes doesn't auto-build on push. Fix:
```bash
# Option 1: touch .nojekyll and push
touch .nojekyll && git add .nojekyll && git commit -m "chore: rebuild pages" && git push

# Option 2: check build status
gh api repos/OWNER/REPO/pages/builds/latest --jq '{commit:.commit, status:.status}'
```

Local testing while iterating:
```bash
cd ~/project-name && python3 -m http.server 8080 &
```

## Pitfalls

- **Canvas touchstart eating all input** — canvas with `touchstart` + `preventDefault()` swallows touches meant for overlay buttons. Fix: separate DOM layer (see Touch Controls above).
- **Minified JS makes debugging impossible** — "Unexpected token" in minified code is untraceable. Always write readable multi-line code.
- **Missing semicolon after object literal method** — `method(){...};` (trailing semicolon after closing `}`) causes "Unexpected token" errors. The semicolon after an object method's `}` is invalid syntax.
- **Optional chaining (`?.`) not working** — older browsers/Safari versions may not support `?.`. Use explicit null checks: `var el = document.getElementById('x'); if (el) el.addEventListener(...)`.
- **`overflow:hidden` clipping touch buttons** — if `#wrap` has `overflow:hidden` and buttons extend beyond its bounds, they're invisible/untappable. Position buttons with `bottom:0` relative to the wrapper.
- **Touch events needing `{passive:false}`** — without this, `preventDefault()` in touch handlers is ignored on Chrome/Safari, causing scroll/zoom behavior during gameplay.
- **Game loop drawing during title/pause** — only call full `draw()` during `play` state. During `title`/`pause`, draw just the background or the overlay divs handle it.
- **Enemy spawn stacking near world edges** — spawning with `player.x + offset * randomDir` causes 50% of spawns to clamp to the same position when player is near the left/right edge. Always spawn AHEAD of the player and spread with `baseX + i * spacing`.
