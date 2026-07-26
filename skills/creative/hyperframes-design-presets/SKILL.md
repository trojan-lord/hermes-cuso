---
name: hyperframes-design-presets
description: Use when creating HyperFrames video compositions. Sources design presets, frame packs, and typography palettes from hyperframes.dev/design and other design systems. Ensures every composition uses proper design language instead of freehand CSS.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hyperframes, design, presets, typography, color, video]
    related_skills: [hyperframes-core, hyperframes-cli, hyperframes-creative]
---

# HyperFrames Design Presets

## Overview

Every HyperFrames composition should use a proper design preset with real typography and curated color palettes — never freehand CSS. This skill documents where to find presets and how to apply them.

## Primary Source: hyperframes.dev/design

The official HyperFrames design page offers 12+ premade frames. Always check here first.

### Available Presets

| Preset | Description | Headline Font | Body Font | Accent Color |
|--------|-------------|---------------|-----------|--------------|
| **Coral** | Bebas Neue uppercase headlines + coral on cream | Bebas Neue | Inter | #FF7F50 |
| **Biennale Yellow** | Warm parchment + solar yellow bloom | Instrument Serif | — | Solar yellow |
| **BlockFrame** | Maximalist neobrutalist, thick borders, hard shadows | — | — | Candy accents |
| **Blue Professional** | Corporate parchment + cobalt primary | Space Grotesk | Inter | Cobalt |
| **Bold Poster** | Shrikhand tilted display + red accent on cream | Shrikhand | — | Red |
| **Broadside** | Industrial newsprint poster, raw cream on ink | Barlow | — | Fire-orange |
| **Capsule** | Pill-shaped editorial, cream paper, candy palette | Bodoni Moda | — | Candy |
| **Cartesian** | Minimal sparse layout, warm parchment | — | — | Taupe |
| **Cobalt Grid** | Editorial parchment + cobalt grid system | Newsreader | Hanken Grotesk | Cobalt |
| **Creative Mode** | Cream + saturated candy accents | Archivo Black | JetBrains Mono | Candy |
| **Daisy Days** | Sunny-garden pastels, 3px charcoal outlines | Fredoka | Quicksand | Pastels |
| **Editorial Forest** | Green/pink/cream editorial triad | Source Serif 4 | JetBrains Mono | Green/pink |

### How to Apply a Preset

1. **Identify the preset** that matches the video's tone (corporate → Blue Professional, editorial → Cobalt Grid, playful → Daisy Days, etc.)
2. **Load the fonts** from Google Fonts in the `<head>`:
   ```html
   <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
   ```
3. **Set the color palette** in CSS variables or inline styles:
   - Background: cream/off-white (#FFFBF5 or #FFF8F0)
   - Headlines: preset accent color, uppercase
   - Body text: dark (#2D2D2D or #1A1A1A)
   - Accents: preset accent color for data numbers, decorative lines
4. **Match the typography hierarchy**:
   - Display/headlines: preset's headline font, 60-120px, uppercase
   - Subheadings: preset's body font or secondary, 24-36px
   - Body/reading: preset's body font, 16-20px
   - Data/numbers: accent color, bold, 48-72px

## How to Download Frame Packs

Frame packs live at `https://www.hyperframes.dev/design/<preset-name>` — NOT `/design`.

### Download Workflow
1. Navigate to `https://www.hyperframes.dev/design/<preset-name>` (e.g., `/design/coral`)
2. Click "Download frame pack" button in the top right (requires login for some, but the iframe content is always accessible)
3. Extract CSS + HTML from the iframe via browser console:
   ```js
   const f = document.querySelector('iframe[title*="coral"]');
   const doc = f.contentDocument;
   const css = Array.from(doc.querySelectorAll('style')).map(s => s.textContent).join('\n');
   const html = doc.body.innerHTML;
   ```
4. Save as `frame-packs/<name>/frame.css` and `frame-packs/<name>/frame.html`
5. Fonts are Google Fonts — always include the `<link>` tags

### All Preset URLs
| Preset | URL | Description |
|--------|-----|-------------|
| Biennale Yellow | `/design/biennale-yellow` | Warm parchment + solar yellow, Instrument Serif |
| BlockFrame | `/design/blockframe` | Maximalist neobrutalist, thick borders |
| Blue Professional | `/design/blue-professional` | Corporate cobalt, Space Grotesk |
| Bold Poster | `/design/bold-poster` | Shrikhand tilted, red on cream |
| Broadside | `/design/broadside` | Industrial newsprint, Barlow, fire-orange |
| Capsule | `/design/capsule` | Pill-shaped editorial, Bodoni Moda |
| Cartesian | `/design/cartesian` | Minimal sparse, warm parchment |
| Cobalt Grid | `/design/cobalt-grid` | Editorial parchment + cobalt grid |
| **Coral** | `/design/coral` | **Bebas Neue + coral on cream** |
| Creative Mode | `/design/creative-mode` | Candy accents, Archivo Black |
| Daisy Days | `/design/daisy-days` | Sunny pastels, Fredoka + Quicksand |
| Editorial Forest | `/design/editorial-forest` | Green/pink/cream triad |

### Using Downloaded Frame Packs
Once downloaded, apply the CSS to any HyperFrames composition:
1. Copy the CSS variables and layout classes from `frame.css`
2. Use the HTML structure from `frame.html` as layout reference
3. Replace content but keep the design tokens (colors, fonts, spacing)
4. For container queries (`cqw`), ensure the frame has `container-type: size`
- **Google Fonts** (fonts.google.com) — free fonts, pairing suggestions in the "Pairings" tab
- **Font Pair** (fontpair.co) — algorithmic font pairing generator
- **Kinsta Font Pairings** (kinsta.com/blog/best-google-fonts-combinations) — tested combinations with examples
- **Fonts In Use** (fontsinuse.com) — see how real designers use specific typefaces
- **Fontjoy** (fontjoy.com) — deep-learning font pairing generator
- **_variable fonts** (v-fonts.com) — variable font directory with axis/weight info

### Color Palettes
- **Color Hunt** (colorhunt.co) — community-voted palettes, filter by mood/season
- **Coolors** (coolors.co) — palette generator + lock-and-explore mode
- **Adobe Color** (color.adobe.com) — extract palettes from images, color wheel, accessibility checker
- **Colormind** (colormind.io) — neural-net palette generator, can lock one color and generate the rest
- **Paletton** (paletton.com) — advanced color wheel with contrast and blindness simulation
- **Realtime Colors** (realtimecolors.com) — preview palettes on a live page mockup
- **Contrast Checker** (webaim.org/resources/contrastchecker) — WCAG AA/AAA validation

### Design Inspiration & Motion Graphics
- **Dribbble** (dribbble.com) — search "motion graphics" or "kinetic typography" for frame-by-frame inspiration
- **Behance** (behance.net) — curated projects, search "title sequence" or "motion design"
- **Mobbin** (mobbin.com) — real UI patterns organized by component type
- **Awwwards** (awwwards.com) — award-winning web design, good for layout composition
- **Godly** (godly.website) — curated creative websites
- **Landingfolio** (landingfolio.com) — landing page components, hero sections, CTAs

### Frame Packs & Templates
- **HyperFrames Catalog** (`npx hyperframes catalog`) — built-in frames, effects, text effects
- **HyperFrames Registry** (`npx hyperframes skills`) — community frame packs
- **Motion Design School** (motiondesign.school) — After Effects templates and techniques
- **Videohive** (videohive.net) — Premiere/After Effects templates (reference only, don't use without license)
- **Mixkit** (mixkit.co) — free video templates and transitions
- **Canva Templates** (canva.com/templates) — visual layout reference (recreate in code, don't copy)

### Gradient & Texture Resources
- **UI Gradients** (uigradients.com) — 200+ linear gradient presets
- **Gradient Hunt** (gradienthunt.com) — community gradient palettes
- **SVG Backgrounds** (svg backgrounds.dev) — patterned backgrounds as CSS/SVG
- **Transparent Textures** (transparenttextures.com) — subtle texture overlays
- **Subtle Patterns** (subtlepatterns.com) — tiling background textures

### CSS/Code-First Design Systems
- **Tailwind CSS** (tailwindcss.com) — utility classes that encode good design defaults
- **Open Props** (open-props.style) — CSS custom properties for spacing, color, typography
- **Radix Colors** (radix-ui.com/colors) — accessible color scale system
- **IBM Carbon** (carbondesignsystem.com) — full design system with tokens

## Workflow: How to Source a Design

1. **Start with hyperframes.dev/design** — check if a preset matches the video's tone
2. **If none fit**, check Typewolf for font pairings + Color Hunt/Coolors for palette
3. **For motion graphics inspiration**, search Dribbble/Behance for "kinetic typography" or "title sequence"
4. **For gradients**, pull from UI Gradients or Gradient Hunt
5. **For textures**, check Transparent Textures or SVG Backgrounds
6. **Always validate** contrast with Adobe Color or WebAIM before finalizing
7. **Document the sources** — save which presets/palettes you used in the composition comments

## Design Language Checklist

Before finalizing any composition:

- [ ] Typography is from a real font family (not system fonts)
- [ ] Color palette is curated (3-5 colors max)
- [ ] Headline font matches the video's tone
- [ ] Body text is readable at 1080p
- [ ] Accent colors are used consistently for data/highlights
- [ ] Background is not pure white (#FFF) — use warm tones
- [ ] Text contrast passes WCAG AA (4.5:1 minimum)

## Common Pitfalls

1. **Using system fonts** — always load real typography from Google Fonts or local @font-face
2. **Pure white backgrounds** — use cream (#FFFBF5), parchment (#FFF8F0), or warm gray
3. **Too many colors** — stick to 3-5 from the preset palette
4. **Inconsistent accent usage** — data numbers, decorative lines, and highlights should all use the same accent color
5. **Ignoring the preset's tone** — a corporate preset doesn't belong on a playful video

## Verification

- [ ] Fonts load correctly (check Google Fonts link)
- [ ] Color palette is consistent across all scenes
- [ ] Typography hierarchy is clear (headline > subhead > body)
- [ ] Contrast passes WCAG AA
- [ ] Design matches the video's emotional tone