#!/usr/bin/env bash
# Launch Steam Big Picture inside gamescope -> true fullscreen on niri/Wayland.
# Steam's BPM window doesn't reliably request fullscreen through XWayland,
# so gamescope owns the surface and presents it as a fullscreen layer.
# Install: ~/.local/bin/steam-bigpicture  (chmod +x)
set -euo pipefail

# If Steam is already running, shut it down gracefully first.
# Otherwise `steam -gamepadui` just signals the existing instance and
# gamescope exits immediately (its child returns right away).
if pgrep -x steam >/dev/null 2>&1; then
    echo "Steam is running -- shutting it down first..."
    steam -shutdown >/dev/null 2>&1 || true
    for _ in $(seq 1 30); do
        pgrep -x steam >/dev/null 2>&1 || break
        sleep 1
    done
fi

exec gamescope -f -e -- steam -gamepadui
