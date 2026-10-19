# Context File Truncation Mechanics

How Hermes decides how much of SOUL.md (and other context files) to inject into the system prompt.

## Dynamic Cap Formula

When no explicit `context_file_max_chars` is set in config.yaml, Hermes computes a budget dynamically:

```
budget = context_length × 4 (chars/token) × 0.06 (6% window fraction)
clamped to [20,000  floor] and [500,000  ceiling]
```

Constants from `prompt_builder.py`:
- `_CONTEXT_FILE_CHARS_PER_TOKEN = 4`
- `_CONTEXT_FILE_WINDOW_FRACTION = 0.06`
- `_CONTEXT_FILE_DYNAMIC_CEILING = 500_000`
- `CONTEXT_FILE_MAX_CHARS = 20_000` (floor, legacy default)

### Examples

| Model context | Raw budget (×4×0.06) | Clamped result |
|--------------|----------------------|----------------|
| 32K | 7,680 | **20,000** (floor kicks in) |
| 128K | 30,720 | 30,720 |
| 200K | 48,000 | 48,000 |
| 256K | 61,440 | 61,440 |
| 1M | 240,000 | 240,000 |

## Truncation Behavior

When a context file exceeds the cap, Hermes applies **head/tail truncation** with a marker in the middle:

- `CONTEXT_TRUNCATE_HEAD_RATIO = 0.7` (first 70% of budget)
- `CONTEXT_TRUNCATE_TAIL_RATIO = 0.2` (last 20% of budget)
- Remaining 10% is the truncation marker text

The marker tells the agent the file was truncated and provides a `read_file` path to recover the full content.

### What gets counted

The cap applies to ALL context files combined in the stable prompt prefix — SOUL.md, AGENTS.md, project context files, etc. They share the same budget. A large SOUL.md leaves less room for project context files, and vice versa.

## Resolution Order for context_file_max_chars

1. Explicit `context_file_max_chars` in config.yaml (always wins)
2. Dynamic cap from model's `context_length` (the formula above)
3. `CONTEXT_FILE_MAX_CHARS` (20K) as fallback when context_length is unknown

## Implications for SOUL.md Sizing

- A 32K SOUL.md on a 256K-context model uses ~53% of the 61K budget — healthy
- A 32K SOUL.md on a 32K-context model hits the 20K floor — gets truncated (head 14K + tail 4K)
- If SOUL.md + AGENTS.md + project files exceed the budget, the later-loaded files get truncated first
- Setting `context_file_max_chars` explicitly overrides the dynamic scaling — useful if you have a large SOUL.md on a small-context fallback model

## Key Source Locations

- `agent/prompt_builder.py:1244-1288` — dynamic cap calculation
- `agent/prompt_builder.py:1855-1885` — head/tail truncation logic
- `agent/system_prompt.py:186-194` — SOUL.md loading into stable parts
