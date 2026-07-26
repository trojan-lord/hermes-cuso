---
name: medical-diagrams
description: "Generate medical/educational diagrams — mechanisms, pathways, life cycles, cascades. Excalidraw for editable hand-drawn flowcharts, HTML/CSS for polished reference versions. Also covers screenshot capture of HTML diagrams."
version: 1.0.0
author: Hermes Agent
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [medical, education, diagrams, flowcharts, pathways, excalidraw, svg]
    related_skills: [excalidraw, architecture-diagram]
---

# Medical Diagrams

Generate visual diagrams for medical and educational content: mechanisms of action, disease pathways, life cycles, signaling cascades, pathophysiology flowcharts, and concept maps.

## When to use

- User asks about a biological mechanism, pathway, or process
- User wants a visual representation of how something works
- User explicitly requests a diagram, flowchart, or visual explanation
- Topic involves branching decisions, feedback loops, or multi-stage processes

## Two rendering approaches

### 1. Excalidraw (preferred for medical content)

**Best for:** editable, hand-drawn style flowcharts. User can open in excalidraw.com, rearrange, annotate, add drug targets.

**Use when:** user wants to study/interact with the diagram, or content has branching/looping pathways.

**Load the excalidraw skill** (`skill_view(name='excalidraw')`) and follow its element format. Key additions for medical content:

- Use **color zones** with background rectangles to group related stages (e.g., human host vs. mosquito host, intracellular vs. extracellular)
- Use **dashed arrows** for inter-compartment transitions (e.g., crossing a membrane, moving between hosts)
- Use **labeled arrows** for molecules/steps that trigger transitions
- Use **diamonds** for decision points (e.g., "Does the patient respond to treatment?")
- Minimum 30px gap between elements to avoid visual clutter
- Titles should be descriptive: "JAK-STAT Signaling Pathway" not just "Signaling"

**File output:** `~/Documents/research/<topic>-excalidraw.excalidraw`

**Shareable link:** Run `python skills/diagramming/excalidraw/scripts/upload.py <file>` (requires `cryptography` pip package).

### 2. HTML/CSS/SVG (polished reference)

**Best for:** clean, dark-themed reference diagrams. Good for presentations or study material.

**Use when:** user wants a polished output or explicitly wants HTML/CSS.

**Workflow:**
1. Write a self-contained HTML file with inline SVG
2. Use the architecture-diagram skill's visual language (dark background, grid, color-coded boxes) **OR** a custom light-themed medical layout
3. Include: title, numbered stages, arrows with labels, legend, summary cards
4. Save to `~/Documents/research/<topic>-architecture.html`

**File output:** `~/Documents/research/<topic>-architecture.html`

**Caution:** The architecture-diagram skill is designed for software infrastructure. For medical content, either adapt its visual language (repurpose color categories: cyan=blood, violet=intracellular, amber=extracellular, etc.) or build a custom layout. Don't force the infrastructure template onto biological content.

## Screenshot capture

To generate PNG screenshots of HTML diagrams (for Discord, documentation, etc.):

```python
import asyncio
from playwright.async_api import async_playwright

async def screenshot_html(html_path, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto(f"file://{html_path}")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=output_path, full_page=True)
        await browser.close()

asyncio.run(screenshot_html("/path/to/diagram.html", "/path/to/output.png"))
```

**Setup (one-time, if playwright not installed):**
```bash
uv venv /tmp/ss-venv
uv pip install --python /tmp/ss-venv/bin/python playwright
/tmp/ss-venv/bin/python -m playwright install chromium
```

**For Excalidraw screenshots:** Open excalidraw.com, load the .excalidraw file via React fiber API (see session transcript for approach), then screenshot.

## Design principles for medical diagrams

1. **Color-code by compartment/location**, not by importance. Consistent color = consistent meaning.
2. **Show directionality.** Arrows must flow in the correct biological direction. Don't make users guess.
3. **Label transitions, not just nodes.** The arrow from "Ligand binds receptor" to "Receptor activated" should be labeled with the mechanism (e.g., "dimerization").
4. **Indicate reversibility.** Double-headed arrows for reversible steps, single-headed for irreversible.
5. **Mark drug targets explicitly.** If relevant, show where interventions act (e.g., with a red X or a different color).
6. **Include scale/context.** A small label indicating "intracellular" vs "extracellular" or "human host" vs "vector" prevents confusion.

## User preference: show both formats

When the user asks for a diagram, offer both Excalidraw and HTML/CSS versions. The user responded well to seeing both side by side — Excalidraw for studying/editing, HTML for polished reference. Default to generating both unless the user specifies one. Generate both in parallel via delegate_task to save time.

## Pitfalls

- **Architecture-diagram skill is NOT suited for medical/biological content.** It's designed for software infrastructure (dark grid aesthetic, tech color coding). For medical content, use Excalidraw (preferred) or build a custom HTML layout. Repurposing the architecture template produces output the user described as "a square peg in a round hole." If you do use it, explicitly reassign color categories (cyan=blood, violet=intracellular, amber=vector, etc.) and warn the user it's a stylistic mismatch.
- **Don't overload a single diagram.** If a pathway has 20+ steps, split into sub-diagrams or use background zones to group phases.
- **Font size matters.** Minimum fontSize 16 in Excalidraw. Small text is unreadable on screens.
- **Check arrow bindings.** Missing `containerId` on bound text produces blank shapes. Always verify both sides of the binding.
- **Playwright screenshots require the page to fully load.** Use `wait_for_timeout(2000)` for font loading, longer for animations.
