# GSAP Patterns for HyperFrames

## The Opacity Trap (gsap_from_opacity_noop)

The most common bug in HyperFrames compositions. Every element affected produces a lint error.

**Root cause:** `gsap.from()` animates FROM the specified value TO the current CSS value. If the element already has `opacity: 0` in CSS/inline style, it animates from 0→0 — nothing happens.

**Rule:** NEVER put `opacity: 0` on elements that will be animated with `gsap.from({opacity: 0})`. GSAP handles the initial hidden state.

```html
<!-- BROKEN -->
<div id="title" style="opacity:0">Hello</div>
<script>tl.from("#title", { opacity: 0, duration: 1 }, 0);</script>

<!-- CORRECT -->
<div id="title">Hello</div>
<script>tl.from("#title", { opacity: 0, duration: 1 }, 0);</script>
```

**Exception:** `gsap.fromTo()` is explicit about both states and doesn't have this problem:
```js
tl.fromTo("#title", { opacity: 0 }, { opacity: 1, duration: 1 }, 0);
```

## Hard Kills at Scene Boundaries

When a scene clip has an exit tween that ends at the clip's `data-start` boundary, non-linear seeking can leave stale visibility. Add a `tl.set()` at the exact boundary:

```js
// Exit tween
tl.to("#scene8", { autoAlpha: 0, duration: 1, ease: "power2.in" }, 169);
// Hard kill — timestamp = data-start of next clip on same track
tl.set("#scene8", { autoAlpha: 0 }, 170);
```

**How to find the kill timestamp:** It's the `data-start` value of the NEXT clip on the same `data-track-index`. The lint error message tells you the exact value.

## Repeat Must Be Finite

`repeat: -1` (infinite) breaks the capture engine. Always compute:

```js
const clipDuration = 10; // from data-duration
const cycleDuration = 1; // time per cycle
const repeatCount = Math.ceil(clipDuration / cycleDuration) - 1;
tl.to(".pulse", { scale: 1.2, repeat: repeatCount, yoyo: true }, 0);
```

## Waveform Generation Pattern

For data-viz scenes with audio waveforms:

```js
function makeWaveform(containerId, count, maxH) {
  const c = document.getElementById(containerId);
  for (let i = 0; i < count; i++) {
    const bar = document.createElement('div');
    bar.className = 'wave-bar';
    // Deterministic pseudo-random: no Math.random()
    const h = 20 + (((i * 7 + 13) * 31) % maxH);
    bar.style.height = h + 'px';
    c.appendChild(bar);
  }
}
```

Call with `tl.call(() => makeWaveform("id", 80, 100), [], startTime)`.

## Chunk Grid Pattern

For visualizing filtering/recognition:

```js
function makeChunkGrid(containerId, total, matched) {
  const c = document.getElementById(containerId);
  for (let i = 0; i < total; i++) {
    const chunk = document.createElement('div');
    chunk.className = 'chunk' + (i < matched ? ' matched' : '');
    c.appendChild(chunk);
  }
}
```

## Mycelium / Network Line Pattern

For abstract network visualizations:

```css
.mycelium-line {
  position: absolute; height: 1px;
  background: linear-gradient(90deg, transparent, #3b82f620, #3b82f640, #3b82f620, transparent);
  transform-origin: left center;
}
```

Animate width from 0 to target with `tl.to()`.

## Particle System Pattern

For floating ambient particles:

```js
function makeParticles(rootId, count) {
  const root = document.getElementById(rootId);
  for (let i = 0; i < count; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    const size = 2 + ((i * 13) % 6);
    p.style.width = size + 'px';
    p.style.height = size + 'px';
    p.style.left = ((i * 67 + 23) % 1920) + 'px';
    p.style.top = ((i * 43 + 11) % 1080) + 'px';
    p.dataset.particle = i;
    root.appendChild(p);
  }
}
```

Animate with staggered `y` drift and `yoyo: true, repeat: N`.

## Key GSAP Easing Reference

| Use case | Ease |
|----------|------|
| Entrances | `power3.out`, `expo.out`, `back.out(1.4)` |
| Exits | `power2.in`, `expo.in` |
| Number count-ups | `power1.inOut` |
| Organic motion | `elastic.out(1, 0.3)` |
| Snappy reveals | `back.out(1.7)` |
| Linear/scrubbed | `none` |
