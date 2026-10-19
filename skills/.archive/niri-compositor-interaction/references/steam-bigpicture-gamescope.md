# Steam Big Picture Fullscreen via Gamescope (native niri, no satellite)

## Symptom

Big Picture Mode (BPM) opens as a normal window on niri — tiled or floating at
requested size — instead of fullscreen. Manual `Mod+F` / `niri msg action
fullscreen-window` fixes it, but the user wants it automatic on every launch.

## Root cause

BPM is the new GamepadUI: `steamwebhelper` (Chromium) running through XWayland.
niri floats XWayland windows at whatever size they ask for, and Steam's
fullscreen request doesn't reliably translate through the X11→Wayland bridge.
The window just sits there window-shaped. Not the user's fault, not really
Steam's — it's the translation layer being unreliable.

## Why not a window rule?

niri 26.04 has NO window-rule property that forces fullscreen. Confirmed by
reading `/usr/share/doc/niri/default-config.kdl` — available rule properties
are only: `open-floating`, `geometry`, `default-column-width`,
`block-out-from`, `geometry-corner-radius`, `clip-to-geometry`, `border`,
`shadow`, `focus-ring`, `opacity`, `active-opacity`, `maximize-column`.
So the only automatic compositor-side route is wrapping the app so IT owns a
fullscreen surface: gamescope.

## The fix (validated end-to-end, live)

1. Launcher script `~/.local/bin/steam-bigpicture` (see
   `templates/steam-bigpicture.sh`): shut Steam down first, then
   `exec gamescope -f -e -- steam -gamepadui`.
2. Desktop entry `~/.local/share/applications/steam-bigpicture.desktop`:
   ```
   [Desktop Entry]
   Name=Steam Big Picture
   Comment=Launch Steam Big Picture in true fullscreen (gamescope wrapper)
   Exec=/home/<user>/.local/bin/steam-bigpicture
   Type=Application
   Icon=steam
   Categories=Game;ActionGame;
   Terminal=false
   StartupNotify=false
   ```
3. Validate the entry: `desktop-file-validate ~/.local/share/applications/steam-bigpicture.desktop`.
4. The stock `/usr/share/applications/steam.desktop` already ships a "Big Picture"
   action (`Exec=/usr/bin/steam steam://open/bigpicture`) — that's the
   windowed path; the gamescope entry is the fullscreen one. Keep both.

## Verification (what "it works" looks like)

```bash
niri msg windows | grep -B2 -A10 -i gamescope
```
Expect:
```
Title: "Steam Big Picture Mode"
App ID: "gamescope"
Is floating: no
Window size: 1920 x 1080        # == output size
Window offset in tile: 0 x 0
```
Also confirm gamescope process tree: `gamescope -f -e` → `gamescopereaper -- steam`.

Journal proof it's inside gamescope: `journalctl --user | grep "Gamescope WSI"`
shows DXVK + Gamescope WSI init from steamwebhelper.

## Pitfalls hit (all real, all resolved)

- **Steam already running → gamescope exits instantly.** `steam -gamepadui`
  signals the existing instance; gamescope's child returns immediately and
  gamescope tears down. ALWAYS `steam -shutdown` + wait loop first.
- **`niri msg action spawn /path` fails** — "unexpected argument". Needs
  `niri msg action spawn -- /path`.
- **Testing the .desktop entry via `gtk-launch` from a shell kills it.**
  When the test shell exits, the wrapper's process group gets cleaned up:
  gamescope dies, but Steam's graceful shutdown already ran — so you end up
  with "steam not running, gamescope not running" and a confusing failure.
  It's a test artifact, not a launcher bug. Launch detached with
  `niri msg action spawn -- ~/.local/bin/steam-bigpicture` instead.
- **`pgrep -x steam` misses transient state during boot** — right after
  spawning, steam's main process may not match yet. Re-poll after a few
  seconds before declaring failure.
- **Gamescope smoke test**: `timeout 8 gamescope -- sh -c 'echo ok; sleep 3'`.
  Clean init = `[gamescope] [Info] xdg_backend: Post-Initted Wayland backend`.
  Trailing `(EE) failed to read Wayland events: Broken pipe` is the expected
  XWayland shutdown noise after gamescope exits — not an error.

## Environment note (hybrid GPU)

On this box (Renoir iGPU + GTX 1650 Ti, niri session), the Wayland session
renders on the AMD iGPU (RADV); the NVIDIA dGPU sits at 0% and is compute-only.
Gamescope therefore runs games on the iGPU — fine for BPM UI and light games.
A heavy game wanting the dGPU needs a prime-offload path (not covered here).
