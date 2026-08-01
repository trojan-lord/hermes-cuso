---
name: web-research
description: Research topics across web sources when standard search engines are blocked or inadequate. Multi-source triangulation, fallback search engines, transcript/media databases, fan wikis, and source reliability assessment. Use when user asks to research a topic, find information about X, build a character/concept analysis, or gather data that requires visiting multiple websites.
tags: [research, web, search, scraping, character-analysis, media]
---

# Web Research

Multi-source web research methodology for building comprehensive knowledge on a topic — especially when Google and common sources are blocked by bot detection.

## When to Load

- User asks to research a person, character, concept, show, product, etc.
- User wants a comprehensive analysis requiring multiple web sources
- Standard search (Google) is blocked or returns no results
- Research requires scraping actual content (transcripts, reviews, wikis)

## Core Workflow

### 1. Parallel Source Discovery (Batch Upfront)

Fire multiple search/extraction attempts simultaneously rather than serially:

```
# Search DuckDuckGo HTML (bypasses bot detection)
curl -s "https://html.duckduckgo.com/html/?q=QUERY" -A "Mozilla/5.0..."

# Try known authoritative URLs directly
curl -s "https://tvtropes.org/pmwiki/pmwiki.php/..." -A "Mozilla/5.0..."
curl -s "https://EN_WIKI_URL" -A "Mozilla/5.0..."

# Reddit JSON API (appends .json to any reddit URL)
curl -s "https://www.reddit.com/r/SUBREDDIT/search.json?q=QUERY&sort=top&t=year"
```

**Critical**: Always include a realistic User-Agent. Many sites block requests without one.

### 2. Reusable HTML Extraction Script (Avoid Quoting Hell)

When doing multi-source web research, **write a reusable extraction script once** and pipe every source through it. Inline `python3 -c` with complex HTML parsing breaks on shell quoting.

```python
# Write to /tmp/extract.py at session start, reuse for every curl call
import sys
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip = True
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self.skip = False
    def handle_data(self, d):
        if not self.skip:
            s = d.strip()
            if s:
                self.text.append(s)
    def get_text(self):
        return " ".join(self.text)

p = TextExtractor()
p.feed(sys.stdin.read())
print(p.get_text()[:8000])
```

**Usage:**
```bash
curl -sL -H 'User-Agent: Mozilla/5.0 ...' 'URL' | python3 /tmp/extract.py
curl -sL -H 'User-Agent: Mozilla/5.0 ...' 'URL2' | python3 /tmp/extract.py
# No quoting issues. Consistent output. Easy to modify once.
```

### 3. Fallback Search When Google is Blocked

Google frequently blocks headless browsers and curl. **DuckDuckGo's HTML endpoint** is the primary fallback:

```bash
curl -s "https://html.duckduckgo.com/html/?q=YOUR+QUERY" \
  -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
```

Parse results with this regex pattern:
```python
results = re.findall(
    r'class="result__title".*?href="(.*?)".*?>(.*?)</a>.*?'
    r'class="result__snippet".*?>(.*?)</span>',
    html, re.DOTALL
)
```

#### Bing via Browser (when DuckDuckGo CAPTCHAs)

DuckDuckGo now throws a "select all squares containing a duck" CAPTCHA at headless traffic — both `html.duckduckgo.com` via curl (returns HTTP 200 but an empty regex parse) AND the browser. **Do not retry DDG**; switch to Bing:

1. `browser_navigate` to `https://www.bing.com/search?q=QUERY` (quote exact phrases with `%22`).
2. Bing curl scraping also fails — the page is a JS shell (HTTP 200 but zero `b_algo` elements). Extract results with `browser_console` instead:
```javascript
(() => {
  const results = document.querySelectorAll('#b_results > li');
  let out = [];
  results.forEach((li, i) => {
    const titleEl = li.querySelector('h2');
    const urlEl = li.querySelector('cite, .b_attribution');
    const snipEl = li.querySelector('.b_caption p, .b_lineclamp2, .b_lineclamp3, .b_lineclamp4');
    if (titleEl) {
      out.push(`${i+1}. ${titleEl.innerText}\n   ${snipEl ? snipEl.innerText.substring(0,250) : ''}\n   ${urlEl ? urlEl.innerText : ''}`);
    }
  });
  return out.join('\n\n') || 'no results found';
})()
```
3. Result hrefs are Bing redirect wrappers (`bing.com/ck/a?...&u=a1aHR0cHM6...`). The `u=` query param is **base64 of the real URL** — decode it:
```bash
python3 -c "import base64,sys; print(base64.b64decode(sys.argv[1]).decode())" 'a1aHR0cHM6Ly93d3cuYmJjLmNvbS9uZXdzL2FydGljbGVzL2NkeDg1dmtrMGdrbw=='
```
(Or grab `h2 a` hrefs via console and decode each in a loop.) Then curl the decoded article URL directly with a realistic User-Agent and pipe through the extraction script — news sites (BBC, Guardian, CNN) serve full text fine to curl once you have the real URL instead of guessing slugs. Verified July 2026: this path got 10 usable results when Google, DDG-HTML, and Bing-curl all failed.

### 3. Source Hierarchy for Different Topics

| Topic Type | Best Sources | Notes |
|---|---|---|
| TV/Film characters | TV Tropes (Characters/ + WesternAnimation/) | Most detailed character tropes and dialogue |
| TV/Film dialogue | **WikiQuote** (`en.wikiquote.org/wiki/SHOW_(film)`) + SpringfieldSpringfield.co.uk | WikiQuote has full film scene dialogue with character attribution — excellent for character speech patterns. SpringfieldSpringfield for episode transcripts; use `s01e01` format. |
| Book/film character quotes | **Goodreads** (`goodreads.com/quotes/tag/CHARACTER`) | Paginated (`?page=1`, `?page=2`). Returns clean, attributed quotes via `class="quoteText"` blocks. Single best source for volume character quotes — often 15-20+ per character. Parse with `re.findall(r'class="quoteText">(.*?)</span>', html, re.DOTALL)`. |
| Literary/book characters | **LitCharts, Shmoop, Goodreads** | Per-chapter character analyses with thematic breakdowns, quotes, timeline. Often accessible when Fandom/Google are blocked. LitCharts tags quotes by character and chapter. Goodreads for quote volume. |
| Literary/encyclopedic | SF Encyclopedia, Wikipedia API | Dense plot summaries, thematic analysis |
| Creator interviews | accio-quote.org (HP), fandom-specific archives | Has a **curated topic index** (Characters → sub-pages like "Students", "Staff", "Voldemort"; Wizarding World → "Animals & Creatures", "Death", "Wands"; Books 1-7) — navigate the topic index FIRST before brute-force grepping individual interviews. Topic pages collect all related quotes from across interviews with links to full sources. |
| Fan community | Reddit JSON API, dedicated wikis | Opinions, theories, corrections |
| Academic | arXiv, Google Scholar | Papers, citations |

See `references/source-reliability.md` for detailed notes on which sources are trustworthy vs. AI-generated.

### 4. Content Extraction Patterns

**TV Tropes character pages** — richest source for character analysis:
```bash
curl -s "https://tvtropes.org/pmwiki/pmwiki.php/Characters/SHOW_NAME" \
  -A "Mozilla/5.0" | python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub(r'<[^>]+>', ' ', html)
text = re.sub(r'\s+', ' ', text)
idx = text.find('CHARACTER_NAME')
if idx >= 0: print(text[idx:idx+8000])
"
```

**Episode transcripts** (SpringfieldSpringfield):
```bash
curl -s "https://www.springfieldspringfield.co.uk/view_episode_scripts.php?\
tv-show=SHOW_NAME&episode=s01e01" -A "Mozilla/5.0" | python3 -c "
import sys, re
html = sys.stdin.read()
match = re.search(r'scrolling-script-container\">(.*?)</div>', html, re.DOTALL)
if match:
    text = re.sub(r'<br\s*/?>', '\n', match.group(1))
    text = re.sub(r'<[^>]+>', '', text)
    print(text[:5000])
"
```

**Wikipedia MediaWiki API** — returns clean wikitext, far better than HTML scraping:
```bash
# Get structured wikitext (article content, references, categories)
curl -s "https://en.wikipedia.org/w/api.php?action=parse&page=TOPIC&prop=wikitext&format=json" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
wikitext = d.get('parse', {}).get('wikitext', {}).get('*', '')
# wikitext contains markup but no HTML — search and slice directly
idx = wikitext.find('KEYWORD')
if idx >= 0: print(wikitext[max(0,idx-200):idx+8000])
"

# Get plain-text extract (cleaner but shorter)
curl -s "https://en.wikipedia.org/w/api.php?action=query&titles=TOPIC&prop=extracts&explaintext=true&format=json" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
pages = d.get('query', {}).get('pages', {})
for pid, page in pages.items():
    print(page.get('extract', '')[:5000])
"
```
**Why wikitext > HTML**: The `prop=wikitext` endpoint returns raw wikitext markup (no `<div>`, no CSS classes, no JS). You can slice it by keyword position without any HTML parsing. For episode summaries, character lists, and production sections, this is the single fastest path.

**Goodreads quote extraction** (character quotes with attribution):
```bash
# Extract quotes tagged with a character name (paginated: page=1, page=2, ...)
curl -sL "https://www.goodreads.com/quotes/tag/CHARACTER_NAME" \
  -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  | python3 -c "
import sys, re, html as h
text = sys.stdin.read()
blocks = text.split('class=\"quoteText\"')
for block in blocks[1:30]:
    quote_part = block.split('</span>')[0] if '</span>' in block else block[:500]
    clean = re.sub(r'<[^>]+>', '', quote_part)
    clean = h.unescape(clean).strip()
    clean = re.sub(r'\s+', ' ', clean)
    if clean and len(clean) > 20:
        print(clean[:500])
        print('---')
"
```
**Why Goodreads**: Returns clean, attributed quotes in bulk. No bot detection. Pagination via `?page=N` gives 15-20+ quotes per character. The `class="quoteText"` block contains the quote text; author/source appears in nearby `<span>`.

**WikiQuote film dialogue extraction**:
```bash
# Full film dialogue — much richer than IMDB quotes
curl -sL "https://en.wikiquote.org/wiki/SHOW_TITLE_(film)" -A "Mozilla/5.0" \
  | python3 -c "
import sys, re, html as h
text = sys.stdin.read()
lines = text.split('\n')
for i, line in enumerate(lines):
    clean = re.sub(r'<[^>]+>', ' ', line)
    clean = h.unescape(clean).strip()
    if clean and 'CHARACTER_NAME' in clean:
        context = lines[max(0,i-2):i+5]
        for c in context:
            c2 = re.sub(r'<[^>]+>', ' ', c).strip()
            c2 = h.unescape(c2)
            if c2 and len(c2) > 5: print(c2)
        print('---')
"
```
**Why WikiQuote**: Full scene dialogue with character attribution, stage directions preserved, much more comprehensive than IMDB quotes section. Covers all characters, not just the one you're searching for — useful for understanding character interactions.

**Wikipedia** — fallback to HTML scraping if API fails:
```bash
curl -s "https://en.wikipedia.org/wiki/TOPIC" -A "Mozilla/5.0" | python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub(r'<[^>]+>', ' ', html)
text = re.sub(r'\s+', ' ', text)
idx = text.find('KEYWORD')
if idx >= 0: print(text[max(0,idx-200):idx+3000])
"
```

### 5. Source Reliability Assessment

**Red flags for unreliable/fabricated content:**
- Character AI / fandom AI sites (e.g., shapes.inc) generate plausible-sounding but fabricated quotes and character details
- Watch for character names that don't appear in verified sources
- Quotes that sound too perfectly crafted or too on-the-nose
- Always cross-reference against at least 2 authoritative sources

**Green flags for reliable content:**
- TV Tropes character pages (community-verified, detailed tropes with episode citations)
- Actual episode transcripts (SpringfieldSpringfield)
- SF Encyclopedia (expert literary analysis)
- Wikipedia (community-edited, sourced)
- **LitCharts, Shmoop** (literary analysis with quotes, themes, character timelines — accessible via curl, content is well-structured)
- **Niche fan analysis sites** (e.g., harrypotterinsider.com, dedicated character blogs) — often more accessible than major platforms, provide comprehensive deep dives. Verify against canon but they're surprisingly good for consolidated overviews.

### 6. Parallel Execution Strategy

When researching a topic, fire off ALL independent requests in the same batch:

```
Batch 1 (all independent):
  - DuckDuckGo search for topic overview
  - Direct URL attempt for known wiki pages
  - Reddit search for community discussion
  - Wikipedia page fetch

Batch 2 (depends on Batch 1 URLs):
  - Visit specific pages found in Batch 1
  - Fetch episode transcripts
  - Get TV Tropes character page

Batch 3 (depends on content):
  - Extract and cross-reference quotes
  - Fill gaps from Batch 2 findings
  - Write final analysis
```

## Indian Educational Portal Research (Exam Marks vs Rank, Cutoffs, etc.)

When researching Indian competitive exam data (NEET PG, NEET UG, JEE, etc.), search engines are almost always blocked. Go directly to known educational portals.

### Working Portals (as of mid-2025)

| Portal | URL Pattern | Notes |
|--------|-------------|-------|
| Careers360 | `medicine.careers360.com/articles/neet-pg-marks-vs-rank` | Subdomain works; main domain often 404s |
| CollegeDekho | `www.collegedekho.com/articles/neet-pg-marks-vs-rank/` | Good multi-year tables |
| Shiksha | Blocked by bot detection | Skip |
| CollegeDunia | CloudFront 403 | Skip |
| PrepLadder, BYJU's | 404 on marks-vs-rank articles | Unreliable URLs |

### DOM Table Extraction Technique

Educational portals render data in HTML `<table>` elements. The snapshot tool truncates large tables. **Use `browser_console` JavaScript instead**:

```javascript
// 1. Find all tables and extract content
(() => {
  const tables = document.querySelectorAll('table');
  return Array.from(tables).map((t, i) => 
    `TABLE ${i}: ${t.innerText.substring(0, 500)}`
  ).join('\n\n');
})()
```

```javascript
// 2. Find which heading labels each table (critical for multi-year data)
(() => {
  const tables = document.querySelectorAll('table');
  let out = [];
  tables.forEach((t, i) => {
    let node = t.parentElement;
    let heading = 'none';
    while (node) {
      if (node.previousElementSibling) {
        let prev = node.previousElementSibling;
        while (prev) {
          if (prev.tagName && prev.tagName.match(/^H[2-6]$/)) {
            heading = prev.textContent.trim();
            break;
          }
          const innerH = prev.querySelector('h2,h3,h4');
          if (innerH) { heading = innerH.textContent.trim(); break; }
          prev = prev.previousElementSibling;
        }
        if (heading !== 'none') break;
      }
      node = node.parentElement;
    }
    out.push(`Table ${i}: heading="${heading}" first_row="${t.rows[0]?.innerText.substring(0,100)}"`);
  });
  return out.join('\n');
})()
```

```javascript
// 3. Extract specific year's table by heading match
(() => {
  const hdgs = document.querySelectorAll('h2, h3, h4');
  let tgt = null;
  hdgs.forEach(h => { if (h.textContent.includes('NEET PG 2024')) tgt = h; });
  if (!tgt) return 'no heading';
  let el = tgt.nextElementSibling;
  let attempts = 0;
  while (el && el.tagName !== 'TABLE' && attempts < 20) {
    el = el.nextElementSibling;
    attempts++;
  }
  return el && el.tagName === 'TABLE' ? el.innerText.substring(0, 3000) : 'no table found';
})()
```

### Pitfalls for Indian Exam Data

- **URLs change yearly** — portals restructure URLs each exam cycle; 404s are common. Try the base article path first, then search for alternate slugs
- **Data is often sample-based** — marks-vs-rank tables on these sites are frequently constructed from individual candidate reports, not official NBE/MCC data. Expect non-monotonic values and treat ranks as approximate (±2-3K)
- **Multiple tables per page** — pages often have current year + previous year data; always verify which heading labels which table before citing data
- **Subdomain routing** — careers360 sometimes serves content only on subdomains (medicine.careers360.com) not the main domain

## YouTube Video Search (curl + JSON extraction)

YouTube's search results page embeds structured data as `ytInitialData` JSON. This is the most reliable way to search YouTube from the terminal:

```bash
curl -s "https://www.youtube.com/results?search_query=YOUR+QUERY" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36" 2>/dev/null | python3 -c "
import sys, re, json
html = sys.stdin.read()
match = re.search(r'var ytInitialData = ({.*?});', html)
if match:
    data = json.loads(match.group(1))
    contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
    count = 0
    for section in contents:
        items = section.get('itemSectionRenderer', {}).get('contents', [])
        for item in items:
            vid = item.get('videoRenderer')
            if vid and count < 10:
                vid_id = vid.get('videoId', '')
                title = vid.get('title', {}).get('runs', [{}])[0].get('text', '')
                channel = vid.get('ownerText', {}).get('runs', [{}])[0].get('text', '')
                length = vid.get('lengthText', {}).get('simpleText', '')
                print(f'{count+1}. [{length}] {title}')
                print(f'   Channel: {channel}')
                print(f'   URL: https://www.youtube.com/watch?v={vid_id}')
                print()
                count += 1
" 2>/dev/null
```

This reliably returns video IDs, titles, channels, and durations. Use it when the user asks for a video example of a tool, technique, or concept.

## Pitfalls

- **Load relevant skills BEFORE starting research.** If the user mentions creating a SOUL.md, building a character analysis, or similar, load `character-soul-forge` FIRST. If the user asks to research a topic, load `web-research`. Skill loading takes one tool call; discovering you missed a comprehensive workflow mid-task costs 20+ calls.
- **NEVER retry an identical failed curl call** — if a curl request returns empty or errors, the result is the result. Re-running the exact same command will produce the exact same empty output. After 2 failed identical calls, STOP and try a different approach (browser_navigate, different search terms, different source). Getting stuck in identical-curl loops has wasted 20+ tool calls in past sessions.
- **Google will block you** — don't waste time retrying; go straight to DuckDuckGo HTML
- **Cloudflare-protected fandom wikis** — most fandom.com wikis are behind Cloudflare challenges; find the same info on TV Tropes or Wikipedia instead. The Fandom API (`/api.php?action=parse&page=TOPIC&format=json`) also fails behind Cloudflare. **Fallback: Wayback Machine** — `web.archive.org/web/TIMESTAMP/URL` often has cached snapshots of wiki pages that bypass Cloudflare entirely. Use the browser to navigate: `https://web.archive.org/web/2023/https://harrypotter.fandom.com/wiki/TOPIC`. The Wayback Machine sometimes renders the full page content including JavaScript, giving you the complete article. For API access, try the raw archived version: `https://web.archive.org/web/TIMESTAMPid_/https://harrypotter.fandom.com/api.php?action=parse&page=TOPIC&format=json`. Check `web.archive.org/web/` homepage for available snapshots first.
- **AI-generated content on character sites** — sites like shapes.inc/fandom generate realistic but fabricated quotes; always verify against transcripts or TV Tropes
- **Reddit JSON API may return empty** — the old.reddit.com JSON endpoint sometimes fails; use DuckDuckGo to find Reddit threads instead. **Also try**: old.reddit.com HTML search (`curl -sL "https://old.reddit.com/r/SUBREDDIT/search?q=QUERY&restrict_sr=on&sort=relevance&t=all"`) piped through the extraction script — this often works even when the JSON API and new Reddit are both blocked.
- **Later episodes may lack transcripts** — SpringfieldSpringfield often only has first few episodes; plan around this
- **Curl User-Agent matters** — many sites require a realistic browser User-Agent or return empty/blocked pages
- **"Everything is blocked" scenario** — When Google, DuckDuckGo, Fandom, TV Tropes, AND Reddit are ALL blocked (aggressive bot detection on the session's IP), fall back to: (1) Wikipedia HTML + API (usually accessible), (2) known entertainment review sites (THR, Variety, Animation Magazine — try status codes first), (3) browser_navigate for JS-rendered pages, (4) follow reference links inside Wikipedia articles (they contain verified URLs to interviews and reviews). Check reference URLs in batch: `curl -sL -o /dev/null -w '%{http_code}' 'URL'` for each before attempting full fetch.
- **Wikipedia redirect trap** — When a topic redirects (e.g., `Dobby_(Harry_Potter)` → `List_of_Harry_Potter_characters`), the `action=parse` API returns `#REDIRECT List of X` with no actual content, and the `action=query&prop=extracts` API returns empty. Detect this by checking if the response starts with `#REDIRECT` or is suspiciously short. Fallback: search the list page's wikitext for the character name, or use browser_navigate on the list page and search the snapshot for the character section.
- **Wikipedia references are goldmines** — Wikipedia articles on TV shows contain direct links to creator interviews, reviews, and analyses. Extract all reference URLs from the article, check which return 200, then fetch those. This bypasses search engine blocking entirely. Pattern: parse `<ref>` tags from wikitext, extract URLs, batch-check HTTP status codes.

## Academic & Patent Database Research

When researching novel technical concepts, prior art, or scientific literature — standard search engines are often blocked. Go directly to academic databases and patent servers.

### Working Databases (as of mid-2026)

| Database | URL | Access | Notes |
|----------|-----|--------|-------|
| **PubMed** | pubmed.ncbi.nlm.nih.gov | ✅ Browser works | Biomedical literature. Best for medical/bio engineering. Zero results = genuinely novel concept |
| **arXiv** | arxiv.org/search | ✅ Browser works | Preprints (CS, physics, engineering). Good for early-stage tech concepts |
| **Google Patents** | patents.google.com | ✅ Browser works | ~38M patents. Best for prior art searches. Use quotes for exact phrases |
| **Semantic Scholar** | semanticscholar.org | ✅ Browser works | AI-powered academic search. Good cross-disciplinary coverage |
| **IEEE Xplore** | ieeexplore.ieee.org | ⚠️ Abstracts free, full-text paywalled | Engineering/robotics specifically |

### Blocked / Unreliable

| Database | Status | Workaround |
|----------|--------|------------|
| Google Scholar | ❌ CAPTCHA/bot detection | Use PubMed or Semantic Scholar instead |
| ResearchGate | ❌ Login wall | Use Google Patents for prior art instead |
| SciHub | ⚠️ Unreliable availability | Not recommended |

### Search Strategy for Novel Concepts

When checking if a concept already exists:

1. **Start with Google Patents** — most comprehensive prior art database. Search with exact technical phrases in quotes.
2. **PubMed** — zero results for highly specific queries means the concept hasn't been published in biomedical literature
3. **arXiv** — check for preprints (often ahead of published papers)
4. **Semantic Scholar** — cross-disciplinary catch-all

**Key insight**: If PubMed, arXiv, AND Google Patents all return zero results for a specific combination of technical terms, the concept is likely novel or at minimum unpublished. This is strong evidence — but not proof — of novelty.

### Pitfalls for Academic Research
- **Search engines geo-block and CAPTCHA** — Google Scholar, Brave, DuckDuckGo all blocked headless browsers in testing. Go straight to the databases.
- **Broad queries return noise** — use the most specific technical terms possible. "piezo motor fabric muscle" returns irrelevant results; "ultrasonic piezo dual strand agonist antagonist" returns zero (meaningful)
- **Zero results IS data** — on PubMed/arXiv, zero results for a specific query is informative. It means the exact concept hasn't been indexed. Don't keep retrying with slightly different terms hoping for a hit.
- **Patent searches use different vocabulary** — patents often describe things differently than academic papers. Try multiple phrasings: "piezoelectric actuator" vs "piezo motor" vs "ceramic transducer"

## Technology Comparison Research

When researching SaaS APIs, open-source models, or competing products:

### LLMs.txt Provider Documentation (Fastest Path)

Many AI providers now publish structured docs at `llms.txt` — a plain-text file designed for LLM consumption. Check this FIRST before scraping HTML:

```bash
# Try the standard location
curl -s "https://provider.com/llms.txt" | head -100

# Or linked from the page header:
# <link rel="llms" type="text/plain" href="./llms.txt">
```

`llms.txt` typically contains: model list with IDs, capabilities, context windows, pricing links, API format docs, and integration guides. It's the single cleanest way to get a provider's full model catalog without parsing JS-rendered pages.

**Known providers with `llms.txt`:** Xiaomi MiMo (`platform.xiaomimimo.com/llms.txt`), and growing. Always try it — if it exists, it saves 5+ tool calls.

**Companion files** to check alongside `llms.txt`:
- `/static/docs/quick-start/model.md` — model IDs, context windows, rate limits
- `/static/docs/price/pay-as-you-go.md` — per-token pricing tables

### Provider Pricing Extraction

Most pricing pages are JS-rendered. Three approaches in order of preference:

**1. Browser navigation** (most reliable for JS-rendered pricing):
```
browser_navigate to provider/pricing → browser_snapshot full=true → extract tables
```

**2. curl + python HTML extraction** (for static/SSR pages):
```bash
curl -sL "https://provider.com/pricing" -A "Mozilla/5.0" | python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub('<[^>]+>', '\n', html)
text = re.sub(r'\n\s*\n', '\n', text)
lines = [l.strip() for l in text.split('\n') if l.strip()]
for i, line in enumerate(lines):
    if any(kw in line.lower() for kw in ['per minute', '\$', 'per hour', 'per month']):
        for j in range(max(0,i-2), min(len(lines), i+3)):
            print(f'{j}: {lines[j]}')
        print('---')
"
```

**3. Check for structured data**: Some providers expose pricing as JSON or in `<table>` elements — try targeted CSS selectors first.

### Open-Source Model Evaluation

Check GitHub repos and HuggingFace for model specs:

```bash
# Raw README from GitHub (benchmarks, VRAM, usage)
curl -sL "https://raw.githubusercontent.com/OWNER/REPO/main/README.md" | head -200

# HuggingFace model card (architecture, languages, size)
curl -sL "https://huggingface.co/ORG/MODEL/raw/main/README.md" | head -100

# HuggingFace API (model metadata)
curl -sL "https://huggingface.co/api/models/ORG/MODEL" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Model:', data.get('id'))
for s in data.get('siblings', []):
    sz = s.get('size', 0)
    if sz: print(f'  {s[\"rfilename\"]}: {sz/1e9:.2f} GB')
"
```

### Comparison Report Format

For technology comparison output, use this structure:
1. **Ranked list** with clear winner justification
2. **Pricing comparison table** (normalize to $/hr for audio, $/1M tokens for LLMs, etc.)
3. **Feature matrix** (accuracy, latency, languages, VRAM requirements)
4. **Hardware-specific recommendations** when user provides specs
5. **Source attribution** with URLs and verification dates

### Pitfalls for Tech Research

- **Search engines geolocalize** — Bing/Google may return irrelevant local results; go straight to provider websites
- **Bot detection on pricing pages** — OpenAI, Cloudflare-heavy sites often block; fall back to curl with User-Agent or cached/third-party sources
- **Pricing pages are often JS-rendered** — raw curl often returns empty/JS shells; use browser tools or check for SSR/API endpoints
- **Model VRAM claims vary by source** — always check the actual model card/HuggingFace page rather than blog posts; VRAM depends on precision (FP16/INT8), batch size, and CUDA overhead
- **"Best" is context-dependent** — always ask or infer: accuracy vs. speed vs. cost vs. VRAM vs. language coverage tradeoffs change the ranking

## Educational / Competitive Exam Data Research

When researching marks-vs-rank, cutoff, or score data for competitive exams (NEET, JEE, GATE, UPSC, etc.):

### Source Hierarchy

| Source Type | Reliability | Notes |
|---|---|---|
| Official body (NBE, NTA, MCC, UPSC) | Highest | Publish individual scorecards/ranks, but **rarely publish aggregate marks-vs-rank tables** |
| Top educational portals (CollegeDekho, Embibe, Shiksha) | Good | Construct marks-vs-rank tables from reported data; include year-on-year trend analysis |
| Coaching institutes / YouTube | Medium | Often early with estimates, but may be promotional |
| Reddit / Quora / forums | Low-Medium | Anecdotal, but useful for validation of trends |

**Key insight**: Official bodies almost never publish aggregated marks-vs-rank tables. Educational portals build these from reported scorecards, coaching data, and trend analysis. Treat portal tables as well-informed estimates, not official figures.

### Extraction Technique for HTML Tables

Indian educational portals often serve table data server-side (no JS needed). Extract with:

```bash
# Method 1: Strip all HTML, grep for relevant terms
curl -sL "URL" -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  | sed 's/<[^>]*>/\n/g' | grep -v '^\s*$' | grep -i -E "(rank|marks|cutoff)"

# Method 2: Extract table rows directly (most reliable)
curl -sL "URL" -A "Mozilla/5.0" \
  | grep -oP '<tr[^>]*>.*?</tr>' | grep -i -E "(4[0-4][0-9]|rank|marks)"
```

### Rank Inflation Pitfall

When cross-referencing data across exam years, **rank inflation** can be extreme. For example, 550 marks in NEET PG might correspond to rank ~2,000 in 2021 but rank ~21,500 in 2025. Always:
1. Use the most recent year's data as baseline
2. Check if the portal explicitly mentions inflation trends
3. When tables stop at a certain marks range, extrapolate downward with a caveat — rank density increases sharply at lower marks

### Portal Access Patterns

Indian educational portals vary in bot tolerance:
- **CollegeDekho, Embibe**: Generally curl-accessible; tables are SSR
- **Shiksha, GetMyUni, Prepp**: Often block curl/UA; try browser tools as fallback
- **JagranJosh**: Frequently returns 404 or JS shells; try browser
- **NBE/official sites**: Usually JS-heavy; browser tools required

### Output Format for Exam Data

Include in results:
1. **Exact rank range** for the requested marks (or best estimate with caveat)
2. **Data source and year** — never present extrapolated data as confirmed
3. **Year-on-year inflation context** if available
4. **Category-specific cutoffs** (General, OBC, SC/ST, EWS) if relevant
5. **Branch/specialization-specific cutoffs** if relevant (for medical/engineering)

## Output Format

For character/concept research, produce a structured markdown document with:
1. Core traits/personality (verified against primary sources)
2. Speaking style / dialogue patterns (with actual quoted examples)
3. Worldview / philosophy
4. Interactions with other characters
5. Background / history
6. Verified quotes (attributed to source)
7. Writing guide (if applicable — how to write in their voice)
8. Sources list (what was used, what was verified where)

Mark any information that couldn't be verified with a note.
