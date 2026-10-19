# Steam / .local Disk Usage (measured 2026-08-02, this machine)

Trigger: user asks "why is .local / ~ so big" or "what's in .local".

Method: du drill-down, top level → biggest child, repeat:
`du -sh ~/.local/* | sort -rh | head` → `share/*` → `Steam/*` → `steamapps/*`.

## Measured map (120G total in ~/.local)

| Path | Size | Notes |
|---|---|---|
| `~/.local` total | 120G | |
| `share/Steam` | 114G | 95% of .local |
| `steamapps/common` | 81G | actual game files |
| `.../common/dota 2 beta` | **73G** | THE whale — 61% of .local |
| `.../common/Proton *` | ~1.3–1.5G each | Hotfix, Experimental, 11.0, 10.0, 9.0-beta |
| `steamapps/compatdata` | 17G | per-app Wine prefixes, ~815M each (27 dirs) |
| `steamapps/shadercache` | 7.2G | GPU shader cache — **SAFE to clear, regenerates** |
| `compatibilitytools.d` | 5.6G | GE-Proton11-3, UMU-Proton builds |
| client (ubuntu12_32/64, steamrt, package, config…) | ~3G | |
| `share/Trash` | 2.6G | empty = instant space, zero risk |
| `share/umu` | 1.5G | UMU runtime |
| `share/lutris` | 476M | |
| `state` | 328M | |
| everything else (uv, zed, akonadi, icons, fonts…) | <1G | |

## Safe wins (in risk order)

1. Empty Trash — 2.6G, zero risk.
2. Clear `steamapps/shadercache/*` — 7.2G, Steam regenerates per-game on next launch.
3. Uninstall Dota 2 beta — 73G, only if not played.

Biggest shadercache dirs were per-appid: 570 (Dota), 2262630052, 2583422298
(non-Steam shortcut appids).

## Pitfall

`compatdata` sizes are NOT static — dirs start as stubs (config_info only) and grow to
~815M prefixes on first REAL Steam launch. Never report "empty stubs" from an old scan;
re-check `find compatdata -maxdepth 2 -name drive_c` + mtimes first.
