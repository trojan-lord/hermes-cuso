---
name: astryx
description: "Meta's open-source Astryx design system — 105+ React components, theming, dark mode. Use when building React UIs, component demos, dashboards, or web apps with Astryx. Covers installation, setup, component availability, and Vite integration."
version: 1.0.0
author: Cuso
tags: [react, design-system, components, ui, meta, astryx]
related_skills: [hyperframes-design-presets, popular-web-designs, claude-design]
---

# Astryx Design System

Meta's open-source design system — 8 years of internal use, 13,000+ apps at Meta. Now public as `@astryxdesign/core`.

## Overview

- **105+ accessible React components** — buttons, forms, modals, tables, nav, etc.
- **Built on React + StyleX** — but consumers don't need StyleX
- **Brand-level theming** via CSS custom properties
- **Dark mode** built in
- **CLI + MCP** for AI agents to scaffold projects
- **Repo:** `facebook/astryx` on GitHub (★10K+)
- **Docs:** https://astryx.atmeta.com
- **Status:** Beta (v0.1.7 as of 2026-07-21)

## Installation

```bash
npm install @astryxdesign/core @astryxdesign/theme-neutral
```

For a Vite + React project:

```bash
mkdir my-project && cd my-project
npm init -y
npm install @astryxdesign/core @astryxdesign/theme-neutral react react-dom
npm install -D @vitejs/plugin-react vite
```

## CSS Imports

Always import in this order:

```js
// In main.jsx or entry point
import '@astryxdesign/core/astryx.css'      // Core styles
import '@astryxdesign/theme-neutral/theme.css' // Theme tokens
import '@astryxdesign/core/reset.css'          // CSS reset
```

## Available Components (verified v0.1.7)

These components exist in `dist/` and import correctly:

**Layout:** Stack, HStack, VStack, Grid, Center, Layout, Divider, Resizable, Section, AspectRatio

**Display:** Heading, Text, Badge, StatusDot, Skeleton, Code, CodeBlock, Blockquote, Citation, Markdown

**Buttons:** Button, ButtonGroup, IconButton, ToggleButton

**Forms:** TextInput, TextArea, NumberInput, Slider, Switch, CheckboxInput, CheckboxList, RadioList, SelectableCard, Selector, MultiSelector, Typeahead, FileInput, DateInput, DateRangeInput, DateTimeInput, TimeInput, Field, FieldStatus, FormLayout, InputGroup, Tokenizer, Token

**Navigation:** TopNav, SideNav, MobileNav, Breadcrumbs, TabList, Pagination, NavMenu, NavIcon, MoreMenu

**Overlays:** Dialog, AlertDialog, Popover, Tooltip, Toast, DropdownMenu, ContextMenu, CommandPalette, Lightbox, Layer, Overlay, HoverCard

**Data:** Table, List, TreeList, MetadataList, EmptyState, ProgressBar

**Media:** Avatar, AvatarGroup, Thumbnail, Carousel

**Containers:** Card, ClickableCard, AppShell, Collapsible, OverflowList, Outline, Banner, Toolbar

**Utilities:** Icon, Kbd, VisuallyHidden, SizeContext, InteractiveRoleContext

## ⚠️ Pitfalls

### Some exports don't exist at runtime

The `package.json` exports map lists ~120 entries, but some components that appear in the exports **do not exist** in `dist/` and will fail at import time:

- `Alert` — does NOT exist. Use `Toast` or `Banner` instead.
- `Tag` — does NOT exist. Use `Badge` or `Token` instead.

**Always verify a component exists before importing:**
```bash
ls node_modules/@astryxdesign/core/dist/ | grep -i <ComponentName>
```

### Component prop variations

Props may differ from what you'd expect from similar libraries. Always check the actual component's TypeScript definitions or Storybook before assuming prop names.

### StyleX is internal

Astryx uses StyleX internally but consumers don't adopt it. Override styles with `className` using Tailwind, CSS modules, or plain CSS.

### Theme customization

Themes are CSS custom property overrides — no forking needed:
```css
:root {
  --astryx-color-primary: #your-color;
  --astryx-color-background: #your-bg;
}
```

## Vite Config

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { port: 5173, host: true }
})
```

## Quick Demo Pattern

```jsx
import React from 'react'
import { Button } from '@astryxdesign/core/Button'
import { Card } from '@astryxdesign/core/Card'
import { Heading } from '@astryxdesign/core/Heading'
import { VStack } from '@astryxdesign/core/VStack'

export default function App() {
  return (
    <Card>
      <VStack gap="1rem">
        <Heading level={2}>Hello Astryx</Heading>
        <Button variant="primary">Click me</Button>
      </VStack>
    </Card>
  )
}
```

## Design System Comparison

| Feature | Astryx | Radix | shadcn/ui |
|---------|--------|-------|-----------|
| Components | 105+ | 30+ | 50+ |
| Theming | CSS vars | CSS vars | Tailwind |
| StyleX | Internal | No | No |
| Agent-ready | Yes (MCP) | No | No |
| Maturity | 8 years internal | 4 years | 2 years |

## When to Use

- Building a **dashboard** or **web UI** for monitoring projects
- Quick **prototype** or **demo app**
- Need **production-grade** accessible components
- Want **agent-friendly** design system (CLI + MCP)
- Building something where **Meta's design language** fits

## When NOT to Use

- HyperFrames videos (use HTML/CSS directly)
- PPTX generation (use pptxgenjs)
- Static HTML pages (use popular-web-designs skill)
- ESP32 firmware (obviously)
