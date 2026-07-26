---
name: esp32-hardware-testing
description: "ESP32 development — board diagnostics, firmware compilation/flashing, captive portal development, AP mode, ESP-NOW patterns. Load when user asks to test, diagnose, flash, or build web interfaces on an ESP32."
tags: [esp32, embedded, hardware, iot, serial]
globs: ["*.ino", "*.cpp", "platformio.ini", "*.bin"]
---

# ESP32 Development, Testing & Diagnostics

Covers board diagnostics, firmware compilation/flashing, captive portal development, AP mode, and ESP-NOW patterns.

## CRITICAL: WiFi Connectivity Rule

**NEVER connect the host machine to the ESP32's WiFi AP.** When the ESP32 runs in AP mode (e.g. captive portal), connecting the host to that AP disconnects it from the internet and kills all services (Discord, AI assistant, etc).

**正确的做法:** Test the ESP32 AP/captive portal from a *separate device* (phone, tablet, another laptop). The host machine stays on its home WiFi.

```bash
# WRONG — this kills your connection
nmcli device wifi connect "ESP32 Keyboard" ifname wlan0

# RIGHT — test from phone instead
# Connect phone to "ESP32 Keyboard" AP, captive portal opens automatically
```

If you accidentally connect: `nmcli device disconnect wlan0` then reconnect to home WiFi.

## Prerequisites Check
Before any work, verify what's available:
```bash
# Serial devices
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
lsusb | grep -i "silicon\|cp210\|ch34\|ftdi\|espressif"

# Existing tools
which esptool esptool.py arduino-cli pio 2>/dev/null
pacman -Qi esptool 2>/dev/null  # Arch packages
```

## esptool Setup (Arch/CachyOS)

PEP 668 prevents direct pip install. Use `uv` venv:
```bash
uv venv /tmp/esp-venv
uv pip install --python /tmp/esp-venv/bin/python esptool
# Binary at: /tmp/esp-venv/bin/esptool
```
**All esptool commands need `sudo`** unless user is in `dialout` group:
```bash
groups h2 | grep -o "dialout\|uucp"
# If missing: sudo usermod -aG dialout h2 (requires re-login)
```

## Board Identification

```bash
sudo /tmp/esp-venv/bin/esptool.py --port /dev/ttyUSB0 chip_id 2>&1
sudo /tmp/esp-venv/bin/esptool.py --port /dev/ttyUSB0 flash_id 2>&1
sudo /tmp/esp-venv/bin/espefuse --port /dev/ttyUSB0 summary 2>&1
```

Key info to capture: chip type/revision, flash size, MAC address, crystal freq, eFuse state.

## Flash Memory Diagnostics

```bash
# Read flash regions to check integrity
for addr in 0x0 0x1000 0x8000 0x10000 0x3FF000; do
    sudo esptool.py --port /dev/ttyUSB0 read_flash $addr 0x100 /tmp/region_${addr}.bin
done
# Analyze: all 0xFF = erased/blank, other content = has firmware
```

Flash map (ESP32 standard):
- `0x0000` — Bootloader
- `0x1000` — Partition table
- `0x8000` — NVS / PHY init data
- `0x10000` — App partition (firmware lives here)
- `0x3FF000` — NVS user data

## Firmware Compilation

### Arduino CLI (preferred for simplicity)
```bash
arduino-cli config add board_manager.additional_urls https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
arduino-cli core update-index
arduino-cli core install esp32:esp32  # SLOW — 500MB+ download, can take 10+ min
arduino-cli compile --fqbn esp32:esp32:esp32 sketch.ino
arduino-cli upload --fqbn esp32:esp32:esp32 --port /dev/ttyUSB0 sketch.ino
```

### PlatformIO (better for projects)
```bash
uv pip install --python /tmp/esp-venv/bin/python platformio
/tmp/esp-venv/bin/pio project init --board esp32dev
# Move sketch to src/main.cpp
/tmp/esp-venv/bin/pio run --target upload
```
**Pitfall:** PlatformIO toolchain download also very slow (xtensa-esp32 toolchain ~400MB). Both Arduino CLI and PlatformIO can timeout on slow connections.

### Pre-compiled MicroPython (fastest path for REPL testing)
```bash
# Download from micropython.org — but URLs change per version
# After flash, use: screen /dev/ttyUSB0 115200
esptool.py --port /dev/ttyUSB0 write_flash -z 0x10000 micropython.bin
```

## Serial Monitor
```bash
# Using screen
screen /dev/ttyUSB0 115200
# Exit: Ctrl+A, then K, then Y

# Using cat (read-only)
timeout 5 sudo cat /dev/ttyUSB0

# Using picocom (if installed)
picocom -b 115200 /dev/ttyUSB0
```

## Deprecation Warnings (esptool v5.x)
The `.py` suffix is deprecated. Use `esptool` not `esptool.py`. Also:
- `chip_id` → `chip-id`
- `flash_id` → `flash-id`
- `read_flash` → `read-flash`
- `erase_flash` → `erase-flash`
- `write_flash` → `write-flash`
- `espefuse` is a separate binary, not a subcommand of esptool

## XIAO ESP32-S3 Specifics

### Factory Test Firmware Detection
XIAO ESP32-S3 boards ship with Seeed's factory test firmware. To identify it:
```bash
/tmp/ss-venv/bin/python3 -m esptool --port /dev/ttyACM0 read_flash 0x10000 0x40000 /tmp/app.bin
strings /tmp/app.bin | grep -iE "arduino-lib-builder|test_passed|seeed|button|wifi|gpio"
```
Signatures: `arduino-lib-builder`, `test_passed`, `Hello from Seeed Studio XIAO ESP32-S3`, `Button PASS`, `WiFi Networks Found`. The bootloader shows `v5.4.1-1-g2f7dcd862a-dirty` and build date.

### Board Info
```bash
/tmp/ss-venv/bin/python3 -m esptool --port /dev/ttyACM0 chip-id   # MAC, chip rev, features
/tmp/ss-venv/bin/python3 -m esptool --port /dev/ttyACM0 flash-id  # 8MB flash, manufacturer, voltage
```
Typical XIAO S3: ESP32-S3R8, rev v0.2, 8MB flash + 8MB PSRAM, 40MHz crystal, USB-Serial/JTAG (CDC). Flash manufacturer: c8 (GigaDevice), device: 4017.

### Permissions: uucp Group
XIAO S3 uses `/dev/ttyACM*` (ACM device) not `/dev/ttyUSB*`. The device is owned by `uucp` group, not `dialout`:
```bash
groups | grep uucp
# If missing: sudo chmod 666 /dev/ttyACM0 /dev/ttyACM1
# Or permanent: sudo usermod -aG uucp h2 (requires re-login)
```

### U.FL Antenna
XIAO ESP32-S3 has **NO onboard chip antenna** — only U.FL (IPEX) connector. WiFi/BT/ESP-NOW all require the external antenna.

**Install:** Hook one side of antenna connector into U.FL block first, then press the other side. **Never press straight down.**

**Remove:** Lift one side at an angle. **Never pull straight up.**

Without antenna: range drops to centimeters, risk of LNA damage from reflected power. Both boards in an ESP-NOW pair need antennas.

### Firmware: Arduino-ESP32
Boots with Arduino-ESP32 firmware (not MicroPython). Partition table shows: `otadata`, `app0`, `app1`, `spiffs`, `coredump`. FQBN: `esp32:esp32:XIAO_ESP32S3:UploadSpeed=921600,USBMode=hwcdc,CDCOnBoot=default,FlashSize=8M,PartitionScheme=default_8MB`.

## Common Pitfalls
1. **Permission denied on /dev/ttyUSB0** — user not in `dialout` group. Use `sudo` or add user to group.
2. **esptool segfault** — GPU process competing for memory (if qwen-codec or similar running). Kill competing process first.
3. **Arduino CLI / PlatformIO timeout** — toolchain download is huge. Run in background with `notify_on_complete=true`.
4. **Crystal freq warning** — "Detected crystal freq 15.55 MHz is quite different to normalized freq 26 MHz" is common on some boards, usually harmless.
5. **Blank flash = normal for new/erased boards** — app partition being all 0xFF means nothing is flashed.
6. **Arduino CLI `upload` fails silently** — needs serial port access. Use esptool directly with `sudo` instead (see flash commands below).
7. **Garbled serial output** — usually baud rate mismatch. Board bootloader outputs at 74880, firmware at 115200. Wait for firmware boot before reading.
8. **Deep sleep disconnects USB serial** — CP210x bridge stays powered but UART goes inactive. Board reconnects after wake. Not a failure.
9. **Captive portal doesn't redirect** — Most common cause: DNS response IP doesn't match the actual AP IP. Verify: (a) `softAPConfig()` called BEFORE `softAP()`, (b) DNS responds with the same IP the AP is using, (c) global `apIP` variable not shadowed by a local declaration. Second most common: `handleNotFound()` doesn't serve the HTML for all paths — captive portal detection URLs vary by OS and must all return the config page.

## Flash Commands (manual with esptool)

When `arduino-cli upload` fails (no serial permissions), flash manually:
```bash
BDIR=$(ls -td ~/.cache/arduino/sketches/*/ | head -1)
sudo /tmp/esp-venv/bin/esptool.py --port /dev/ttyUSB0 --baud 460800 \
  write_flash \
  0x1000 "$BDIR/sketch.ino.bootloader.bin" \
  0x8000 "$BDIR/sketch.ino.partitions.bin" \
  0xe000 "$BDIR/boot_app0.bin" \
  0x10000 "$BDIR/sketch.ino.bin"
```

Flash address layout (huge_app partition):
| Address | Content |
|---------|---------|
| 0x1000 | Bootloader |
| 0x8000 | Partition table |
| 0xe000 | boot_app0 (OTA selector) |
| 0x10000 | Application firmware |

For merged binary (simpler): `write_flash 0x0 sketch.ino.merged.bin`

## Captive Portal Development

### Architecture
- ESP32 runs as WiFi AP (no external WiFi connection)
- Custom DNS server intercepts all queries → responds with AP IP
- HTTP server serves config page + handles captive portal detection
- Client devices auto-open browser when connecting to AP

### softAPConfig Order (CRITICAL)
```cpp
// MUST be in this order — softAPConfig BEFORE softAP
WiFi.mode(WIFI_AP);
WiFi.softAPConfig(apIP, apGateway, apSubnet);  // FIRST
WiFi.softAP(ssid, password);                     // SECOND
```
If reversed, AP uses default 192.168.4.1 regardless of config.

### Custom DNS Server (for captive portal)
DNS must respond to ALL queries with the AP IP. **The ESP32 DNSServer library in Arduino ESP32 core v3.3.10 removed the wildcard `"*"` pattern** — `dnsServer.start(DNS_PORT, "*", apIP)` silently fails or doesn't intercept all queries. Use a custom UDP handler instead:

```cpp
WiFiUDP dnsUdp;
IPAddress apIP(192, 168, 4, 1);

// In setup(): dnsUdp.begin(53);
// In loop(): handleDNS();

void handleDNS() {
  int packetSize = dnsUdp.parsePacket();
  if (!packetSize) return;
  byte buffer[512];
  int len = dnsUdp.read(buffer, sizeof(buffer));
  if (len < 12) return;
  byte response[512];
  memcpy(response, buffer, len);
  response[2] = 0x81;  // QR=1, AA=1
  response[3] = 0x80;  // RA=1, RCODE=0
  response[6] = 0x00; response[7] = 0x01;  // Answer count = 1
  int off = len;
  response[off++]=0xC0; response[off++]=0x0C;  // Name pointer
  response[off++]=0x00; response[off++]=0x01;  // Type A
  response[off++]=0x00; response[off++]=0x01;  // Class IN
  response[off++]=0x00; response[off++]=0x00; response[off++]=0x00; response[off++]=0x3C;  // TTL 60s
  response[off++]=0x00; response[off++]=0x04;  // Data length
  response[off++]=apIP[0]; response[off++]=apIP[1];
  response[off++]=apIP[2]; response[off++]=apIP[3];
  dnsUdp.beginPacket(dnsUdp.remoteIP(), dnsUdp.remotePort());
  dnsUdp.write(response, off);
  dnsUdp.endPacket();
}
```

### Captive Portal Detection URLs (HTTP 404 handler)
Each OS probes different URLs. Respond with 200 + meta refresh for detection URLs, 302 redirect for everything else:

| OS | Detection URL pattern |
|----|----------------------|
| iOS/macOS | `captive.apple.com`, `hotspot-detect.html` |
| Android | `connectivitycheck.gstatic.com`, `generate_204` |
| Windows | `msftconnecttest.com`, `msftncsi.com`, `dns.msftncsi.com` |
| Linux | `connectivity-check.ubuntu.com` |
| General | `example.com`, `detectportal` |

### ESP32 Web Server Size Limits
- 4MB flash with huge_app partition: ~1.5MB for firmware
- 320KB RAM: keep embedded HTML under ~30KB for stability
- Use `PROGMEM` for large HTML strings: `const char PAGE[] PROGMEM = R"rawliteral(...)rawliteral";`
- Use `server.send_P()` to serve PROGMEM content

## ESP-NOW Architecture Patterns

### Wireless Keyboard (Sender → USB HID Receiver)
**Architecture:** Sender board (ESP32) scans key matrix, transmits keystrokes via ESP-NOW to a receiver board (ESP32-S3) plugged into PC via USB. The receiver enumerates as a native USB HID keyboard.

```
Sender (ESP32)                    Receiver (ESP32-S3)
┌──────────────┐    ESP-NOW     ┌──────────────┐
│ Matrix scan  │───────────────→│ ESP-NOW recv  │
│ Row/Col GPIO │   <5ms, ~200m  │ USB HID out   │──→ PC
│ LED control  │                │ Native USB OTG│
└──────────────┘                └──────────────┘
```

**Critical design principles:**
- **No relay/receiver dongle between halves** — adds unnecessary latency and complexity. The receiver board IS the dongle.
- **Native USB HID ≠ Bluetooth** — USB HID makes the PC see a physical keyboard. No pairing, no drivers. ESP32 (original) cannot do this; ESP32-S3 can.
- **Two-board minimum:** ESP32 original has no native USB HID (only CP2102 serial). ESP32-S3 has native USB OTG. Use S3 for receiver, any ESP32 for sender.
- **Split keyboard variant:** Two ESP32-S3 boards — left scans left half, ESP-NOW to right half, right half outputs USB HID to PC. No cable between halves.

### ESP32 Variant Selection for Keyboard Projects

| Board | GPIO | Native USB HID | BT Classic | ESP-NOW | Best Role |
|-------|------|---------------|------------|---------|-----------|
| ESP32-D0WD-V3 | 30+ | ❌ | ✅ | ✅ | Sender (matrix scanning) |
| ESP32-S3 DevKit | 30+ | ✅ | ❌ | ✅ | Receiver or standalone keyboard |
| ESP32-S3 XIAO | 11 | ✅ | ❌ | ✅ | USB dongle (too few GPIO for matrix) |
| ESP32-C3 | 15+ | ✅ | ❌ | ✅ | Budget receiver |

**XIAO ESP32-S3 pinout trap:** Only 11 usable GPIO (GPIO0-10). Flash (GPIO12-17), USB (GPIO18-21), strapping (GPIO11), and module internals (GPIO38-48) are all reserved. No hardware DAC on any pin. For full-size keyboard matrix (~24 pins) need I2C GPIO expander (PCF8574).

### Key Matrix Pin Count
| Keyboard Size | Keys | Matrix | GPIO Needed |
|--------------|------|--------|-------------|
| 40% | 40 | 5×8 | 13 |
| 60% | 61 | 6×11 | 17 |
| TKL | 87 | 6×15 | 21 |
| Full-size | 104 | 6×18 | 24 |

### User Design Preference (from corrections)
- **Don't suggest unnecessary intermediaries** — if a direct A→C path works, don't insert B. User called out ESP32 DevKit as BT dongle relay "stupid idea, uselessly increases latency."
- **Wireless preferred over wired** for keyboard peripherals — one less cable, dedicated receiver dongle is fine.
- **Split keyboard > full-size mod** if starting fresh — cleaner build, better ergonomics, no hacking someone else's PCB.

### GPIO Limitations by Board
| Board | Total GPIO | Usable GPIO | Native USB | Notes |
|-------|-----------|-------------|------------|-------|
| ESP32-D0WD-V3 | 34 | 30+ | ❌ (CP2102 serial only) | Original ESP32, no USB HID |
| ESP32-S3 | 45 | 30+ (DevKitC) / 11 (XIAO) | ✅ | XIAO form factor = limited pins |
| ESP32-C3 | 22 | 15+ | ✅ | Single core RISC-V |
| ESP32-C6 | 30 | 22+ | ❌ | WiFi 6, Thread/Zigbee |

**Key matrix pin requirement:** Full-size keyboard (104 keys) needs ~24 pins (6 rows + 18 cols). XIAO boards need GPIO expanders (PCF8574 via I2C) for full-size.

### Captive Portal Preview Technique
When the ESP32 captive portal can't be tested from the host machine (WiFi connectivity rule), extract the HTML and serve it publicly:
```bash
# Extract HTML from PROGMEM
python3 -c "
import re
with open('sketch.ino') as f: content = f.read()
match = re.search(r'R\"rawliteral\((.*?)\)rawliteral\"', content, re.DOTALL)
if match: open('preview.html','w').write(match.group(1))
"
# Serve via localtunnel
python3 -m http.server 8888 &
npx --yes localtunnel --port 8888
# Share the URL with user for visual preview
```
