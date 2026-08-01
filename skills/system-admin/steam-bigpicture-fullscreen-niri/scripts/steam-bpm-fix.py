#!/usr/bin/env python3
"""
Steam Big Picture fullscreen watcher for niri.

Steam's BPM window requests fullscreen through XWayland, but niri only
honors it sometimes (race at window map time). Result: BPM opens windowed
at ~935x1068 instead of covering the screen.

This watcher polls niri's IPC every 0.7s and:
  - when a "Steam Big Picture Mode" window stays windowed for 2+ polls
    (~1.4s debounce) -> fullscreens it
  - when that window goes away (user exited BPM) -> un-fullscreens the
    desktop Steam window if we had fullscreened it (so desktop mode returns
    to normal tiling)

Only acts on transitions, so it never fights the user's own window juggling.

PITFALLS LEARNED (niri 26.04):
- `niri msg --json outputs` returns a DICT keyed by output name, and
  `current_mode` is an index (0), NOT a dict. Use `logical` width/height —
  window sizes in `niri msg --json windows` are logical pixels.
  Getting this wrong breaks the fullscreen-state check and the watcher
  toggles `fullscreen-window` every poll → visible flicker.
- `niri msg action focus-window` takes `--id <ID>`, not a positional arg.
- `fullscreen-window` TOGGLES — the size-vs-output check is what prevents
  re-toggling. Confirm the watcher logs exactly ONE fullscreen line per
  window id (except when manually interfered with).
- The BPM window appears ~8s after `steam://open/bigpicture` (Steam is slow
  to switch UI); it is a NEW window each time ("Steam Big Picture Mode").
  niri honors its fullscreen request only sometimes — that's the race.
- Singleton: keep the flock fd referenced (assign it in main) or GC closes
  the fd and the lock silently releases.
- Debounce matters: without it, the watcher toggles windows that niri was
  about to fullscreen anyway (transient size during map animation).
- Verify with a slow-motion trace: trigger BPM, dump `niri msg --json
  windows` every 1s for ~12s; expect a new steam window at [1920, 1080].
"""

import json
import subprocess
import time
import sys
import fcntl

POLL_SECONDS = 0.7


def acquire_singleton_lock():
    """Ensure only one watcher runs (fcntl locks die with the process)."""
    lock_fd = open("/tmp/steam-bpm-fix.lock", "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("steam-bpm-fix: another instance is already running, exiting",
              flush=True)
        sys.exit(0)
    return lock_fd


def niri_json(args):
    """Run `niri msg --json <args>` and return parsed JSON."""
    try:
        out = subprocess.run(
            ["niri", "msg", "--json", *args],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode != 0:
            return None
        return json.loads(out.stdout)
    except Exception:
        return None


def output_size():
    """Return (w, h) of the first output in logical pixels, or None."""
    outs = niri_json(["outputs"])
    if not outs:
        return None
    try:
        # outputs is a dict keyed by output name; window sizes are in
        # logical pixels, so use the logical geometry (handles scaling).
        o = next(iter(outs.values()))
        return (o["logical"]["width"], o["logical"]["height"])
    except Exception:
        return None


def steam_windows(windows):
    """Split steam windows into (bpm_list, desktop_list)."""
    bpm, desktop = [], []
    for w in windows or []:
        if w.get("app_id") != "steam":
            continue
        title = (w.get("title") or "").lower()
        if "big picture" in title:
            bpm.append(w)
        else:
            desktop.append(w)
    return bpm, desktop


def is_fullscreen(w, size):
    """Heuristic: fullscreen window covers the entire output."""
    if not size:
        return False
    ws = w.get("layout", {}).get("window_size")
    return ws == list(size)


def do_fullscreen(w):
    subprocess.run(["niri", "msg", "action", "focus-window", "--id", str(w["id"])],
                   capture_output=True, timeout=5)
    subprocess.run(["niri", "msg", "action", "fullscreen-window"],
                   capture_output=True, timeout=5)


def main():
    lock_fd = acquire_singleton_lock()  # keep referenced for process lifetime
    print("steam-bpm-fix: watcher started", flush=True)
    bpm_fullscreen_handled = False  # did WE put BPM into fullscreen?
    pending = None  # (window_id, consecutive_non_fullscreen_polls) debounce
    while True:
        try:
            windows = niri_json(["windows"])
            size = output_size()
            bpm, desktop = steam_windows(windows)

            if bpm:
                w = bpm[0]
                if is_fullscreen(w, size):
                    pending = None
                else:
                    # Debounce: only act if window stays windowed for 2 polls
                    # (~1.4s) — avoids toggling during the map/fullscreen
                    # animation race when niri honors the request anyway.
                    if pending and pending[0] == w["id"]:
                        pending = (w["id"], pending[1] + 1)
                    else:
                        pending = (w["id"], 1)
                    if pending[1] >= 2:
                        do_fullscreen(w)
                        pending = None
                        bpm_fullscreen_handled = True
                        print(f"steam-bpm-fix: fullscreened BPM window {w['id']}",
                              flush=True)
            elif bpm_fullscreen_handled:
                # BPM gone; if the desktop Steam window is still fullscreen
                # (shouldn't be, but be safe), un-fullscreen it.
                for w in desktop:
                    if is_fullscreen(w, size):
                        do_fullscreen(w)  # toggle back off
                        print(f"steam-bpm-fix: un-fullscreened {w['id']}",
                              flush=True)
                bpm_fullscreen_handled = False
                pending = None
        except Exception as exc:  # never die silently
            print(f"steam-bpm-fix: error: {exc}", flush=True)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
