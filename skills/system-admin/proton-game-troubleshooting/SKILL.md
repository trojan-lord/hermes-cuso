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

**VERIFY WHERE THE PREFIX ACTUALLY LIVES (2026-08 finding, this machine)**: per-app
`compatdata/*/` prefixes are NOT guaranteed — an Aug 1 audit found all 27 dirs as empty
stubs (just `config_info`), but RE-AUDIT Aug 2 after real Steam shortcut launches found
full prefixes (`pfx/drive_c`, ~815M each, 17G total): per-app prefixes get initialized
on first REAL Steam launch, so a stale "stubs" conclusion goes wrong. Always re-check
`find compatdata -maxdepth 2 -name drive_c` + dir mtimes before claiming anything.
Non-Steam game CONFIGS/saves live in the SHARED umu prefix `~/Games/umu/umu-default/`
(GAMEID-less runs); `GAMEID=<appid>` runs create per-game prefixes at
`~/Games/umu/<gameid>/`, and the Steam wrapper ALSO initializes compatdata/<id>. NEVER
"fix prefix corruption" by deleting compatdata/<id> here — the real game data survives
in ~/Games/umu/, confusing the diagnosis. Also: xdg default for .exe is `protontricks-launch`,
which REQUIRES a Steam appid — file-manager double-click is NOT the launch path on
this machine; games launch from Steam shortcuts.

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
- Launching shortcuts headlessly via `GAMEID=<unsigned_appid> umu-run` (the
  steam://rungameid URL CRASHES Steam — see "Reproducing a Steam shortcut launch" below)
- Monitoring launch in Steam logs
- Process detection limitations when testing from a headless terminal

## Games Open Windowed on Wayland/niri (fullscreen request lost in XWayland)

Symptom: game launches from the Steam library but appears as a tiled window (~935x1068),
never covering the screen — while the game's own settings say FullscreenMode=1. Same root
cause as Steam BPM: the X11 fullscreen request crosses XWayland and the compositor honors
it INCONSISTENTLY (race at window map time — same launch command can fullscreen once and
window next). Not a game setting, not a Steam setting.

### Investigate how the game ACTUALLY launches (don't guess)
- Non-Steam shortcuts = BINARY VDF: `~/.local/share/Steam/userdata/<uid>/config/shortcuts.vdf`.
  Decode with Python `vdf.binary_loads` (fields: AppName, exe, appid = negative signed 32-bit).
- Proton pinned per shortcut: `~/.local/share/Steam/config/config.vdf` →
  InstallConfigStore.Software.Valve.Steam.CompatToolMapping[appid].name.
- Launch options: `userdata/<uid>/config/localconfig.vdf` → ...apps[appid].LaunchOptions.
- Games' own display configs live in the wine prefix
  (`~/Games/umu/umu-default/drive_c/users/<user>/AppData/Local/<Game>/...`):
  check FullscreenMode + ResolutionSizeX/Y. Watch for resolution mismatch — e.g.
  Everholm/REANIMAL set to 3840x2160 on a 1920x1080 output: even an honored fullscreen
  request can't match the screen.
- Wine driver: prefix `user.reg` `[Software\\\\Wine\\\\Drivers]` — no virtual desktop /
  wayland driver override → default X11 driver (XWayland path confirmed).
- UE games can SELF-RESOLVE: splash window born fullscreen, real game window appears
  windowed (935x1068) for a few seconds, then goes fullscreen on its own — watch
  ≥10-15s before calling it windowed (observed on It Takes Two, 2026-08).

### Fix: per-shortcut Launch Options
`gamescope -f -e -- %command%`
- gamescope is a native Wayland client → the compositor fullscreens it RELIABLY
  (mechanism verified: gamescope BPM test went true fullscreen on niri), unlike the
  XWayland race. Inside gamescope the game is always fullscreen regardless of its
  internal resolution; add `-F fsr` to upscale (e.g. 4K-native games on a 1080p panel).
- Apply per shortcut: Steam UI (Properties → Launch Options) or edit config.vdf while
  Steam is closed. ASK the user which — this user green-lights before any change.
- NOTE: this was proposed + mechanism-verified, NOT yet applied on this machine.

### umu-run testing pitfall (prefix churn — happened 2026-08)
NEVER test non-Steam games with bare `umu-run <exe>`: it defaults to a different Proton
(e.g. UMU-Proton-10.0-4) and "upgrades"/churns the prefix that was built with another
build (GE-Proton11-3) — rewrites version/tracked_files/pfx.lock, logs "Prefix has an
invalid version?!". Always pin the build:
`PROTONPATH=~/.local/share/Steam/compatibilitytools.d/<build> umu-run <exe>`.
Also: first umu-run of a prefix runs pv-verify (30-60s, ~100% CPU) before any game
window appears — not a hang. A window that flashes ~2s then dies is a SEPARATE crash
(e.g. Blur, old DX9 under GE-Proton11), not the fullscreen bug.

### Test through the USER'S real launch path (user will ask "did you run it through Steam?")
A bare `umu-run <exe>` is NOT the same as launching from a Steam shortcut (missing
overlay, per-game protonfixes, Steam env). Before reporting a diagnosis from a direct
test, either (a) reproduce the Steam launch faithfully with
`GAMEID=<unsigned_appid> umu-run "<exe>"` (below), or (b) prove prefix equivalence:
compatdata stubs + game-config timestamps inside the shared prefix. This user WILL call
it out — 2026-08 session, Blur diagnosis via umu-run was challenged exactly this way.

### Reproducing a Steam shortcut launch without Steam (VALIDATED 2026-08)
`steam://rungameid/<unsigned_appid>` CRASHES the Steam client for non-Steam shortcuts —
verified crash dump: `YAssert( Unknown GameID type )` (steamid.cpp:696), minidump in
/tmp/dumps/, Steam restarts, nothing launches. The URL scheme and `steam -applaunch`
both assert on shortcut ids. The faithful headless repro is the umu GAMEID form:

```bash
GAMEID=<unsigned_appid> umu-run "/path/to/Game.exe"
```

This is what Steam actually does for a shortcut: protonfixes run with that GAMEID and a
PER-GAME prefix is created at `~/Games/umu/<gameid>/` (vs shared `~/Games/umu/umu-default/`
when GAMEID is unset). Validated: It Takes Two launched via this and went fullscreen,
stable. Steam's internal 64-bit gameID for shortcuts decodes as
`(unsigned_appid << 32) | 0x02000000` (see "Adding process ... for gameID" in console-linux.txt).

### Silent crash before any window (not a fullscreen issue)
A game that spawns processes but NEVER creates a window, then exits ~40s later, is
crashing pre-window. Evidence to gather:
- `~/.local/share/Steam/logs/console-linux.txt`: `Adding process ... for gameID` lines,
  then `Removing process ... for gameID` a minute later = game died; `Game Recording -
  game stopped` confirms it.
- No config dir written in the prefix (no `AppData/LocalLow/<Game>`, no
  GameUserSettings.ini) = game never got far enough to save settings.
- Steam client asserts: `/tmp/dumps/assert_*.dmp` + `h2_log.txt`; read the reason with
  `strings <dmp> | grep -i assert`.
- Isolate proton-version crashes: same game via Steam (pinned GE-Proton) crashing vs
  `GAMEID=... umu-run` (default UMU-Proton) running fine = switch the shortcut's
  CompatToolMapping to the working build. (2026-08: It Takes Two crashed pre-window
  under GE-Proton11-3 via Steam; ran fullscreen under UMU-Proton-10.0-4 via umu.)

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

## ⚠️ Critical: Rabbit Hole Awareness

The most common failure pattern in this domain is **silent persistence through dead ends**. If you hit a wall (command not found, auth required, no assets, permission denied), do NOT silently try 3+ different approaches.

**Rule**: After 2 consecutive failed approaches to achieve any single task (installing a tool, downloading a Proton version, etc.), stop and report to the user:
- What you tried
- What failed (exact error)
- What you need from them to proceed (credentials, decision, alternative)

Do not go past 2 silent failures. The user would rather hear "I need X" than read 10 failed terminal outputs.

## Proton Version Availability

### Older Proton Versions
- **GitHub releases (ValveSoftware/Proton)**: Only contain source code tarballs, NOT compiled binaries. The `assets` array on any tag release is typically empty.
- **Binary distribution**: Proton binaries are served exclusively through Steam's content delivery system (depots).
- **DepotDownloader**: CAN download older Proton depots, but **requires an authenticated Steam account** — anonymous login does not have access. You'll need either:
  - The user's Steam password (use `-username <user>` and it will prompt)
  - QR code login (`-qr` flag)
  - Already-remembered password (`-remember-password` after first login)
- **steamcmd**: Same limitation — cannot download Proton depots anonymously.
- **Recommended approach**: Before attempting any Proton depot download, ask the user how they want to authenticate first. Do not try anonymous methods first — they will all fail.

## Known Incompatible Crack Patterns

- CODEX OrangeEmu64.dll: NO - Windows RPC dependency, RPC_S_SERVER_UNAVAILABLE crash
- CODEX OrangeEmu.dll (32-bit): NO - Same RPC dependency
- Empress: Varies - Some newer cracks avoid RPC, check per-game
- FitGirl: N/A - Installer uses whatever crack was in the ISO
- STP (STEAMPUNKS) Origin Emulator (`stp-origin_emu.dll`): NO - Same class as CODEX, Origin launcher bypass, crashes with exit code 10 on all Proton versions. See `references/crack-patterns-stp-origin-emu.md`.
