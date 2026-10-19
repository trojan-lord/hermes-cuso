# System State Tools — Niri/Noctalia Desktop

Quick reference for querying and controlling the desktop from terminal.

## Niri Compositor Control (`niri msg`)

**Socket requirement:** `NIRI_SOCKET` must be set. Only available inside an active niri session (not from systemd user services with Linger=yes).

**Finding the socket when NIRI_SOCKET is not set** (e.g. running from systemd/Linger):
```bash
# The socket is always at this path pattern:
NIRI_SOCKET=$(ls /run/user/$(id -u)/niri.*.sock 2>/dev/null | head -1)
# Then use it:
export NIRI_SOCKET="$NIRI_SOCKET"
niri msg -j windows
```

**Important:** The `-j` flag goes BEFORE the subcommand, not after:
```bash
niri msg -j windows          # ✅ correct
niri msg windows -j          # ❌ wrong — unexpected argument
```

```bash
# Query state (JSON output with -j flag BEFORE subcommand)
niri msg -j windows          # list open windows
niri msg -j workspaces       # list workspaces
niri msg -j outputs          # list connected outputs (resolution, modes, VRR)
niri msg -j focused-window   # focused window info (id, title, app_id, pid, layout)
niri msg -j focused-output   # focused output info
niri msg -j layers           # layer-shell surfaces
niri msg event-stream        # real-time event stream
niri msg version             # niri version
```

**Window properties returned by `-j windows`:**
- `id`, `title`, `app_id`, `pid`, `workspace_id`
- `is_focused`, `is_floating`, `is_urgent`
- `layout` with `tile_size`, `window_size`, `pos_in_scrolling_layout`

```bash
# Actions (niri msg action <ACTION>)
niri msg action spawn "firefox"
niri msg action spawn-sh "command"
niri msg action close-window
niri msg action fullscreen-window
niri msg action toggle-window-floating
niri msg action focus-column-left
niri msg action focus-workspace 2
niri msg action move-window-to-workspace 3
niri msg action screenshot
niri msg action toggle-overview
niri msg action load-config-file
niri msg action center-column
niri msg action maximize-column
niri msg action toggle-column-tabbed-display
niri msg action set-window-width <pixels>
niri msg action set-window-height <pixels>
```

**Full action list (100+ actions):** Window focus/move/swap, column management, workspace switching/naming, monitor focus/move, floating/tiling toggle, fullscreen, overview, screenshots, output config, keyboard layout, debug tint, screencast control, and more. Run `niri msg action --help` for the complete list.

## System State Queries

```bash
# Battery
cat /sys/class/power_supply/BAT*/capacity
cat /sys/class/power_supply/BAT*/status

# Brightness (brightnessctl)
brightnessctl get / brightnessctl set +5% / brightnessctl set -5%

# Volume (wpctl for WirePlumber/PipeWire)
wpctl get-volume @DEFAULT_AUDIO_SINK@
wpctl set-volume @DEFAULT_AUDIO_SINK@ 0.5
wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
wpctl list-sinks

# Media player (playerctl)
playerctl status / playerctl metadata --format "{{artist}} - {{title}}"
playerctl play-pause / playerctl next / playerctl previous

# Network (NetworkManager)
nmcli general status / nmcli device status / nmcli dev wifi list

# Screen color temperature (gammastep)
gammastep -m manual -t 4000:4000  # warm
gammastep -m manual -t 6500:6500  # neutral

# Desktop input simulation (ydotool) — requires ydotoold daemon
sudo systemctl enable --now ydotoold
ydotool mousemove --absolute -x 500 -y 300
ydotool click 1 / ydotool click 0xC0
ydotool type "hello world"
```

## Notifications

Noctalia shell has a built-in notification system. `notify-send` works when the shell is running (it claims D-Bus `org.freedesktop.Notifications`). From systemd services without a graphical session, notifications may not display.

```bash
notify-send "Title" "Body"
notify-send -u critical "Alert" "Important"
```
