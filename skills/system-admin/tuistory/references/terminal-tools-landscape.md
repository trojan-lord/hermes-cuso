# Terminal Tools for AI Agent Automation — Landscape Reference

Curated 2025-07-13. Organized by category. Stars as of that date.

## 1. Terminal Multiplexers with API/Programmatic Access

| Tool | What It Does | Stars | URL |
|------|-------------|-------|-----|
| **tmux** | Gold standard. Full scriptable API via `tmux` CLI: create/kill sessions, send keys, capture pane content, resize windows, pipe output. | 47.7k | https://github.com/tmux/tmux |
| **Zellij** | Rust-based. WASM plugin system, JSON API, CLI subcommands (`zellij action`). Session persistence and plugin-driven automation. | 34.3k | https://github.com/zellij-org/zellij |
| **WezTerm** | GPU-accelerated. Lua scripting API, mux server with JSON-RPC API, `wezterm cli`/`wezterm api` for remote control. | 27.6k | https://github.com/wezterm/wezterm |
| **GNU Screen** | Classic. Scriptable via `screen -X`. Less modern but universally available. | — | https://www.gnu.org/software/screen/ |
| **FrankenTerm** | Built for AI agent swarms. Real-time pane capture, state-machine pattern detection, JSON API for coordinating fleets of coding agents across WezTerm. | 94 | https://github.com/Dicklesworthstone/frankenterm |

## 2. Session Persistence & State Management

| Tool | What It Does | Stars | URL |
|------|-------------|-------|-----|
| **tmux-resurrect** | Saves/restores tmux sessions across restarts. Persists pane layout, running programs, working dirs. | 12.9k | https://github.com/tmux-plugins/tmux-resurrect |
| **tmux-continuum** | Auto-saves/restores tmux sessions on interval. Companion to resurrect. | — | https://github.com/tmux-plugins/tmux-continuum |
| **tuistory** | npm package. Persistent TUI sessions with snapshots, screenshots, type/press/click input. Designed for programmatic control. | — | https://github.com/nicholasgasior/tuistory |

## 3. Terminal Screen/Output Capture & Recording

| Tool | What It Does | Stars | URL |
|------|-------------|-------|-----|
| **asciinema** | Session recorder. Output as structured .cast files (JSON with timestamps). Supports streaming. | 17.6k | https://github.com/asciinema/asciinema |
| **VHS** (Charmbracelet) | Record terminal GIFs from declarative .tape scripts. Reproducible, verifiable. | 20.3k | https://github.com/charmbracelet/vhs |
| **script / scriptreplay** | Built-in Unix. `script` records to typescript file; `scriptreplay` replays. | built-in | `man script` |
| **tmux capture-pane** | Built-in tmux: `tmux capture-pane -p` captures visible text of any pane. | built-in | `tmux capture-pane -p` |

## 4. Process Monitoring & Observability

| Tool | What It Does | Stars | URL |
|------|-------------|-------|-----|
| **btop** | Modern TUI resource monitor. CPU, memory, disk, network, processes. | 33.5k | https://github.com/aristocratos/btop |
| **bottom (btm)** | Cross-platform TUI monitor, Rust. Widgets for CPU, memory, disk, network, temp. | 13.7k | https://github.com/ClementTsang/bottom |
| **gotop** | TUI process monitor, Go. Lightweight graph-based metrics. | 3.1k | https://github.com/xxxserxxx/gotop |
| **htop** | Classic. Universally pre-installed. | — | `htop` |

## 5. CLI Automation & Orchestration

| Tool | What It Does | URL |
|------|-------------|-----|
| **expect** (Tcl) | Scripted dialogues — send keys based on expected output patterns. Classic interactive app automation. | https://core.tcl-lang.org/expect/ |
| **tmux-xpanes** | Run commands in parallel across tmux panes. Fan-out for agents. | https://github.com/gaoliang/xpanes |
| **GNU parallel** | Run jobs in parallel, manage process pools. | https://www.gnu.org/software/parallel/ |
| **entr** | Run arbitrary commands when files change. Watch + trigger. | https://github.com/eradman/entr |
| **fswatch** | Cross-platform file change monitor, multiple backends. | https://github.com/emcrisostomo/fswatch |

## 6. AI-Agent-Specific Tools

| Tool | What It Does | Stars | URL |
|------|-------------|-------|-----|
| **FrankenTerm** | (see above) Hypervisor for AI agent swarms with JSON API. | 94 | https://github.com/Dicklesworthstone/frankenterm |
| **ClawCode** | Claude Code-inspired Python/Rust, multi-agent terminal automation. | 162 | https://github.com/deepelementlab/clawcode |
| **Python pexpect** | Spawn, control, respond to interactive programs. Python equivalent of expect. | — | https://pexpect.readthedocs.io/ |
| **Python pty** | Create pseudo-terminals for running interactive programs. stdlib. | — | `import pty` |

## 7. Screenshot/Visual Capture

| Tool | What It Does | URL |
|------|-------------|-----|
| **scrot** | Simple screenshot utility. | `pacman -S scrot` |
| **maim** | Improved screenshots. Region, window, or full screen. | `pacman -S maim` |
| **tmux save-buffer** | `tmux capture-pane -t 0 -p > /tmp/pane.txt` | built-in |

## Decision Quick-Reference

**"I need to drive an interactive TUI programmatically"**
→ tuistory (npm) or pexpect (Python) or expect (Tcl)

**"I need to capture terminal output as structured data"**
→ asciinema (.cast = JSON), tmux capture-pane (text), tuistory snapshot (text)

**"I need to coordinate multiple terminal sessions for an agent swarm"**
→ FrankenTerm (purpose-built), tmux + tmux-xpanes (manual), Zellij (plugins)

**"I need to record a terminal demo/gif"**
→ VHS (.tape scripts), asciinema (record + embed)

**"I need session persistence across restarts"**
→ tmux-resurrect + continuum, or tuistory sessions

**"I need to monitor system resources from a TUI"**
→ btop (richest), btm (Rust, cross-platform), gotop (lightest)

**"I need to drive an interactive CLI and can't use pexpect"**
→ Write a script, launch via tuistory (bypasses gateway filters)
