#!/bin/bash
# OpenCode delegate wrapper for Hermes
# Usage:
#   opencode-delegate.sh "task" [workdir] [model]           # new session
#   opencode-delegate.sh --continue SESSION_ID "task" [workdir] [model]  # continue session
#
# Outputs: text response to stdout, session ID to stderr (for capture)

OPENCODE=~/.opencode/bin/opencode
CONTINUE=false
SESSION_ID=""

# Parse --continue flag
if [ "$1" = "--continue" ]; then
    CONTINUE=true
    SESSION_ID="$2"
    shift 2
fi

TASK="${1:?Usage: opencode-delegate.sh [\"task\"] [workdir] [model]}"
WORKDIR="${2:-.}"
MODEL="${3:-}"

# Build command
CMD=("$OPENCODE" "run" "$TASK" "--format" "json" "--pure" "--dir" "$WORKDIR" "--auto")

if [ "$CONTINUE" = true ] && [ -n "$SESSION_ID" ]; then
    CMD+=("--session" "$SESSION_ID")
fi

if [ -n "$MODEL" ]; then
    CMD+=("--model" "$MODEL")
fi

# Run and extract text + session ID from JSON stream
"${CMD[@]}" 2>/dev/null | python3 -c "
import sys, json

session_id = None
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        event = json.loads(line)
        # Capture session ID
        sid = event.get('sessionID')
        if sid and not session_id:
            session_id = sid
        # Output text responses
        if event.get('type') == 'text':
            text = event.get('part', {}).get('text', '')
            if text:
                print(text)
    except json.JSONDecodeError:
        pass

# Print session ID to stderr for capture
if session_id:
    print(f'SESSION_ID={session_id}', file=sys.stderr)
"
