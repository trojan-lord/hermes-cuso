# Hermes Agent Config Backup

Backup of Hermes Agent configuration, SOUL.md, skills, scripts, cron jobs, and memories.

**Not included** (sensitive/generated): `.env`, `auth.json`, `tokens.json`, `state.db`, sessions, logs, cache.

## Restore

```bash
# Copy files back to ~/.hermes/
cp config.yaml ~/.hermes/
cp SOUL.md ~/.hermes/
rsync -a skills/ ~/.hermes/skills/
rsync -a scripts/ ~/.hermes/scripts/
rsync -a cron/ ~/.hermes/cron/
rsync -a memories/ ~/.hermes/memories/
```
