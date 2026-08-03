# Mel — ESP32 taste-learning radio (A2DP + SD + foraging)

Self-feeding music player: plays MP3s from SD over Bluetooth A2DP to earbuds,
learns the listener's taste from plays/skips, and forages Jamendo for new
songs when WiFi is available. It is not a music player — it's a pet.

Repo: `~/mel/` (git-init'd locally, NOT pushed). Full blueprint:
`~/mel/docs/architecture.md` — this file is the condensed decision record.

## Decisions that are locked (don't relitigate)
- Brain = ESP32 **classic** (D0WD-V3 DevKit) — user owns one; S3 N16R8 is
  BLE-only, no A2DP (see SKILL.md Bluetooth gotcha). The S3 stays a spare —
  its PSRAM isn't needed, the taste model is tiny.
- Library = microSD in SPI mode: CS=5, SCK=18, MOSI=23, MISO=19, 3.3V.
- Stack: Arduino core v3 + `pschatzmann/ESP32-A2DP` (source) + `libhelix-mp3`.
- FreeRTOS tasks: audio_task on core 0 (decode is the hot path);
  taste/forage/ctrl on core 1.
- Taste model = 24 × int8 feature dims + per-track int16 bias. Online updates:
  play ≥30s → w += 0.02·f, b += 1 (cap 100); skip <15s → w −= 0.03·f, b −= 2
  (floor −50); daily decay b *= 0.98, w *= 0.995. Fixed-point Q7.8, no floats.
  The weights ARE the taste.
- Selection mix: 50% top-scored favorites / 30% nearest-neighbor to last-liked
  track / 20% lowest-played in top genre; no repeat within last 10 plays.
- index.bin: 48-byte records (features + counts), 4k tracks ≈ 192KB, streamed
  from SD in 4KB pages — classic chip has no PSRAM, never hold full index in RAM.
- Foraging: Jamendo API → score candidates with the live model BEFORE download
  → keep top 5–10 → staging/ → sharpen features from first ~20s during idle CPU.
  Needs free Jamendo client_id; verify `audioformat` params at build time.
- User naming: "mel" = melody, but needs its own name because it's intelligent
  (user names their creations — consistent with their SOUL/embodiment interest).

## Build order (verify each phase before the next)
1. SD → MP3 → helix decode → A2DP → earbuds (biggest risk; prove the audio path)
2. `tools/feature_extractor.py` (librosa) → index.bin
3. Taste model + 50/30/20 mix + skip detection
4. Jamendo foraging loop
5. Polish: buttons (skip/ban/love), LED, boot chime, OLED status

## Risks
- 320kbps CPU headroom on LX6 — fallback: pre-decode to 128kbps.
- TLS to Jamendo needs ~40KB heap — short connections, release before playback.
- Keep SD SPI/DMA traffic off core 0 during playback to avoid audio glitches.
