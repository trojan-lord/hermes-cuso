#!/bin/bash
# Sync local .hermes config to GitHub backup repo
# Runs silently if nothing changed
#
# Usage: sync-hermes-backup.sh [--dry-run]
#   --dry-run  stage changes in a throwaway clone and report, but do not push.

set -u

REPO="trojan-lord/hermes-cuso"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
SCRATCH="${TMPDIR:-$HOME/.hermes/cache/scratch}"
REPO_DIR="$SCRATCH/.hermes-Cuso-sync"
DRY_RUN=0

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
        *) echo "unknown argument: $arg" >&2; exit 2 ;;
    esac
done

mkdir -p "$SCRATCH"

# Single instance only -- two concurrent syncs would fight over the clone/push.
exec 9>"$SCRATCH/.hermes-backup.lock"
if ! flock -n 9; then
    echo "ERROR: another backup sync is already running" >&2
    exit 1
fi

cleanup() { rm -rf "$REPO_DIR"; }
trap cleanup EXIT

# Clone fresh each time (avoids stale state)
rm -rf "$REPO_DIR"
if ! gh repo clone "$REPO" "$REPO_DIR" 2>/dev/null; then
    echo "ERROR: could not clone $REPO" >&2
    exit 1
fi

cd "$REPO_DIR" || { echo "ERROR: cd failed" >&2; exit 1; }

# --- Config files -----------------------------------------------------------
cp "$HERMES_HOME/SOUL.md" "$REPO_DIR/SOUL.md"
cp "$HERMES_HOME/config.yaml" "$REPO_DIR/config.yaml"

# --- Memories ---------------------------------------------------------------
mkdir -p "$REPO_DIR/memories"
cp "$HERMES_HOME/memories/MEMORY.md" "$REPO_DIR/memories/MEMORY.md"
cp "$HERMES_HOME/memories/USER.md" "$REPO_DIR/memories/USER.md"

# --- Scripts ----------------------------------------------------------------
mkdir -p "$REPO_DIR/scripts"
cp "$HERMES_HOME/scripts/"* "$REPO_DIR/scripts/"

# --- Skills -----------------------------------------------------------------
# Several skills (hyperframes*, media-use) are symlinks into ~/.claude/skills.
# -L dereferences them so the backup holds real file content and a restore is
# self-contained instead of pointing at a directory we never backed up.
# --delete propagates removals.
rsync -aL --delete "$HERMES_HOME/skills/" "$REPO_DIR/skills/"

# The source of those symlinks is backed up too, so Claude Code's own skill
# tree survives a restore as well.
if [ -d "$CLAUDE_HOME/skills" ]; then
    mkdir -p "$REPO_DIR/claude-skills"
    rsync -a --delete "$CLAUDE_HOME/skills/" "$REPO_DIR/claude-skills/"
fi

# --- Cron -------------------------------------------------------------------
# Job definitions + run history only. Volatile runtime state (lock files,
# ticker heartbeats, admission receipts, execution databases) is excluded.
mkdir -p "$REPO_DIR/cron"
cp "$HERMES_HOME/cron/jobs.json" "$REPO_DIR/cron/jobs.json"
if [ -d "$HERMES_HOME/cron/output" ]; then
    # Append-only: keep history that is already in the repo.
    rsync -a "$HERMES_HOME/cron/output/" "$REPO_DIR/cron/output/"
fi
# Runtime state was committed before it was excluded; drop it.
rm -f "$REPO_DIR/cron/.jobs.lock" "$REPO_DIR/cron/.tick.lock" "$REPO_DIR/cron/.fire-"*.lock \
      "$REPO_DIR/cron/ticker_heartbeat" "$REPO_DIR/cron/ticker_last_success"

# --- Repo docs --------------------------------------------------------------
cp "$HERMES_HOME/scripts/README-backup.md" "$REPO_DIR/README.md"
cat > "$REPO_DIR/sync.sh" <<'EOF'
#!/bin/bash
# Thin wrapper -- the live sync script lives in ~/.hermes/scripts/.
exec "$HOME/.hermes/scripts/sync-hermes-backup.sh" "$@"
EOF
chmod +x "$REPO_DIR/sync.sh"

# --- Commit -----------------------------------------------------------------
git add -A
CHANGES=$(git diff --cached --stat)

if [ -z "$CHANGES" ]; then
    echo "No changes."
    exit 0
fi

if [ "$DRY_RUN" = "1" ]; then
    echo "DRY RUN -- would sync:"
    echo "$CHANGES"
    exit 0
fi

TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")
if ! git commit -m "Auto-sync .hermes config ($TIMESTAMP)"; then
    echo "ERROR: commit failed" >&2
    exit 1
fi

if ! git push; then
    echo "ERROR: push failed -- backup NOT saved" >&2
    exit 1
fi

echo "Synced: $(echo "$CHANGES" | tail -1)"
