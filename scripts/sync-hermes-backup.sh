#!/bin/bash
# Sync local .hermes config to GitHub backup repo
# Runs silently if nothing changed

REPO_DIR="/tmp/.hermes-Cuso-sync"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

# Clone fresh each time (avoids stale state)
rm -rf "$REPO_DIR"
gh repo clone trojan-lord/hermes-cuso "$REPO_DIR" 2>/dev/null || exit 1

# Copy config files
cp "$HERMES_HOME/SOUL.md" "$REPO_DIR/SOUL.md" 2>/dev/null
cp "$HERMES_HOME/config.yaml" "$REPO_DIR/config.yaml" 2>/dev/null

# Copy memories
mkdir -p "$REPO_DIR/memories"
cp "$HERMES_HOME/memories/MEMORY.md" "$REPO_DIR/memories/MEMORY.md" 2>/dev/null
cp "$HERMES_HOME/memories/USER.md" "$REPO_DIR/memories/USER.md" 2>/dev/null

# Copy scripts
mkdir -p "$REPO_DIR/scripts"
cp "$HERMES_HOME/scripts/"* "$REPO_DIR/scripts/" 2>/dev/null

# Sync skills
rsync -a --delete "$HERMES_HOME/skills/" "$REPO_DIR/skills/" 2>/dev/null

# Check for changes
cd "$REPO_DIR"
git add -A
CHANGES=$(git diff --cached --stat)

if [ -z "$CHANGES" ]; then
    echo "No changes."
    rm -rf "$REPO_DIR"
    exit 0
fi

# Commit and push
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")
git commit -m "Auto-sync .hermes config ($TIMESTAMP)" 2>/dev/null
git push 2>/dev/null

echo "Synced: $(echo "$CHANGES" | tail -1)"

# Cleanup
rm -rf "$REPO_DIR"
