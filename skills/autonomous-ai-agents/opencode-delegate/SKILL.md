---
name: opencode-delegate
description: Delegate coding tasks to OpenCode CLI as a background agent. Use for provider fallback, large refactors, or parallel coding work.
tags: [opencode, coding, delegation, fallback]
related_skills: [opencode, claude-code, codex]
---

# OpenCode Delegate for Hermes

## When to Use
- **Provider fallback**: big-pickle/opencode-zen is down, need local coding agent
- **Large refactors**: task too big for subagents or would blow context
- **Parallel work**: need a second agent working while Hermes handles other tasks
- **Long-running tasks**: something that takes many steps, better isolated

## Quick Start

### One-shot task (new session)
```bash
~/.hermes/scripts/opencode-delegate.sh "task description" /path/to/workdir
```

### Continue a previous session
```bash
# First run captures session ID to stderr
OUTPUT=$(~/.hermes/scripts/opencode-delegate.sh "task" /path/to/workdir 2>&1)
SESSION=$(echo "$OUTPUT" | grep -oP 'SESSION_ID=\K.*')
TEXT=$(echo "$OUTPUT" | grep -v 'SESSION_ID=')

# Continue it
~/.hermes/scripts/opencode-delegate.sh --continue "$SESSION" "follow-up task" /path/to/workdir
```

### With specific model
```bash
~/.hermes/scripts/opencode-delegate.sh "task" /path/to/workdir "ollama/qwen3.5:4b"
```

## How It Works
- OpenCode runs non-interactively via `opencode run --format json --pure --auto`
- JSON events are parsed, only text responses go to stdout
- Session ID goes to stderr for capture
- `--auto` auto-approves permissions (safe for delegated tasks)
- `--pure` runs without plugins (faster, fewer deps)

## Key Flags
- `--format json` — machine-readable output
- `--pure` — no external plugins
- `--auto` — auto-approve file writes/commands
- `--continue` / `--session` — resume previous context
- `--model` — override which model to use
- `--dir` — working directory

## Fallback Pattern (Provider Down)
When opencode-zen is down, delegate to local Ollama:
```bash
~/.hermes/scripts/opencode-delegate.sh "task" /path/to/workdir "ollama/qwen3.5:4b"
```

## vs. Subagents
| Feature | Hermes subagent | OpenCode delegate |
|---------|----------------|-------------------|
| Auto result delivery | Yes | No (manual capture) |
| Session continuity | No | Yes (session IDs) |
| Model flexibility | Same as parent | Any configured provider |
| Context isolation | Yes | Yes (clean start) |
| Works when provider down | No | Yes (local model) |
| Setup overhead | None | Script invocation |

## Pitfalls
- Results don't auto-deliver into conversation — must capture and relay manually
- `--auto` approves all permissions — only use for trusted tasks
- JSON output must be parsed — the wrapper handles this
- OpenCode must be in PATH or use full path (~/.opencode/bin/opencode)
- Session IDs are transient — don't persist across Ollama restarts
- **Ollama model loading is on-demand:** First request after idle has 10-30s delay while model loads into VRAM. Model unloads after 5 min idle (default `keep_alive`). `OLLAMA_KEEP_ALIVE=24h` keeps it loaded permanently but was not chosen — default behavior is acceptable. Ollama service has `Restart=on-failure` via systemd, so no health check cron needed.
- **ACP server dies immediately:** OpenCode's `opencode acp` server shuts itself down right after "setup connection" if no client connects instantly. It is designed for editor integration (VS Code connects the moment it starts), not for persistent agent-to-agent communication. The `opencode run` non-interactive mode is the working workaround. Both OpenCode and Hermes have ACP adapters, and the `acp` Python package has `connect_to_agent` and `Client` support, but the server lifecycle issue blocks ACP-based delegation today. If this gets fixed upstream, ACP would be the preferred integration path — it handles session management, tool sharing, and bidirectional communication natively.
- **Overlapping skill exists:** The bundled `opencode` skill covers general OpenCode CLI usage (one-shot, interactive, PR review). This skill (`opencode-delegate`) is specifically about the Hermes-to-OpenCode delegation wrapper script and the provider fallback pattern. If the bundled `opencode` skill gets an integration section in the future, consolidate this skill into it.
