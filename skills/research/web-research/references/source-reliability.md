# Source Reliability Notes — Pop Culture Research

## Tier 1: Highly Reliable

### TV Tropes
- **URL pattern**: `https://tvtropes.org/pmwiki/pmwiki.php/Characters/SHOW_NAME` (character pages)
- **URL pattern**: `https://tvtropes.org/pmwiki/pmwiki.php/WesternAnimation/SHOW_NAME` (main show pages)
- **Content**: Community-verified character tropes with episode citations. Extremely detailed — physical descriptions, personality traits, arc progressions, direct quotes
- **Parsing**: Strip HTML tags, collapse whitespace, search by character name. Character pages have rich structured content under each character heading
- **Caveat**: Content is trope-catalogued, not narrative — read around the trope names

### SpringfieldSpringfield.co.uk
- **URL pattern**: `https://www.springfieldspringfield.co.uk/view_episode_scripts.php?tv-show=SHOW-NAME-YEAR&episode=s01e01`
- **Content**: Actual episode transcripts with speaker labels and stage directions
- **Parsing**: Extract from `scrolling-script-container` div. Replace `<br>` with newlines, strip HTML
- **Caveat**: Not all episodes available — first few seasons usually present, later episodes may be missing. Speaker labels use character names, not "MARSHALL:" — dialogue appears as plain lines after a dash or character name

### SF Encyclopedia (sf-encyclopedia.com)
- **URL pattern**: `https://sf-encyclopedia.com/entry/ENTRY_NAME`
- **Content**: Expert literary/genre analysis. Dense, authoritative plot summaries with thematic commentary
- **Parsing**: Strip HTML, collapse whitespace. Usually the full entry is on one page
- **Best for**: Getting a reliable high-level plot overview and thematic context

### Wikipedia
- **Content**: Community-edited, sourced. Good for overview but often less detailed on character specifics
- **Parsing**: The `wgArticleId` being 0 means the page doesn't exist yet — check before investing time

## Tier 2: Useful but Verify

### Reddit (JSON API)
- **URL pattern**: `https://www.reddit.com/r/SUBREDDIT/search.json?q=QUERY&sort=top&t=year`
- **Caveat**: Often returns empty or blocked. Use old.reddit.com as alternative. Better to find Reddit threads via DuckDuckGo and visit directly
- **Best for**: Community opinions, fan theories, corrections to other sources

### MovieSense.io / Similar Analysis Sites
- **Content**: Can be useful for character summaries and cast info
- **Caveat**: Some content is AI-generated — verify specific claims against Tier 1 sources

## Tier 3: Unreliable / AI-Generated — VERIFY EVERYTHING

### Character AI / Fandom AI Sites (shapes.inc, character.ai, etc.)
- **Red flag**: Sites like `shapes.inc/fandom/` generate realistic-sounding but **fabricated** character analyses, quotes, and dialogue
- **Evidence from this session**: Generated fake character names ("Agent Gurny", "CEO Thorne") that don't exist in the show. Fabricated quotes that sound plausible but are entirely made up
- **Rule**: NEVER use these as primary sources. If a quote or detail only appears here, mark it as unverified

## API Tips

### Reddit JSON
```bash
# Search
curl -s "https://www.reddit.com/r/SUBREDDIT/search.json?q=QUERY&limit=10&sort=top&t=all" \
  -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
# Parse with: data.data.children[].data.{title, selftext, score, permalink}
```

### DuckDuckGo HTML
```bash
# Search (bypasses most bot detection)
curl -s "https://html.duckduckgo.com/html/?q=QUERY" \
  -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
# Results in: class="result__title" -> href, text
#             class="result__snippet" -> snippet text
```

### TVmaze API (episode metadata)
```bash
# Get episode list with summaries
curl -s "https://api.tvmaze.com/shows/SHOW_ID/episodes" -A "Mozilla/5.0"
```
