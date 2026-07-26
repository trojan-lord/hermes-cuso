#!/bin/bash
# Sync hermes config to backup repo
set -e

BACKUP_DIR="/home/h2/hermes-backup"
HERMES_DIR="/home/h2/.hermes"

cd "$BACKUP_DIR"

# Copy updated files
cp "$HERMES_DIR/config.yaml" .
cp "$HERMES_DIR/SOUL.md" .
rsync -a --delete --exclude='__pycache__' "$HERMES_DIR/skills/" skills/
rsync -a "$HERMES_DIR/scripts/" scripts/ 2>/dev/null || true
rsync -a "$HERMES_DIR/cron/" cron/ 2>/dev/null || true
rsync -a "$HERMES_DIR/memories/" memories/ 2>/dev/null || true

# Commit and push
git add -A
CHANGES=$(git status --porcelain)
if [ -n "$CHANGES" ]; then
    git commit -m "Backup sync: $(date '+%Y-%m-%d %H:%M')"
    git push
    echo "Backup pushed to GitHub."
else
    echo "No changes to backup."
fi
