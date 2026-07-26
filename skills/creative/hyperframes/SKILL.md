---
name: hyperframes
description: "Create HTML-based video compositions, animated title cards, social overlays, captioned talking-head videos, audio-reactive visuals, and shader transitions using HyperFrames. HTML is the source of truth for video. Use when the user wants a rendered MP4/WebM from an HTML composition, wants to animate text/logos/charts over media, needs captions synced to audio, wants TTS narration, or wants to convert a website into a video."
version: 1.1.0
author: heygen-com
license: Apache-2.0
platforms: [linux, macos, windows]
prerequisites:
  commands: [node, ffmpeg, npx]
metadata:
  hermes:
    tags: [creative, video, animation, html, gsap, motion-graphics]
    related_skills: [manim-video]
    category: creative
    requires_toolsets: [terminal]
---

# HyperFrames

HTML is the source of truth for video. A composition is an HTML file with `data-*` attributes for timing, a GSAP timeline for animation, and CSS for appearance. The HyperFrames engine captures the page frame-by-frame and encodes to MP4/WebM with FFmpeg.

**Complement to `manim-video`:** Use `manim-video` for mathematical/geometric explainers (equations, 3B1B-style). Use `hyperframes` for motion-graphics, talking-head with captions, product tours, social overlays, shader transitions, and anything driven by real video/audio media.

## When to Use

- User asks for a rendered video from text, a script, or a website
- Animated title cards, lower thirds, or typographic intros
- Captioned narration video (TTS + captions synced to waveform)
- Audio-reactive visuals (beat sync, spectrum bars, pulsing glow)
- Scene-to-scene transitions (crossfade, wipe, shader warp, flash-through-white)
- Social overlays (Instagram/TikTok/YouTube style)
- Website-to-video pipeline (capture a URL, produce a promo)
- Any HTML/CSS/JS animation that must render deterministically to a video file

Do **not** use this skill for:
- Pure math/equation animation (→ `manim-video`)
- Image generation or memes (→ image models)
- Live video conferencing or streaming

## Quick Reference

```bash
npx hyperframes init my-video               # scaffold a project
cd my-video
npx hyperframes lint                        # validate before preview/render
npx hyperframes preview                     # live-reload browser preview (port 3002)
npx hyperframes render --output final.mp4   # render to MP4
npx hyperframes doctor                      # diagnose environment issues
```

Render flags: `--quality draft|standard|high` · `--fps 24|30|60` · `--format mp4|webm` · `--docker` (reproducible) · `--strict`.

## Setup (one-time)

```bash
# From the optional-skills path (if not installed as a regular skill)
bash "$(dirname "$(find ~/.hermes/hermes-agent/optional-skills -path '*/hyperframes/SKILL.md' 2>/dev/null | head -1)")/scripts/setup.sh"

# OR if installed as a regular skill
bash "$(dirname "$(find ~/.hermes/skills -path '*/hyperframes/SKILL.md' 2>/dev/null | head -1)")/scripts/setup.sh"
```

The script:
1. Verifies Node.js >= 22 and FFmpeg are installed (prints fix instructions if not).
2. Installs the `hyperframes` CLI globally (`npm install -g hyperframes@>=0.4.2`).
3. Pre-caches `chrome-headless-shell` via Puppeteer — **required** for best-quality rendering.
4. Runs `npx hyperframes doctor` and reports the result.

**Pitfall:** The setup script must be found via `find` — the skill may live at `~/.hermes/hermes-agent/optional-skills/creative/hyperframes/` (bundled) or `~/.hermes/skills/creative/hyperframes/` (installed). Always search both paths.

## Procedure

### 1. Plan before writing HTML

Before touching code, articulate at a high level:
- **What** — narrative arc, key moments, emotional beats
- **Structure** — compositions, tracks (video/audio/overlays), durations
- **Visual identity** — colors, fonts, motion character (explosive / cinematic / fluid / technical)
- **Hero frame** — for each scene, the moment when the most elements are simultaneously visible

**Visual Identity Gate.** Before writing ANY composition HTML, a visual identity must be defined:
1. **`DESIGN.md` at project root?** → Use its exact colors, fonts, motion rules
2. **User named a style?** → Generate a minimal `DESIGN.md`
3. **None of the above?** → Ask 3 questions: Mood? Light/dark? Brand colors/fonts?

### 2. Scaffold

```bash
npx hyperframes init my-video --example blank --non-interactive
```

Templates: `blank`, `warm-grain`, `play-mode`, `swiss-grid`, `vignelli`, `decision-tree`, `kinetic-type`, `product-promo`, `nyt-graph`.

### 2a. Design Presets (hyperframes.dev/design)

The HyperFrames design page at `https://www.hyperframes.dev/design/` hosts **Premade frames** — curated visual design languages (typography + color + layout). These are NOT code templates; they are design specs you apply to existing compositions.

**Available presets** (as of v0.7.64):

| Preset | Description |
|--------|-------------|
| Biennale Yellow | Warm parchment + solar yellow, Instrument Serif, indigo ink |
| BlockFrame | Neobrutalist — thick black borders, hard offset shadows, candy accents |
| Blue Professional | Corporate parchment + cobalt, Space Grotesk display, Inter body |
| Bold Poster | Shrikhand tilted display + red accent, magazine cover energy |
| Broadside | Industrial newsprint — raw cream on ink, Barlow display, fire-orange |
| Capsule | Pill-shaped editorial — cream paper, candy palette, Bodoni Moda serif |
| Cartesian | Minimal sparse — warm parchment, ink display type, taupe accents |
| Cobalt Grid | Editorial parchment + cobalt grid, Newsreader display, Hanken Grotesk |
| **Coral** | **Bebas Neue uppercase headlines + coral on cream, Inter reading** |
| Creative Mode | Cream + saturated candy accents, Archivo Black, JetBrains Mono data |
| Daisy Days | Sunny-garden pastels, 3px charcoal outlines, Fredoka + Quicksand |
| Editorial Forest | Green/pink/cream editorial triad, Source Serif 4, JetBrains Mono chrome |

**Redesign workflow** (apply a preset to an existing composition):

1. **Read the original** — understand scene structure, timing, data attributes, GSAP animations
2. **Identify the design tokens** — fonts (display + body), accent color, background color, decorative elements
3. **Rewrite CSS only** — change colors, fonts, shadows, decorative lines. Preserve ALL HTML structure, `data-*` attributes, and GSAP timeline code
4. **Lint + validate** — same as any composition
5. **Render** — standard render pipeline

The design page also allows uploading a `design.md` file to generate a `frame.md` (composition directive). This is useful for converting brand guidelines into HyperFrames-ready specs.

**Pitfall:** Presets define visual language, not code structure. A Coral preset means "use Bebas Neue for headlines, coral #FF7F50 for accents, cream #FFFBF5 for background, Inter for body text" — you still write the HTML/CSS yourself.

### 3. Layout before animation

Write the static HTML+CSS for the **hero frame first** — no GSAP yet. The `.scene-content` container must fill the scene (`width:100%; height:100%; padding:Npx`) with `display:flex` + `gap`.

Only after the hero frame looks right, add `gsap.from()` entrances and `gsap.to()` exits.

### 4. Animate with GSAP

Every composition must:
- Register its timeline: `window.__timelines["<composition-id>"] = tl`
- Start paused: `gsap.timeline({ paused: true })`
- Use finite `repeat` values (no `repeat: -1`)
- Be deterministic — no `Math.random()`, `Date.now()`, or wall-clock logic
- Build synchronously — no `async`/`await`, `setTimeout`, or Promises

### 5. Transitions between scenes

1. **Always use a transition between scenes** — no jump cuts
2. **Always use entrance animations** on every scene element (`gsap.from(...)`)
3. **Never use exit animations** except on the final scene — the transition IS the exit

### 6. Audio, captions, TTS, audio-reactive

- **Audio:** always a separate `<audio>` element (video is `muted playsinline`)
- **TTS:** `npx hyperframes tts "Script" --voice af_nova --output narration.wav`
- **Captions:** `npx hyperframes transcribe narration.wav` → word-level transcript
- **Audio-reactive:** pre-extract audio bands, sample per-frame with `tl.call(draw, [], f / fps)`

### 7. Lint, validate, preview, render

```bash
npx hyperframes lint              # structural issues
npx hyperframes validate          # WCAG contrast audit
npx hyperframes inspect           # layout audit
npx hyperframes preview           # live browser preview
npx hyperframes render --quality draft --output draft.mp4
```

## Critical Pitfalls (Discovered in Production)

### 1. `gsap_from_opacity_noop` — Elements Stay Invisible

**The bug:** Elements with `style="opacity:0"` AND `gsap.from({opacity: 0})` animate from 0→0 (noop). `gsap.from()` animates FROM the specified value TO the current CSS value — since CSS is already 0, nothing happens.

**The fix:** REMOVE `style="opacity:0"` from the HTML elements. Let `gsap.from({opacity: 0})` handle the initial hidden state — it sets the element to opacity 0 at the start and animates TO the CSS default (1).

```html
<!-- WRONG — element stays invisible -->
<div id="title" style="opacity:0">Hello</div>
<script>tl.from("#title", { opacity: 0, duration: 1 }, 0);</script>

<!-- CORRECT — gsap.from handles the initial state -->
<div id="title">Hello</div>
<script>tl.from("#title", { opacity: 0, duration: 1 }, 0);</script>
```

**Lint catches this** as `gsap_from_opacity_noop`. It fires on every element where both conditions are true. In a multi-scene composition this can silently break ALL scenes.

### 2. `gsap_exit_missing_hard_kill` — Stale Visibility on Non-Linear Seek

**The bug:** Scene clips that have exit tweens (`gsap.to("#scene", { autoAlpha: 0 })`) end at the clip boundary, but non-linear seeking (scrubbing, seeking to a timestamp) can land after the fade and leave stale visibility state.

**The fix:** Add a `tl.set()` hard kill at the clip boundary:

```js
tl.to("#scene8", { autoAlpha: 0, duration: 1, ease: "power2.in" }, 169);
tl.set("#scene8", { autoAlpha: 0 }, 170);  // hard kill at boundary
```

**The lint catches this** as `gsap_exit_missing_hard_kill`. The error message tells you the exact timestamp for the hard kill (it's the `data-start` of the NEXT clip on the same track).

### 3. `repeat: -1` Breaks Capture

Infinite-repeat tweens break the frame capture engine. Always compute a finite repeat count:

```js
// WRONG
tl.to(".pulse", { scale: 1.2, repeat: -1, yoyo: true }, 0);

// CORRECT — compute based on clip duration
const clipDuration = 10; // seconds
const cycleDuration = 1; // seconds per cycle
tl.to(".pulse", { scale: 1.2, repeat: Math.ceil(clipDuration / cycleDuration) - 1, yoyo: true }, 0);
```

### 4. Google Fonts Need Resolution

The producer resolves Google Fonts during compile/render, but raw external font requests add latency. If fonts fail to load before capture, text renders in fallback font. Prefer mapped family names or local `@font-face` declarations.

### 5. `visibility` and `display` Can't Be Animated by GSAP

Use `autoAlpha` (handles both visibility and opacity). Never animate `visibility` or `display` directly.

### 6. Don't Call `video.play()` or `audio.play()`

The framework owns playback. Calling play() yourself causes double-play or desync.

### 7. Async Timeline Construction Breaks Capture

The capture engine reads `window.__timelines` synchronously after page load. Never wrap timeline construction in `async`, `setTimeout`, or a Promise.

## Performance Baselines

| Content | FPS | Quality | Duration | Render Time | File Size |
|---------|-----|---------|----------|-------------|-----------|
| 9-scene text/waveform composition | 30 | standard | 3 min | ~80s (4 workers, AMD GPU) | 5.6 MB |
| 9-scene text/waveform composition | 30 | draft | 3 min | ~68s | 4.7 MB |
| Simple title card | 30 | draft | 10s | ~5s | <1 MB |

Draft quality is fine for iteration. Use `--quality high` for final delivery.

## References

- [composition.md](references/composition.md) — data attributes, timeline contract, non-negotiable rules
- [cli.md](references/cli.md) — every CLI command
- [gsap.md](references/gsap.md) — GSAP core API for HyperFrames
- [features.md](references/features.md) — captions, TTS, audio-reactive, marker highlighting, transitions
- [troubleshooting.md](references/troubleshooting.md) — common render errors
- [design-presets.md](references/design-presets.md) — hyperframes.dev/design preset catalog (Coral, BlockFrame, etc.) and redesign workflow

## Installation Note

This skill may exist at two locations:
- **Bundled:** `~/.hermes/hermes-agent/optional-skills/creative/hyperframes/`
- **Installed:** `~/.hermes/skills/creative/hyperframes/`

If not found via `skill_view(name='hyperframes')`, check the bundled path and install it:
```bash
cp -r ~/.hermes/hermes-agent/optional-skills/creative/hyperframes ~/.hermes/skills/creative/
```
