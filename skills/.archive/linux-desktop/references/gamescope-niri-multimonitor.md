# Gamescope + Niri Multi-Monitor Controller Debugging

## Environment
- **Compositor:** Niri (Wayland)
- **GPU:** NVIDIA GTX 1650 Ti + AMD Radeon integrated (hybrid laptop)
- **Display:** Laptop eDP-1 (1920x1080) + HDMI-A-1 TV (3840x2160)
- **Game:** REANIMAL (cracked, RUNE, Steam ID 2583422298, via GE-Proton11-1)
- **Controllers:** 2x DualSense (054c:0ce6) Bluetooth
- **Shell:** Noctalia via Quickshell

## Original Problem
Game displays properly on HDMI TV, but controller inputs only work when game window is on the laptop display. No controller response on TV.

## Diagnosis

### Step 1: Confirm game is an XWayland window
```bash
cat /proc/$(pgrep -f "REANIMAL.exe")/environ | tr '\0' '\n' | grep DISPLAY
# DISPLAY=:1  ← XWayland
```

### Step 2: Check compositor window list
```bash
NIRI_SOCKET=/run/user/$(id -u)/niri.wayland-*.sock niri msg windows
# Only "Steam" window appears — game is invisible to Niri
```

The game runs as XWayland (X11 through the XWayland bridge). Niri cannot see or focus the window, so input routing fails on secondary outputs.

### Step 3: Check controller devices
```bash
cat /proc/bus/input/devices | grep -B1 -A4 "DualSense"
# DualSense: 054c:0ce6, presents as controller + motion + touchpad
# SDL_GAMECONTROLLER_IGNORE_DEVICES includes 054c/0ce6
```

SDL ignoring physical controllers = Steam Virtual Gamepad in use. But Steam Input overlay doesn't route properly across XWayland + multi-monitor.

## Gamescope Setups Tested

### Attempt 1: `gamescope -e -f -- %command%`
- **Result:** Black screen with audio (controller dings heard)
- **Cause:** `-e` = exclusive fullscreen = DRM takeover attempt. Gamescope tried to take over the display but Niri already owns the seat. `[Error] Could not take control of session: Device or resource busy`

### Attempt 2: `gamescope -b -- %command%`
- **Result:** `[Error] Failed to create session`
- **Cause:** `-b` (borderless) still defaults to DRM backend, not Wayland

### Attempt 3: `gamescope -f --force-composition --synchronous-x11 -- %command%`
- **Result:** Same black screen
- **Cause:** Still using default DRM backend; `--force-composition` and `--synchronous-x11` don't affect the backend selection

### Attempt 4: `gamescope -W 3840 -H 2160 --display-index 1 --force-windows-fullscreen --force-composition -- %command%`
- **Result:** Same error: `Could not take control of session`
- **Cause:** `--display-index` triggers DRM takeover

### Attempt 5: `gamescope --backend wayland ...` (no env vars)
- **Result:** `[Error] Couldn't connect to Wayland display`
- **Cause:** `WAYLAND_DISPLAY` not set in the shell session

### Attempt 6: `WAYLAND_DISPLAY=wayland-1 gamescope -W 3840 -H 2160 --backend wayland --force-windows-fullscreen -- %command%`
- **Result:** Game launched, rendered at 60 FPS through gamescope
- **Key log lines:**
  ```
  xdg_backend: Initted Wayland backend
  wlserver: Running compositor on wayland display 'gamescope-0'
  [Gamescope WSI] Application info: pApplicationName: REANIMAL.exe
  [Gamescope WSI] Swapchain received new refresh cycle: 16.67ms  ← 60 FPS
  ```

## Working Launch Option (final)

```
gamescope -W 3840 -H 2160 --backend wayland --force-windows-fullscreen -- %command%
```

Steam sets `WAYLAND_DISPLAY` automatically, so it doesn't need to be in the launch option.

## Key Lessons

1. **`--backend wayland` is mandatory** when running gamescope under a Wayland compositor. Without it, gamescope defaults to DRM/KMS mode which tries session takeover and fails.

2. **`-e`, `-f`, `--display-index` all trigger DRM takeover**, not nested mode. Only use these when gamescope IS the compositor (Steam Deck). Never under Niri/Hyprland/Sway.

3. **Black screen + audio = gamescope running but not displaying.** The game launched (you can hear it), but the compositor can't see the gamescope surface. Fix: switch from DRM mode to `--backend wayland`.

4. **`[Error] Couldn't connect to Wayland display` = missing `WAYLAND_DISPLAY`.** When testing manually, set `WAYLAND_DISPLAY=wayland-1`. Steam handles this automatically.

5. **`[Error] Could not take control of session` = DRM conflict.** Gamescope is trying to take over a display already controlled by the compositor. Remove `-e`/`-f`/`--display-index` and use `--backend wayland`.

6. **`%comand%` vs `%command%`:** One missing 'm' silently breaks the launch option. Steam ignores malformed variables and runs the game without the wrapper.

## Editing Steam Non-Steam Game Launch Options via VDF

For non-Steam games, the shortcuts file is binary VDF:
```bash
pip3 install vdf
python3 -c "
import vdf, os
path = os.path.expanduser('~/.local/share/Steam/userdata/1451718653/config/shortcuts.vdf')
with open(path, 'rb') as f: data = vdf.binary_loads(f.read())
for e in data.get('shortcuts', {}).values():
    if 'REANIMAL' in e.get('AppName', ''):
        e['LaunchOptions'] = 'gamescope -W 3840 -H 2160 --backend wayland --force-windows-fullscreen -- %command%'
with open(path, 'wb') as f: f.write(vdf.binary_dumps(data))
"
# Restart Steam after modifying
```

For Steam library games, launch options are stored in `config.vdf` internally and are best edited through the Steam GUI.
