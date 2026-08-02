---
name: steam-bigpicture-fullscreen-niri
description: Steam BPM windowed on niri? Watcher forces fullscreen.
---

# Steam Big Picture Fullscreen on niri/Wayland

## Trigger
- Steam Big Picture Mode (new GamepadUI) opens as a window, not fullscreen, on niri.
- User wants BPM fullscreen AUTOMATICALLY, but desktop mode windowed (in-app toggle).
- Any "app won't go fullscreen through XWayland on niri" report.

## Root Cause (verified empirically on niri 26.04)
- Steam BPM is steamwebhelper = Chromium via XWayland. When BPM opens, Steam creates a
  NEW X11 window ("Steam Big Picture Mode") and requests fullscreen.
- niri honors that request only SOMETIMES — race at window map time. Same command
  (`steam steam://open/bigpicture`) opens fullscreen once, windowed (~935x1068) the next.
- niri has NO fullscreen window-rule (window-rule supports open-floating, geometry,
  block-out-from, etc. — NOT fullscreen). So no static config fix.
- niri IPC JSON does NOT expose a fullscreen flag per window; detect it by comparing
  `layout.window_size` to the output's `logical` size.

## FIX (primary): watcher daemon — `~/steam-bpm-fix/steam-bpm-fix.py`
See skill file `scripts/steam-bpm-fix.py` (or reconstruct): poll `niri msg --json windows`
every ~0.7s; when a steam window titled "Steam Big Picture Mode" is not fullscreen,
`focus-window --id N` + `fullscreen-window`; when it disappears (user exited BPM),
un-fullscreen the desktop Steam window if we set it. Acts only on transitions.

Lives in `~/steam-bpm-fix/` (user rule: keep task artifacts in ONE folder, never
scattered in home/.local). README.md in the folder explains it.

Autostart: add to `~/.config/niri/cfg/autostart.kdl`:
```
spawn-sh-at-startup "python3 /home/h2/steam-bpm-fix/steam-bpm-fix.py &" // Steam BPM fullscreen fix
```

## FIX (alternative, REJECTED on this machine — do not rebuild): gamescope wrapper
`gamescope -f -e -- steam -gamepadui` — makes EVERYTHING fullscreen including Steam
desktop mode. This confused the user ("desktop mode became fullscreen" = unwanted)
and the launcher + desktop entry were DELETED 2026-08-02. Revisit only if the user
ever explicitly wants both modes fullscreen.

## Watcher pitfalls (learned the hard way, niri 26.04)
- **`niri msg --json outputs`**: returns a DICT keyed by output name; `current_mode` is
  an index (0), NOT a dict. Use `logical` width/height — window sizes are logical px.
  Getting this wrong breaks the fullscreen-state check and the watcher toggles
  `fullscreen-window` every poll → visible flicker.
- **`niri msg action focus-window` takes `--id <ID>`**, not a positional arg.
- **`fullscreen-window` TOGGLES** — the size-vs-output check is what prevents
  re-toggling. Confirm the watcher logs exactly ONE fullscreen line per window id.
- **Verify with live loop**: `steam steam://open/bigpicture`; check
  `niri msg --json windows`; expect window_size == [1920, 1080]. Close BPM (or
  `niri msg action close-window`); desktop Steam window must return to normal tiling.
- **steamwebhelper crash pattern**: if BPM is janky beyond fullscreen, check
  `~/.steam/steam/config/htmlcache/Default/Preferences` for `"exit_type":"Crashed"`
  repeats and Millennium mods in `~/.steam/steam/millennium`.

## Related
- Exiting BPM normally (power menu) closes gamescope too. Regular Steam launcher untouched for desktop mode.
- User machine: niri 26.04, gamescope 3.16.24 (cachyos), Steam with Millennium skin mod present.
