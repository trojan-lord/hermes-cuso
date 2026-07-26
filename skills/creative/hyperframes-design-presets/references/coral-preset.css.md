# Coral Preset — Working CSS Template

Source: hyperframes.dev/design — "Coral" preset. Tested 2026-07-21.

## Fonts

```html
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```

## CSS Variables

```css
:root {
  --coral: #FF7F50;
  --cream: #FFFBF5;
  --dark: #2D2D2D;
  --coral-light: #FFB299;
  --coral-shadow: rgba(255, 127, 80, 0.15);
}
```

## Base Styles

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1920px; height: 1080px; overflow: hidden; }
body { background: var(--cream); font-family: 'Inter', sans-serif; color: var(--dark); }
```

## Typography Classes

```css
.headline {
  font-family: 'Bebas Neue', sans-serif;
  text-transform: uppercase;
  color: var(--coral);
  letter-spacing: 0.05em;
}
.body { font-family: 'Inter', sans-serif; color: var(--dark); }
.accent { color: var(--coral); font-weight: 600; }
.data-number {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 96px;
  color: var(--coral);
  letter-spacing: 0.02em;
}
```

## Decorative Elements

```css
.line {
  width: 120px; height: 3px;
  background: var(--coral);
  border-radius: 2px;
}
.dot {
  width: 12px; height: 12px;
  background: var(--coral);
  border-radius: 50%;
}
.grid-bg {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(var(--coral-shadow) 1px, transparent 1px),
    linear-gradient(90deg, var(--coral-shadow) 1px, transparent 1px);
  background-size: 60px 60px;
  opacity: 0.3;
}
```

## Usage Notes

- Headlines: 60-120px, always uppercase, always coral
- Body text: 16-28px, dark (#2D2D2D), Inter font
- Data numbers: 48-120px, Bebas Neue, coral accent
- Background: cream (#FFFBF5), never pure white
- Decorative lines: coral, 3px height, 120px width
- Grid overlay: 60px grid, 15% opacity, coral shadow color
- Contrast: coral on cream = 3.8:1 (use dark text for body, coral for headlines/decorative)
