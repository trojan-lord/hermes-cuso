# OpenCode + Kimaki Schema Reference

Discovered during migration session on 2026-07-12.

## OpenCode Database

Location: `~/.local/share/opencode/opencode.db`

### Tables

| Table | Purpose |
|-------|---------|
| `session` | Session metadata (id, title, agent, model, timestamps) |
| `message` | Message metadata (id, session_id, role, tokens, cost) |
| `part` | **Actual text content** (id, message_id, session_id, data JSON) |
| `project` | Project metadata |
| `todo` | Session-associated todos |
| `session_share` | Shared session URLs |

### Key Schema Details

```sql
-- Session list with message counts
SELECT s.id, s.title, s.agent, s.model, COUNT(m.id) as msg_count
FROM session s
LEFT JOIN message m ON m.session_id = s.id
GROUP BY s.id
ORDER BY s.time_created ASC;

-- Extract text from parts (CRITICAL: text is in `part.data`, not `message`)
SELECT data FROM part 
WHERE session_id='ses_xxx' 
AND data LIKE '%"type":"text"%'
ORDER BY time_created ASC;

-- Find user identity markers
SELECT data FROM part 
WHERE data LIKE '%discord-user%' 
LIMIT 5;
```

### Part JSON Structure

```json
{
  "type": "text",
  "text": "The actual conversation text",
  "id": "prt_xxx",
  "messageID": "msg_xxx",
  "sessionID": "ses_xxx"
}
```

### Message JSON Structure

```json
{
  "role": "user|assistant",
  "agent": "cuso|build|plan",
  "model": {"providerID": "opencode", "modelID": "big-pickle"},
  "time": {"created": 1783804063190},
  "tokens": {"input": 24143, "output": 25, "reasoning": 323}
}
```

## Kimaki Discord Sessions Database

Location: `~/.kimaki/discord-sessions.db`

### Tables

| Table | Purpose |
|-------|---------|
| `bot_tokens` | Discord bot token, app ID, client secret |
| `bot_api_keys` | API keys for different providers |
| `channel_directories` | Discord channels mapped to project directories |
| `channel_agents` | Agent assignments per channel |
| `thread_sessions` | Discord thread → OpenCode session mapping |
| `session_events` | Event-sourced session history (JSON blobs) |
| `part_messages` | Part → message → thread linkage |
| `session_agents` | Agent used per session |
| `session_models` | Model used per session |
| `scheduled_tasks` | Cron-like scheduled tasks |

### Key Queries

```sql
-- Bot configuration
SELECT * FROM bot_tokens;
SELECT * FROM bot_api_keys;

-- Thread to session mapping
SELECT ts.thread_id, ts.session_id, ts.last_synced_name, 
       cd.directory, cd.channel_type
FROM thread_sessions ts
JOIN channel_directories cd ON cd.channel_id = ts.thread_id;

-- Session events (event-sourced)
SELECT event_json FROM session_events 
WHERE session_id='ses_xxx' 
ORDER BY timestamp ASC;

-- Find text in events
SELECT event_json FROM session_events 
WHERE event_json LIKE '%"type":"text"%' 
ORDER BY timestamp ASC;
```

### Event JSON Structure

Events are nested JSON with type-based dispatch:

```json
{
  "id": "evt_xxx",
  "type": "message.part.updated",
  "properties": {
    "sessionID": "ses_xxx",
    "part": {
      "type": "text",
      "text": "The conversation text",
      "messageID": "msg_xxx"
    }
  }
}
```

Event types: `session.created`, `session.updated`, `session.status`, 
`message.updated`, `message.part.updated`

## Restored Dobby Session

Location: `~/.kimaki/restored-session-dobby.db`

Same schema as `discord-sessions.db` but contains a single restored session 
from a previous bot persona called "Dobby" (house-elf style responses).

Session ID: `ses_dobby_restored_1520402675173425202`

## Configuration Files

### OpenCode Config

Location: `~/.config/opencode/opencode.json`

Contains:
- Model provider settings (Ollama, OpenCode, etc.)
- Agent definitions (cuso agent with SOUL.md reference)
- Permission settings
- Skill paths
- Plugin references (Kimaki plugin)

### Kimaki Config

Location: `~/.kimaki/opencode-config.json`

Contains:
- OpenCode server settings
- Permission configurations
- Provider settings (XAI/Grok models)
- Skill paths

### SOUL.md

Location: `~/.config/opencode/SOUL.md` (957 lines)

The "Cuso" persona definition. References in OpenCode config via:
```json
"agent": {
  "cuso": {
    "prompt": "{file:~/.config/opencode/SOUL.md}",
    "description": "Observer. Collector of anomalies. Anxiety avatar."
  }
}
```

## Discord Identity

- Bot: cuso#9713 (App ID: 1487198452546015232)
- Guild: 1491816940673568960
- Main channel: 1514661214817488936
- Users: mumble_monster (395258910455365642), Pola' Bea' (421188027683962882)

## Common Pitfalls Discovered

1. **Text in `part` table, not `message`**: The `message` table only has metadata. 
   Actual conversation text is in `part.data` as JSON.

2. **Event-sourced databases**: Kimaki stores every state change as an event. 
   Must deduplicate by message ID to avoid repeated text.

3. **WAL files present**: Both `.db-wal` and `.db-shm` files exist alongside 
   the main `.db` file. The database may have uncommitted data.

4. **JSON field extraction**: Event JSON is deeply nested. Use recursive 
   text extraction to find all conversation content.

5. **Discord user tags in messages**: User messages contain 
   `<discord-user name="..." user-id="..." />` tags that identify who sent what.
