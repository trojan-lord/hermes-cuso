# Discord Slash Command Parity Audit

Goal: prove that what the user sees in Discord's slash picker == what the
gateway actually serves. Verified working Aug 2026 (Hermes v0.20.0, 60 commands).

## 1. Live commands on Discord's side (the "visible" list)

```bash
TOKEN=$(grep -E "DISCORD_BOT_TOKEN" ~/.hermes/.env | head -1 | cut -d= -f2- | tr -d '"' | tr -d ' ')
# App ID is NOT in config.yaml/.env — resolve it:
curl -s -H "Authorization: Bot $TOKEN" "https://discord.com/api/v10/applications/@me"   # → .id
curl -s -H "Authorization: Bot $TOKEN" "https://discord.com/api/v10/applications/{APP_ID}/commands"
```

## 2. What the gateway registers (the "available" list)

Three sources, all in `~/.hermes/hermes-agent/plugins/platforms/discord/adapter.py`:

- **27 native commands** — hand-built in `_register_slash_commands()` (~line 5427):
  new, reset, model, reasoning, personality, retry, undo, status, sethome, stop,
  steer, compress, title, resume, usage, help, insights, reload-mcp, reload-skills,
  voice, update, restart, approve, deny, thread, queue, background
- **Auto-registered from COMMAND_REGISTRY** (`hermes_cli/commands.py`) — every
  command where `_is_gateway_available()` is true (skips `cli_only` commands,
  honors `gateway_config_gate` via `_resolve_config_gates()`).
- **One consolidated `/skill` group** — flat command with autocomplete, NOT one
  command per skill. The old nested layout (category/name) grew the payload past
  Discord's ~8000-byte per-command limit and rejected the whole batch
  (issues #11321, #10259, #11385...). Autocomplete options don't count against
  the registration budget.
- **Plugin commands** — `_iter_plugin_command_entries()` mirror into the tree
  (0 on this install).

Hard cap: Discord allows **100 global commands per application** (error 30032
rejects an over-limit batch and silently breaks ALL slash commands). The adapter
reserves 1 slot for `/skill` and drops lower-priority auto-registrations past
the cap, logging `Reached Discord's limit of 100...; skipped N`.

Compute the gateway-available registry set with the REAL code (don't eyeball):

```bash
cd ~/.hermes/hermes-agent && ./venv/bin/python3 -c "
import sys; sys.path.insert(0, '.')
from hermes_cli.commands import COMMAND_REGISTRY, _is_gateway_available, _resolve_config_gates
overrides = _resolve_config_gates()
gw = [c for c in COMMAND_REGISTRY if _is_gateway_available(c, overrides)]
print(len(gw), ' '.join(c.name for c in gw))
"
```

## 3. Sync health from the gateway log

```bash
grep -E "Safely reconciled|same slash-command fingerprint|Reached Discord's limit" ~/.hermes/logs/gateway.log | tail
```

- `Safely reconciled N slash command(s): unchanged=U updated=W recreated=R created=C deleted=D`
  → a full sync ran; check created/deleted for drift (Jul 31: created=4 = curator,
  kanban, blueprint, bundles joined → count ticked 56→60).
- `Skipping Discord slash command sync: same slash-command fingerprint already synced`
  → desired set == live set byte-for-byte. GOOD — means no drift, no sync needed.
- `Reached Discord's limit of 100...` → over cap, some commands never made it.

## 4. Math check

total = native + gateway-available-from-registry (deduped against native) +
/skill group + plugin commands, all ≤ 99 (100 − 1 reserved). On this install:
27 native + 32 auto + 1 skill + 0 plugin = 60 == Discord's live count.

## Pitfalls

- **CommandDef regex**: the name is the FIRST POSITIONAL arg —
  `CommandDef\(\s*"([a-z0-9-]+)"`. A naive `name="..."` search returns **0
  matches** and looks like an empty registry. Caught this live; the registry
  actually has 92 entries.
- **App ID**: not in config.yaml or .env — always resolve via `/applications/@me`.
- **CLI-only commands** (clear, save, config, cron, quit, etc.) are correctly
  ABSENT from Discord — `cli_only=True` excludes them. Not a bug.
- After a `hermes update`, the post-restart sync line is usually the fingerprint
  skip — that's the desired state, not a failure.
- Discord command names: lowercase, hyphens OK, max 32 chars.
