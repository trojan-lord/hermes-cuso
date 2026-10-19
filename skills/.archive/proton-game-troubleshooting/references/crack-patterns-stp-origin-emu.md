# STP / STEAMPUNKS Origin Emulator Crack

## Identifiers

- **DLL**: `stp-origin_emu.dll` (sometimes `stp-origin_emu.ini` alongside it)
- **Ini config**: `stp-origin_emu.ini` contains `[Globals]` with `Language` and `PersonaId`/`PersonaName`
- **Group**: STEAMPUNKS (STP) — early Origin/EA launcher bypass group
- **Directory clue**: Often includes `STEAMUNLOCKED » Free Steam Games Pre-installed for PC.url`
- **Launchers**: May include `stp-selector.exe` and `stp-unravel.exe` alongside the main game exe

## Behavior

Replaces the EA/Origin launcher with a local stub DLL. The game normally requires Origin running in the background; the emulator intercepts Origin communication and returns dummy responses so the game thinks it's authenticated.

## Compatibility with Proton/Wine

**INCOMPATIBLE** — Same class as CODEX OrangeEmu64.dll:

- Calls Windows-specific services (RPC, named pipes, registry hooks) that Wine does not implement
- Process crashes immediately with exit code 10 (STATUS_BREAKPOINT / unhandled exception)
- All Proton versions (Experimental, GE-Proton, stable) fail identically
- Removing the crack DLLs does NOT help — the game binary expects them for initialization

## Detection Command

```bash
strings "/path/to/game.exe" | grep -i -E "OrangeEmu|stp-origin|originu"
ls -la "/path/to/game/dir/"*.dll | grep -i "emu"
```

## Verdict

Cannot be made to work under Proton/Wine. Only runs on actual Windows.
