---
name: linux-desktop
description: "Wayland/Linux desktop troubleshooting — notification conflicts, compositor config, shell integration, service management. Load when user reports UI oddities, missing features, or desktop environment issues on Linux."
tags: [linux, wayland, niri, hyprland, desktop, troubleshooting, notifications, systemd]
---

# Linux Desktop Troubleshooting

Diagnostic and repair workflows for Linux desktop environments, especially Wayland compositors (Niri, Hyprland, Sway) with shell overlays (Noctalia, Quickshell, eww).

---

## Diagnostic Pattern: Notification Conflicts

**Trigger:** User reports notifications looking wrong, appearing twice, or not appearing at all.

**Root cause:** Two notification daemons claiming `org.freedesktop.Notifications` on D-Bus simultaneously. Common on Niri where `mako` is an optional dependency that auto-starts via systemd, but the shell (Noctalia/Quickshell) has its own built-in notification system.

### Step-by-step diagnosis

1. **Check which notification daemons are running:**
   ```bash
   ps aux | grep -iE 'notif|dunst|mako|swaync|fnott' | grep -v grep
   ```

2. **Check who owns the D-Bus notification interface:**
   ```bash
   busctl --user list | grep -i notif
   ```
   Look for `org.freedesktop.Notifications` — whoever owns it is intercepting notifications.

3. **Check if the shell has its own notification system enabled:**
   ```bash
   # Noctalia
   cat ~/.config/noctalia/settings.json | grep -A5 '"notifications"'
   # Quickshell-based shells
   grep -r "notification" ~/.config/quickshell/ --include="*.qml" -l
   ```

4. **Check systemd user services for auto-started daemons:**
   ```bash
   systemctl --user list-units --type=service | grep -iE 'notif|mako|dunst'
   systemctl --user cat mako.service  # check if preset-enabled
   ```

5. **Check when the conflicting daemon was installed:**
   ```bash
   grep -A2 "installed <daemon>" /var/log/pacman.log
   ```
   Often installed as an optional dependency in a bulk package install.

### Fix

Stop and disable the conflicting daemon. The shell's built-in system should reclaim the D-Bus bus on next login (or restart the shell process).

```bash
systemctl --user stop mako.service
systemctl --user disable mako.service
```

### Verification

After disabling the conflicting daemon, confirm the shell reclaimed the bus:

```bash
busctl --user list | grep org.freedesktop.Notifications
```

The owning process should now be `qs` (Noctalia/Quickshell), not `mako`. If the shell auto-reclaimed, no restart needed. Test with:

```bash
notify-send "test" "Notifications working"
```

If the shell did NOT reclaim the bus, restart it or log out/in.

### Pitfall

- `mako` is listed as `Optional For: niri` in pacman. It gets pulled in during bulk niri/sway installs (e.g. `pacman -S niri` or the `cachyos-niri-noctalia` group) and starts automatically via a preset-enabled systemd user service. Users often don't realize it's running.
- Killing the daemon without disabling it (`systemctl --user disable`) will cause it to restart on next login.
- Some shells (Noctalia) only register as the notification server on startup — if mako grabs the bus first, the shell's notification UI never activates. However, Noctalia's Quickshell process often auto-reclaims the bus when mako releases it, so a full restart is not always needed. Check `busctl` before assuming a restart is required.
- The package `cachyos-niri-noctalia` provides Niri config + Noctalia settings. It does NOT pull in mako — mako comes from the separate `niri` optional deps.

**See also:** `references/noctalia-notification-architecture.md` for full details on the notification flow, config paths, `notify-send` usage, and failure modes.

---

## Diagnostic Pattern: notify-send Timeout (Shell Not Running)

**Trigger:** `notify-send` hangs and eventually times out with no error message. No notifications appear. This is **distinct from the daemon-conflict pattern above** — here, nobody owns the bus at all.

### Root cause

The Quickshell/Noctalia process is not running, so no process claims `org.freedesktop.Notifications` on D-Bus. `notify-send` waits for a reply that never comes.

### Step-by-step diagnosis

1. **Check if the shell process exists:**
   ```bash
   pgrep -a "quickshell|qs" || echo "NO SHELL PROCESS RUNNING"
   ```

2. **Verify no one owns the notification bus:**
   ```bash
   busctl --user list | grep org.freedesktop.Notifications
   # No output = no owner = shell not running
   ```

3. **Check how the shell is supposed to start:**
   ```bash
   # Niri
   grep -i "qs\|quickshell\|noctalia" ~/.config/niri/cfg/autostart.kdl
   # Hyprland
   grep -i "qs\|quickshell\|noctalia" ~/.config/hypr/hyprland.conf
   # Systemd (deprecated in newer versions)
   systemctl --user list-unit-files | grep -iE 'noctalia|quickshell'
   ```

### Fix

Start the shell:
```bash
qs -c noctalia-shell &
```
Once the Quickshell process starts and claims `org.freedesktop.Notifications`, `notify-send` will work immediately.

### Pitfall

- This is often confused with the daemon-conflict scenario. If `busctl` shows `qs` already owns the bus but notifications still fail, look at the conflict pattern instead.
- The `systemd` slice `app-dbus\x3a1.1-org.freedesktop.Notifications.slice` may appear in `systemctl` output as inactive — this is normal when no notification daemon is active, and does NOT mean the bus is blocked.
- On Niri, `qs -c noctalia-shell` is launched via `spawn-sh-at-startup` in `~/.config/niri/cfg/autostart.kdl`. If niri is running but the shell didn't start, check for errors in `journalctl --user` or run `qs -c noctalia-shell` manually to see output.
- **There is no `noctalia-cli` or custom notification CLI.** `notify-send` is the only way. Do not look for a Noctalia-specific tool.

---

## Diagnostic Pattern: Service and Process Conflicts

**General pattern for any "something looks wrong" desktop issue:**

1. What processes are running that could be responsible?
2. What D-Bus services are claimed?
3. What systemd user services are enabled/active?
4. What was recently installed or changed? (`/var/log/pacman.log`, `journalctl --user`)
5. What does the shell/compositor config expect vs what is actually running?

---

## Diagnostic Pattern: Hermes Gateway — Connected but Silent

**Trigger:** Hermes Discord (or other platform) bot appears online, sends startup notifications, but never responds to user messages.

### Symptoms
- `hermes gateway status` shows active/running
- Gateway logs show "Connected as <bot>" and startup notification sent
- Log file timestamp stops updating (no new entries for 10+ minutes)
- Earlier logs may show: "Discord messages are being denied because no allowlist is configured"
- `/proc/<pid>/environ` may be missing env vars that are present in `~/.hermes/.env`

### Diagnosis

1. **Check if the log file is still updating:**
   ```bash
   ls -la ~/.hermes/logs/gateway.log; sleep 5; ls -la ~/.hermes/logs/gateway.log
   ```
   If the timestamp didn't change, the event loop is stuck.

2. **Check for allowlist warnings in gateway logs:**
   ```bash
   grep -i "denied\|allowlist\|allow" ~/.hermes/logs/gateway.log | tail -5
   ```

3. **Check if env vars reached the process:**
   ```bash
   cat /proc/$(pgrep -f "gateway run")/environ | tr '\0' '\n' | grep DISCORD
   ```
   If DISCORD vars are missing but the token works (bot connected), dotenv loaded the token but the allowlist vars aren't reaching the adapter.

### Fix

Restart the gateway cleanly — this forces a full env reload:
```bash
hermes gateway restart
```

Do NOT just `systemctl --user restart hermes-gateway` — the `hermes gateway restart` command handles graceful shutdown and reconnection.

### Verification

After restart, confirm the allowlist warning is gone and the log is updating:
```bash
tail -5 ~/.hermes/logs/gateway.log
```
Send a test message on Discord and watch for new log entries.

### Pitfall
- The systemd service file (`~/.config/systemd/user/hermes-gateway.service`) does NOT source `~/.hermes/.env` directly — Hermes loads dotenv programmatically at startup. If the gateway was started by systemd but dotenv loading failed or was partial, the process runs with incomplete env vars. The bot token might load (from config.yaml or partial dotenv) while allowlist vars don't.
- A gateway that shows "Connected" in logs but has a stale log timestamp is effectively dead — the Discord websocket may be up but the message processing loop is not running.
- The restart loop (`RestartForceExitStatus=75` in the service file) can cause rapid restart cycling if the gateway exits with status 75 (TEMPFAIL). Check `journalctl --user -u hermes-gateway` for crash loops.

---

Related: `references/system-state-tools.md` for quick reference on querying desktop state (niri msg, brightnessctl, wpctl, playerctl, gammastep, ydotool).

## Diagnostic Pattern: Game Controllers Not Working on Secondary Display (Wayland/XWayland)

**Trigger:** Steam game runs fine on laptop display, but Bluetooth/controllers stop responding when game is moved to external monitor (HDMI/DP). User has controllers connected and confirmed working.

**Environment:** Wayland compositor (Niri, Hyprland, Sway) with XWayland bridge. Game runs via Proton/Wine as an X11 window.

### Root Cause

On Wayland compositors with XWayland, X11 game windows may not appear in the compositor's window list. The compositor cannot route input events to windows it cannot see. When the game is on the laptop display (primary), input may work through the XWayland bridge's fallback behavior. On secondary outputs, the bridge fails to forward input.

Additionally, SDL's controller ignore list may include the physical device IDs while relying on Steam's virtual gamepad overlay — which has its own output-dependent behavior.

### Step-by-step Diagnosis

1. **Check which compositor is running:**
   ```bash
   ps aux | grep -iE 'niri|hyprland|sway|gamescope' | grep -v grep
   ```

2. **Check connected outputs:**
   ```bash
   # For Niri (must run inside niri session)
   NIRI_SOCKET=/run/user/$(id -u)/niri.wayland-*.sock niri msg outputs
   # For Hyprland
   hyprctl monitors
   ```

3. **Check if game window appears in compositor's window list:**
   ```bash
   # Niri
   NIRI_SOCKET=/run/user/$(id -u)/niri.wayland-*.sock niri msg windows
   # Hyprland
   hyprctl clients
   ```
   If the game is missing from this list, the compositor cannot route input to it.

4. **Check X11 window properties (XWayland):**
   ```bash
   DISPLAY=:1 xdotool search --name "GameName" getwindowgeometry
   ```
   Verify the window position matches the HDMI output (e.g., `Position: 1920,0` for secondary at right of 1920px primary).

5. **Check SDL controller environment:**
   ```bash
   cat /proc/$(pgrep -f "GameProcessName")/environ | tr '\0' '\n' | grep -i SDL
   ```
   Look for `SDL_GAMECONTROLLER_IGNORE_DEVICES` — physical controllers (DualSense: `054c/0ce6`) may be in the ignore list.

### Fix: Gamescope Wrapper

Gamescope creates a proper Wayland surface that the compositor can track, solving the input routing issue.

**CRITICAL: Choose the right mode for your environment.**

**Mode A — Nested under an existing compositor (desktop Linux with Niri/Hyprland/Sway):**
Gamescope runs as a regular Wayland window inside the running compositor. It MUST use `--backend wayland` to avoid trying DRM/KMS takeover.

```bash
# Generic nested mode (works under any Wayland compositor):
gamescope -W 3840 -H 2160 --backend wayland --force-windows-fullscreen -- %command%

# The --backend wayland flag is MANDATORY when running under a compositor.
# Without it, gamescope defaults to DRM mode which tries to take over the
# display seat — and fails because the compositor already owns it.
```

**Mode B — DRM takeover (Steam Deck, standalone, no existing compositor):**
Only use this mode when gamescope IS the compositor. It takes direct DRM control.

```bash
# Direct DRM mode (standalone):
gamescope -e -- %command%
```

**Do NOT use `-e` or `--display-index` under a running compositor** — these trigger DRM takeover and fail with:
```
[Error] wlserver: Could not take control of session: Device or resource busy
```

**How to detect which mode to use:**
- If `ps aux | grep -iE 'niri|sway|hyprland'` shows a compositor → Mode A (nested)
- If on Steam Deck or standalone → Mode B (DRM, -e)

### Fix: Gamescope on NVIDIA Multi-Monitor (Black Screen Debugging)

Gamescope may show black screen with audio on NVIDIA + multi-output Wayland setups. This means gamescope is running but not rendering to the display. Audio/controller dong sounds confirm the game launched — the issue is display output.

**Debugging sequence** (kill game + gamescope first, restart Steam between each attempt):
1. `gamescope -b -- %command%` — borderless windowed, least aggressive
2. `gamescope -f -- %command%` — fullscreen
3. `gamescope -f --force-composition --synchronous-x11 -- %command%` — force composition + sync X11 for NVIDIA
4. `gamescope -f --force-composition --synchronous-x11 --prefer-vk-device <NVIDIA-PCI-ID> -- %command%` — force NVIDIA GPU on hybrid setups

**NVIDIA-specific flags:**
- `--force-composition` — disables direct scanout (fixes black screen on some NVIDIA configs)
- `--synchronous-x11` — forces X11 sync (fixes frame delivery issues on XWayland)
- `--prefer-vk-device <PCI-ID>` — forces specific GPU for compositing (use `lspci | grep VGA` to find IDs)
- `__NV_PRIME_RENDER_OFFLOAD=1` prefix — forces rendering on NVIDIA GPU on hybrid AMD+NVIDIA laptops
- `--display-index N` — **DO NOT USE under a compositor** — triggers DRM takeover and fails

**Common failure modes:**
- Black screen + audio = gamescope running but not displaying. Likely missing `--backend wayland` (if under a compositor) or `--force-composition` (NVIDIA)
- `[Error] Could not take control of session` / `[Error] Failed to create session` = gamescope trying DRM mode under a running compositor → remove `-e`/`--display-index`, add `--backend wayland`
- `[Error] Couldn't connect to Wayland display` = `--backend wayland` set but `WAYLAND_DISPLAY` not defined. Steam sets this automatically via the launcher, but manual tests need `WAYLAND_DISPLAY=wayland-1` prefix
- Black screen + no audio = game not launching at all (check launch option syntax, `%command%` typo)
- Gamescope not found = not installed (`pacman -S gamescope`)

### Fix: Force SDL Controller Passthrough

If the issue is SDL ignoring physical devices via the Steam ignore list:

```bash
# Add as launch option to bypass ignore list:
SDL_GAMECONTROLLER_IGNORE_DEVICES=0x0 %command%
```

### Editing Steam Launch Options Programmatically

Steam stores non-Steam game launch options in `shortcuts.vdf` (binary VDF format) under `~/.local/share/Steam/userdata/<userid>/config/shortcuts.vdf`. These can be edited with the `vdf` Python library:

```python
import vdf, os

path = os.path.expanduser("~/.local/share/Steam/userdata/<userid>/config/shortcuts.vdf")
with open(path, 'rb') as f:
    data = vdf.binary_loads(f.read())

for key, entry in data.get('shortcuts', {}).items():
    if 'GameName' in entry.get('AppName', ''):
        entry['LaunchOptions'] = 'gamescope -e -f -- %command%'

with open(path, 'wb') as f:
    f.write(vdf.binary_dumps(data))
```

Install: `pip3 install vdf`. Restart Steam after editing.

**Common typos that break launch options:** `%comand%` (missing m) — Steam silently ignores malformed `%command%` variables and runs the game without the wrapper.

### Pitfall

- On Niri specifically, `niri msg windows` only shows Wayland-native windows. XWayland windows (Proton/Wine games) may not appear even though they are rendered. The `xwayland-satellite` process bridges X11 to Wayland but doesn't always register windows in the compositor's tracking.
- `focus-follows-mouse` in Niri config means input follows mouse cursor, not the game window. If the mouse is on a different output, the game loses focus.
- DualSense controllers via Bluetooth present as three separate input devices (controller, motion sensors, touchpad). SDL picks the main controller node (`js0`), but the compositor's input routing applies to all of them.
- **Do not tell the user to use the GUI when a programmatic solution exists.** Binary formats (VDF, protobuf, etc.) almost always have Python libraries. Try the library first. If it fails, then suggest the GUI — not before.
- Cracked/pirated games (RUNE, CODEX, etc.) bypass Steam's Steam Input layer entirely. Controller input goes through raw SDL/evdev instead. This means Steam Input configuration (controller layout, per-game bindings) has no effect. If controllers work on one display but not another, the issue is XWayland input routing, not Steam Input.
- `%comand%` (missing m) is a common typo that silently breaks gamescope launch options. Steam ignores malformed `%command%` variables and runs the game without the wrapper.

**See also:** `references/gamescope-niri-multimonitor.md` for the full debugging session, error messages, and tested attempts that produced this diagnostic pattern.

**See also:** `references/proton-game-debugging.md` for Wine debug commands, error signature reference table, and Proton version selection guide.

---

## Pattern: Syncing Local Config/Files to GitHub

**Trigger:** User says "push to GitHub" or "sync to GitHub" for local config, projects, or backups.

### Pitfall: Do Not Create New Repos When Syncing Existing Ones

When the user says "push the things to GitHub," they mean **update existing repos that already have remotes configured**. Do NOT create new repos unless explicitly asked. Always check first:

```bash
cd /path/to/project
git remote -v  # Has origin? → push to existing
# No remote and no git? → STOP. Ask user before creating.
```

User correction: "Only push what's already set up" / "take off the new ones u added"

### Workflow for Syncing Existing Repos

1. Check `git remote -v` for existing remotes
2. If remote exists: `git add -A && git commit -m "..." && git push`
3. If no remote: **ask user** — do not auto-create with `gh repo create`

### Syncing .hermes Config Backup to GitHub

```bash
# Clone the backup repo
gh repo clone ryan0ezekiel/.hermes-Cuso /tmp/.hermes-Cuso

# Copy current local files
cp ~/.hermes/SOUL.md /tmp/.hermes-Cuso/
cp ~/.hermes/config.yaml /tmp/.hermes-Cuso/
cp ~/.hermes/memories/MEMORY.md /tmp/.hermes-Cuso/memories/
cp ~/.hermes/memories/USER.md /tmp/.hermes-Cuso/memories/
rsync -av --delete ~/.hermes/skills/ /tmp/.hermes-Cuso/skills/

# Check for changes and push
cd /tmp/.hermes-Cuso
git add -A
CHANGES=$(git diff --cached --stat)
if [ -n "$CHANGES" ]; then
    git commit -m "Sync .hermes config ($(date -u +'%Y-%m-%d'))"
    git push
    echo "Synced: $CHANGES"
else
    echo "No changes."
fi
rm -rf /tmp/.hermes-Cuso
```

**Set up automatic sync** with a cron job (every 6h, silent unless changes):
```bash
# Script at ~/.hermes/scripts/sync-hermes-backup.sh
# Cron job: every 6h, deliver=local (silent)
```

### Pitfall: Editing Steam shortcuts.vdf

Binary VDF format can be edited programmatically with Python `vdf` library — **do not tell the user to use the GUI first**. Binary formats almost always have libraries. Try the library first:

```python
import vdf, os
path = os.path.expanduser("~/.local/share/Steam/userdata/<userid>/config/shortcuts.vdf")
with open(path, 'rb') as f:
    data = vdf.binary_loads(f.read())
# ... edit entries ...
with open(path, 'wb') as f:
    f.write(vdf.binary_dumps(data))
```

Install: `pip3 install vdf`. Restart Steam after editing.

---

## Diagnostic Pattern: Non-Steam Game Won't Launch Through Proton

**Trigger:** User adds a Windows game (non-Steam) to Steam, selects Proton compatibility tool, hits Play, and the game silently fails — play button bounces back with no error message, no crash dialog.

### Workflow: Verify Before Diagnosing

**Ask what the user already tried BEFORE assuming the fix.** The most common mistake is walking them through the basic Proton setup when they already did it. If they say "I already tried forcing GE-Proton," skip straight to deeper diagnostics. Do not re-explain the basic fix.

### Root Cause: No Proton Compatibility Tool Mapped

Non-Steam games added to Steam do NOT automatically get a Proton compatibility tool assigned. The shortcut entry in `shortcuts.vdf` has no `compat_tool` field, and Steam's `CompatToolMapping` in `config.vdf` only lists games where the user explicitly set a tool. Without a mapping, Steam tries to run the Windows `.exe` natively on Linux — which silently fails.

### Step-by-step Diagnosis

**0. Check Steam console log FIRST.** Before any manual Wine debugging, look at what Steam actually ran:
```bash
grep -i "gamename\|unravel\|<game>" ~/.steam/steam/logs/console_log.txt | tail -20
```
This shows the exact Proton version, SteamLinuxRuntime, exe path, and whether the process was created and removed (launch failed). This single step often reveals the problem (wrong Proton, missing path, etc.) without any further investigation.

**0b. Check ProtonDB for the game's Steam App ID.** `https://www.protondb.com/app/<appid>` — if the game is rated Gold/Platinum and others report it works with Proton, the issue is likely your specific setup (crack, prefix, path) not the game itself. If it's rated Silver/Bronchite, there may be a known workaround.

1. **Find the non-Steam game's shortcut entry:**
   ```python
   import vdf, os, glob
   for f in glob.glob(os.path.expanduser('~/.steam/steam/userdata/*/config/shortcuts.vdf')):
       try:
           data = vdf.binary_loads(open(f,'rb').read())
           for k,v in data.get('shortcuts',{}).items():
               if 'gamename' in str(v).lower():  # or check by appid
                   print(f"AppID: {v.get('appid')}, Exe: {v.get('Exe')}")
                   print(f"LaunchOptions: {v.get('LaunchOptions', '(empty)')}")
                   # If no 'compat_tool' or 'ShortcutOverride' key → Proton not set
       except: pass
   ```

2. **Check if a Proton tool is mapped in Steam config:**
   ```bash
   grep -A5 "<appid>" ~/.steam/steam/config/config.vdf
   ```
   The `CompatToolMapping` section maps numeric appids to Proton versions. Non-Steam games use negative appids (e.g., `-1212480517`). If the negative appid is NOT in this list, no Proton tool is set.

3. **Check if a compatdata directory exists:**
   ```bash
   ls ~/.steam/steam/steamapps/compatdata/<appid>/
   ```
   Non-Steam games with a working Proton setup will have a `pfx/` directory (the Wine prefix). If it doesn't exist, the game has never successfully launched through Proton.

4. **Check for Wine/EGL errors (usually a red herring):**
   ```
   libEGL warning: pci id for fd 37: 10de:1f95, driver (null)
   libEGL warning: egl: failed to create dri2 screen
   ```
   These warnings appear during Wine prefix initialization on systems with NVIDIA GPUs (especially hybrid AMD+NVIDIA). They are **not** the cause of game launch failures — they occur during the prefix setup phase before the game even starts. Do not spend time debugging these unless the prefix creates successfully but the game still fails.

### Fix

In Steam GUI:
1. Right-click the game → **Properties** → **Compatibility**
2. Check **"Force the use of a specific Steam Play compatibility tool"**
3. Select a Proton version (GE-Proton recommended for non-Steam games)

Or programmatically via `shortcuts.vdf`:
```python
import vdf, os
path = os.path.expanduser("~/.steam/steam/userdata/<userid>/config/shortcuts.vdf")
with open(path, 'rb') as f:
    data = vdf.binary_loads(f.read())
for k, entry in data.get('shortcuts', {}).items():
    if entry.get('appid') == <negative_appid>:
        entry['compat_tool'] = 'GE-Proton11-3'
with open(path, 'wb') as f:
    f.write(vdf.binary_dumps(data))
```

### Pitfall: Cracked/Repacked Games (CODEX, FitGirl, etc.)

FitGirl repacks, CODEX cracks, RUNE, etc. use DLL hooking (e.g., `OrangeEmu64.dll`, `codex.cfg`) that frequently fails under Proton/Wine. If the Proton tool IS set but the game still fails:

**Identify the crack type:** Look for telltale files in the game directory:
- `OrangeEmu64.dll` / `OrangeEmu.dll` — CODEX crack
- `codex.cfg` — CODEX configuration
- `_Redist/` folder with `fitgirl.md5`, `QuickSFV.EXE` — FitGirl repack
- `steam_api64.dll` (cracked) — various

**Wine debug workflow to confirm crack failure:**

```bash
# Kill leftover processes first (stuck wineserver blocks new launches)
pkill -9 wineserver; pkill -9 -f wine; sleep 1

# Run with crash/exception debugging through the Proton prefix
WINEPREFIX=~/.steam/steam/steamapps/compatdata/<compatdata_id>/pfx \
WINEDEBUG=+seh,err+seh \
wine "Z:/path/to/game/Game.exe" 2>&1 | grep -E "(exception|Exception|RPC|0x8000|err:)" | head -20
```

**Key error signatures for crack failure:**
- `code=6ba (RPC_S_SERVER_UNAVAILABLE)` — crack trying to connect to non-existent Windows RPC service. This is the #1 cause of silent launch failure with CODEX cracks.
- `Exception 0x80000004` (STATUS_BREAKPOINT) — game crashing immediately after crack initialization fails
- `dumped core` / segfault — the process exits with a signal, not an error code
- `err:module:import_dll Library libvkd3d-utils-1.dll not found` — Wine prefix missing required DLLs (happens when prefix was created by a different Proton version than the one being used)

**What does NOT cause game launch failures (common red herrings):**
- `libEGL warning: pci id for fd N: 10de:XXXX, driver (null)` — NVIDIA GPU enumeration warning during Wine prefix init. Harmless.
- `libEGL warning: egl: failed to create dri2 screen` — Same category, not the cause.
- `OpenVR: Failed to initialize OpenVR` — Normal when no VR headset is connected.
- `OpenXR: Unable to get required Vulkan instance extensions` — Normal on non-VR setups.

**Fix options (in order of reliability):**
1. Get the legit copy — cracked games + Proton is inherently fragile
2. Try a different crack release — newer CODEX patches sometimes handle Wine better
3. Try older Proton (GE-Proton9-25 or Proton 9.0-4) — some cracks work on older Wine versions
4. Use `WINEDLLOVERRIDES` to force native versions of crack DLLs: `WINEDLLOVERRIDES="OrangeEmu64=b;OrangeEmu=b" %command%`
5. Run in a Windows VM with GPU passthrough — nuclear option but guaranteed

### Pitfall: Stuck Wine/Proton Processes

When debugging game launches, always check for leftover Wine/Proton processes:
```bash
ps aux | grep -E "wine|proton|wineserver" | grep -v grep
```
A stuck `wineserver` process (often consuming high CPU) from a previous failed launch can block new launches. Kill them before retrying:
```bash
pkill -f wineserver; pkill -f wine; pkill -f proton
```

---

## Common Packages and Their Roles

| Package | Role | Conflict Risk |
|---------|------|---------------|
| `mako` | Notification daemon | Conflicts with shell built-in notification systems |
| `dunst` | Notification daemon | Same as mako |
| `swaybg` | Wallpaper setter | May conflict with shell wallpaper modules |
| `waybar` | Status bar | May conflict with shell bar widgets |
| `fuzzel` | App launcher | May conflict with shell launcher widgets |
| `swaylock` | Screen locker | May conflict with shell lock screen |

On Noctalia/Quickshell setups, the shell handles most of these functions natively. External tools should be disabled unless specifically needed.
