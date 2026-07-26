---
name: pinecil-firmware-update
description: Update Pinecil V2 soldering iron firmware (IronOS) via USB using blisp on Linux. Covers research, download, flash, and verification.
trigger: When user mentions updating Pinecil firmware, flashing Pinecil, IronOS update, or Pinecil V2 ISP mode.
---

# Pinecil V2 Firmware Update

## Overview

The Pinecil V2 uses a Bouffalo BL706 RISC-V MCU. Firmware lives at [Ralim/IronOS](https://github.com/Ralim/IronOS). Flashing uses `blisp` (Bouffalo Labs ISP tool), NOT `dfu-util` (that's Pinecil V1 only).

## Prerequisites

- **Linux** (Arch/CachyOS — `blisp` is in extra repos)
- **USB-C data cable** (not charge-only — BL706 has a weak USB PHY, cheap cables fail)
- **No DC barrel jack connected** — NEVER plug DC + USB simultaneously, it fries hardware

## Step 1: Install blisp

```bash
sudo pacman -S --noconfirm blisp
blisp --version
```

## Step 2: Download Latest Firmware

```bash
mkdir -p ~/pinecil-update && cd ~/pinecil-update

# Check latest release
curl -sL "https://api.github.com/repos/Ralim/IronOS/releases/latest" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Latest: {data[\"tag_name\"]}')
for a in data.get('assets', []):
    if 'Pinecilv2.zip' in a['name'] and 'multi' not in a['name']:
        print(f'URL: {a[\"browser_download_url\"]}')
"

# Download (replace TAG with actual latest version)
curl -sL "https://github.com/Ralim/IronOS/releases/download/TAG/Pinecilv2.zip" -o Pinecilv2.zip
unzip -o Pinecilv2.zip -d firmware
```

Language files: `Pinecilv2_EN.bin` (English), `Pinecilv2_DE.bin` (German), etc. Only use `.bin` files for V2.

## Step 3: Enter ISP/Flash Mode

Tell the user:
1. Hold down the **minus [-] button** on the Pinecil
2. **While holding [-]**, plug USB-C cable into PC
3. Keep holding for **10-15 seconds** until screen goes black/empty
4. Release button

Verify device:
```bash
sudo dmesg | grep -i -E "usb|acm|bliot" | tail -5
# Should show: Manufacturer: BLIOT, Product: CDC Virtual ComPort
ls /dev/ttyACM*
```

## Step 4: Flash Firmware

```bash
cd ~/pinecil-update
sudo blisp write -c bl70x --reset firmware/Pinecilv2_EN.bin
```

Flags:
- `-c bl70x` — target chip type (BL702/BL706 family)
- `-p /dev/ttyACMx` — optional, specify port explicitly
- `--reset` — reset MCU after flashing

Expected: handshake (may show first-attempt error, then succeeds) → 100% → `Program OK!` → `Flash complete!`

## Step 5: Verify

```bash
sudo dmesg | tail -5
```

User unplugs and replugs iron normally. Hold [-] briefly to see firmware version. Do Advanced Settings > Restore Default Settings to clear old artifacts.

## Gotchas

| Issue | Fix |
|-------|-----|
| Device not detected | Try different USB port, different cable, avoid USB hubs |
| "Failed to receive response" | Normal — blisp retries and succeeds |
| Black screen after flash | Wrong file type (.dfu instead of .bin). Re-flash with .bin |
| DC jack + USB simultaneously | **STOP.** Unplug one immediately. Can destroy hardware |
| Screen stuck on boot logo (looks bricked) | "Infinite Boot Logo" setting enabled — hold [-] + [+] together during boot to enter settings and disable it. OR re-flash to reset. |
| Cannot permanently brick | ROM bootloader is immutable. Always re-enter ISP mode and re-flash |

## Notes

- BLE off by default in v2.23+ (security). User enables manually if desired.
- BL706 USB PHY is weak — use short, high-quality USB-C cables.
- No udev rules needed — kernel `cdc_acm` handles the device.
- `dfu-util` is for Pinecil V1 only. V2 requires `blisp`.
