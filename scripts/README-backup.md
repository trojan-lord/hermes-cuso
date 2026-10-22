# Hermes Agent Config Backup

Backup of Hermes Agent configuration, SOUL.md, skills, scripts, cron jobs, and memories.

**Not included** (sensitive/generated): `.env`, `auth.json`, `tokens.json`, `state.db`,
sessions, logs, cache, and volatile cron runtime state (lock files, ticker heartbeats,
admission receipts, execution databases).

## Restore

```bash
# Clone this repo
gh repo clone trojan-lord/hermes-cuso hermes-cuso

# Copy files back to ~/.hermes/
cp hermes-cuso/config.yaml ~/.hermes/
cp hermes-cuso/SOUL.md ~/.hermes/
rsync -a hermes-cuso/skills/ ~/.hermes/skills/
rsync -a hermes-cuso/scripts/ ~/.hermes/scripts/
rsync -a hermes-cuso/cron/ ~/.hermes/cron/
rsync -a hermes-cuso/memories/ ~/.hermes/memories/
```

## Notes

- `skills/` is stored as **real file content**, not symlinks. Several skills
  (`hyperframes*`, `media-use`) live in `~/.claude/skills/` and are symlinked into
  `~/.hermes/skills/`. The sync dereferences them (`rsync -L`) so a restore is
  self-contained and does not depend on `~/.claude/` existing.
- `cron/jobs.json` holds the job definitions (schedule, prompt, enabled state).
  `cron/output/` holds historical run logs and is append-only.
- The live sync script is `~/.hermes/scripts/sync-hermes-backup.sh`. The `sync.sh`
  in this repo root is a thin wrapper that calls it.
