---
name: esp32-development
description: ESP32 firmware development — compile, flash, captive portals, board selection, ESP-NOW, hardware projects
triggers:
  - ESP32
  - esp32
  - esptool
  - captive portal
  - ESP-NOW
  - Arduino CLI ESP32
  - microcontroller firmware
  - keyboard matrix
  - GPIO mapping
  - softAP
---

# ESP32 Development

## Compile & Flash Workflow

### Arduino CLI (preferred for ESP32)
```bash
# Compile
arduino-cli compile --fqbn esp32:esp32:esp32:PartitionScheme=huge_app,FlashMode=qio,FlashSize=4M /path/to/sketch

# Find output binaries
BDIR=$(ls -td ~/.cache/arduino/sketches/*/ | head -1)
ls "$BDIR"/*.bin
```

### Flash with esptool
```bash
# Requires sudo if user not in dialout group
sudo /tmp/esp-venv/bin/esptool.py --port /dev/ttyUSB0 --baud 460800 \
  write_flash \
  0x1000 "$BDIR/sketch.ino.bootloader.bin" \
  0x8000 "$BDIR/sketch.ino.partitions.bin" \
  0xe000 "$BDIR/boot_app0.bin" \
  0x10000 "$BDIR/sketch.ino.bin"
```

### Erase flash (clean wipe)
```bash
sudo esptool.py --port /dev/ttyUSB0 erase-flash
```

### Serial monitor
```bash
sudo python3 -c "
import serial, time
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)
while True:
    line = ser.readline()
    if line: print(line.decode('utf-8', errors='replace'), end='')
"
```

## Pitfalls

### 🔴 NEVER connect to a non-home WiFi network
**The host machine runs on a specific WiFi network. Connecting the machine to the ESP32's AP or any other network KILLS the internet connection and drops Discord.** The ESP32's WiFi AP is for the USER's phone/laptop to connect to, not the host machine. Test captive portals from the user's phone, not from the development machine.

### ESP32 Arduino Core v3 — DNSServer API changed
The old `dnsserver.start(DNS_PORT, "*", apIP)` API no longer works. Options:
- Use `dnsserver.start(DNS_PORT, domain, resolvedIP)` with a specific domain
- Or write a custom UDP DNS handler (more reliable for captive portals — responds to ALL queries)

### softAPConfig MUST be called BEFORE softAP
```cpp
WiFi.softAPConfig(apIP, apGateway, subnet);  // FIRST
WiFi.softAP(ssid, password);                   // THEN
WiFi.softAPConfig() after WiFi.softAP() doesn't take effect properly.
```

### AP IP must match DNS responses
If DNS responds with `192.168.4.1` but you set the AP to `4.4.4.4`, the captive portal won't redirect. Use `192.168.4.1` (standard ESP32 AP default) and make DNS respond with the same IP.

### esptool deprecation warnings
`esptool.py` is deprecated in v5.x — use `esptool` (no `.py`). Also `erase_flash` → `erase-flash`. Warnings don't break functionality but will eventually.

## Captive Portal Pattern

1. **DNS server** — respond to ALL queries with ESP32 AP IP (wildcard)
2. **HTTP server** — intercept captive portal detection URLs:
   - Apple: `/hotspot-detect.html` → respond `200 OK` with HTML containing `<title>Success</title>`
   - Android: `/generate_204` → respond `200 OK` (empty body works)
   - Windows: `/connecttest.txt` → respond `200 OK`
   - Fallback: serve the actual webpage for everything else
3. **WebServer notFoundHandler** — catch-all that serves the main page (most captive portals just need any HTTP 200)

## Board Verification Workflow

When new ESP32 boards arrive, verify them before starting any project:

```bash
# 1. Check what appeared
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null

# 2. XIAO S3 shows as ttyACM* (USB CDC), NOT ttyUSB* (that's CH340/CP2102)
# Identify boards:
for dev in /dev/ttyACM*; do
    udevadm info --query=all --name=$dev | grep -E "ID_MODEL|ID_SERIAL_SHORT"
done

# 3. Check chip type + flash
/tmp/ss-venv/bin/python3 -m esptool --port /dev/ttyACM0 chip-id
/tmp/ss-venv/bin/python3 -m esptool --port /dev/ttyACM0 flash-id

# 4. Check for existing firmware
/tmp/ss-venv/bin/python3 -m esptool --port /dev/ttyACM0 read-flash 0x10000 0x40000 /tmp/app_check.bin
strings /tmp/app_check.bin | grep -iE "arduino|micro|hello|test|sketch"
```

### ⚠️ Pitfall: Permission denied on ttyACM*
XIAO S3 boards need the `uucp` group. If `ls -la /dev/ttyACM*` shows `crw-rw---- root uucp`, the user must be in the `uucp` group:
```bash
sudo usermod -aG uucp $USER
# Then log out and back in (or newgrp uucp for current session)
```
Temporary fix: `sudo chmod 666 /dev/ttyACM*` (resets on replug).

### XIAO S3 Factory Test Firmware
Seeed ships XIAO S3 with a factory test sketch. Identifiable by:
- `arduino-lib-builder` string in flash at 0x10000
- `Hello from Seeed Studio XIAO ESP32-S3` output
- Tests: WiFi scan, button, GPIO, NVS write
- Built with ESP-IDF v5.4.1, date stamp in bootloader
This is normal -- the board passed QC. Safe to flash over.

### esptool setup (temp venv)
```bash
uv venv /tmp/ss-venv
uv pip install --python /tmp/ss-venv/bin/python esptool playwright pyserial
/tmp/ss-venv/bin/python -m esptool  # verify it works
```

## Board Selection for Projects

| Board | GPIO | Native USB | ESP-NOW | Price | Best for |
|-------|------|------------|---------|-------|----------|
| ESP32-D0WD-V3 (DevKit) | 30+ | ❌ | ✅ | ~₹650 | General purpose, matrix scanning, ESP-NOW sender |
| ESP32-S3 DevKit (Quartz N16R8) | 36 | ✅ (dual USB-C) | ✅ | ₹684 | Full-featured: keyboard, robotics, best value S3 |
| ESP32-S3 XIAO | 11 | ✅ | ✅ | ₹1,200+ | Tiny dongle, macro pad, gamepad (needs I2C expander for 40+ keys) |
| ESP32-C3 | 22 | ✅ | ✅ | ₹400+ | Budget BLE |
| ESP32-C6 | 30 | ❌ | ✅ | ₹500+ | WiFi 6, Thread/Zigbee |

### 🏆 Value pick: Quartz S3-N16R8 (₹684)
36 GPIO, 16MB flash, 8MB PSRAM, dual USB-C, native USB OTG. More GPIO, more memory, and cheaper than the XIAO S3.

### 🔴 Bluetooth: Classic vs BLE — the A2DP gotcha
- **ESP32 classic (D0WD-V3 / WROOM-32): has Bluetooth Classic AND BLE.** Classic enables A2DP **source** — streaming stereo audio to BT headphones/earbuds. The only mainstream ESP32 that can.
- **ESP32-S3 / C3 / C6: BLE-only.** No Bluetooth Classic → no A2DP source → cannot play audio to BT earbuds. (LE Audio isn't supported on the S3, and most earbuds don't do LE Audio yet anyway.)
- Rule: any project that must play audio to Bluetooth headphones uses the **classic ESP32** (or an external I2S→BT transmitter module).
- Proven audio stack: `pschatzmann/ESP32-A2DP` (source mode) + `libhelix-mp3` (software decode) → PCM → A2DP. MP3 decode ≈ 60–80% of one LX6 core at 240MHz — pin decode to core 0, SD/DMA traffic to core 1.
- Example build: `references/mel-taste-radio.md` — Mel, a self-feeding AI radio (online taste model + SD library + Jamendo foraging + A2DP out).

### XIAO S3 GPIO details
- **11 usable GPIO:** GPIO0–GPIO10 (all have ADC)
- **No hardware DAC** — zero analog output. Use PWM for analog-like output
- **GPIO11:** strapping pin (boot mode) — avoid
- **GPIO12-17:** reserved for flash/PSRAM — cannot use
- **GPIO18-21:** reserved for USB (default = USB Device mode). **BUT** the USB D+/D- lines (GPIO19/20) are broken out to **castellated pads on the bottom** of the board — can be soldered directly for custom USB wiring. ESP32-S3 supports USB Host via ESP-IDF (community Arduino lib: `esp32beans/ESP32_USB_Host_HID`, 97 stars). See `references/usb-host-relay.md` for the USB Host relay architecture.
- **GPIO43,44:** UART TX/RX (serial debug)
- **GPIO48:** built-in WS2812B RGB LED

### Key matrix GPIO math
- 104-key full size: ~6 rows × 18 cols = **24 pins** (needs expanders on XIAO)
- 40-key split half: ~5 rows × 8 cols = **13 pins** (XIAO needs 1 I2C expander)
- 30-key gamepad: ~5 rows × 6 cols = **11 pins** (fits XIAO exactly)

### I2C GPIO expander
`PCF8574` — $0.50, adds 8 GPIO via I2C (uses SDA + SCL = 2 pins). Stack two for 16 extra pins.

## Project Architecture: GK300 Keyboard Mod

### Plan A: USB Host Relay (no keyboard modification)
**User's preferred approach — zero teardown required.** Taps the existing 2.4GHz dongle's USB output.

```
GK300 ──2.4GHz──→ GameSir Dongle ──USB (soldered to XIAO pads)──→ XIAO S3 (USB Host)
                                                                    │
                                                                ESP-NOW
                                                                    │
                                                            ESP32 DevKit (USB HID) ──→ PC
```

- XIAO S3 reads HID data from dongle via USB Host (needs `ESP32_USB_Host_HID` library)
- ESP-NOW relays keystrokes to a second ESP32 board
- Second board shows up as USB HID keyboard on PC
- **Requires TWO boards** — XIAO S3 can't be USB Host AND USB HID simultaneously
- XIAO S3's castellated pads on the bottom break out USB D+/D- (GPIO19/20), 5V, GND — solder directly to dongle's USB lines, no connector needed

### Plan B: Inside-keyboard mod (original approach)
DevKit goes inside the keyboard, scans the key matrix, sends over ESP-NOW.

```
┌──────────────────────┐         ┌──────────────────┐
│ ESP32-D0WD-V3        │ ESP-NOW │ XIAO ESP32-S3    │
│ - Key matrix scanning│────────→│ - ESP-NOW receive │
│ - LED control        │ <5ms    │ - USB HID output  │
│ - 30+ GPIO           │         │ - Native USB OTG  │
│ - Wireless sender    │         │ - 11 GPIO (unused)│
└──────────────────────┘         └───────┬──────────┘
                                         │
                                    USB-C to PC
                                    PC sees: 🖨 Keyboard
```

- Requires opening the keyboard, mapping the matrix, soldering inside
- **No wired mode** — DevKit lacks native USB
- **XIAO is native USB HID** — NOT Bluetooth. PC sees a physical keyboard device
- **~5ms latency** via ESP-NOW — suitable for gaming

### ⚠️ Pitfall: XIAO S3 USB dual-role limitation
The XIAO S3's USB pins (GPIO18-21) can only function as **one** USB role at a time — Host OR Device, not both. For the relay architecture, this means you MUST use two separate boards. One board with USB Host reads from the dongle; a different board with USB HID outputs to the PC. Do not attempt to use one XIAO for both roles.

## ESP-NOW Wireless Keyboard Pattern

```
LEFT HALF ──ESP-NOW──→ RIGHT HALF ──USB──→ PC
(scans matrix)         (scans matrix, merges, outputs HID)
```
- Latency: ~5ms
- No router needed — direct peer-to-peer
- Both halves scan their own matrix, right half merges and outputs as USB HID

## Piezo Motor Driving (ESP32 + High Voltage)

Piezo motors need 20-200V, far beyond ESP32's 3.3V GPIO. ESP32 generates timing signals; a separate driver board amplifies.

### CrossFixx ultrasonic piezo (Xeryon)
- Runs at **20-48V** (battery-compatible!) vs traditional 100-200V
- 166kHz resonant — silent, low wear, 100x longer lifetime
- 2-phase sinusoidal drive: ESP32 PWM → MOSFET H-bridge → high voltage
- Speeds up to 1000mm/s
- 4 electrodes (diagonal pairs = 2 phases) + 1 common ground
- Phase ±90° controls direction; amplitude controls speed

### Stepping piezo (walking motor)
- 3+ piezo actuators: 2 clamping, 1 pushing
- Cycle: clamp A → extend C (push) → clamp B → retract C → repeat
- Closest to actin-myosin cross-bridge cycling (grab → pull → release → reset)
- Slow (<10mm/s) but precise and high force

### Biomimetic actuator comparison
| Technology | Strain | Speed | Drive Voltage | ESP32 compatible? |
|---|---|---|---|---|
| Ultrasonic piezo | 0.1% | Very fast | 20-200V | Need HV driver |
| CrossFixx piezo | 0.1% | Very fast | 20-48V | ✅ MOSFET H-bridge |
| Stepping piezo | 0.1% | Slow | 50-200V | Need HV driver |
| SMA (Nitinol wire) | 3-8% | Slow | Low (current) | ✅ MOSFET |
| McKibben pneumatic | 20-40% | Medium | Air pressure | ✅ Solenoid valve |

## Flash Partition Addresses (ESP32)
| Component | Address |
|-----------|---------|
| Bootloader | 0x1000 |
| Partition table | 0x8000 |
| OTA data / boot selector | 0xe000 |
| Application | 0x10000 |

Use `PartitionScheme=huge_app` for maximum app space (~3MB).
