# Non-Steam Game Proton Version Switching

## Finding a Non-Steam Game's Internal AppID

Non-Steam games added to Steam get a generated appid stored in `shortcuts.vdf` (binary VDF format).

```bash
# Parse shortcuts.vdf using the Python vdf library
python3 << 'PYEOF'
import vdf, struct

data = open(os.path.expanduser("~/.local/share/Steam/userdata/<userid>/config/shortcuts.vdf"), 'rb').read()
parsed = vdf.binary_loads(data)

for key, val in parsed.items():
    if isinstance(val, dict):
        print(f"Shortcut index {key}: {val.get('AppName', '?')}")
        print(f"  Exe: {val.get('Exe', '?')}")
        print(f"  AppID (signed): {val.get('appid', '?')}")
        unsigned = val.get('appid', 0) & 0xFFFFFFFF
        print(f"  AppID (unsigned): {unsigned}")
PYEOF
```

The **unsigned** appid is the one used for:
- compatdata directory name: `~/.local/share/Steam/steamapps/compatdata/<unsigned_appid>/`
- CompatToolMapping key in config.vdf
- `steam://rungameid/<unsigned_appid>` URL
- `steam -applaunch <unsigned_appid>` CLI flag

## Changing Proton Version for a Non-Steam Game

Edit `~/.local/share/Steam/config/config.vdf` (text VDF format):

```python
import vdf

config = vdf.load(open(os.path.expanduser("~/.local/share/Steam/config/config.vdf")))
cm = config["InstallConfigStore"]["Software"]["Valve"]["Steam"]["CompatToolMapping"]
cm["<unsigned_appid>"] = {
    "name": "GE-Proton11-3",        # Proton version name
    "config": "",
    "priority": "250"
}
with open(os.path.expanduser("~/.local/share/Steam/config/config.vdf"), 'w') as f:
    vdf.dump(config, f)
```

**Proton version names** (as stored in config.vdf):
- `GE-Proton11-3`, `GE-Proton11-1`, `GE-Proton10-34` (GE-Proton versions)
- `proton_experimental` (Proton Experimental)
- `proton_hotfix` (Proton Hotfix)
- `proton_11`, `proton_10`, `proton_9_0` (Stable Proton versions)
- `proton_8_0`, etc. (Older stable versions)

**Note**: Steam reads config.vdf on startup. Changes take effect after restarting Steam, OR can sometimes be picked up live when launching a game.

## Launching a Non-Steam Game

Two methods:

```bash
# Method 1: URI scheme (works with running Steam)
xdg-open steam://rungameid/<unsigned_appid>

# Method 2: Direct applaunch
steam -applaunch <unsigned_appid>
```

Method 1 is preferred when Steam is already running. Method 2 starts a new Steam instance.

## Monitoring Game Launch

Steam logs the launch in `~/.local/share/Steam/logs/console-linux.txt`:

```bash
grep "<unsigned_appid>" ~/.local/share/Steam/logs/console-linux.txt
grep "ProtonFixes\|Proton:" ~/.local/share/Steam/logs/console-linux.txt | tail -20
```

Look for these signals:
- `Proton: Creating prefix from None to <version>` — first-time prefix creation
- `Proton: Upgrading prefix from <old> to <new>` — prefix migration
- `ProtonFixes... Running checks` — game is being processed
- `ntsync: up and running.` — Proton sync primitives working
- `Adding process <pid> for gameID <gameID>` — game spawning

## Limitations

- Game process detection from a headless terminal is unreliable — the Windows exe wraps inside Proton/Wine and doesn't appear as a Linux process with the same name
- Process names like "Unravel.exe" are not visible via `ps` from a non-graphical session
- The actual game process tree looks like: steam → SteamLinuxRuntime → pressure-vessel → proton → wine → (Windows exe inside Wine)
- For headless testing, check Steam console logs and compatdata creation instead
