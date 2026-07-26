# Long-Form Content Generation with Hermes Tools

Technical lessons from generating ~18K words of novel prose across 7 chapters.

## write_file Size Limit

The `write_file` tool has an effective limit of ~8K tokens per call. Attempts to write larger content (e.g., an entire 18K-word combined output) cause a stream timeout with no output.

### Correct Pattern

1. Write each chapter/section to its own file: `/tmp/chatgpt-export/ch03.txt`, `ch04.txt`, etc.
2. Concatenate with shell: `cat ch03.txt ch04.txt ... ch09.txt > combined-output.txt`
3. Verify with `wc -w` per-file and total.

### Wrong Pattern

```python
# DON'T: single huge write_file call
write_file(path="output.txt", content="...18000 words...")  # TIMEOUT
```

## patch Tool Duplicate Line Pitfall

When using `patch` to expand text by adding paragraphs near existing content, the fuzzy matching can cause the tool to match the wrong location or leave duplicate lines.

### Symptom

After patching, you see:
```
The old line.
 The old line.   # <-- duplicate, indented differently
```

### Cause

The patch tool's fuzzy matching finds multiple matches for `old_string` when it's generic (e.g., a single sentence that appears in two places). Even with `replace_all=false`, the tool may partially match and leave residual text.

### Prevention

1. **Use unique context** in `old_string`: include 2-3 surrounding lines, not just the target line.
2. **Verify after every patch**: run `wc -w` and `grep -c` to check for duplicates.
3. **Prefer write_file over patch for large expansions**: if adding >200 words to a chapter, it's safer to rewrite the whole chapter file with `write_file` than to patch in additions.
4. **When expanding multiple chapters**: write each complete chapter to its own file from the start, rather than patching a single growing file repeatedly.

### Fix When Detected

```bash
# Find duplicates
grep -n "duplicate line text" file.txt

# Best fix: rewrite the section with write_file using the corrected content
```

## Style-Matching Workflow for Novel Continuation

When continuing an existing novel or writing chapters to match a source text:

### Step 1: Read Source Material

Read all existing chapters and any outline/plan documents in full. Do not skip this — the voice must be internalized before writing begins.

### Step 2: Extract Style Profile

Document these elements from the source:

| Element | What to Extract | Example |
|---------|----------------|---------|
| POV | First/second/third, limited/omniscient | "Second-person from killer's unconscious, addressing Mori" |
| Tense | Past/present, consistent or shifting | "Past tense, occasional present for internal voice" |
| Sentence structure | Long flowing vs short punchy | "Long, compound sentences with em dashes" |
| Vocabulary register | Formal/colloquial/archaic | "Literary, formal, occasional classical Japanese references" |
| Dialogue ratio | How much dialogue vs narration | "Minimal dialogue (~5-10%), mostly narration and interiority" |
| Interiority depth | How deep into character's thoughts | "Very deep — direct address from unconscious, philosophical musing" |
| Recurring imagery | Motifs, symbols, sensory details | "Rain, smoke, neon light, white cloth, kneeling figures" |
| Paragraph length | Short/medium/long | "Medium-long (3-6 sentences), rarely single-line paragraphs" |
| Scene breaks | How scenes transition | "Horizontal rules (---), sometimes with time/location shifts" |

### Step 3: Match Outline to Source Patterns

For each chapter in the outline, plan how the source style will render that content:
- What imagery will carry this scene?
- How will the internal voice address the reader?
- What sensory details will anchor the description?
- Where will dialogue appear (and how minimal)?

### Step 4: Write, Then Verify Consistency

After writing all chapters, do a spot-check:
- Read first and last paragraphs of each chapter — do they sound like the source?
- Check dialogue style consistency
- Verify POV hasn't shifted
- Confirm recurring imagery appears with similar frequency

## Batch Verification Commands

```bash
# Per-chapter word counts
for f in /tmp/chatgpt-export/ch*.txt; do
  echo "$(basename $f): $(wc -w < $f) words"
done

# Total word count
wc -w /tmp/chatgpt-export/seppuku-chapters-3-9.txt

# Verify chapter structure
grep -c "^### \*\*Chapter" combined.txt  # should match expected count
grep "^### \*\*Chapter\|End of" combined.txt  # list all chapter headings

# Check for duplicate lines (common patch artifact)
sort combined.txt | uniq -d | head -20
```
