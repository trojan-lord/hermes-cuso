# USB Host Relay Architecture (GK300 Project)

## Overview
Wireless keyboard relay using ESP32-S3 USB Host capability. Reads HID data from an existing 2.4GHz USB dongle and retransmits via ESP-NOW to a second ESP32 that acts as USB HID on the PC.

## Hardware Requirements
- **XIAO ESP32-S3** (USB Host side — reads from dongle)
- **ESP32 DevKit or second XIAO** (USB HID side — outputs to PC)
- GameSir GK300 + its original 2.4GHz USB dongle
- Soldering iron + thin wire (for tapping dongle USB pads)

## USB Host Library
- **`esp32beans/ESP32_USB_Host_HID`** — 97 stars, Arduino-ready
  - https://github.com/esp32beans/ESP32_USB_Host_HID
  - Port of ESP-IDF USB host HID example to Arduino IDE
  - Last updated: 2 years ago (may need minor fixes for arduino-esp32 v3.1+)
  - Tested on ESP32-BOX-S3 with USB host dock
  - Examples: `hid_host_example` (keyboard), `hid_host_joystick` (gamepad)

## XIAO S3 Castellated Pad Pinout (bottom of board)
The castellated pads on the XIAO S3's bottom break out:
- **5V, 3V3, GND** — power
- **GPIO19 (D+), GPIO20 (D-)** — USB data lines
- **GPIO0-GPIO10** — general purpose
- **GPIO43 (TX), GPIO44 (RX)** — UART serial

For USB Host relay: solder wires from dongle's USB connector (D+, D-, 5V, GND) to the corresponding castellated pads on the XIAO's bottom.

## Wiring
```
GameSir Dongle USB connector    XIAO S3 (bottom pads)
┌─────────────────┐            ┌─────────────────┐
│ VCC (5V) ───────│────────────│── 5V pad        │
│ D-     ───────│────────────│── GPIO20 pad    │
│ D+     ───────│────────────│── GPIO19 pad    │
│ GND    ───────│────────────│── GND pad       │
└─────────────────┘            └─────────────────┘
```

## Firmware Sketch Pattern
1. XIAO S3 (USB Host side):
   - Init USB Host via ESP-IDF USB host library
   - Enumerate connected HID device
   - Parse HID reports (keyboard usage codes)
   - Send key data over ESP-NOW to paired board
   - Serial debug via UART0 (GPIO43/44) since USB port is in Host mode

2. ESP32 (USB HID side):
   - Init as USB HID keyboard device
   - Receive ESP-NOW packets
   - Re-emit as USB HID reports to PC

## Pitfalls
- **USB Host mode disables Serial Console on USB port** — must use UART0 (GPIO43/44) for debug. Set 'USB CDC on Boot: Disabled' in Arduino IDE.
- **Some dongles use non-standard USB descriptors** — may not enumerate as standard HID. Need to test with the actual GameSir dongle.
- **Library may need patches** for arduino-esp32 v3.1+ (was tested on v3.0.0)
- **XIAO S3 USB pins (GPIO18-21) can only be one role** — Host OR Device, never both simultaneously. This is why two boards are required.
- **Power**: the dongle draws power from USB. The XIAO's 5V pad must supply this. XIAO can source ~500mA from USB, which is plenty for a dongle.

## Alternative: SDR Protocol Decode (not recommended)
The GK300's 2.4GHz protocol is proprietary (likely FHSS + GFSK + custom packet format). Decoding it directly would require:
- HackRF One (~₹15-20k) for RF capture
- Weeks of protocol reverse engineering
- Unknown packet structure, encryption, hopping pattern
The USB Host relay avoids all of this by letting the dongle do the RF work.
