# Noctalia Shell — Notification Architecture

## Package Stack

| Package | Role |
|---------|------|
| `cachyos-niri-noctalia` | Niri config + Noctalia settings (skeleton files to `~/.config/niri/` and `~/.config/noctalia/`) |
| `noctalia-shell` | The shell itself — QML modules under `/etc/xdg/quickshell/noctalia-shell/` |
| `noctalia-qs` | Custom Quickshell binary (`qs` and `quickshell` commands) that runs noctalia-shell |

**There is no `noctalia-cli` or custom notification CLI.** The standard freedesktop `notify-send` is the only way.

## How Noctalia Receives Notifications

Noctalia implements the **`org.freedesktop.Notifications`** D-Bus interface via Quickshell's `NotificationServer` component. Source: `/etc/xdg/quickshell/noctalia-shell/Services/System/NotificationService.qml`.

Key implementation details from the source:
- Creates `NotificationServer { imageSupported: true; actionsSupported: true }` from `Quickshell.Services.Notifications`
- Only claims the D-Bus name when `Settings.data.notifications.enabled !== false`
- Destroyed and recreated when settings change
- Supports notification replacement (same D-Bus ID updates existing popup), deduplication (content hash), urgency-based durations, action invocation via `dbus-send`, and history persistence to JSON

## Notification Flow

```
notify-send "Title" "Body"
    → D-Bus session bus → org.freedesktop.Notify.SendNotification
    → Quickshell NotificationServer (owns org.freedesktop.Notifications)
    → NotificationService.qml handleNotification()
    → evaluates notification rules (block/hide/mute/allow)
    → popupModel (shows toast) + historyModel (saves to JSON)
    → Toast renders via Modules/Notification/Notification.qml
```

## Sending Notifications from Terminal

```bash
# Basic
notify-send "Title" "Body text"

# With app name (shown in Noctalia toast header)
notify-send -a "MyScript" "Title" "Body"

# Urgency levels map to configurable durations:
#   low=3s, normal=8s, critical=15s (defaults from settings.json)
notify-send -u low "Low urgency"
notify-send -u normal "Normal urgency"
notify-send -u critical "Critical alert"

# With icon
notify-send -i dialog-information "Title" "Body"

# Persistent notification (requires allow_permanent per the filter)
notify-send -t 0 "Title" "Persistent"
```

## Key Config Paths

- **Noctalia settings:** `~/.config/noctalia/settings.json` → `notifications` section
  - `enabled`: bool — master switch for the notification daemon
  - `location`: string — toast position (e.g. `"top_right"`)
  - `lowUrgencyDuration`, `normalUrgencyDuration`, `criticalUrgencyDuration`: seconds
  - `sounds.enabled`, `sounds.normalSoundFile`, etc.: notification sound config
  - `saveToHistory`: which urgency levels to persist
- **Niri autostart:** `~/.config/niri/cfg/autostart.kdl` — `spawn-sh-at-startup "qs -c noctalia-shell"`
- **Notification service source:** `/etc/xdg/quickshell/noctalia-shell/Services/System/NotificationService.qml`
- **Toast UI:** `/etc/xdg/quickshell/noctalia-shell/Modules/Notification/Notification.qml`
- **History panel:** `/etc/xdg/quickshell/noctalia-shell/Modules/Panels/NotificationHistory/NotificationHistoryPanel.qml`
- **Notification rules:** `/etc/xdg/quickshell/noctalia-shell/Services/System/NotificationRulesService.qml`

## Documentation

- v4 docs (current stable): https://docs.noctalia.dev/v4/ — no dedicated notifications page
- v5 docs (beta): https://docs.noctalia.dev/v5/services/notifications/ — has config reference and filter docs
  - `enable_daemon = true` controls whether the shell claims `org.freedesktop.Notifications`
  - Per-sender filtering via `[notification.filter.<name>]` sections

## D-Bus Ownership Check

```bash
busctl --user list | grep org.freedesktop.Notifications
```

- `qs` = Noctalia in control (correct)
- `mako` = mako intercepted (problem — stop/disable it)
- `dunst` = dunst intercepted (problem — stop/disable it)
- No output = nobody owns the bus → shell not running → notifications silently dropped or `notify-send` times out

## Failure Modes

### 1. Shell not running (notify-send times out)
No Quickshell process → nobody claims `org.freedesktop.Notifications` → `notify-send` gets no reply.
Fix: `qs -c noctalia-shell &`

### 2. Competing daemon (mako/dunst steals the bus)
Shell is running but another daemon grabbed the bus first.
Fix: stop and disable the competing daemon.

### 3. Notifications disabled in config
`notifications.enabled = false` in settings.json → Quickshell creates and immediately destroys the NotificationServer.
Fix: set `notifications.enabled` to `true`.

## How mako Gets Installed

`mako` is `Optional For: niri` in pacman. Installed as part of bulk niri/sway package sets. The systemd user service is preset-enabled, so it auto-starts on graphical session. No config file exists at `~/.config/mako/config` by default — runs on hardcoded defaults.

## Noctalia Bus Reclaim Behavior

Noctalia's Quickshell process monitors the D-Bus notification interface. When a conflicting daemon (mako) releases it, Quickshell can auto-reclaim without restart. Verified by checking `busctl --user list` after stopping mako.
