---
name: proton-game-troubleshooting
description: "Proton game debugging: cracked vs legit triage."
---

# Proton Game Troubleshooting

## Triage First, Debug Later

1. Identify the game type: Legit Steam, non-Steam added to Steam, or cracked/repacked?
2. Check ProtonDB: Visit protondb.com for the game's Steam App ID.
3. Check the crack type: Identify which crack group and whether it uses Windows-specific services.
4. Only then start debugging.

## Identifying Game Type

**Legit Steam Game**: Installed via Steam normally. Real Steam App ID. Uses Proton via Steam compatibility tool.

**Non-Steam Game Added to Steam**: Added via "Add a Non-Steam Game". Gets negative App ID internally. Actual compatdata ID differs - find in shortcuts.vdf. Compatdata path: ~/.steam/steam/steamapps/compatdata/internal_id/

**Cracked/Repacked Game**: Contains crack DLLs (OrangeEmu64.dll for CODEX). Check with: strings exe | grep -i ".dll"

## Cracked Game Compatibility

### CODEX Crack (OrangeEmu64.dll)
- Will NOT work under Proton/Wine
- Calls Windows RPC services (RpcServerRegisterIf, etc.)
- Error: RPC_S_SERVER_UNAVAILABLE (0x6ba) + STATUS_BREAKPOINT exception
- Crack is load-bearing: game binary expects it for initialization
- Removing crack DLLs does NOT help
- All Proton versions fail identically

### Key Finding
Cracked games using Windows-specific DRM/launcher bypass DLLs are fundamentally incompatible with Wine. Architecture mismatch, not configuration issue.

### Can We Bypass the Crack?
Sometimes if purely for online features. But launcher-replacement cracks (CODEX for EA/Origin/Ubisoft) ARE the bypass. Without it, no way to start.

## Proton Debugging Workflow (Legit Games)

### Step 1: Check Steam Logs
cat ~/.steam/steam/logs/console_log.txt | grep -i -A5 -B2 "game_name_or_id"

### Step 2: Enable Proton Logging
Set PROTON_LOG=1 in Steam launch options. Log at ~/steam-appid.log.

### Step 3: Check ProtonDB
Visit protondb.com/app/steam_app_id for Proton version, launch options, DLL overrides.

### Step 4: Try Different Proton Versions
1. Proton Experimental (most compatible)
2. GE-Proton latest (community fixes)
3. Proton 9.x/10.x stable
4. Proton Hotfix

### Step 5: Common Fixes
- EA Launcher: WINEDLLOVERRIDES="EADesktop.exe=b;EALaunchHelper.exe=b" or protontricks appid ealink
- Missing DLLs: protontricks appid vcrun2019 d3dx11_43
- Dual GPU: __NV_PRIME_RENDER_OFFLOAD=1 %command%
- Path with spaces: Symlink to path without spaces as diagnostic
- Prefix corruption: Delete ~/.steam/steam/steamapps/compatdata/appid/ and relaunch

### Step 6: Wine Direct Debugging
WINEPREFIX=~/.steam/steam/steamapps/compatdata/appid/pfx WINEDEBUG=err+seh,err+loaddll wine "Z:/path/to/game.exe"

## Non-Steam Game Setup

1. Add via "Add a Non-Steam Game" in Steam
2. Set compatibility tool BEFORE first launch
3. Compatdata created on first launch

**Pitfall**: If Proton tool not set before first launch, compatdata may be corrupted. Delete and relaunch.

### Non-Steam Game AppID & Proton Switching

See `references/non-steam-game-proton-switching.md` for the complete workflow:
- Extracting a non-Steam game's internal appid from shortcuts.vdf
- Signed-to-unsigned appid conversion
- Changing Proton versions programmatically via config.vdf's CompatToolMapping
- Launching via steam://rungameid/ and -applaunch
- Monitoring launch in Steam logs
- Process detection limitations when testing from a headless terminal

## Cleanup Protocol

ALWAYS clean up after troubleshooting. Before debugging, note what exists. After, restore it.

```bash
rm -rf ~/.steam/steam/steamapps/compatdata/test_ids/
rm -rf ~/.wine-test_prefixes/
rm -f ~/steam-*.log
rm -f symlinks_created
rm -rf "game_dir/_backup"
pkill -9 wineserver 2>/dev/null; pkill -9 wine 2>/dev/null
```

**User preference**: Clean up proactively. Do not leave test prefixes, compatdata dirs, or symlinks behind.

## When to Stop

Stop and recommend alternatives when:
1. ProtonDB says legit version works - suggest buying it
2. Crack uses Windows-specific services Wine cannot provide
3. 3+ Proton versions tried with no success
4. Game requires unsupported kernel-level anti-cheat

Do research BEFORE diving deep into debugging. Be direct with the user when something will not work.

## Known Incompatible Crack Patterns

- CODEX OrangeEmu64.dll: NO - Windows RPC dependency, RPC_S_SERVER_UNAVAILABLE crash
- CODEX OrangeEmu.dll (32-bit): NO - Same RPC dependency
- Empress: Varies - Some newer cracks avoid RPC, check per-game
- FitGirl: N/A - Installer uses whatever crack was in the ISO
