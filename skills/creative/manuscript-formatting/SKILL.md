---
name: manuscript-formatting
description: "Format creative writing into industry-standard manuscript .docx files, and answer questions about manuscript formatting, editing standards, fiction grammar/style rules, submission guidelines, and professional typesetting. Extract chapters from AI chat exports, clean artifacts, apply professional formatting. See references/standards.md for comprehensive formatting & editing knowledge bank."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [writing, manuscript, formatting, creative, docx, publishing]
    category: creative
    related_skills: [humanizer, platform-data-ingestion]
---

# Manuscript Formatting

Extract creative writing from AI chat exports (ChatGPT, etc.) and produce industry-standard manuscript .docx files ready for submission or review.

## When to Use

- User has written fiction in an AI chat and wants it formatted professionally
- User wants to extract specific content (chapters, drafts) from a ChatGPT export
- User asks for "manuscript format" or "submission-ready" document
- User has raw chapter text that needs cleaning and professional formatting
- User asks about fiction grammar rules (dialogue punctuation, em dashes, italics, tense/POV)
- User asks about editing levels (developmental, line, copy, proofreading)
- User asks about submission guidelines for agents/publishers
- User asks about typesetting standards for final book production (kerning, leading, widows/orphans)

## Reference: Standards Knowledge Bank

For comprehensive coverage of all five areas — manuscript format specs, editing levels, fiction grammar/style rules, submission guidelines, and typesetting standards — see:

**`references/standards.md`**

This file contains the full compiled reference from industry sources (CMOS, Kindlepreneur, Reedsy, Wikipedia typography). Use it when answering formatting/style questions that go beyond the AI-export extraction workflow below.

## Industry Standard Manuscript Format

Quick reference — see `references/standards.md` for the full version including all punctuation rules, submission checklists, genre word counts, and typesetting standards.

| Element | Format |
|---------|--------|
| Font | Times New Roman, 12pt |
| Spacing | Double-spaced, no extra space between paragraphs |
| Margins | 1 inch all sides (8.5" x 11" page) |
| Paragraphs | 0.5 inch first-line indent |
| Chapter headings | Centered, bold, 14-16pt, each starts a new page |
| Scene breaks | Three centered asterisks (* * *) |
| Title page | Title ~1/3 down (24pt bold), subtitle (16pt), author (14pt), word count at bottom |
| Dialogue | Standard curly quotes or straight quotes consistently |
| Section breaks | "#" or "---" in source -> "* * *" in output |

## Workflow

### Step 1: Locate Source Content

If from ChatGPT export:
```bash
# Find sessions by title
grep -l -i "search term" /tmp/chatgpt-export/chatgpt-data/conversations-*.json

# Or search Hermes DB (already imported)
session_search(query="chapter title", limit=5)
```

### Step 2: Extract Chapter Text

**From Hermes DB (preferred if imported):**
```python
import sqlite3
db_path = Path.home() / '.hermes' / 'state.db'
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Find session
cur.execute("SELECT id FROM sessions WHERE title LIKE '%search%'")
sid = cur.fetchone()[0]

# Get assistant messages > 500 words
cur.execute("""
    SELECT id, content, timestamp FROM messages
    WHERE session_id = ? AND role = 'assistant'
    ORDER BY timestamp
""", (sid,))
```

**From ChatGPT JSON directly:**
```python
# ChatGPT uses tree structure with parent pointers
# Walk backwards from current_node, then reverse
mapping = conv.get("mapping", {})
current = conv.get("current_node")
messages = []
seen = set()  # Cycle protection
while current and current not in seen:
    seen.add(current)
    node = mapping.get(current, {})
    msg = node.get("message")
    if msg and msg["author"]["role"] == "assistant":
        parts = msg.get("content", {}).get("parts", [])
        text = "\n".join(str(p) for p in parts if isinstance(p, str))
        if text.strip():
            messages.append({"text": text, "ts": msg.get("create_time", 0)})
    current = node.get("parent")
messages.reverse()
```

**Critical: ChatGPT splits long outputs across messages.** A single chapter may be in 2-3 separate messages. Identify by content markers ("Part 1", "Part 2", character names) and combine.

#### Marker-Based Extraction (Preferred for Chapter Prose)

ChatGPT conversations mix planning, brainstorming, and prose in the same session. Don't grab every long assistant message — **filter first, then extract between known markers**:

```python
# Step A: Filter to candidate messages (role + length + content markers)
candidates = []
for msg in messages:
    if msg["role"] != "assistant":
        continue
    text = msg["text"]
    lower = text.lower()
    if len(text) > 3000 and ("chapter" in lower or "prologue" in lower):
        candidates.append(msg)

# Step B: Extract prose between start/end markers
# ChatGPT chapter messages typically have a preamble, then ### Chapter N,
# then prose, then **End of Chapter N**
for msg in candidates:
    start = msg["text"].find("### **Chapter 1: The Spring Corpse**")
    end = msg["text"].find("**End of Chapter 1**")
    if start >= 0 and end >= 0:
        chapter_prose = msg["text"][start:end + len("**End of Chapter 1**")].strip()
```

**Why `str.find()` + markers instead of regex**: Chapter prose in ChatGPT exports is wrapped in markdown (`### **Chapter Title**` ... `**End of Chapter N**`). These markers are consistent enough to use as extraction boundaries. Regex-based `re.split(r'^Chapter\s+\d+...')` works for clean text but fails when the conversation mixes planning bullets, markdown tables, and prose in the same message.

**When to use which approach**:
- **Marker-based** (`str.find`): When content has consistent start/end markers (most ChatGPT creative writing)
- **Regex-based**: When scanning cleaned text for chapter boundaries after all messages are already concatenated

### Step 3: Clean Artifacts

Remove from extracted text:
- ChatGPT framing ("Got it.", "Perfect.", "Here's **Chapter...")
- Word count summaries ("**Roman's Section:** ~2,050 words")
- Markdown headers (### **Chapter Title**) -> plain text
- Bold/italic markers (**text** -> text, *text* -> text)
- Horizontal rules (--- -> * * * for scene breaks)
- Source metadata ("Source: ChatGPT session...")
- Planning text ("If you want, we can move to Chapter 6...")

```python
import re
def clean_ai_artifacts(text):
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        s = line.strip()
        # Skip framing
        if s.startswith(('Got it.', 'Perfect.', 'Understood.', "Here's", "Here is")):
            if 'Chapter' in s or 'chapter' in s:
                continue
        if s.startswith(('Would you like', 'Just tell me', 'If you want')):
            continue
        if s.startswith(('**Roman', '**Jonah', '**Total', '**Novel', '**Page')):
            continue
        # Convert --- to scene breaks
        if re.match(r'^-{3,}$', s):
            cleaned.append('* * *')
            continue
        # Remove markdown
        s = re.sub(r'^#{1,4}\s+', '', s)
        s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
        s = re.sub(r'\*(.+?)\*', r'\1', s)
        cleaned.append(s)
    return '\n'.join(cleaned)
```

### Step 4: Structure Chapters

Detect chapter boundaries and organize:
```python
# Match "Chapter N: Title" patterns (top-level headings only)
CHAPTER_RE = re.compile(r'^Chapter\s+(\d+)\s*:\s*(.+)')

# Do NOT match sub-headers like:
#   "CHAPTER ONE — JONAH LEWIS"
#   "CHAPTER TWO — IMPULSE VS. RESTRAINT"
```

### Step 5: Format to .docx

Use `python-docx`:
```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING

doc = Document()
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(12)
style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE

# Title page, chapter headings, scene breaks, body paragraphs
# See format_manuscript.py for full implementation
```

### Step 6: Verify

```python
from docx import Document
doc = Document('output.docx')
total_words = sum(len(p.text.split()) for p in doc.paragraphs)
# Check chapter headings are 16pt bold centered
# Check body text is 12pt Times New Roman
# Check scene breaks are centered "* * *"
```

## Pitfalls

- **ChatGPT duplicate chapters**: The same chapter appears 3-5 times as drafts. Always use the latest timestamp (create_time) or the longest version.
- **Sub-headers matching chapter regex**: "CHAPTER ONE — JONAH LEWIS" looks like a chapter heading but is a section within a chapter. Only match "Chapter N: Title" patterns with colons.
- **Trailing spaces**: ChatGPT adds trailing spaces for markdown line breaks. Strip all trailing whitespace.
- **Metadata bleeding into output**: ChatGPT often includes word counts, page estimates, and "would you like me to continue?" text. Filter aggressively.
- **python-docx font enforcement**: Must set font on each run, not just the style. Use `_set_font(run)` helper to set ascii/hAnsi/cs fonts.
- **Title page spacing**: Use blank paragraphs to push title to ~1/3 down page. Word count goes at bottom.

## Formatter Scripts

### v1 (basic): `/tmp/chatgpt-export/format_manuscript.py`
- Times New Roman 12pt, basic chapter detection
- Works for quick formatting but misses some standards

### v2 (submission-standard, RECOMMENDED): `/tmp/chatgpt-export/format_manuscript_v2.py`
- **Courier New 12pt** (industry submission standard)
- Title page with title (18pt bold), subtitle, author, word count
- Chapter headings: 14pt bold centered, 3 blank lines before first paragraph
- Scene breaks: centered `* * *`
- Left-justified (not full-justified)
- 0.5" first-line paragraph indent
- Page numbers at bottom center
- "THE END" marker after final chapter
- CLI: `python format_manuscript_v2.py input.txt -o output.docx --title "Title" --author "Name"`

### PDF Conversion (fpdf2)
When LibreOffice is unavailable, use fpdf2 with a system Unicode font:
```python
from fpdf import FPDF
pdf = FPDF()
font_path = '/usr/share/fonts/Adwaita/AdwaitaSans-Regular.ttf'
pdf.add_font('Adwaita', '', font_path)
# Note: fpdf2 built-in fonts (Helvetica, etc.) do NOT support Unicode
# (curly quotes, em dashes, accented chars). Always use a TTF with Unicode coverage.
```

## Generating Long-Form Prose with Hermes Tools

When the task is *writing* novel chapters (not just formatting), the workflow differs from extraction. See **`references/long-form-generation.md`** for the full technical guide. Key points:

- **write_file has a ~8K token stream limit.** Writing an entire 18K-word output in one call times out. Write each chapter to its own file (`/tmp/chatgpt-export/ch03.txt` etc.), then concatenate with `cat ch03.txt ch04.txt ... > output.txt`.
- **patch tool causes duplicate lines** when expanding text near existing matching content. Always verify with `wc -w` and `grep` after each patch. Prefer writing complete chapter files over patching individual files to grow them.
- **Style matching**: Read existing source chapters first. Extract patterns: POV (first/second/third), sentence structure (long/short), vocabulary register, recurring imagery, dialogue ratio, interiority depth, paragraph length. Reproduce all consistently.

## Pitfalls (Lessons from Production)

- **User rejected formatting twice** before accepting v2. Key complaints: wrong font (Times New Roman vs Courier), missing page numbers, no "THE END", poor chapter heading spacing. Always match submission standards, not just "looks nice."
- **ChatGPT splits chapters across messages.** A single chapter may span 2-3 separate assistant messages. Identify by content markers ("Part 1", character names, chapter titles) and concatenate. Never extract just one message per chapter.
- **Sub-headers matching chapter regex**: "CHAPTER ONE — JONAH LEWIS" looks like a chapter heading but is a section within a chapter. Only match `"Chapter N: Title"` patterns with colons.
- **Duplicate chapter headings**: ChatGPT sometimes outputs the chapter heading twice (once as a markdown header, once as inline text). Deduplicate consecutive identical headings.
- **Trailing ChatGPT meta-text**: Lines like "Here's Chapter 1 — (Part 1: ..." or "**Roman's Section:** ~2,050 words" or "If you want, I can move to Chapter 6..." must be stripped. Filter aggressively.
- **Scene break rendering**: `---` in source must become `* * *` (centered) in output. Some formatters render `---` as horizontal rules instead of scene breaks.
- **Parallel narratives**: When a book has dual POV (e.g., Roman + Jonah), ensure both characters' sections appear in each chapter. Verify by checking chapter content for both character names.
- **Incomplete novels**: ChatGPT exports often contain only partial novels. Always check completeness before formatting — count chapters written vs chapters planned.
- **TTS Unicode failure**: When narrating manuscript text via voice memo, smart quotes (""), em dashes (—), and curly apostrophes can crash the TTS provider. Strip to ASCII before sending: `"->"`, `'->'`, `—->--`, `…->...`. The TTS provider script handles punctuation-based splitting but not Unicode glyphs. Always test a short sample first; if it fails, clean the full text.
- **"Read to me" = voice memo**: When the user says "read [something] to me" or "read this page," they want a voice memo (TTS), not typed text. Generate audio via `text_to_speech` and deliver with the MEDIA: tag.
