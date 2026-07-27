# Proton/Wine Game Debugging Quick Reference

## Pre-flight: Kill Stuck Processes

Always do this first. A stuck `wineserver` from a previous failed launch blocks new launches.

```bash
pkill -9 wineserver; pkill -9 -f wine; pkill -9 -f proton; sleep 2
ps aux | grep -E "wine|proton" | grep -v grep  # verify clean
```

## Find the Compatdata ID

Non-Steam games use a numeric ID that Steam assigns internally (NOT the negative shortcut appid).

```bash
# From Steam console log (~/.steam/steam/logs/console_log.txt):
grep -i "gamename\|unravel" ~/.steam/steam/logs/console_log.txt | head -5

# Or check recently modified compatdata dirs:
ls -lt ~/.steam/steam/steamapps/compatdata/ | head -10
```

## Wine Debug Commands

### See crash exceptions (most useful)
```bash
WINEPREFIX=~/.steam/steam/steamapps/compatdata/<ID>/pfx \
WINEDEBUG=+seh,err+seh \
wine "Z:/path/to/game.exe" 2>&1 | grep -v -E "(ftrace|fixme:)" | head -40
```

### See DLL loading errors
```bash
WINEPREFIX=... WINEDEBUG=err+loaddll,err+module \
wine "Z:/path/to/game.exe" 2>&1 | grep -v "ftrace" | head -30
```

### See all errors (noisy but comprehensive)
```bash
WINEPREFIX=... WINEDEBUG=err+all \
wine "Z:/path/to/game.exe" 2>&1 | grep -v "ftrace" | head -50
```

### Run through Proton with debug
```bash
STEAM_COMPAT_DATA_PATH=~/.steam/steam/steamapps/compatdata/<ID> \
STEAM_COMPAT_INSTALL_PATH="/path/to/game/dir" \
STEAM_COMPAT_CLIENT_INSTALL_PATH=~/.steam/steam \
PROTON_LOG=1 \
cd ~/.steam/steam/compatibilitytools.d/GE-Proton11-3 && \
./proton run "/path/to/game/Game.exe" 2>&1 | tail -40
```

## Error Signature Reference

| Error | Meaning | Fix |
|-------|---------|-----|
| `code=6ba (RPC_S_SERVER_UNAVAILABLE)` | Crack DLL trying to connect to non-existent Windows service | Crack incompatibility with Wine; try different crack or legit copy |
| `Exception 0x80000004` (STATUS_BREAKPOINT) | Game crashing after initialization failure | Usually downstream of RPC/DRM failure |
| `err:module:import_dll Library X not found` | Wine prefix missing DLL | Prefix created by wrong Proton version; delete and recreate |
| `libEGL warning: driver (null)` | NVIDIA GPU enumeration during prefix init | **Harmless** — not the cause of launch failures |
| `OpenVR: Failed to initialize OpenVR` | No VR headset | **Harmless** |
| `dumped core` | Segfault | Game process crashed; check Wine debug output for cause |
| `ProtonFixes: Skipping fix execution. We are probably running a unit test.` | ProtonFixes not applying game-specific fixes | **Harmless** when running from command line — ProtonFixes detects it's not a real Steam launch. Not the cause of game failures. |
| `EXCEPTION handling: System.ComponentModel.Win32Exception: Invalid window handle.` | xalia.exe (accessibility tool) can't find a window | **Harmless** — xalia.exe is ProtonFixes' accessibility component, not the game itself. Ignore. |

## Non-Steam Game Steam Launch Flow

From `~/.steam/steam/logs/console_log.txt`, the launch command shows exactly what Steam runs:

```
steam-launch-wrapper -- reaper SteamLaunch AppId=<ID> -- \
  SteamLinuxRuntime_sniper/_v2-entry-point --verb=waitforexitandrun -- \
  GE-Proton11-3/proton waitforexitandrun /path/to/game.exe
```

Key things to check in this output:
- Which Proton version is Steam actually using? (may differ from what user expects)
- Which SteamLinuxRuntime? (`sniper` = newer, `steamrt_4` = older)
- Is the exe path correct? (spaces in path can cause argument parsing issues)

## Pitfall: Spaces in Game Path

Game directories with spaces (e.g., `/home/h2/Games/Unravel Two/`) can break Proton's argument parsing. The exe path gets split on the space and Proton receives a garbled command. Quick test: create a symlink without spaces and run from there:
```bash
ln -sfn "/path/to/Unravel Two" /path/to/UnravelTwo
# Then try launching from the space-free path
```

## Proton Version Selection

For cracked games specifically:
- **GE-Proton9-25** — older, sometimes handles CODEX cracks better
- **GE-Proton10-34** — middle ground
- **GE-Proton11-3** — latest GE, may have newer Wine that breaks older cracks
- **Proton 9.0-4** — Valve's stable, generally compatible
- **Proton Experimental** — bleeding edge, works for most legit games

For legit Steam games: Proton Experimental or GE-Proton latest usually works.
