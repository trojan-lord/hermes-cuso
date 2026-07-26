# niri msg — Desktop Control from Terminal

## Setup

When Hermes runs under systemd with `Linger=yes`, `NIRI_SOCKET` is not set. Find it dynamically:

```bash
NIRI_SOCKET=$(ls /run/user/$(id -u)/niri.*.sock 2>/dev/null | head -1)
export NIRI_SOCKET="$NIRI_SOCKET"
```

Socket path includes the Wayland display number and changes each boot (e.g., `niri.wayland-1.28106.sock`).

## JSON Output

All query commands support `-j` flag (must come BEFORE the subcommand):

```bash
niri msg -j windows       # List all open windows (JSON)
niri msg -j focused-window # Current focused window details
niri msg -j workspaces     # All workspaces with active/focused state
niri msg -j outputs        # All monitors with resolution/modes
```

## Window Management

```bash
niri msg action spawn -- <command>     # Launch app
niri msg action close-window           # Close focused window
niri msg action fullscreen-window      # Toggle fullscreen
niri msg action toggle-window-floating # Toggle tiling ↔ floating
niri msg action center-column          # Center current column
niri msg action focus-column-left      # Navigate columns
```

## Workspace Control

```bash
niri msg action focus-workspace -- <index>        # Switch workspace
niri msg action move-window-to-workspace-down     # Move window to workspace below
niri msg action set-workspace-name -- "name"      # Name workspace
```

## Window Properties (from -j windows)

Each window object contains:
- `id`, `title`, `app_id`, `pid`
- `is_focused`, `is_floating`, `is_urgent`, `workspace_id`
- `layout.pos_in_scrolling_layout` — `[col, row]` position
- `layout.tile_size` — `[width, height]` in pixels
- `layout.window_size` — actual window dimensions
- `focus_timestamp` — when window was last focused

## Action List

100+ actions available. Key categories:
- **Focus**: `focus-window-*`, `focus-column-*`, `focus-workspace-*`, `focus-monitor-*`
- **Move**: `move-column-*`, `move-window-*`, `move-workspace-*`
- **Layout**: `set-window-width`, `set-column-width`, `maximize-column`, `toggle-column-tabbed-display`
- **Display**: `screenshot`, `screenshot-screen`, `screenshot-window`, `toggle-overview`
- **System**: `spawn`, `close-window`, `quit`, `load-config-file`, `power-off-monitors`

Full list: `niri msg action --help`
