---
title: Google Docs HTML Export Parser
source: OBG Flag Book session (Aug 2026)
---

# Google Docs HTML Export Parsing

Google Docs HTML exports have a predictable structure that can be parsed with Python's `html.parser.HTMLParser`.

## Source Access

```bash
# Export as HTML (requires link sharing: anyone with link)
curl -sL "https://docs.google.com/document/d/{DOC_ID}/export?format=html" -o doc.html
```

If the doc requires login, the export returns a login page. The user must share the doc (view access) first.

## Google Docs HTML Structure

- Headings: `<h1 class="c6" id="..."><span class="c10 c8">text</span></h1>`
- Tables: `<table class="c5"><tr class="c7"><td class="c12" colspan="1" rowspan="1"><p class="c11"><span class="c8">text</span></p></td></tr></table>`
- Body paragraphs: `<p class="c18">text</p>` or `<p class="c0"><span class="c8">text</span></p>`
- CSS classes (c0, c5, c8, c10, c15, etc.) encode font sizes and styles but are NOT meaningful — strip them all
- HTML entities common: `&#39;` (apostrophe), `&plusmn;`, `&times;`, `&rarr;`, `&#11088;` (gold star emoji)

## Parser Pattern

Use `html.parser.HTMLParser` with a state machine tracking:
- `in_table` counter (for nested context)
- Current row (`self.row`) and cell parts (`self.cell_parts`)
- Current heading level and parts

### Key Rules

1. **All spans are colspan=1, rowspan=1** — no merged cells in Google Docs tables
2. **First row of every table is the header** — map to `<thead>`
3. **Cell text** is concatenation of all `<p>` and `<span>` text inside `<td>`, with `<br>` converted to space
4. **Empty h1s** (spacer headings with only whitespace) — skip
5. **Entity decoding** — Python's `convert_charrefs=True` handles most; manual decode for &#11088; (gold star)
6. **Body-level paragraphs** outside tables (class c18) are notes/annotations — keep as small italic text

### Minimal Parser Skeleton

```python
from html.parser import HTMLParser

class DocParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []   # ('h', level, text) | ('table', rows) | ('note', text)
        self.in_table = 0
        self.rows, self.row, self.cell_parts = None, None, None
        self.heading_level, self.heading_parts = None, None

    def handle_starttag(self, tag, attrs):
        if tag in ('h1','h2','h3','h4','h5','h6'):
            self.heading_level = int(tag[1]); self.heading_parts = []
        elif tag == 'table':
            self.in_table += 1; self.rows = []
        elif tag == 'tr' and self.in_table: self.row = []
        elif tag in ('td','th') and self.in_table: self.cell_parts = []
        elif tag == 'br' and self.cell_parts is not None: self.cell_parts.append(' ')

    def handle_data(self, data):
        if self.heading_parts is not None: self.heading_parts.append(data)
        elif self.cell_parts is not None: self.cell_parts.append(data)

    def handle_endtag(self, tag):
        import re
        if tag in ('h1','h2','h3','h4','h5','h6'):
            text = re.sub(r'\\s+', ' ', ''.join(self.heading_parts)).strip()
            if text: self.blocks.append(('h', self.heading_level, text))
            self.heading_level = self.heading_parts = None
        elif tag in ('td','th') and self.in_table and self.row is not None:
            text = re.sub(r'\\s+', ' ', ''.join(self.cell_parts)).strip()
            self.row.append(text); self.cell_parts = None
        elif tag == 'tr' and self.in_table and self.row is not None:
            self.rows.append(self.row); self.row = None
        elif tag == 'table':
            if self.rows: self.blocks.append(('table', self.rows))
            self.in_table -= 1; self.rows = None
```

## Heading Classification

For medical/study flag books, heading text patterns map to roles:

| Pattern | Role | CSS class |
|---------|------|-----------|
| Starts with book emoji (e.g. flag book) | Document title | .titleline |
| Contains "SECTION" or section divider | Section header | h1.section |
| Contains "MASTER TABLE" | Table title | h2.table-title |
| Starts with star | Rapid recall | h3.sub |
| Other emoji prefixes | Subsection | h3.sub |

## Common Pitfalls

- Google Docs exports 80+ tables with no rowspan/colspan — but other docs may differ. Always check first with: `re.findall(r'(?:colspan|rowspan)="(\\d+)"', html)` and verify all values are 1
- The export includes CSS classes with inline font sizes (14pt, 23pt, 17pt) — these are Google's formatting, not the user's intended sizes. Always strip and rebuild with your own CSS
- Entity `&#11088;` is the gold star emoji — it appears in heading text and may not decode with convert_charrefs. Handle with: `text.replace('&#11088;', '\\u2b50')`
- Some tables have empty trailing rows (e.g., the pregnancy signs table) — these are formatting artifacts, keep them for layout fidelity
- WeasyPrint needs `font-family` to include "Noto Color Emoji" for emoji rendering; otherwise they appear as empty boxes
