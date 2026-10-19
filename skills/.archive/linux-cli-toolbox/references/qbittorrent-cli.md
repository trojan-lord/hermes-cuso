# qBittorrent CLI Patterns

## GUI vs Headless

The GUI version (`qbittorrent`) supports full CLI usage -- no need to install `qbittorrent-nox` for headless operation.

```bash
# Check CLI options
qbittorrent --help
```

Key flags:
- `--save-path=/path` -- set download directory
- `--no-splash` -- skip splash screen
- `--skip-dialog=true` -- **critical** -- bypass the "Add New Torrent" confirmation dialog. Without this, the torrent appears in the UI but does NOT start downloading.
- `--sequential` -- sequential download order
- Magnet URLs work as positional arguments

## Magnet URLs: Shell Escaping Problem

Magnet URLs contain `&` characters which bash interprets as background operators. Even quoted, the shell can split them in some contexts.

**Broken** (shell splits on `&`):
```bash
qbittorrent "magnet:?xt=urn:btih:HASH&dn=name&tr=udp://..."  # works sometimes
qbittorrent magnet:?xt=urn:btih:HASH&dn=name&tr=udp://...    # always broken
```

**Reliable fix** -- use Python subprocess to pass the magnet as a single argv:
```python
import subprocess
magnet = 'magnet:?xt=urn:btih:HASH&dn=name&tr=udp://...'
subprocess.Popen(['qbittorrent', '--save-path=/home/user/Downloads', '--no-splash', '--skip-dialog=true', magnet])
```

**Why not `.magnet` files?** qBittorrent treats them as torrent files and tries to bencode-decode them, which fails with "expected value in bencoded string". The file approach does not work for magnet URIs.

**Why not `xargs`?** Even `echo "magnet:..." | xargs qbittorrent` does not reliably preserve the full URL. Python subprocess is the only reliable method.

## Torrent Removal Without Deleting Files

Kill qBittorrent, then manually remove only the BT_backup files:

```bash
kill $(pgrep qbittorrent)
# Find the torrent hash
ls ~/.local/share/qBittorrent/BT_backup/*.torrent
# Remove the specific torrent's files (keep the download)
rm ~/.local/share/qBittorrent/BT_backup/<HASH>.fastresume
rm ~/.local/share/qBittorrent/BT_backup/<HASH>.torrent
# Clear the queue
echo "" > ~/.local/share/qBittorrent/BT_backup/queue
# Restart qBittorrent
qbittorrent --no-splash &
```

The WebUI API can also be used (requires enabling WebUI in config), but manual BT_backup cleanup is more reliable when WebUI auth is not configured.

## Post-Removal Cleanup

After removing qBittorrent-nox (or any variant), check for:
1. Config settings added for the variant (e.g. WebUI settings in shared config)
2. Temp files in `/tmp` (magnet files, cookie jars, etc.)
3. BT_backup state files that could confuse the remaining variant
4. Leftover partial downloads in the download directory

Do NOT remove shared config/data directories that belong to the remaining variant.
