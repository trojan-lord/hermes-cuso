# Pinecil V2 Flash Session — 2026-07-26

## Device Info (from dmesg)
```
usb 1-1: new full-speed USB device number 5 using xhci_hcd
usb 1-1: New USB device found, idVendor=ffff, idProduct=ffff, bcdDevice= 2.00
usb 1-1: Product: CDC Virtual ComPort
usb 1-1: Manufacturer: BLIOT
usb 1-1: SerialNumber: 000000020000
cdc_acm 1-1:1.0: ttyACM0: USB ACM device
```

## Firmware Details
- **Version:** IronOS v2.23 (published 2025-08-31)
- **File:** Pinecilv2_EN.bin (194508 bytes)
- **MD5:** 06de5f46fdc198e82bc0059d31df0bb1
- **Download URL:** https://github.com/Ralim/IronOS/releases/download/v2.23/Pinecilv2.zip
- **blisp version:** v0.0.5 (cachyos-extra-v3)

## Flash Command Used
```bash
sudo blisp write -c bl70x --reset ~/pinecil-update/firmware/Pinecilv2_EN.bin
```

## Flash Output (success)
```
Testing if we can skip the handshake...
Failed to receive response, ret: 0
We can't; ignore the previous error.
Sending a handshake...
Received incorrect handshake response from chip (attempt 1/5).
Could not find 0x4F 0x4B ('O', 'K') in:
Handshake successful!
Getting chip info...
BootROM version 1.0.2.7, ChipID: 00008785D8FDD7C4
[... progress 0-100% ...]
Sending a handshake...
Received incorrect handshake response from chip (attempt 1/5).
Could not find 0x4F 0x4B ('O', 'K') in:
Handshake with eflash_loader successful.
Input file identified as a .bin file
Erasing flash to flash boot header
Flashing boot header...
Erasing flash for firmware, this might take a while...
Flashing the firmware 194508 bytes @ 0x00002000...
[... progress 0-100% ...]
Checking program...
Program OK!
Resetting the chip.
Flash complete!
```

## Notes
- Handshake warnings ("Received incorrect handshake response") are normal — blisp retries automatically
- Flash took ~2 minutes total
- Chip ID: 00008785D8FDD7C4, BootROM: 1.0.2.7
- The iron rebooted automatically after `--reset` flag
