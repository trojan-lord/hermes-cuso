---
name: niri-compositor-interaction
description: "Niri (Wayland) IPC from terminal - spawn, query windows."
tags: [niri, wayland, compositor, IPC, linux-desktop]
---

# Niri Compositor Interaction

## Overview

Niri is a Wayland compositor with a JSON-based IPC protocol. From a terminal session, you can interact with it via `niri msg` commands -- but only if the environment variables are correctly set.

## Environment Setup

When running from a terminal that may not inherit the Wayland session environment (e.g. an agent or SSH session), you MUST set these variables:

```bash
export NIRI_SOCKET="/run/user/$(id -u)/niri.wayland-1.$(pgrep -x niri).sock"
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export WAYLAND_DISPLAY="wayland-1"
```

### Finding the Niri Socket

The socket path is: `/run/user/<uid>/niri.wayland-1.<pid>.sock`

```bash
NIRI_PID=$(pgrep -x niri)
NIRI_SOCKET="/run/user/$(id -u)/niri.wayland-1.${NIRI_PID}.sock"
```

### Verifying Connection

```bash
niri msg version
```

## Spawning GUI Applications

To launch a GUI application that appears in the user's Niri session:

```bash
niri msg action spawn -- <command> [args...]
niri msg action spawn -- /usr/bin/steam -silent
niri msg action spawn -- xdg-open steam://rungameid/2327381328
```

## Querying Windows

```bash
niri msg windows
niri msg windows 2>/dev/null | grep -i "steam\|firefox"
niri msg focused-window
```

## Common Actions

- `spawn -- <cmd>` -- Launch a command
- `close-window` -- Close focused window
- `fullscreen-window` -- Toggle fullscreen
- `screenshot` -- Take screenshot
- `load-config-file` -- Reload configuration
- `quit` -- Exit Niri

## Pitfalls

- **NIRI_SOCKET not set**: `niri msg` errors with "NIRI_SOCKET is not set" -- always set this var.
- **Wrong socket path**: The PID in the socket filename is Niri's PID. Use `pgrep -x niri`.
- **pkill -f steam is dangerous**: Can match the agent's own processes. Use specific patterns.
- **Spawn doesn't return PID**: Use `pgrep -f <pattern>` after spawning to find the process.
