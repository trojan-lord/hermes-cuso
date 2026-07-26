---
name: html5-game-dev
description: "Architecture patterns and production techniques for HTML5 browser games — Canvas 2D / p5.js side-scrollers, platformers, and 2D action games in single or multi-file structures."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [game-dev, html5, canvas, p5js, side-scroller, platformer, game-architecture]
    related: [p5js]
---

# HTML5 Game Development — Architecture & Patterns

## When to use
Building browser-based 2D games: side-scrollers, platformers, action games, endless runners. Covers Canvas 2D API and p5.js rendering. Single-file or multi-file projects.

## What's inside
Production architecture patterns distilled from analyzing 4 open-source HTML5 game repos: humancto/legacy-games (shared engine powering 12 retro games), KosMaster87/El-pollo-loco (Jump'n'Run with OOP entity hierarchy), EnginKARATAS/platform-advanced (p5.js + TypeScript), and **solankianandwork-zorro/grand-line-quest** (3117-line single-file One Piece action platformer — the gold standard for single-file architecture). Covers game loops, physics, collision detection, state management, input, camera, sprites, audio, and entity design.

## Engine Choice: Pure Canvas2D vs p5.js

**Recommendation: Pure Canvas2D for single-file games.**

| Factor | p5.js | Pure Canvas2D |
|--------|-------|---------------|
| CDN dependency | Yes (breaks offline) | None |
| File size | +150KB+ overhead | Zero |
| Performance | Slower (wrapper) | Native speed |
| Learning curve | Easier for artists | More boilerplate |
| Procedural drawing | `rect()`, `ellipse()` | `ctx.fillRect()`, `ctx.arc()` |
| Game loop | `draw()` callback | `requestAnimationFrame` |
| Mobile reliability | CDN can fail | Always works |

p5.js is fine for sketches, prototyping, and art tools. For production games — especially single-file — pure Canvas2D is the right call. The grand-line-quest reference (3117 lines, zero deps) proves this works at scale.

When to use p5.js anyway: rapid prototyping, educational projects, or when the user specifically requests it.

## Quick Reference — Architecture Checklist

| System | Pattern | Source |
|--------|---------|--------|
| Game loop | Fixed timestep with accumulator | `references/game-architecture.md` § Fixed Timestep |
| Collision | Separated X/Y tilemap resolution | `references/game-architecture.md` § Separated X/Y |
| Input | Frame-based justPressed + endFrame clearing | `references/game-architecture.md` § Frame-Based Input |
| State | FSM with enter/update/render/exit lifecycle | `references/game-architecture.md` § State Machine |
| Camera | Deadzone follow + parallax layers | `references/game-architecture.md` § Camera |
| Sprites | SpriteSheet + AnimatedSprite with frame timing | `references/game-architecture.md` § SpriteSheet |
| Audio | Web Audio API procedural sound effects | `references/game-architecture.md` § Audio |
| Particles | Emitter with configurable burst params | `references/game-architecture.md` § Particle System |
| Entity OOP | Entity → MovableEntity → Player/Enemy | `references/game-architecture.md` § Entity Hierarchy |

## Recommended Single-File Structure (Pure Canvas2D)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
  <title>Game Title</title>
  <style>
    *{margin:0;padding:0;box-sizing:border-box}
    html,body{height:100%;background:#0a0e08;overflow:hidden;touch-action:none}
    canvas{display:block;image-rendering:pixelated}
  </style>
</head>
<body>
<canvas id="game" width="800" height="480"></canvas>
<script>
"use strict";
const cv = document.getElementById('game'), ctx = cv.getContext('2d');
const W = cv.width, H = cv.height;

// §1 UTILITIES (clamp, lerp, AABB, rnd, sign)
// §2 INPUT (keys object + touch bridge)
// §3 AUDIO (WebAudio procedural — tone(), noise())
// §4 GAME STATE (state machine: title/play/win/lose)
// §5 PLAYER (object literal with state, physics, drawing)
// §6 ENEMIES (spawn templates, AI update, drawing)
// §7 LEVEL (platforms, parallax backgrounds)
// §8 EFFECTS (particles, floaters, screen shake)
// §9 UPDATE (fixed 60Hz timestep with accumulator)
// §10 DRAW (render everything each frame)
// §11 MAIN LOOP (requestAnimationFrame + accumulator)
// §12 EVENT WIRING (keyboard, touch, buttons)
</script>
</body>
</html>
```

### Legacy Structure (p5.js, if requested)

```html
<!-- Only use when user specifically requests p5.js -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/p5.min.js"></script>
<script>p5.disableFriendlyErrors = true;</script>
```

## Critical Pitfalls

1. **Never use `setInterval` for physics.** Use the fixed timestep accumulator. Interval-based gravity produces frame-rate-dependent behavior.

2. **Always separate X and Y collision resolution.** Moving both axes then resolving all overlaps causes corner-cutting on tilemaps. Move X → resolve X → move Y → resolve Y.

3. **Cap delta time.** On tab-unfocus, `rawDt` can spike to seconds. Always `Math.min(rawDt, 0.1)` to prevent the "spiral of death" where entities teleport through walls.

4. **Don't use p5.js for production single-file games.** CDN dependency breaks offline/mobile. Pure Canvas2D is smaller, faster, and more reliable. The grand-line-quest (3117 lines) proves pure Canvas works at scale.

5. **Research real projects before building.** User expectation: study 2-3 well-built open-source games first, learn their patterns, then build. Don't start from scratch without references. Search GitHub for `html5 game side scrolling platformer javascript` and examine top results.

6. **Use `requestAnimationFrame` + fixed accumulator, not p5's `draw()`.** The rAF pattern gives you control over timestep and doesn't depend on any framework.

7. **Procedural audio > external files.** WebAudio tone/noise functions eliminate asset dependencies. `oscillator` + `gain` envelope = jump/attack sounds. `bufferSource` + noise buffer = hit/impact sounds.

8. **Canvas must have `image-rendering: pixelated`** for retro/16-bit aesthetic. Without it, scaling blurs pixel art.

## References

| File | Contents |
|------|----------|
| `references/game-architecture.md` | Full architecture patterns with code: fixed timestep, collision, input, state machine, camera, sprites, entities, audio, particles, source repos |
| `references/grand-line-quest-patterns.md` | Gold standard single-file architecture: pure Canvas2D, procedural pixel art, parallax, boss AI, screen shake, floating damage, procedural audio. Extracted from 3117-line One Piece action platformer. |

## Source Repos Analyzed

| Repo | Stars | Key Contribution |
|------|-------|------------------|
| [humancto/legacy-games](https://github.com/humancto/legacy-games) | 3★ | Shared engine modules: fixed timestep loop, state machine, camera deadzone, sprite animation, particle emitter, tilemap, audio, input system. 12+ games built on same engine. |
| [KosMaster87/El-pollo-loco](https://github.com/KosMaster87/El-pollo-loco) | 3★ | OOP entity hierarchy (DrawableObject→MovableObject→Character/Enemy), handler pattern (CollisionHandler, RenderHandler), hitbox offsets, parallax backgrounds, touch input. |
| [EnginKARATAS/platform-advanced](https://github.com/EnginKARATAS/platform-advanced) | 7★ | p5.js + TypeScript game architecture with manager pattern, interfaces, constants system. |
| [solankianandwork-zorro/grand-line-quest](https://github.com/solankianandwork-zorro/grand-line-quest) | — | **Gold standard single-file architecture.** 3117 lines, zero deps, pure Canvas2D. Features: HTML overlay menus, fixed 60Hz timestep, procedural WebAudio, multi-layer parallax, procedural pixel art characters (Luffy, Crocodile, Arlong, etc.), camera lerp, screen shake, floating damage, boss AI with attack patterns, state machines. The reference to study when building action games. |
