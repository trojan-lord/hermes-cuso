# Case Study: Steam Big Picture not fullscreen on niri (Jul 2026)

## Symptom
Big Picture launched tiled at ~1000x1068 (half screen) like a normal app, instead of
fullscreen 1920x1080. Games and manually-fullscreened windows worked fine.

## Evidence chain (the reusable part)

1. **niri side**: `niri msg windows` showed the Steam window with `Tile size` ~1000x1068,
   NOT fullscreen, despite the app claiming otherwise.
2. **X side probe** (the decisive test) — xwayland-satellite's X server is `DISPLAY=:1`:
   ```bash
   /usr/bin/python3 -m venv /tmp/xlibenv && /tmp/xlibenv/bin/pip install python-xlib
   /tmp/xlibenv/bin/python3 << 'EOF'
   from Xlib import display
   d = display.Display(':1')
   root = d.screen().root
   for w in root.query_tree().children:
       # read _NET_WM_NAME, _NET_WM_STATE; check FULLSCREEN atom
   EOF
   ```
   Result: the BPM window had `_NET_WM_STATE_FULLSCREEN` set and requested 1920x1080 —
   yet niri rendered it tiled. **Fullscreen request dropped in the satellite handoff at
   window birth.** (Games don't hit this: they request fullscreen after the window exists.)
3. **Correlation**: pacman log showed xwayland-satellite 0.8.1→0.8.2 on Jul 30; Steam
   client self-updated Jul 28. The 0.8.2 diff (`compare/v0.8.1...v0.8.2`) was entirely
   window-classification code: `guess_is_popup` rewrites, WM_CLASS parsing
   (`allow WM_CLASS with multiple trailing \0 bytes`), SPLASH/DIALOG/UTILITY heuristics.
   That code decides whether a window's initial fullscreen state survives the handoff.

## Upstream context (search these before re-reporting)
- xwayland-satellite issues: #438 "Some steam games are starting inside steam client",
  #392 "Forza Horizon 5 starts embedded into steam", #18 (closed) "Steam big picture
  mode doesn't work" — same family of Steam window-misclassification bugs.
- No fix on master as of Jul 31 2026 (0.8.2 is the tip).

## Fixes offered
1. Manual `niri msg action fullscreen-window` — instant, sticks.
2. Downgrade: `pacman -U /var/cache/pacman/pkg/xwayland-satellite-0.8.1-2-x86_64.pkg.tar.zst`
   (0.8.1-2 was still in cache). Kills all X11 windows on restart — defer until user is
   done with X apps.
3. Report upstream with the X-side-vs-niri-side evidence split (maintainer is responsive).

## Other diagnostics that paid off
- Steam toggle history: `grep BigPicture ~/.local/share/Steam/logs/console-linux.txt`
  (timestamps show exactly when BPM was entered/exited).
- Steam restart detection: `grep "exec ./steamwebhelper" ~/.steam/steam/logs/webhelper-linux.txt`
  — proved the window swap was user-side, not a webhelper crash.
- BPM preferences live in Chromium leveldb under `config/htmlcache/Local Storage/leveldb/`
  (grep strings for fullscreen keys) — not in plain-text config.
