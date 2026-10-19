# Game Architecture Patterns for HTML5/p5.js

Research from analyzing humancto/legacy-games, KosMaster87/El-pollo-loco, and EnginKARATAS/platform-advanced. Synthesized for single-file p5.js side-scrollers and platformers.

---

## Fixed Timestep Game Loop

p5.js `draw()` runs at monitor refresh rate (60-144Hz+). For deterministic physics, use an accumulator with fixed dt. This decouples physics from render rate.

**Pattern:** `references/game-architecture.md` § Fixed Timestep

```javascript
const FIXED_DT = 1 / 60;
let accumulator = 0;
let lastTime = 0;

function draw() {
  const now = performance.now() / 1000;
  const rawDt = now - lastTime;
  lastTime = now;
  accumulator += Math.min(rawDt, 0.1); // cap prevents spiral of death

  while (accumulator >= FIXED_DT) {
    gameState.update(FIXED_DT);
    accumulator -= FIXED_DT;
  }

  const alpha = accumulator / FIXED_DT;
  gameState.render(alpha); // interpolation between physics ticks
}
```

Source: legacy-games/engine.js

---

## Separated X/Y Collision Resolution

**Critical for tile-based games.** Moving both axes then resolving all overlaps causes corner-cutting. Move X → resolve X → move Y → resolve Y.

```javascript
function resolvePlayerTilemap(player, tilemap, dt) {
  player.x += player.vx * dt;
  resolveAxisX(player, tilemap);
  player.y += player.vy * dt;
  resolveAxisY(player, tilemap);
}

function resolveAxisX(entity, tilemap) {
  const tiles = tilemap.getOverlappingTiles(entity);
  for (const tile of tiles) {
    if (!tile.solid) continue;
    if (entity.vx > 0) entity.x = tile.left - entity.w;
    else if (entity.vx < 0) entity.x = tile.right;
  }
}

function resolveAxisY(entity, tilemap) {
  entity.onGround = false;
  const tiles = tilemap.getOverlappingTiles(entity);
  for (const tile of tiles) {
    if (!tile.solid) continue;
    if (entity.vy > 0) { entity.y = tile.top - entity.h; entity.onGround = true; }
    else if (entity.vy < 0) entity.y = tile.bottom;
    entity.vy = 0;
  }
}
```

Source: legacy-games/grotto-escape/game.js

---

## Frame-Based Input System

`keyIsDown()` tells current state. You also need `justPressed` for one-shot actions (jump, attack, pause). Clear per-frame with `endFrame()`.

```javascript
class Input {
  constructor() {
    this.keys = {};
    this.justPressed = {};
    this.justReleased = {};
    window.addEventListener('keydown', e => {
      if (!this.keys[e.code]) this.justPressed[e.code] = true;
      this.keys[e.code] = true;
      if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)) e.preventDefault();
    });
    window.addEventListener('keyup', e => {
      this.keys[e.code] = false;
      this.justReleased[e.code] = true;
    });
  }
  isDown(code) { return !!this.keys[code]; }
  pressed(code) { return !!this.justPressed[code]; }
  get left() { return this.isDown('ArrowLeft') || this.isDown('KeyA'); }
  get right() { return this.isDown('ArrowRight') || this.isDown('KeyD'); }
  get jump() { return this.pressed('Space') || this.pressed('KeyW'); }
  get attack() { return this.pressed('KeyZ') || this.pressed('KeyJ'); }
  endFrame() { this.justPressed = {}; this.justReleased = {}; }
}
```

In p5.js: feed Input from `keyPressed()`/`keyReleased()` p5 hooks, or use window event listeners (shown above). The Input class lives outside p5.

Source: legacy-games/input.js

---

## State Machine

For game states (menu, playing, paused, gameOver) and entity states (idle, walk, attack, hurt, dead).

```javascript
class StateMachine {
  constructor() { this.states = {}; this.current = null; this.name = ''; }
  add(name, state) { this.states[name] = state; }
  // state: { enter(ctx), update(dt, ctx), render(ctx), exit(ctx) }
  switch(name, ctx) {
    if (this.current?.exit) this.current.exit(ctx);
    this.name = name;
    this.current = this.states[name];
    if (this.current?.enter) this.current.enter(ctx);
  }
  update(dt, ctx) { this.current?.update?.(dt, ctx); }
  render(ctx) { this.current?.render?.(ctx); }
}

// Usage:
const states = new StateMachine();
states.add('menu', { enter() { /* show title */ }, update(dt) { if (input.jump) states.switch('playing'); }, render() { drawMenu(); } });
states.add('playing', { enter() { resetLevel(); }, update(dt) { updatePlayer(dt); updateEnemies(dt); }, render() { drawLevel(); } });
states.add('gameOver', { enter() { playSound('die'); }, update(dt) { if (input.jump) states.switch('menu'); }, render() { drawGameOver(); } });
```

Source: legacy-games/state.js

---

## Camera with Deadzone

Deadzone prevents jittery camera on small movements. Parallax layers create depth.

```javascript
class Camera {
  constructor(viewW, viewH, worldW, worldH) {
    this.x = 0; this.y = 0;
    this.viewW = viewW; this.viewH = viewH;
    this.worldW = worldW; this.worldH = worldH;
    this.dz = { x: viewW * 0.35, y: viewH * 0.35, w: viewW * 0.3, h: viewH * 0.3 };
  }
  follow(target, lerp = 0.1) {
    let dx = 0, dy = 0;
    const sx = target.x - this.x, sy = target.y - this.y;
    if (sx < this.dz.x) dx = sx - this.dz.x;
    if (sx > this.dz.x + this.dz.w) dx = sx - (this.dz.x + this.dz.w);
    if (sy < this.dz.y) dy = sy - this.dz.y;
    if (sy > this.dz.y + this.dz.h) dy = sy - (this.dz.y + this.dz.h);
    this.x = Math.max(0, Math.min(this.worldW - this.viewW, this.x + dx * lerp));
    this.y = Math.max(0, Math.min(this.worldH - this.viewH, this.y + dy * lerp));
  }
  begin(g) { g.push(); g.translate(-Math.round(this.x), -Math.round(this.y)); }
  end(g) { g.pop(); }
  drawParallax(g, img, speedX = 0.5) {
    const px = -(this.x * speedX) % img.width;
    g.image(img, px, 0);
    g.image(img, px + img.width, 0);
  }
}
```

Source: legacy-games/camera.js

---

## SpriteSheet + AnimatedSprite

Frame-based animation with flip support, loop vs one-shot.

```javascript
class AnimatedSprite {
  constructor(sheetImg, frameW, frameH, frameRate = 10) {
    this.img = sheetImg;
    this.frameW = frameW; this.frameH = frameH;
    this.cols = Math.floor(sheetImg.width / frameW);
    this.totalFrames = Math.floor(sheetImg.width / frameW) * Math.floor(sheetImg.height / frameH);
    this.frameRate = frameRate;
    this.currentFrame = 0; this.elapsed = 0; this.finished = false;
    this.flipX = false;
  }
  update(dt) {
    this.elapsed += dt;
    if (this.elapsed >= 1 / this.frameRate) {
      this.elapsed -= 1 / this.frameRate;
      this.currentFrame++;
      if (this.currentFrame >= this.totalFrames) { this.currentFrame = 0; this.finished = true; }
    }
  }
  draw(g, x, y, scale = 1) {
    const col = this.currentFrame % this.cols;
    const row = Math.floor(this.currentFrame / this.cols);
    g.push();
    if (this.flipX) {
      g.translate(x + this.frameW * scale, y);
      g.scale(-1, 1);
      g.image(this.img, 0, 0, this.frameW * scale, this.frameH * scale,
              col * this.frameW, row * this.frameH, this.frameW, this.frameH);
    } else {
      g.image(this.img, x, y, this.frameW * scale, this.frameH * scale,
              col * this.frameW, row * this.frameH, this.frameW, this.frameH);
    }
    g.pop();
  }
  reset() { this.currentFrame = 0; this.elapsed = 0; this.finished = false; }
}
```

Source: legacy-games/sprite.js (adapted for p5.js `image()` API)

---

## Entity Hierarchy

OOP chain with hitbox offsets for accurate collision. (Synthesized from El-pollo-loco + legacy-games.)

```javascript
class Entity {
  constructor(x, y, w, h) {
    this.x = x; this.y = y; this.w = w; this.h = h;
    this.alive = true;
    this.offset = { top: 0, bottom: 0, left: 0, right: 0 };
  }
  get hitbox() {
    return {
      x: this.x + this.offset.left, y: this.y + this.offset.top,
      w: this.w - this.offset.left - this.offset.right,
      h: this.h - this.offset.top - this.offset.bottom
    };
  }
  collidesWith(other) {
    const a = this.hitbox, b = other.hitbox;
    return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  }
}

class MovableEntity extends Entity {
  constructor(x, y, w, h) {
    super(x, y, w, h);
    this.vx = 0; this.vy = 0; this.onGround = false;
    this.speed = 100; this.maxFallSpeed = 600;
  }
  applyGravity(dt) {
    this.vy += CONFIG.gravity * dt;
    if (this.vy > this.maxFallSpeed) this.vy = this.maxFallSpeed;
  }
}

class Player extends MovableEntity {
  constructor(x, y) {
    super(x, y, 32, 48);
    this.hp = 5; this.invincible = 0;
    this.anim = new StateMachine();
    // Add states: idle, walk, jump, attack, hurt, dead
  }
}

class Enemy extends MovableEntity {
  constructor(x, y) {
    super(x, y, 32, 32);
    this.hp = 1; this.patrolDir = 1;
    this.patrolLeft = x - 100; this.patrolRight = x + 100;
  }
  patrol(dt) {
    this.vx = this.patrolDir * this.speed * 0.5;
    if (this.x <= this.patrolLeft) this.patrolDir = 1;
    if (this.x >= this.patrolRight) this.patrolDir = -1;
  }
}
```

---

## Audio Without External Assets

Web Audio API procedural 8-bit sound effects. Init on first user interaction (browser autoplay policy).

```javascript
let audioCtx;
function initAudio() { audioCtx = new (window.AudioContext || window.webkitAudioContext)(); }
function playTone(freq, duration, type = 'square', vol = 0.3) {
  if (!audioCtx) initAudio();
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = type; osc.frequency.value = freq;
  gain.gain.value = vol;
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
  osc.connect(gain); gain.connect(audioCtx.destination);
  osc.start(); osc.stop(audioCtx.currentTime + duration);
}
// Presets — call on first user click/tap:
function sfxJump() { playTone(440, 0.1); setTimeout(() => playTone(660, 0.12), 50); }
function sfxHit() { playTone(200, 0.15, 'sawtooth', 0.4); }
function sfxSlash() { playTone(800, 0.06, 'sawtooth', 0.3); playTone(400, 0.1, 'square', 0.2); }
function sfxPickup() { playTone(880, 0.08); setTimeout(() => playTone(1100, 0.1), 80); }
function sfxDie() { playTone(440, 0.2, 'sawtooth', 0.3); setTimeout(() => playTone(220, 0.3, 'sawtooth', 0.4), 150); }
```

Source: legacy-games/audio.js

---

## Particle System

Lightweight burst emitter for hit sparks, dust clouds, slash trails.

```javascript
class ParticleEmitter {
  constructor() { this.particles = []; }
  emit(config) {
    const { x, y, count = 10, speedMin = 20, speedMax = 80, lifeMin = 0.3, lifeMax = 0.8, colors = ['#fff','#ff0'], gravity = 0, angle = 0, spread = Math.PI * 2 } = config;
    for (let i = 0; i < count; i++) {
      const a = angle - spread/2 + Math.random() * spread;
      const speed = speedMin + Math.random() * (speedMax - speedMin);
      this.particles.push({
        x, y,
        vx: Math.cos(a) * speed, vy: Math.sin(a) * speed,
        life: lifeMin + Math.random() * (lifeMax - lifeMin),
        maxLife: lifeMax,
        color: colors[Math.floor(Math.random() * colors.length)],
        size: 1 + Math.random() * 3,
        gravity
      });
    }
  }
  update(dt) {
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx * dt; p.y += p.vy * dt; p.vy += p.gravity * dt; p.life -= dt;
      if (p.life <= 0) this.particles.splice(i, 1);
    }
  }
  draw(g) {
    for (const p of this.particles) {
      g.noStroke();
      g.fill(p.color);
      g.globalAlpha = Math.max(0, p.life / p.maxLife);
      g.rect(p.x - p.size/2, p.y - p.size/2, p.size, p.size);
    }
    g.globalAlpha = 1;
  }
}
```

Usage for slash hit:
```javascript
particles.emit({ x: hitX, y: hitY, count: 15, angle: -Math.PI/2, spread: Math.PI/3, colors: ['#fff','#ff0','#f80'], speedMin: 50, speedMax: 150, lifeMin: 0.2, lifeMax: 0.5, gravity: 300 });
```

Source: legacy-games/particles.js

---

## TileMap

Render only visible tiles. Separate visual layers from collision layer.

```javascript
class TileMap {
  constructor(tilesetImg, tileSize) {
    this.tileset = tilesetImg;
    this.tileSize = tileSize;
    this.layers = []; // 2D arrays of 1-based tile indices (0 = empty)
    this.collisionLayer = null;
    this.mapWidth = 0; this.mapHeight = 0;
  }
  addLayer(data, w, h) { this.layers.push(data); this.mapWidth = w; this.mapHeight = h; }
  setCollisionLayer(data) { this.collisionLayer = data; }
  isSolid(worldX, worldY) {
    if (!this.collisionLayer) return false;
    const col = Math.floor(worldX / this.tileSize);
    const row = Math.floor(worldY / this.tileSize);
    if (row < 0 || row >= this.mapHeight || col < 0 || col >= this.mapWidth) return true;
    return this.collisionLayer[row * this.mapWidth + col] > 0;
  }
  getOverlappingTiles(entity) {
    const t = this.tileSize;
    const startCol = Math.floor(entity.x / t), endCol = Math.floor((entity.x + entity.w) / t);
    const startRow = Math.floor(entity.y / t), endRow = Math.floor((entity.y + entity.h) / t);
    const tiles = [];
    for (let r = startRow; r <= endRow; r++) {
      for (let c = startCol; c <= endCol; c++) {
        if (r < 0 || r >= this.mapHeight || c < 0 || c >= this.mapWidth) continue;
        const idx = this.collisionLayer[r * this.mapWidth + c];
        if (idx > 0) tiles.push({ col: c, row: r, left: c*t, right: (c+1)*t, top: r*t, bottom: (r+1)*t, solid: true });
      }
    }
    return tiles;
  }
  renderLayer(g, layerIndex, camera) {
    const data = this.layers[layerIndex];
    if (!data) return;
    const t = this.tileSize;
    const startCol = Math.max(0, Math.floor(camera.x / t));
    const endCol = Math.min(this.mapWidth, Math.ceil((camera.x + camera.viewW) / t) + 1);
    const startRow = Math.max(0, Math.floor(camera.y / t));
    const endRow = Math.min(this.mapHeight, Math.ceil((camera.y + camera.viewH) / t) + 1);
    for (let r = startRow; r < endRow; r++) {
      for (let c = startCol; c < endCol; c++) {
        const idx = data[r * this.mapWidth + c];
        if (idx <= 0) continue;
        const ti = idx - 1;
        const sx = (ti % this.cols) * t, sy = Math.floor(ti / this.cols) * t;
        g.image(this.tileset, c*t - camera.x, r*t - camera.y, t, t, sx, sy, t, t);
      }
    }
  }
}
```

Source: legacy-games/tilemap.js

---

## Utility Functions

```javascript
const Utils = {
  clamp(v, min, max) { return Math.max(min, Math.min(max, v)); },
  lerp(a, b, t) { return a + (b - a) * t; },
  randomRange(min, max) { return Math.random() * (max - min) + min; },
  randomInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; },
  dist(x1, y1, x2, y2) { return Math.sqrt((x2-x1)**2 + (y2-y1)**2); },
  easeOutQuad(t) { return t * (2 - t); },
  easeInOutQuad(t) { return t < 0.5 ? 2*t*t : -1 + (4-2*t)*t; },
};

class Timer {
  constructor(duration, callback, loop = false) { this.duration = duration; this.callback = callback; this.loop = loop; this.elapsed = 0; this.active = true; }
  update(dt) { if (!this.active) return; this.elapsed += dt; if (this.elapsed >= this.duration) { this.callback(); this.loop ? (this.elapsed -= this.duration) : (this.active = false); } }
  get progress() { return Utils.clamp(this.elapsed / this.duration, 0, 1); }
}
```

Source: legacy-games/utils.js
