---
name: html-to-print-pdf
description: "Structured HTML to print-quality PDF via WeasyPrint."
version: 1.0.0
author: Cuso
tags: [pdf, weasyprint, html, print, google-docs]
related_skills: [pdf, docx]
---

# HTML-to-Print-PDF

Convert structured HTML (Google Docs exports, web pages, table-heavy documents) to print-quality PDFs.

## When to Use

User has structured HTML content and needs a compact, readable, print-ready PDF. Covers study guides, reference tables, medical flag books, and any document that needs to go from screen to paper.

## Core Tool: WeasyPrint

```bash
pip install weasyprint
```

```python
from weasyprint import HTML
HTML(string=html_content).write_pdf("output.pdf")
```

**Why WeasyPrint:** Respects CSS @page, thead repetition, page-break-inside, font fallback chains. LibreOffice has poor CSS support. Reportlab is painful for HTML tables.

## Print Design Specs

These defaults produce a dense-but-usable A4 print document.

| Element | Size |
|---------|------|
| Section headers | 13-13.5pt bold |
| Table titles | 11.5-12pt bold |
| Body/table text | 9.5-10pt sans-serif |
| Header cells | 9.5pt bold, gray bg |
| Cell padding | 2-3px vert, 4px horiz |
| Borders | 0.5-0.6pt light gray |
| Margins | 10-12mm A4 |

## Essential Print CSS

```css
@page { size: A4; margin: 12mm 10mm 14mm 10mm; }
body { font-family: "Liberation Sans","DejaVu Sans","Noto Color Emoji",sans-serif; font-size: 10pt; line-height: 1.32; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th { background: #e4e4e4; border: 0.6pt solid #999; padding: 3px 4px; font-size: 9.5pt; }
td { border: 0.6pt solid #aaa; padding: 3px 4px; font-size: 9.5pt; }
```

## Workflow

1. Get source HTML (curl export, web_extract, or build from parsed content)
2. Parse structured blocks: headings + tables in document order
3. Rebuild as clean HTML, stripping source CSS cruft
4. Apply print CSS from specs above
5. Render with WeasyPrint
6. Verify: pdfinfo for page count, pdftoppm for visual check

## Pitfalls

- Google Docs HTML uses inline CSS classes with hardcoded sizes: strip and rebuild, do NOT preserve
- Tables >5 columns on A4 portrait get tight at 9pt
- page-break-inside avoid on tall tables causes gaps: use thead repeat instead
- Noto Color Emoji required for emoji: check with fc-list | grep emoji
- pango + cairo must be installed (pre-installed on Arch, manual on minimal Docker)
- Google OAuth wall: cannot edit docs directly without credentials; export HTML and rebuild as PDF instead

## Verification

1. pdfinfo output.pdf for page count and A4 size
2. pdftoppm -png -r 80 -f 1 -l 3 output.pdf preview for visual spot-check
3. Count tables in output HTML vs source document

## Reference

- google-docs-parsing.md for the Google Docs HTML export parser
