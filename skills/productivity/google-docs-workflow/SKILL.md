---
name: google-docs-workflow
description: "Use when a Google Doc link needs reading or reformatting."
tags: [google-docs, formatting, apps-script, export, productivity]
related_skills: [google-workspace]
---

# Google Docs Workflow (no-OAuth path)

Read, inspect, and reformat Google Docs when the machine has **no Google API credentials** (`~/.hermes/google_token.json` absent → the `google-workspace` skill reports `NOT_AUTHENTICATED`). This is the zero-setup route: export endpoints for reading, HTML parsing for diagnosis, and a pasted Apps Script for editing.

## When to use
- User drops a `docs.google.com/document/d/<ID>/edit` link and asks you to read/review/modify it
- "Apply this formatting throughout the doc" / "make headers Xpt and body Ypt like the last section" tasks
- Only fall back to this when `google-workspace` auth is unavailable — if OAuth IS configured, use `google-workspace` for direct API edits (it's the richer path)

## 1. Read the doc — export endpoints (plain curl, no auth)

```bash
# Text (loses all formatting)
curl -sL "https://docs.google.com/document/d/<ID>/export?format=txt" -o /tmp/gdoc.txt
# HTML (keeps structure + styles — needed for diagnosis)
curl -sL "https://docs.google.com/document/d/<ID>/export?format=html" -o /tmp/gdoc.html
```

- **Login-wall detection**: if the response is `<!DOCTYPE html>` with Google sign-in CSS / "Sign in" page, the doc is **not shared**. Don't fight it — tell the user to set **Share → General access → Anyone with the link → Viewer**, then retry. Docs shared that way work from plain curl immediately.
- `export?format=txt` output is tab-separated table content — easy to read with `read_file`.
- Google-native formats (Sheets→csv, Slides→pdf, Drawings→png) also export; `format=pdf` works for docs.

## 2. Diagnose formatting — parse the HTML export

Google Docs HTML exports keep a `<style>` block mapping classes → properties, and every element carries its class list. To find which font sizes are used where:

```python
import re
html = open('/tmp/gdoc.html', encoding='utf-8').read()
style = re.search(r'<style[^>]*>(.*?)</style>', html, re.S).group(1)
fs_map = {}
for m in re.finditer(r'\.(c\d+)\{([^}]*)\}', style):
    cls, body = m.group(1), m.group(2)
    fs = re.search(r'font-size:([\d.]+pt)', body)
    if fs: fs_map[cls] = fs.group(1)

# Headings carry size via their <span> classes:
for m in re.finditer(r'<(h\d) class="([^"]+)"[^>]*><span class="([^"]+)">(.*?)</span></h\d>', html, re.S):
    tag, hcls, scls, inner = m.groups()
    sizes = [fs_map.get(x, '11') for x in scls.split()]
    text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', inner)).strip()
    print(f"[{tag} span {sizes}] {text[:70]}")
```

Key facts learned the hard way:
- **Emoji are HTML-entity-encoded** (`&#128681;` = 🚩, `&#11088;` = ⭐). Regex-matching raw emoji against the export fails. Match on ASCII text like `MASTER TABLE`, or decode entities first.
- Font size lives on **span classes inside headings**, not the heading tag itself. `font-size:14pt` on a span class means "headers are 14pt"; `default` (no class font) usually means the base 11pt body size.
- A doc built by copy-paste is almost always a **patchwork**: same logical element (e.g. "MASTER TABLE" titles) may be 23pt in one section, 14pt in another, 13pt/17pt/18pt elsewhere. One section may even use a different heading level (h3 vs h1). Diagnose before proposing a fix — the user's "last section" is usually the accidental clean one to copy.

## 3. Edit the doc — Apps Script fallback (zero credentials)

When there's no OAuth, you cannot write via API. The clean path: give the user a **Google Apps Script** they paste into the doc and run — it executes with *their* auth, no client credentials needed.

1. Open doc in browser → **Extensions → Apps Script**
2. Replace default code with the template (see `templates/format-headings-apps-script.gs`)
3. **Run** → pick the main function → first run asks authorization: **Advanced → Go to <project name> (unsafe) → Allow** — expected for personal scripts
4. Switch back to the doc tab; done. Safe to run twice (idempotent).

Apps Script essentials for doc-wide passes:
- `DocumentApp.getActiveDocument().getBody()` → `getNumChildren()` / `getChild(i)` / `getType()` to walk paragraphs, tables, list items
- **Table content needs recursive descent**: `TABLE` → `getRow(r)` → `getCell(c)` → walk again
- Paragraph-level `setAttributes({FONT_SIZE: n})` can be **overridden by run-level spans** that carry their own sizes — also call `p.editAsText().setFontSize(0, text.length - 1, n)` to normalize runs
- Skip empty/spacer paragraphs (`getText().length === 0`)
- `isHeader` test: paragraph `getHeading() !== NORMAL` and not inside a table

## Pitfalls
- Don't claim you edited the doc when you couldn't — the agent has no write access without OAuth. Deliver the script + run instructions, and say plainly what you did and didn't do.
- **Confirm scope before normalizing**: a blanket "everything to 14/11" will shrink big title/divider blocks (e.g. a 23pt "DOC TITLE" banner) down to body-adjacent size. Ask if the user wants those preserved; the template has a `keepBigTitles` flag for that.
- `google-workspace` skill (`setup.py --check`) is the first thing to run to confirm auth state — it prints `NOT_AUTHENTICATED` or `AUTHENTICATED` in seconds.
- Never write the Apps Script into a file the user can't see — save it under `~/<task-folder>/` and paste the full code in chat too.

## Support files
- `templates/format-headings-apps-script.gs` — ready-to-paste Apps Script: headings → 14pt, body/table content → 11pt (edit the two sizes at the top)
- `references/obg-flagbook-formatting.md` — worked example: diagnosis output and script result for a real 71-table study doc
