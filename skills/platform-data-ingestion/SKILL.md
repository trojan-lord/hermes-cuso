---
name: platform-data-ingestion
description: "Ingest session history, configuration, and identity from external AI platforms into Hermes. Discover data stores, navigate SQLite schemas, extract conversations and user context."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Migration, Data-Ingestion, SQLite, Session-History, Platform-Integration]
    related_skills: [opencode, hermes-agent]
---

# Platform Data Ingestion

Ingest session history, configuration, and user context from external AI platforms (OpenCode, Kimaki, Claude, Cursor, etc.) into Hermes Agent.

## When to Use

- User is migrating from another AI platform and wants conversation history preserved
- User wants you to "know what the old bot knew"
- User references past sessions from a different platform
- User asks you to import or merge data from another AI assistant

## Discovery Phase

### Step 0: Check GitHub for Persona Repos

Many users store AI persona definitions in GitHub repos BEFORE you start local discovery. Check early — it reveals the full collection of personas (not just the active one) and often has research/history.

**Do this FIRST, before local file discovery.** GitHub repos are the richest source — they have the full persona collection (not just the active one), research docs, agent configs, and skill definitions. Local discovery fills in tokens and conversation history that GitHub doesn't have.

```bash
# Check if gh CLI is authenticated
gh auth status 2>&1

# List user's repos
gh repo list <username> --limit 20

# Look for persona/soul repos by name patterns
gh repo list <username> --limit 50 --json name,description | \
  python3 -c "import sys,json; [print(r['name'],r.get('description','')) for r in json.load(sys.stdin) if any(k in (r['name']+r.get('description','')).lower() for k in ['soul','agent','persona','config'])]"
```

Common repo patterns:
- `SOULS` or `souls` — collection of persona definitions (.md files), often with research subdirectories
- `.config-opencode` — OpenCode agent configs, skills, persona references
- `scripts` — system utility scripts

Fetch ALL files from persona repos (not just the ones you recognize):
```bash
# List repo contents
gh api repos/<owner>/<repo>/contents/<path>

# Download a file (base64 encoded)
gh api repos/<owner>/<repo>/contents/<path>/<file> -q .content | base64 -d

# Download ALL files in a directory in a loop
for f in $(gh api repos/<owner>/<repo>/contents/<dir> -q '.[].name' 2>/dev/null); do
  gh api repos/<owner>/<repo>/contents/<dir>/$f -q .content | base64 -d > "$f"
done

# Or get raw download URL
gh api repos/<owner>/<repo>/contents/<path>/<file> -q .download_url | xargs curl -sL
```

See `references/persona-repository-patterns.md` for the full pattern.

### Step 1: Find Platform Data Stores

AI platforms typically store data in these locations:

| Platform | Config | Data/DB | Skills |
|----------|--------|---------|--------|
| OpenCode | `~/.config/opencode/` | `~/.local/share/opencode/opencode.db` | `~/.config/opencode/skills/` |
| Kimaki | `~/.kimaki/` | `~/.kimaki/discord-sessions.db` | npm-bundled: `find /usr/lib/node_modules/kimaki/skills -name SKILL.md` |
| Claude | `~/.claude/` | `~/.claude/projects/` | none |
| Cursor | `~/.cursor/` | `~/.cursor/sessions/` | none |
| ChatGPT | none | ZIP export (Settings → Data Controls → Export Data) | none |

**ChatGPT data comes as a ZIP**, not a local DB. The user requests an export via ChatGPT settings, gets an email with a ZIP, and provides it to you (upload, cloud link, or local path). See `## ChatGPT Export Import` below.

**Kimaki skills are NOT in a user directory.** They ship inside the npm package:
```bash
# Find Kimaki skills
find /usr/lib/node_modules/kimaki/skills -name 'SKILL.md' -exec dirname {} \;
# Or if installed via npx
find ~/.npm/_npx -path '*/kimaki/skills/*/SKILL.md' 2>/dev/null
```

Search broadly first:

```bash
find ~ -maxdepth 3 -name '*.db' -o -name '*.sqlite' 2>/dev/null | grep -iE 'opencode|kimaki|claude|cursor|session'
find ~ -maxdepth 3 -name 'config.json' -o -name 'opencode.json' 2>/dev/null | grep -v node_modules
find ~ -maxdepth 3 -name 'SOUL.md' -o -name 'AGENTS.md' -o -name 'CLAUDE.md' 2>/dev/null
```

### Step 2: Read Configuration Files

Config files contain:
- Model provider settings (which LLM, which provider)
- Agent persona definitions (SOUL.md, system prompts)
- API keys and tokens (Discord bot tokens, provider keys)
- Permission settings
- Skill paths

Look for:
- `opencode.json` or `config.json` in platform config dirs
- `.env` files in platform directories
- `SOUL.md` or persona files referenced in configs
- `package.json` for npm-installed platforms

### Step 3: Identify User Identity

Extract user identity markers for context:
- Discord usernames and IDs (from message metadata)
- Git user.name / user.email (from repo configs)
- Platform-specific usernames
- Any names/handles mentioned in conversations

## Database Navigation

### SQLite Schema Exploration

Most AI platforms use SQLite for session storage. Navigate schemas systematically:

```bash
# List tables
sqlite3 database.db ".tables"

# Show schema
sqlite3 database.db ".schema"

# Count records per table
sqlite3 database.db "SELECT name, (SELECT count(*) FROM pragma_table_info(name)) as cols FROM sqlite_master WHERE type='table';"
```

### Finding Conversation Text

**Critical pattern**: Conversation text is often NOT in the `message` table. It's typically in a `part` or `event` table with a type field.

Common schema patterns:

1. **OpenCode pattern**: `message` table has metadata, `part` table has text content
   ```sql
   SELECT data FROM part WHERE session_id='...' AND data LIKE '%"type":"text"%';
   ```

2. **Event-sourced pattern**: Events stored as JSON blobs
   ```sql
   SELECT event_json FROM session_events WHERE event_json LIKE '%"type":"text"%';
   ```

3. **Message-parts pattern**: Messages split into parts
   ```sql
   SELECT data FROM message_parts WHERE message_id='...';
   ```

### Extracting Text from JSON Parts

Parts are often JSON with nested text. The `find_all_text` recursive pattern is the most reliable way to extract from deeply nested event-sourced databases:

```python
import json

def find_all_text(obj, path=""):
    """Recursively find all text fields in a nested structure.
    
    This is the critical technique for event-sourced databases where
    conversation text is buried 3-4 levels deep in JSON blobs.
    Works on Kimaki session_events, OpenCode parts, and similar.
    """
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'text' and isinstance(v, str) and len(v) > 3:
                results.append(v)
            results.extend(find_all_text(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            results.extend(find_all_text(item, f"{path}[{idx}]"))
    return results

# Usage on Kimaki session_events:
# for line in sqlite_result:
#     event = json.loads(line)
#     texts = find_all_text(event)
#     for t in texts:
#         if t.strip() and not t.startswith(('evt_', 'msg_', 'prt_', 'call_')):
#             print(t)
```

**Why recursive**: Event JSON is deeply nested — `event.properties.part.text` or `event.properties.info.content`. A recursive search finds text regardless of nesting depth. Filter out IDs (evt_, msg_, prt_, call_ prefixes) to avoid noise.

### Session Linking

Sessions often have relationships:
- `parent_id` links continuation sessions
- `thread_id` links Discord threads to sessions
- `session_id` in parts links parts to sessions

Build a session graph:

```sql
SELECT s.id, s.title, s.parent_id, COUNT(m.id) as msg_count
FROM session s
LEFT JOIN message m ON m.session_id = s.id
GROUP BY s.id
ORDER BY s.time_created ASC;
```

## Extraction Phase

### Token and Secret Extraction

**Discord bot tokens** are stored in SQLite, not .env files:

```sql
-- Kimaki stores bot tokens here
SELECT app_id, token, client_id, client_secret, bot_mode FROM bot_tokens;
SELECT * FROM bot_api_keys;
```

**API keys** may be in the same database or in `.env` files. Check both:
```bash
find ~ -maxdepth 3 -name '.env*' 2>/dev/null
cat ~/.kimaki/.env 2>/dev/null
cat ~/.hermes/.env 2>/dev/null
```

**Save tokens to a dedicated file**, not to memory:
```python
# Save to a JSON file, NOT to the memory tool
# Memory is injected into every conversation turn — tokens don't belong there
write_file("/home/h2/<project>-reference/tokens.json", json.dumps({
    "discord": {"token": "...", "app_id": "...", ...},
    "github": {"username": "...", "note": "Token in gh keyring"},
}, indent=2))
```

**Never save tokens to memory.** Memory is injected into every future turn. Tokens in memory = tokens in every API call.

### What to Grab Before Deletion

When the user says "I'm going to delete X after this", be THOROUGH. Check these:

| Category | What | Where |
|----------|------|-------|
| Personas/SOULs | All .md persona files | `~/.config/opencode/SOUL.md`, GitHub repos, agent dirs |
| Configs | Platform config files | `~/.config/opencode/opencode.json`, `~/.kimaki/opencode-config.json` |
| Skills | Platform-specific skills | npm-bundled dirs, `~/.config/opencode/skills/` |
| Tokens | Discord/API tokens | SQLite `bot_tokens` table, `.env` files |
| Conversations | Session transcripts | SQLite databases (see schema reference) |
| Session metadata | All session IDs/titles | Export as CSV for future reference |
| Git history | Repo logs | `git log --oneline` in project dirs |
| Uploads | User-uploaded files | `~/.kimaki/projects/*/uploads/` |
| User identity | Discord IDs, git config | `~/.gitconfig`, Discord message metadata |

Save everything to a `<platform>-reference/` directory at the user's home.

### What to Extract

Priority order:
1. **User identity**: Names, IDs, preferences mentioned
2. **Session topics**: Titles, main themes, projects discussed
3. **Key decisions**: What was built, configured, or changed
4. **User preferences**: Communication style, pet peeves, workflow preferences
5. **Technical context**: Systems used, tools configured, projects in progress
6. **Full conversation text**: For sessions the user specifically wants preserved

### Saving to Memory

Use the memory tool to save durable facts:

```
memory(action='add', target='user', content='User identity and preferences...')
memory(action='add', target='memory', content='Technical context and setup...')
```

Keep entries compact. Memory is injected into every turn.

### Saving to Skills

If the ingestion reveals reusable patterns (not just one-off data), create or update skills:

- Platform-specific schema details → `references/<platform>-schema.md`
- Common extraction patterns → skill body under "## Database Navigation"
- Pitfalls discovered → "## Pitfalls" section

## ChatGPT Export Import

ChatGPT exports come as a ZIP containing JSON conversation files, user settings, and `.dat` attachment files.

### ZIP Structure

```
conversations-000.json    # 100 conversations each (typically 10 files)
conversations-001.json
...
conversations-009.json
user.json                 # Account metadata
user_settings.json        # UI preferences
export_manifest.json      # Export metadata
file_*.dat                # Attached files (images, etc.)
```

### Conversation Format (Critical)

ChatGPT uses a **tree structure with parent pointers**, NOT children arrays. Each node has:
- `parent`: ID of the parent node (null for root)
- `message`: object with `author.role` ("user"/"assistant") and `content.parts` (array of text strings)
- `children`: always `null` or `[]` (never populated — the tree is built backwards via parent links)

**Do NOT try to walk children.** Walk parent pointers instead.

### Flattening Technique

```python
def flatten_conversation(conv: dict) -> list[dict]:
    """Walk backwards from current_node via parent pointers, then reverse.
    
    Includes cycle protection: tracks visited nodes to prevent infinite loops
    in malformed exports (rare but possible with corrupted ZIP files).
    """
    mapping = conv.get("mapping", {})
    current_node = conv.get("current_node")
    if not current_node:
        # Fallback: find root (parent=None)
        for nid, node in mapping.items():
            if node.get("parent") is None:
                current_node = nid
                break

    messages = []
    seen = set()
    node_id = current_node
    while node_id and node_id not in seen:
        seen.add(node_id)
        node = mapping.get(node_id, {})
        msg = node.get("message")
        parent = node.get("parent")
        if msg:
            role = msg.get("author", {}).get("role", "")
            if role in ("user", "assistant"):
                parts = msg.get("content", {}).get("parts", [])
                text = "\n".join(str(p) for p in parts if p and str(p).strip())
                if text:
                    ts = msg.get("create_time") or msg.get("update_time") or conv.get("create_time", 0)
                    messages.append({"role": role, "content": text, "timestamp": ts})
        node_id = parent
        if not node_id or node_id in seen:
            break

    messages.reverse()  # Chronological order
    return messages
```

### Hermes state.db Import

Hermes sessions table requires unique `title` values. Handle duplicates by appending `(2)`, `(3)`, etc.

```python
# Session insert with dedup
base_title = title
suffix = 2
while True:
    try:
        cur.execute("INSERT INTO sessions (id, source, started_at, ended_at, message_count, title, archived) VALUES (?, ?, ?, ?, ?, ?, 0)",
                    (session_id, "chatgpt_import", create_time, update_time, len(messages), title))
        break
    except sqlite3.IntegrityError:
        title = f"{base_title} ({suffix})"
        suffix += 1

# Messages use auto-increment IDs
for msg in messages:
    max_msg_id += 1
    cur.execute("INSERT INTO messages (id, session_id, role, content, timestamp, active, compacted) VALUES (?, ?, ?, ?, ?, 1, 0)",
                (max_msg_id, session_id, msg["role"], msg["content"], msg["timestamp"]))

# MUST rebuild FTS after bulk insert
cur.execute("INSERT INTO messages_fts(messages_fts) VALUES('rebuild')")
```

### Key Schema Fields

**sessions**: `id` (text PK, format `YYYYMMDD_HHMMSS_<hex6>`), `source` ("chatgpt_import"), `started_at`/`ended_at` (unix float), `title` (UNIQUE), `message_count`, `archived`

**messages**: `id` (int PK, auto-increment), `session_id` (FK), `role` ("user"/"assistant"/"tool"), `content` (text), `timestamp` (unix float), `active` (1), `compacted` (0)

### Downloading from Google Drive

User may share a Google Drive link. Direct download requires either:
1. File set to "Anyone with the link" → `gdown` works
2. File NOT public → ask user to change sharing, or use browser

```bash
pip install gdown -q
gdown "https://drive.google.com/uc?id=FILE_ID" -O output.zip
# File ID is the long string in the URL: /d/FILE_ID/view
```

If gdown fails with "Cannot retrieve the public link" → file isn't public. Ask user to change sharing to "Anyone with the link".

## Discord Channel Ingestion (API-Based)

When the user wants to absorb conversations from a Discord channel (e.g., "read all messages in #kimaki and ingest them"), use the `discord` tool's `fetch_messages` action instead of SQLite extraction.

### Pattern

```
1. Find channel ID: discord_admin(action='list_channels', guild_id=<id>)
2. Fetch messages: discord(action='fetch_messages', channel_id=<id>, limit=100)
3. Paginate backward: discord(..., before=<oldest_message_id>)
4. Repeat until count=0
```

### Context Absorption

After fetching, distill key context into memory:
- **Who**: Usernames, display names, IDs of all participants
- **What**: Topics discussed, decisions made, tasks requested
- **Patterns**: User preferences, correction signals, workflow habits
- Save to memory tool, not as raw message dumps

### Caveats

- Bot must have READ_MESSAGE_HISTORY permission for the channel
- `discord_admin` does NOT have `delete_channel` — grant bot MANAGE_CHANNELS + use raw REST API (`curl -X DELETE`), or have user delete manually
- `fetch_messages` returns empty content for image/file-only messages (API doesn't render attachments as text)
- Threads may exist — check with archived threads endpoint (requires permission)
- Max 100 messages per fetch; paginate with `before` parameter

### Post-Extraction: Platform Gateway Migration

When migrating from a bot platform (Kimaki, OpenClaw, etc.), the extraction phase should include setting up the new platform's gateway BEFORE deleting the old one:

1. **Extract bot tokens** from the old platform's database
2. **Configure Hermes gateway** with the extracted token:
   ```bash
   echo 'DISCORD_BOT_TOKEN=<token>' >> ~/.hermes/.env
   echo 'DISCORD_HOME_CHANNEL=<channel_id>' >> ~/.hermes/.env
   ```
3. **Install and start gateway**:
   ```bash
   hermes gateway install
   hermes gateway start
   ```
4. **Send test message** to verify:
   ```bash
   hermes send --to discord:<channel_id> "Migration complete."
   ```
5. **Only then** remove the old platform

This prevents a window where the bot is offline and users can't reach it.

## Pitfalls

- **Text not in obvious tables**: Always check `part`, `event`, or JSON blob tables. The `message` table often only has metadata.
- **JSON encoding varies**: Some platforms store JSON with escaped quotes, others with single quotes. Use `json.loads` with `strict=False` for safety.
- **WAL files**: SQLite WAL files (`.db-wal`) contain uncommitted data. If a DB seems incomplete, check for WAL files and merge them.
- **Large JSON blobs**: Event-sourced databases can have huge JSON fields. Extract only what you need, don't dump entire blobs.
- **Binary data**: Some parts contain binary data (images, files). Skip these when extracting text.
- **Session ID formats vary**: OpenCode uses `ses_...`, Kimaki uses numeric Discord IDs, Claude uses UUIDs. Don't assume a format.
- **Duplicate events**: Event-sourced databases log every state change. Deduplicate by message ID before extracting text.
- **Kimaki skills not in user dir**: Kimaki skills ship inside the npm package (`/usr/lib/node_modules/kimaki/skills/`), not in `~/.config/`. Use `find` to locate them.
- **Tokens in SQLite, not .env**: Discord bot tokens and API keys are often stored in the SQLite database's `bot_tokens` table, not in `.env` files. Check both.
- **Recursive text extraction is necessary**: Event JSON is deeply nested (3-4 levels). Simple `json.loads` + key access won't find all text. Use the `find_all_text` recursive pattern.
- **ID prefixes in extracted text**: When using recursive text extraction, filter out IDs that start with `evt_`, `msg_`, `prt_`, `call_` — these are internal identifiers, not conversation content.
- **ChatGPT tree uses parent pointers, not children**: The `children` array in every node is always empty. Walk from `current_node` backwards through `parent` links, then `reverse()`. Trying to walk children yields 1-message conversations.
- **ChatGPT `sessions.title` is UNIQUE**: Bulk inserts will fail on duplicate titles (many conversations share names like "New chat"). Append `(2)`, `(3)` etc. in a retry loop.
- **ChatGPT export ZIP may be large**: The ZIP itself can be 50-100MB+. Discord's 25MB limit won't handle it. Use Google Drive, local filesystem, or transfer.sh.
- **ChatGPT messages are `content.parts` arrays, not strings**: Each message's content is `{"parts": ["text1", "text2"]}`. Join with `\n`, filter out None/empty parts.
- **Don't save tokens to memory**: Memory is injected into every future conversation turn. Tokens in memory = tokens leaked into every API call. Save to files instead.
- **ChatGPT has multiple drafts of the same content**: When extracting specific content (chapters, code, analyses), the same section often appears in 3-5 iterations. Always sort by `create_time` and use the latest. Don't grab the first match.
- **ChatGPT long outputs split across messages**: When the assistant splits content (e.g., "Part 1" + "Part 2"), the parts live in separate nodes in the mapping dict. Identify them by content markers, not by position. Verify the combination is narrative-complete before saving.
- **ChatGPT mapping keys are UUIDs, not sequential**: The `mapping` dict uses random UUIDs as keys. You cannot iterate in order — you must sort by `create_time` or walk parent pointers.
- **`hermes send` syntax`
- **Gateway must be running for `hermes send`**: Unlike what the help text says, `hermes send` works without the gateway running for bot-token platforms. But verify with `hermes gateway status` if delivery fails.

## Targeted Content Extraction from ChatGPT Exports

When the user wants specific content (chapters, drafts, code, decisions) from a ChatGPT export — not a full import — use these patterns.

### Step 1: Find the Session by Title

ChatGPT exports contain 10+ conversation files. Search across all of them:

```bash
# Find which file(s) contain the target session
grep -l -i "search term" /tmp/chatgpt-export/chatgpt-data/conversations-*.json

# Or extract all titles with their file locations
for f in /tmp/chatgpt-export/chatgpt-data/conversations-*.json; do
  python3 -c "
import json, sys
with open('$f') as fh:
    data = json.load(fh)
for c in data:
    t = c.get('title','')
    if t: print(f'$f  {t}  ({len(c.get(\"mapping\",{}))} msgs)')
"
done
```

### Step 2: Identify Content Versions (Iterative Drafts)

ChatGPT often produces multiple drafts of the same content. To find the **final/latest version**:

```python
mapping = conv.get("mapping", {})
messages = []
for key, val in mapping.items():
    msg = val.get("message")
    if msg and msg.get("author", {}).get("role") == "assistant":
        parts = msg.get("content", {}).get("parts", [])
        text = "\n".join(str(p) for p in parts) if parts else ""
        ts = msg.get("create_time")
        if len(text) > 1000:  # Filter noise
            messages.append((ts, key, len(text), text[:200]))

# Sort by timestamp — latest = final version
messages.sort(key=lambda x: x[0] if x[0] else 0)
```

**Pattern**: The assistant's final revision is always the latest `create_time` for a given content marker (e.g., "Chapter 4", "CONVICTION"). Earlier versions are drafts. When content spans multiple revisions, the last one before the user moves to the next topic is definitive.

### Step 3: Combine Multi-Part Outputs

ChatGPT sometimes splits long content across multiple messages (e.g., "Roman Part 1", "Roman Part 2", "Jonah"). To combine:

1. Identify related messages by content markers (chapter number, character name)
2. Verify the combination makes narrative sense (check first/last lines of each part)
3. Concatenate with appropriate separators

```python
# Example: combining Chapter 1 parts
parts = [ch1_roman_part1, ch1_roman_part2, ch1_jonah]
combined = "\n\n".join(parts)
```

**Pitfall**: Don't assume order by message position — some parts may appear out of order in the mapping dict. Use content markers ("Part 1", "Part 2", "Roman", "Jonah") or the message tree's parent/child structure to determine correct order.

### Step 4: Verify Extraction Completeness

```bash
# Word count per chapter
python3 -c "
import re
with open('output.txt') as f:
    text = f.read()
chapters = re.split(r'={80}\n.*CHAPTER', text)
for ch in chapters[1:]:
    title = ch.split('\n')[0][:60]
    words = len(ch.split())
    print(f'  CHAPTER {title}: ~{words} words')
print(f'  Total: ~{len(text.split())} words')
"
```

## Verification

After ingestion, verify completeness:

1. Count extracted sessions vs source
2. Spot-check a few conversations for accuracy
3. Confirm user identity markers are captured
4. Verify no sensitive tokens are saved to memory (only save what's needed for context)

## Example: OpenCode + Kimaki Full Migration

```bash
# === DISCOVERY ===
# Find all databases
find ~ -name 'opencode.db' -o -name 'discord-sessions.db' 2>/dev/null

# Check GitHub for persona repos
gh repo list <username> --limit 20

# === EXTRACTION ===
# Extract session list with message counts
sqlite3 ~/.local/share/opencode/opencode.db \
  "SELECT id, title, agent, model, 
   datetime(time_created/1000, 'unixepoch') as created 
   FROM session ORDER BY time_created ASC;"

# Extract conversation text from a session (OpenCode)
sqlite3 ~/.local/share/opencode/opencode.db \
  "SELECT data FROM part WHERE session_id='ses_xxx' AND data LIKE '%text%';"

# Extract from Kimaki event-sourced DB
sqlite3 ~/.kimaki/discord-sessions.db \
  "SELECT event_json FROM session_events WHERE session_id='ses_xxx' ORDER BY timestamp;"

# Extract Discord bot tokens
sqlite3 ~/.kimaki/discord-sessions.db "SELECT * FROM bot_tokens;"

# Extract thread-to-session mapping
sqlite3 ~/.kimaki/discord-sessions.db "SELECT * FROM thread_sessions;"

# === GITHUB PERSONA FETCH ===
# List SOULS repo
gh api repos/<user>/SOULS/contents/

# Download a persona file
gh api repos/<user>/SOULS/contents/CUSO.md -q .content | base64 -d > CUSO.md

# Download all personas in a loop
for f in $(gh api repos/<user>/SOULS/contents/ -q '.[].name'); do
  gh api repos/<user>/SOULS/contents/$f -q .content | base64 -d > $f
done

# === SAVE EVERYTHING ===
mkdir -p ~/platform-reference/{souls,agents,skills,uploads}
# ... copy files ...
```

See `references/opencode-kimaki-schema.md` for detailed schema documentation.
See `references/kimaki-schema.md` for concrete Kimaki/OpenCode table structures, token extraction, and gateway migration steps.
See `references/persona-repository-patterns.md` for GitHub persona repo patterns and agent config formats.
See `references/chatgpt-import-script.py` for a ready-to-run ChatGPT ZIP-to-Hermes import script.
