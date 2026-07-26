---
name: embedded-firmware-flash
description: Flash firmware on embedded devices — Pinecil (Bouffalo BL70x via blisp), ESP32 (esptool), and other MCUs. Covers tool installation, DFU/ISP modes, cable requirements, and verification.
triggers:
  - Pinecil
  - Pinecil V2
  - blisp
  - Bouffalo
  - BL706
  - BL702
  - firmware update
  - flash firmware
  - DFU mode
  - ISP mode
  - soldering iron firmware
  - IronOS
  - embedded firmware
  - mcu flash
---

# Embedded Firmware Flash

Generic skill for flashing firmware on embedded devices. Each chip family has its own toolchain and flash procedure.

## Supported Devices

| Device | Chip | Flash Tool | Flash Mode | Notes |
|--------|------|------------|------------|-------|
| Pinecil V2 | Bouffalo BL706 | `blisp` | ISP (hold [-] + USB) | `.bin` files only |
| Pinecil V1 | GD32VF103 | `dfu-util` | DFU | Older model, uses `.dfu` files |
| ESP32 family | ESP32/S3/C3/C6 | `esptool` | Boot mode (GPIO0) | See `esp32-development` skill |

## Pinecil V2 — Bouffalo BL706

### Install blisp
```bash
# Arch/CachyOS — in extra repos
sudo pacman -S blisp

# Verify
blisp --version  # should show v0.0.5+
```

### Download Firmware
```bash
# IronOS releases at github.com/Ralim/IronOS
# Latest release page: check https://github.com/Ralim/IronOS/releases/latest
mkdir -p ~/pinecil-update && cd ~/pinecil-update
curl -sL "https://github.com/Ralim/IronOS/releases/download/v2.23/Pinecilv2.zip" -o Pinecilv2.zip
unzip Pinecilv2.zip -d firmware
# Firmware file: firmware/Pinecilv2_EN.bin (English, or other language codes)
```

### Enter ISP/Flash Mode
1. **Hold down [-] button** on the iron
2. **Plug USB-C cable** while still holding [-]
3. **Keep holding for 10-15 seconds** after plugging in
4. **Screen should go black/empty** — this means ISP mode is active
5. Release the button

### Verify Device
```bash
# Check dmesg for BLIOT manufacturer
sudo dmesg | grep -i blilot
# Should show: Manufacturer: BLIOT, Product: CDC Virtual ComPort

# Check device node
ls -la /dev/ttyACM*
# Should show: /dev/ttyACM0 (or next available)
```

### Flash
```bash
# Basic command
sudo blisp write -c bl70x --reset ~/pinecil-update/firmware/Pinecilv2_EN.bin

# If port needs explicit specification
sudo blisp write -p /dev/ttyACM0 -c bl70x --reset ~/pinecil-update/firmware/Pinecilv2_EN.bin
```

**Flags:**
- `-c bl70x` — target chip type (BL702/BL706 family)
- `--reset` — reset MCU after flashing
- `-p /dev/ttyACMx` — (optional) specify serial port explicitly

### Verify Flash
1. Unplug USB
2. Plug back in normally (no button holding)
3. Screen should light up with new firmware
4. Hold [-] briefly (2 sec) to see firmware version
5. Go to Advanced > Restore Default Settings to clear old settings

## Pitfalls

### 🔴 NEVER plug DC barrel + USB-C simultaneously
This can destroy both the PC and the Pinecil. Only one power source at a time. This is the single biggest danger.

### USB cable quality matters (especially BL706)
The Bouffalo BL706 has a notoriously weak USB PHY. Cheap/thin/Apple cables often fail. Use a short, high-quality USB-C data cable. If flash fails, try:
- Different cable
- USB 2.0 port (not 3.0/hub)
- Direct motherboard connection (no hubs)
- USB-C → USB-A → USB-C adapter chain

### BL706 does NOT use standard DFU
The Pinecil V2 uses ISP protocol via `blisp`, NOT `dfu-util`. The V1 used DFU — do not confuse them. If someone says "use dfu-util for Pinecil V2" they are wrong.

### Only use .bin files for V2
Flashing `.dfu` or `.hex` files will cause a black screen. Use `.bin` only. If you accidentally flash the wrong format, just re-flash with the correct `.bin` — the bootloader is in ROM and cannot be bricked.

### Cannot permanently brick
The bootloader is in ROM. Even if firmware goes bad (black screen), you can always re-enter ISP mode and re-flash. This is by design.

### Handshake warnings during flash are normal
`blisp` may show "Received incorrect handshake response" on first attempt — this is normal. It retries automatically and succeeds. Do not panic.

### Permission issues
The device appears as `/dev/ttyACM0` owned by `root:uucp`. You need `sudo` to flash, or add your user to the `uucp` group.

## Research Notes

- IronOS source: github.com/Ralim/IronOS (not Pine64/Pinecil — that repo doesn't exist)
- blisp source: github.com/pine64/blisp
- Official docs: ironos.app
- Pinecil V2 firmware zip contains all languages + 3 formats each (.bin, .dfu, .hex)
- `.dfu` format is for older tools, `.hex` is for JTAG — use `.bin` for blisp
