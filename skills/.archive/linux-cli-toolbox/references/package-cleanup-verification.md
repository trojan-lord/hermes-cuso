# Package Cleanup Verification

After uninstalling a package, verify removal across ALL dimensions. A "clean" uninstall means zero remnants anywhere.

## Verification Checklist

```bash
# 1. Binary gone
which <binary-name> || echo "Clean"

# 2. Package database entry gone
pacman -Qi <pkg-name> 2>/dev/null | head -2 || echo "Clean"

# 3. No process running
pgrep -a <binary-name> || echo "Clean"

# 4. Config files
find ~/.config -iname "*<pkg>*" 2>/dev/null || echo "Clean"

# 5. Data directories
find ~/.local/share -iname "*<pkg>*" -type d 2>/dev/null || echo "Clean"

# 6. Cache
find ~/.cache -iname "*<pkg>*" 2>/dev/null || echo "Clean"

# 7. Systemd services
find /etc/systemd /usr/lib/systemd ~/.config/systemd -name "*<pkg>*" 2>/dev/null || echo "Clean"

# 8. Desktop/integration files
find /usr/share/applications ~/.local/share/applications -name "*<pkg>*" 2>/dev/null || echo "Clean"

# 9. Temp files
find /tmp -name "*<pkg>*" 2>/dev/null || echo "Clean"

# 10. Shell history / aliases (sometimes auto-added)
grep "<pkg>" ~/.bashrc ~/.zshrc ~/.config/fish/config.fish 2>/dev/null || echo "Clean"
```

## Common Pitfalls

- **Shared config directories**: Two packages (e.g. qbittorrent GUI and qbittorrent-nox) may share `~/.config/<app>/`. Uninstalling one may leave config entries for the other that cause confusion on next launch. Check config files for settings added by the removed package and clean those specific lines.
- **Package manager hooks**: `pacman -Rns` removes the package, config, and unused deps, but does NOT clean data directories (`~/.local/share/`, `~/.cache/`). Always check those manually.
- **Icon theme packages**: Icons from removed apps may persist in icon theme directories (e.g. `shelly-icons/`). These are harmless theme assets, not actual package remnants -- do not chase them.
- **Fast resume / state files**: Some apps (qBittorrent, Transmission) store download state in data directories. Removing the package leaves orphaned state that can confuse a re-install or alternate variant. Delete the entire data directory for a clean slate.

## When to Do Full Wipe vs Surgical Cleanup

**Full wipe** (delete all config + data + cache): When starting fresh, switching variants (GUI -> nox), or when the user explicitly asks "remove everything."

**Surgical cleanup** (remove only what the removed package added): When sharing a config directory with another installed package, or when the user wants to preserve settings for a future reinstall.
