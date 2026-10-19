---
name: static-site-dev
description: Build, merge, and verify multi-page static HTML/CSS/JS websites. Covers site composition from multiple sources, CSS extension patterns, asset management, and automated link/structure verification.
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [html, css, static-site, web, merge, verify, link-checking, composition]
    related_skills: [claude-design, popular-web-designs, sketch]
---

# Static Site Development

Build, merge, and verify multi-page static HTML/CSS/JS websites.

Use this skill when the task involves:
- Creating or scaffolding multi-page HTML sites from scratch
- Merging two or more HTML codebases into one
- Extending an existing site with new pages or sections
- Converting/redesigning static sites while preserving content
- Verifying link integrity and structure of HTML sites

Do NOT use this skill for:
- Designing one-off single-file HTML artifacts (use `claude-design`)
- Throwing away mockups (use `sketch`)
- Matching a known brand's design system (use `popular-web-designs`)

## Merge Workflow (Base + Enhance)

When combining two HTML sites into one:

1. **Read both codebases fully** — read every HTML file, the CSS, and the JS from both sites before writing anything. Understanding comes before creation.

2. **Inventory and diff** — for each page in the target site, identify:
   - Which source has the richer version of that page (more content, better structure, more features)
   - What unique content/sections exist only in one source
   - What CSS classes/styles are needed for new content

3. **Choose the base** — pick the source with the richer page structure, more complete CSS, and better JS as the base. This becomes the structural foundation.

4. **Base + Enhance strategy** — for each page:
   - Start with the base source's HTML structure (nav, footer, page template)
   - Insert unique content sections from the other source into the base template
   - Adapt new content to use the base's CSS classes where possible
   - Add new CSS only for components that don't exist in the base

5. **CSS extension pattern** — append new styles to the base CSS:
   ```css
   /* Section description (from other-source-name) */
   .new-component { ... }
   ```
   Use the base's CSS variables (`var(--gold)`, `var(--text-light)`, etc.) for new components so they inherit the design system.

6. **Assets** — copy assets from both sources, preferring the higher-quality or more complete versions.

7. **Verify** — run the verification script (see `scripts/verify-links.sh`) before declaring done.

## Key Patterns

### Parallel Reading
When analyzing two codebases, read all files from both in parallel batches. Each site's files are independent — no need to serialize reads across sites.

### CSS Class Mapping
When adapting content from Site B to Site A's CSS:
- Map Site B's `.card` → Site A's `.offer-card` if the visual role matches
- Don't duplicate existing class names; create new ones when the component is genuinely different
- Always use the base site's CSS variables for colors, spacing, and typography

### Link Path Normalization
When copying HTML between sites, fix all internal paths:
- `css/style.css` → `style.css` (if base uses flat structure)
- `js/main.js` → `main.js` (same)
- Ensure `href` and `src` attributes point to files that exist in the target directory

### Footer Consistency
Every page must have the same footer with the same links. Use one canonical footer and paste it identically into every page.

### Active State Navigation
Each page's nav must mark the current page with `class="active"` on the correct link. This is per-page, not shared.

## Deployment

For exposing local dev sites to the internet, see [references/cloudflare-tunneling.md](references/cloudflare-tunneling.md) — covers cloudflared quick tunnels (free, no account, random URLs).

## Verification

Always run the link verification script after building or modifying a static site. See `scripts/verify-links.sh`.

The script checks:
- All required files exist (HTML, CSS, JS, assets)
- Every HTML page links to all other pages (nav + footer consistency)
- All internal `href`/`src` references resolve to real files
- No stale path patterns from a source site (e.g., `css/` prefix when target uses flat structure)
- Favicons and key metadata present on all pages

## Pitfalls

- **Forgetting active states** — after copying a nav to all pages, each page needs its own `class="active"` on the right link. Don't use the same active class everywhere.
- **Stale path prefixes** — when copying HTML from a site with `css/style.css` and `js/main.js` paths into a flat-structure site, these break silently. Grep for `href="css/` and `src="js/` after merging.
- **Footer drift** — if you update the footer in one page but not others, links diverge. Always update all footers atomically or copy one canonical footer to all pages.
- **Missing CSS for new components** — when you add HTML for new sections, the CSS must also be added or the sections render unstyled. Verify by checking that every new class used in HTML exists in the CSS.
- **Over-appending CSS** — when extending a CSS file, append new blocks at the end with clear section comments. Don't insert into the middle of existing blocks.
