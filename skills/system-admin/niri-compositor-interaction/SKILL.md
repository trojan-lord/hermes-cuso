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

## X11 Apps via xwayland-satellite: Window-State Debugging

When an X11 app (Steam Big Picture, games, Wine) shows up tiled/half-screen on niri but should be fullscreen, the failure is usually in the X11→Wayland handoff, not in the app. Diagnose in three layers:

1. **What niri thinks**: `niri msg windows` — check `Tile size` vs the monitor size, and `Is floating`.
2. **What the app asked for (the key probe)**: query the X server directly. xwayland-satellite runs its own X server on `DISPLAY=:1`:
   ```bash
   /usr/bin/python3 -m venv /tmp/xlibenv   # python-xlib is rarely installed system-wide
   /tmp/xlibenv/bin/pip install --quiet python-xlib
   /tmp/xlibenv/bin/python3 << 'EOF'
   from Xlib import display
   d = display.Display(':1')
   # enumerate root children, read _NET_WM_NAME + _NET_WM_STATE
   # check for _NET_WM_STATE_FULLSCREEN in _NET_WM_STATE
   EOF
   ```
   If the X side HAS `_NET_WM_STATE_FULLSCREEN` but niri shows it tiled → the fullscreen request is being dropped in the satellite→niri handoff (app requests it at window-birth; satellite misses it). If the X side lacks it → the app isn't asking; look at the app's own settings.
3. **What changed**: correlate the regression with package upgrades in `/var/log/pacman.log` (xwayland-satellite, xorg-xwayland, niri), and check the satellite release diff (`https://api.github.com/repos/Supreeeme/xwayland-satellite/compare/v<old>...v<new>`) — window-classification commits (popup heuristics, WM_CLASS parsing) are the usual suspects.

**Fixes that work**: manual `niri msg action fullscreen-window` (works instantly, sticks); downgrade xwayland-satellite from the pacman cache (`pacman -U /var/cache/pacman/pkg/xwayland-satellite-<old>-*.pkg.tar.zst` — NOTE: restarts the satellite, which closes ALL X11 windows, so only do it when the user is done using X apps); report upstream with the X-side vs niri-side evidence (maintainer is active and responsive).

Steam-specific case study (Big Picture fullscreen regression, issue numbers, evidence): see `references/steam-fullscreen-xwayland-case.md`.

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
- **All X11 windows report the SAME PID in `niri msg windows`**: xwayland-satellite owns every X window, so `niri msg windows` attributes them all to the satellite's PID. Match on Title/App ID instead — never filter X11 windows by PID.
- **python-xlib not installed**: don't `pip install --user` into the system python (fails on Arch-managed envs) — make a throwaway venv at /tmp/xlibenv.
