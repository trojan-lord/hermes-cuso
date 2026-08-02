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

## Steam Big Picture Fullscreen: Gamescope Wrapper (Automatic Fix)

If BPM never goes fullscreen on niri (window sits tiled/floating at request size) and the user wants it AUTOMATIC every launch — not a manual Mod+F — wrap Steam in gamescope:

```bash
gamescope -f -e -- steam -gamepadui
```

- `-e` = "enable Steam integration" (gamescope 3.16+). `-f` = fullscreen. Gamescope owns the surface and presents it as a true fullscreen layer, so the XWayland fullscreen handoff problem disappears.
- **CRITICAL pitfall**: if Steam is already running, `steam -gamepadui` just signals the existing instance and gamescope exits immediately (its child returns right away). The launcher MUST shut Steam down first (`steam -shutdown`, poll `pgrep -x steam` up to ~30s) before starting gamescope.
- niri 26.04 has **no window-rule that forces fullscreen** (checked `/usr/share/doc/niri/default-config.kdl`: only open-floating, geometry, default-column-width, block-out-from exist). So gamescope is the only compositor-side automatic route; manual alternative stays `Mod+F` / `niri msg action fullscreen-window`.
- **Verification**: `niri msg windows` → the gamescope window shows Title `Steam Big Picture Mode`, App ID `gamescope`, tiled full (Window size == output size, offset `0 x 0`, `Is floating: no`).
- **Smoke test without touching the real session**: `timeout 8 gamescope -- sh -c 'echo ok; sleep 3'` — a clean Wayland backend init + child run means gamescope works on this session. Trailing `(EE) failed to read Wayland events: Broken pipe` is harmless (XWayland closing after gamescope exits).
- **REJECTED for BPM on this machine (2026-08)**: gamescope wraps the WHOLE Steam session as fullscreen — leaving BPM back to desktop mode leaves Steam desktop mode fullscreen too. This user wanted BPM fullscreen but desktop mode windowed, so the wrapper was deleted. Use the watcher pattern (next section) for that requirement.
- Session rendering context matters: on hybrid GPU boxes the Wayland session usually renders on the iGPU, so games within gamescope run on the iGPU, not the dGPU (dGPU stays compute-only unless prime-offload is set up).

Known-good launcher script + desktop entry: `templates/steam-bigpicture.sh` and the reference `references/steam-bigpicture-gamescope.md`.

## Forcing Fullscreen for XWayland Apps: Watcher Daemon Pattern

When the user wants ONLY the app fullscreen (and other modes windowed), gamescope is the wrong tool. Instead: a small polling watcher that forces fullscreen on transition. Verified working for Steam BPM on niri 26.04; known-good implementation on disk at `~/steam-bpm-fix/steam-bpm-fix.py`.

Pattern:
1. Poll `niri msg --json windows` every ~0.7s; find the app window (match app_id + title substring, e.g. `"Big Picture"`).
2. Fullscreen check: compare `layout.window_size` to the output's **`logical`** size from `niri msg --json outputs`. Pitfalls: outputs is a DICT keyed by output name (not a list), and `current_mode` is an INDEX (0), not a dict — use `logical.width/height`. Window sizes in `niri msg --json windows` are logical pixels.
3. Act: `niri msg action focus-window --id <ID>` (REQUIRES `--id`), then `niri msg action fullscreen-window` — which TOGGLES, so the size check is what prevents re-toggle flicker.
4. **Debounce** 2 consecutive windowed polls (~1.4s) before acting — niri sometimes honors the XWayland fullscreen request itself at map time (the race), and acting during the map animation would toggle a window that was about to fullscreen anyway.
5. **Singleton**: fcntl flock on a lockfile; second instance exits. CRITICAL: assign the returned fd in main() and keep it referenced — GC closing the fd releases the lock silently (observed bug).
6. When the app window disappears, un-fullscreen any sibling window (e.g. Steam desktop) that WE fullscreened, so leaving the app returns to normal tiling.
7. Autostart via `spawn-sh-at-startup "python3 /path/to/watcher.py &"` in niri config (systemd user services don't inherit the Wayland env).
8. Verify with a slow-motion trace: trigger the app, dump `niri msg --json windows` every 1s for ~12s, expect a new window at full output size. Steam BPM takes ~8s to appear after `steam://open/bigpicture`; first umu-run of a prefix runs pv-verify (30-60s) before a game window appears — not a hang.

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
- **`niri msg action spawn` REQUIRES `--`**: `niri msg action spawn /path/to/cmd` fails with "unexpected argument" — must be `niri msg action spawn -- /path/to/cmd`. (`niri msg action spawn-sh` takes a plain string, no `--`.)
- **Desktop entries launched from a test shell die with it**: running `gtk-launch <entry>` or the .desktop Exec from a foreground test shell means the wrapper process group gets cleaned up when the shell exits — gamescope vanishes, Steam's shutdown logic may still have run. To launch detached for real, use `niri msg action spawn -- <launcher>`.
- **All X11 windows report the SAME PID in `niri msg windows`**: xwayland-satellite owns every X window, so `niri msg windows` attributes them all to the satellite's PID. Match on Title/App ID instead — never filter X11 windows by PID.
- **python-xlib not installed**: don't `pip install --user` into the system python (fails on Arch-managed envs) — make a throwaway venv at /tmp/xlibenv.
