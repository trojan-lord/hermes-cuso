# HyperFrames Design Presets

Source: https://www.hyperframes.dev/design/

## What Are Presets

Presets are curated visual design languages — not code templates. Each preset specifies:
- **Display font** (headlines, large text)
- **Body font** (reading text, labels)
- **Background color** (canvas)
- **Accent color** (highlights, numbers, decorative elements)
- **Layout character** (hairline rules, grid system, shadows)

You apply presets by rewriting CSS in an existing composition. The HTML structure and GSAP animations stay the same.

## Full Preset Catalog (v0.7.64)

### Biennale Yellow
- Display: Instrument Serif
- Background: warm parchment
- Accent: solar yellow bloom
- Ink: indigo
- Rules: 1px hairline
- Vibe: art gallery, exhibition catalog

### BlockFrame
- Style: Maximalist neobrutalist
- Borders: thick black
- Shadows: hard offset candy accents
- Vibe: protest poster, brutalist web

### Blue Professional
- Display: Space Grotesk
- Body: Inter
- Background: corporate parchment
- Accent: cobalt primary
- Vibe: enterprise, SaaS landing page

### Bold Poster
- Display: Shrikhand (tilted)
- Accent: red on cream
- Vibe: magazine cover, editorial splash

### Broadside
- Display: Barlow
- Background: raw cream on ink
- Accent: fire-orange register
- Vibe: industrial newsprint poster

### Capsule
- Display: Bodoni Moda (serif)
- Background: cream paper
- Palette: candy
- Vibe: pill-shaped editorial, fashion

### Cartesian
- Style: Minimal sparse
- Background: warm parchment
- Display: ink display type
- Accents: taupe
- Rules: hairline
- Vibe: architecture portfolio, Swiss design

### Cobalt Grid
- Display: Newsreader
- Body: Hanken Grotesk
- Background: editorial parchment
- System: cobalt grid
- Vibe: newspaper, data journalism

### Coral
- Display: Bebas Neue (uppercase)
- Body: Inter
- Background: cream (#FFFBF5)
- Accent: coral (#FF7F50)
- Vibe: bold editorial, clean corporate

### Creative Mode
- Display: Archivo Black
- Data: JetBrains Mono
- Background: cream
- Palette: saturated candy accents
- Vibe: dev tools, hackathon branding

### Daisy Days
- Display: Fredoka
- Body: Quicksand
- Style: 3px charcoal outlines, hard offset shadows
- Vibe: children's content, garden party

### Editorial Forest
- Display: Source Serif 4
- Chrome: JetBrains Mono
- Palette: green/pink/cream triad
- Rules: hairline
- Vibe: literary magazine, nature editorial

## Applying a Preset (Redesign Workflow)

1. Read the original composition — catalog every scene, timing, data attributes
2. Extract the preset's design tokens (fonts, colors, spacing)
3. Rewrite only CSS: `font-family`, `color`, `background-color`, `border`, `box-shadow`, `text-transform`
4. Preserve ALL:
   - HTML structure and class names
   - `data-track-label`, `data-start`, `data-duration`, `data-track-index` attributes
   - GSAP timeline code and animation targets
   - Composition ID and meta.json
5. Lint → validate → render

## design.md to frame.md Conversion

The design page accepts a `design.md` upload (brand guidelines) and outputs a `frame.md` (composition directive). The frame.md describes pacing, scale, dwell, and motion for the 16:9 frame. Drop it into a HyperFrames project as the composition spec.
