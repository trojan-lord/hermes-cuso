---
name: unicode-text-editing
description: Use when read_file/patch misdetect unicode text as binary.
triggers:
  - Binary file - cannot display as text
  - binary file refused for valid UTF-8 text
  - patch V4A rejects markdown as binary
  - em-dash / math symbols / CJK in markdown
  - read_file says binary but file is text
---

# Editing Unicode-Heavy Text Files

## When this fires
`read_file` or `patch` (V4A mode) refuse a file with **"Binary file - cannot
display as text"** even though it's a normal text/markdown doc. Happens with
unicode-heavy content: em-dashes (—), math symbols (μ σ → § ≈ ≥ − × √),
CJK, accented text. Real case: a markdown blueprint with ~70 em-dashes plus
math symbols — a single em-dash in a header line near the top flipped the
whole file to "binary" for the file tools.

## First: prove the file is actually fine
```bash
file /path/to/file.md          # "Unicode text, UTF-8 text" = content is OK
python3 - <<'EOF'
data = open('/path/to/file.md','rb').read()
print('NUL bytes:', b'\x00' in data)
try:
    data.decode('utf-8'); print('valid UTF-8: yes')
except UnicodeDecodeError as e:
    print('INVALID UTF-8:', e)
ctrls = [hex(b) for b in data if b < 0x20 and b not in (0x0a,0x0d,0x09)]
print('control chars:', ctrls[:10])
EOF
```
If valid UTF-8 + no NULs + no control chars → the **file is fine**; it's the
tool's binary-detection heuristic misfiring. `git diff`/`git show` still work
on it. Do NOT rewrite the content to ASCII.

## Why it misfires (empirically — don't reverse-engineer further)
Detection is a positional/sampling heuristic, not a clean rule. Observed:
- Files with FEWER multibyte bytes read fine while near-identical files flip
  to "binary"; same char at a different position reads fine; size/count/ratio
  bisection does NOT reproduce it. Two files with byte-identical high-byte
  distributions (checked at 1K/2K/4K/8K windows) got different verdicts —
  one extra ASCII line flipped text→binary.
- Position matters: the SAME inserted block read fine appended at end-of-file
  but flipped to binary placed near the top next to the header.
Burn zero time modeling the heuristic. Swap one char and move on.

## The fix (works in practice)
1. `cp` the file to /tmp. Strip ONE suspect character — start with the first
   em-dash / multibyte char near the TOP of the file — replace with an ASCII
   hyphen. Test `read_file` on the copy.
2. If the copy reads as text, apply the same one-char replacement to the real
   file (python one-liner or patch replace-mode), then continue editing.
3. For the rest of the session use `patch` with **mode='replace'**
   (old_string/new_string) — NOT V4A patch mode. Replace mode handles unicode
   fine; V4A mode rejects the same file as "binary".

## After the fix: more unicode is safe
Once the trigger char is swapped, keep using replace-mode patch and don't
worry about the multibyte count climbing — observed: the file grew to 1,242
high bytes (~3.7% of 33 KB, 720 lines, dozens of em-dashes/μ/σ/§/→) across
later edit batches with zero re-triggers. The heuristic is position-bound,
not ratio-bound; replace-mode patch never tripped it. After each edit batch
on a known trigger file, verify readability (head read_file, or a python
high-byte + content-assert check) before committing.

## Pitfalls
- Don't convert the whole file to ASCII — the unicode is often meaningful
  (math symbols in specs, em-dashes in prose). Fix one char at the detection
  point; the rest of the file is fine as-is.
- `read_file` dedup: after a failed "binary" read, re-reading the same path
  may report "File unchanged since last read" — use a fresh /tmp copy for
  tests.
- Loop warning: if read_file fails 2–3× in a row, STOP retrying the same call.
  Diagnose (file + python checks above), then apply the fix.
- After `rm -rf` of the directory you were cd'd into, bash loses cwd
  ("getcwd: cannot access parent directories") — run `cd /` first, then your
  commands.
- Keep `file` + python validation in the loop: they prove the disk content is
  fine, which de-risks the "is my file corrupted?" panic.

## Related
- Mel's `~/mel/docs/architecture.md` is a known trigger file (μ/σ/→/§ +
  em-dashes). See esp32-development `references/mel-taste-radio.md`.
