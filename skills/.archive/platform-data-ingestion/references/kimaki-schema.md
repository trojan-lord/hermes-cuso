# Kimaki + OpenCode Schema Reference

Concrete schema details discovered during the OpenCode→Hermes migration (2026-07-12).

## Kimaki Discord Sessions DB

Location: `~/.kimaki/discord-sessions.db`

### Tables

| Table | Key Columns | Notes |
|-------|-------------|-------|
| `bot_tokens` | `app_id`, `token`, `client_id`, `client_secret`, `bot_mode` | **Discord bot token lives here**, not in .env |
| `bot_api_keys` | provider, key | API keys for LLM providers |
| `session_events` | `session_id`, `thread_id`, `timestamp`, `event_json` | Event-sourced. JSON blobs contain all conversation text |
| `thread_sessions` | thread_id, session_id | Maps Discord thread IDs to session IDs |

### bot_tokens row structure

```
app_id: 1487198452546015232
token: MTQ4NzE5ODQ1MjU0NjAxNTIzMg.GzrkdV.xxxxx  (Discord bot token)
client_id: 1487198452546015232
client_secret: xxxxx
bot_mode: 2
```

### session_events JSON structure

Events are deeply nested. The useful fields:
- `event.type`: "message.updated", "message.part.updated", "session.started", etc.
- `event.properties.message.role`: "user", "assistant", "system"
- `event.properties.message.agent`: "claude", "codex", etc.
- `event.properties.message.model`: model name
- `event.properties.part.text`: actual conversation text (may be 3-4 levels deep)
- `event.properties.part.info.content`: alternative text location

### Extracting conversation text

Recursive extraction is necessary because text is buried in JSON:

```python
import json

def find_all_text(obj):
    """Find all text fields in deeply nested event JSON."""
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'text' and isinstance(v, str) and len(v) > 3:
                results.append(v)
            results.extend(find_all_text(v))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_all_text(item))
    return results

# Filter out internal IDs
for text in find_all_text(event_json):
    if text.strip() and not text.startswith(('evt_', 'msg_', 'prt_', 'call_')):
        print(text)
```

## Restored Session DB (Dobby)

Location: `~/.kimaki/restored-session-dobby.db`

Same schema as `discord-sessions.db` but contains the Dobby house-elf bot's conversation history. Text content IS present in event_json (unlike the main DB where it's sparse).

```bash
sqlite3 ~/.kimaki/restored-session-dobby.db \
  "SELECT event_json FROM session_events ORDER BY timestamp;"
```

## OpenCode Session DB

Location: `~/.local/share/opencode/opencode.db`

### Key tables

| Table | Purpose |
|-------|---------|
| `session` | Session metadata (id, title, agent, model, time_created) |
| `message` | Message metadata (role, session_id, provider) |
| `part` | Message content (text, tool calls, tool results) |

### Schema

```sql
-- Session list
SELECT id, title, agent, model, 
       datetime(time_created/1000, 'unixepoch') as created
FROM session ORDER BY time_created ASC;

-- Conversation text for a session
SELECT data FROM part 
WHERE session_id='ses_xxx' AND data LIKE '%text%';

-- Full conversation with messages
SELECT m.id, m.role, p.data
FROM message m
JOIN part p ON p.message_id = m.id
WHERE m.session_id = 'ses_xxx';
```

## Kimaki Config Files

### opencode-config.json (`~/.kimaki/opencode-config.json`)

Contains:
- Model/provider settings
- Agent persona reference (SOUL.md path)
- Tool configurations
- Agent names and roles

### Kimaki skills location

Kimaki skills ship inside the npm package, NOT in user directories:

```bash
# Find all Kimaki skills
find /usr/lib/node_modules/kimaki/skills -name 'SKILL.md' -exec dirname {} \;

# Copy skills to reference directory
for skill_dir in $(find /usr/lib/node_modules/kimaki/skills -name 'SKILL.md' -exec dirname {} \;); do
  skill_name=$(basename "$skill_dir")
  cp "$skill_dir/SKILL.md" "/target/dir/${skill_name}.md"
done
```

## Kimaki → Hermes Discord Gateway Migration

After extracting the bot token from Kimaki's SQLite DB:

### 1. Add token to Hermes .env

```bash
echo 'DISCORD_BOT_TOKEN=<token_from_bot_tokens_table>' >> ~/.hermes/.env
echo 'DISCORD_HOME_CHANNEL=<channel_id>' >> ~/.hermes/.env
```

### 2. Install and start gateway

```bash
hermes gateway install   # Creates systemd user service
hermes gateway start     # Starts the service
hermes gateway status    # Verify it's running
```

### 3. Send test message

```bash
hermes send --to discord:<channel_id> "Migration complete. Bot is alive."
```

### 4. Remove Kimaki

```bash
systemctl --user stop kimaki
systemctl --user disable kimaki
rm ~/.config/systemd/user/kimaki.service
systemctl --user daemon-reload
npm uninstall -g kimaki
rm -rf ~/.kimaki ~/.config/opencode ~/.opencode ~/.local/share/opencode ~/.cache/opencode
```

## Pitfalls Discovered

1. **Session events may be sparse in main DB**: The `discord-sessions.db` `session_events` table had event types (message.updated, session.started) but text content was often empty or minimal. The actual conversation text was more complete in the OpenCode DB and the restored session DB.

2. **Restored session DB has more text**: `restored-session-dobby.db` contained the full conversation text in event_json, while `discord-sessions.db` often had empty text parts. Check both databases.

3. **Kimaki bot token format**: Discord bot tokens start with the app ID as a snowflake, followed by a random component. The full token from `bot_tokens` table works directly in Hermes `.env`.

4. **Gateway auto-enables Discord**: When `DISCORD_BOT_TOKEN` is set in `.env`, Hermes gateway automatically enables the Discord platform. No need to manually configure in `config.yaml`.

5. **Message Content Intent required**: The Discord bot must have "Message Content Intent" enabled in the Discord Developer Portal under Bot → Privileged Gateway Intents for the bot to read messages.
