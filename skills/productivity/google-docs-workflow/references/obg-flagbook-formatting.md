# Worked example: OBG FLAG BOOK formatting pass (Aug 2026)

Real diagnosis + fix for a 71-table NEET PG study doc ("OBG FLAG BOOK", ~36 KB text export).
User request: "headers in 14pt and subject matter 11pt, just like the last section."

## Diagnosis from `export?format=html`

Size distribution in the doc was a copy-paste patchwork:

| Element | Size found | Notes |
|---|---|---|
| "OBG FLAG BOOK" title blocks (3×) | 23pt | big banners |
| MASTER TABLE 3–27 titles (Embryology→Fetal Medicine) | 23pt | the "inconsistent" sections |
| MASTER TABLE 28+ (Placenta onward) | 14pt | matches what user wanted |
| MASTER TABLE 49 (VVF) | 18pt | lone outlier |
| MASTER TABLE 37 | h3 element instead of h1 | wrong heading level |
| "PAS Summary", "Clinical Criteria", "Laboratory Criteria" | 13pt | sub-headers |
| ⭐ "Rapid Recall" / "One-Page" lines (h2) | 17pt | recall sections |
| All table cell content | 11pt | already consistent |

Net effect: the "last section" (Reproductive Endocrinology, tables 66–71) was the only
uniform block — 14pt h1 titles + 11pt content. Every earlier section drifted.

## How the sizes were found

1. `curl -sL "<doc>/export?format=html" -o /tmp/gdoc.html`
2. Parse `<style>` block: `\.(c\d+)\{([^}]*)\}` → regex `font-size:([\d.]+pt)` → class→size map
3. Walk headings: `<h\d class="..."><span class="cXX cYY">` — resolved each span class
   against the map. Span classes hold the size, NOT the heading tag.
4. Emoji trap: export encodes emoji as HTML entities (🚩 = `&#128681;`), so matching
   headers by emoji fails — match `MASTER TABLE` text instead.

## Fix delivered

Google Apps Script (`formatDoc` in `templates/format-headings-apps-script.gs`):
walk body children; PARAGRAPH with heading != NORMAL and not in table → 14pt;
everything else (incl. recursive TABLE descent) → 11pt; `editAsText().setFontSize()`
overrides run-level spans that paragraph `setAttributes` alone misses.

User ran it via Extensions → Apps Script → paste → Run → authorize (Advanced →
"Go to <project> (unsafe)" → Allow). Only font sizes touched; bold/colors/structure preserved.

## Lesson reinforced

For study docs the user maintains, ALWAYS confirm scope before normalizing: the 23pt
"OBG FLAG BOOK" banners and 17pt rapid-recall lines get flattened by a blanket
14/11 pass. Offer the `KEEP_BIG_TITLES` flag or an explicit carve-out for dividers.
