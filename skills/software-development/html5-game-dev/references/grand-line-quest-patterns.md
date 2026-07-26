# Grand Line Quest — Architecture Reference

Source: [solankianandwork-zorro/grand-line-quest](https://github.com/solankianandwork-zorro/grand-line-quest) (3117 lines, single HTML file)

## Architecture

- Pure Canvas2D (no p5.js, no dependencies)
- HTML overlays for title/win/lose screens (not canvas-drawn)
- Fixed 60Hz game loop: `requestAnimationFrame` + accumulator pattern
- Web Audio API for all sounds (procedural, no files)

## Key Code Patterns

### Fixed Timestep Loop
```javascript
let last = performance.now(), acc = 0;
const STEP = 1000 / 60;
function frame(now) {
  acc += now - last; last = now;
  if (acc > 200) acc = 200; // cap to prevent spiral
  while (acc >= STEP) { update(); acc -= STEP; }
  draw();
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
```

### Procedural Pixel Art Characters
Characters drawn with canvas primitives (fillRect, arc, beginPath/closePath). No spritesheets needed. Example from grand-line-quest:
```javascript
function drawPlayer() {
  // Shadow
  ctx.fillStyle = 'rgba(0,0,0,.2)';
  ctx.beginPath(); ctx.ellipse(x+p.w/2, GROUNDY, p.w*0.7, 4, 0, 0, 7); ctx.fill();
  // Legs (running bob)
  const run = (keys['a']||keys['d']) && p.onGround;
  const lb = run ? Math.sin(p.animT/4)*4 : 0;
  ctx.fillStyle='#1f6fb0';
  ctx.fillRect(x+5, y+30, 8, 16+lb);
  ctx.fillRect(x+p.w-13, y+30, 8, 16-lb);
  // Body
  ctx.fillStyle='#d6342b'; rr(x+3,y+12,p.w-6,18,3);
  // Head
  ctx.fillStyle='#f0c79a'; ctx.beginPath(); ctx.arc(x+p.w/2,y+8,9,0,7); ctx.fill();
  // Hair
  ctx.fillStyle='#15110f'; ctx.beginPath(); ctx.arc(x+p.w/2,y+12,15,Math.PI,0); ctx.fill();
}
```

### Parallax Background Layers
Multiple layers at different scroll speeds:
- Far mountains: `camX * 0.15`
- Mid trees: `camX * 0.3`
- Near ground: `camX * 0.6`
- Torii gate/landmarks: `camX * 0.25`

### Boss AI State Machine
```javascript
// Bosses have states: idle, walk, attack1, attack2, hurt, dying
// Each state has duration and transitions
if (boss.state === 'hook' && boss.t > 46) {
  // Wind-up tell: show danger zone
  ctx.strokeStyle='rgba(255,210,63,.5)';
  ctx.beginPath(); ctx.arc(x+b.w/2, y+b.h/2, b.w*0.9, 0, 7); ctx.stroke();
}
```

### HUD Pattern
Canvas-drawn HUD with:
- Health bar with background + foreground + border
- Score and lives display
- Status badges (e.g. "DRY! Find water →")
- Objective hints at bottom

### Screen Shake
```javascript
if (shake > 0) shake *= 0.85;
if (shake < 0.5) shake = 0;
// In draw:
const sx = shake ? rnd(-shake, shake) : 0;
const sy = shake ? rnd(-shake, shake) : 0;
ctx.translate(sx, sy);
```

### Floating Damage Numbers
```javascript
function spawnFloater(x, y, text, col) {
  floaters.push({ x, y, t: 40, text, col: col || '#fff' });
}
// Update: float up, fade out
f.y -= 0.8; f.t--;
// Draw: alpha based on remaining life
ctx.globalAlpha = clamp(f.t / 40, 0, 1);
```

## What Makes It Work

1. **HTML overlays for menus** — cleaner than canvas-drawn menus, easier to style, naturally tappable
2. **No dependencies** — loads instantly, works offline, no CDN failures
3. **Procedural characters** — unique art style without external assets
4. **Procedural audio** — no audio files to load or fail
5. **Fixed timestep** — deterministic physics regardless of frame rate
6. **Camera lerp** — smooth following without jerky snaps
7. **Juice** — particles, screen shake, floating numbers, flash on hit
