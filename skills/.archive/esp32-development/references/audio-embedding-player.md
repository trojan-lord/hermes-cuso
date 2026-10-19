# Audio-Understanding Player on ESP32 (Mel blueprint)

Architecture for a self-feeding BT music player: plays to earbuds via A2DP,
learns the listener's taste on-chip, and forages for new songs over WiFi.
Proven design discussion from the Mel project (user repo: trojan-lord/mel,
public; full spec in `~/mel/docs/architecture.md`).

## Two-tier music understanding

| Tier | What | Where it runs | Cost |
|---|---|---|---|
| 1. Stats (24 × int8) | BPM, energy, valence, danceability, acousticness, instrumentalness, liveness, speechiness, mode, key, artist hash, genre bits | On-chip, instant | 192KB on SD @ 4k tracks |
| 2. Embedding (128 × int8) | CLAP embedding of the actual audio | PC batch pass, streamed from SD | 512KB on SD @ 4k tracks |

Stats = the reflex layer (fast scoring, daily mix). Embeddings = the
understanding layer ("what you loved is closest to these 5 tracks").
The stats say *what* the song is; the embeddings say *why* you like it.

## Model selection for music similarity — the "Shazam trap"

- **Chromaprint / Shazam fingerprints: WRONG TOOL.** They're noise-robust
  hashes built to answer *"which song is this?"* — no similarity metric
  between different songs. An ID card, not a personality profile. Never
  use for taste/recommendation.
- **CLAP** (LAION Contrastive Language-Audio Pretraining, ~85M params):
  audio **and text** in the same embedding space — a song can be scored
  against a *description* ("melancholy acoustic, female vocals"). Best for
  foraging against metadata-poor catalogs (Jamendo). Choice for Mel.
- **MERT** (music-specific transformer, 95M): best pure audio structure,
  no text side. Backup option.
- Neither runs on a 240MHz/520KB chip. Compute embeddings once per track
  on the PC (1650 Ti: ~10–20 min for 4k tracks, fp16 small batches; CPU
  overnight as fallback), PCA-compress to 128 dims, int8-quantize.

## On-chip taste model (fits 520KB SRAM, no floats)

```
score(t) = Σ(w[i] · f[t][i]) / 127 + b[t]    # Q7.8 fixed point
```
- `w` = 24 × int8 taste weights; `f[t]` = track stats; `b[t]` = per-track
  int16 affinity bias. Weights ARE the taste — learned online, no training
  runs, no cloud.
- Updates: play ≥30s → `w += 0.02·f`, `b += 1` (cap 100); skip <15s →
  `w -= 0.03·f`, `b -= 2` (floor −50); daily decay `b *= 0.98`, `w *= 0.995`.
- Selection mix (the "radio accustomed to taste"):
  - 50% top-10 scored among played tracks (exact favorites)
  - 30% embedding nearest-neighbors to last-liked track (similar)
  - 20% genre pool, lowest play_count (new)
  - Hard rule: no repeat within last 10 plays.
- Embedding nearest-neighbor: stream embeddings.bin in 8KB pages from SD,
  int8 dot-product vs seed, keep top-K. ~64 page reads = sub-second, run
  between songs, never during playback.

## Foraging loop (self-feeding library)

1. On boot, connect to known SSID if present, else retry every 30 min.
2. Jamendo API (CC-licensed, legal; free `client_id`):
   `tracks/?tags=<top-2-genres>&limit=50&audioformat=mp32&client_id=...`
3. **Pre-filter candidates ON DEVICE before downloading** — score with the
   current model using metadata as proxy features. Keep top 5–10. Don't
   waste bandwidth/SD on skips.
4. Download MP3 → `staging/`, mark embedding pending.
5. PC sync pass (plug-in or WiFi HTTP sync): compute real embeddings for
   staged tracks, promote to rotation. **Never play un-embedded tracks** —
   keeps the "soul" honest.
6. Skipped 3× in a row → delisted (bias floor).

## index.bin format (streamed from SD in 4KB pages — never hold in RAM)

Header 32B: magic `MELX`, version, record size (48), n_tracks, flags.
Record 48B: track_id u32, duration_s u32, play_count u32, skip_count u32,
last_played_unix u32, 24×int8 stats, path_offset u32 (string table at EOF).
Per-track bias: separate int16 array appended after string table (rewritten
in place). embeddings.bin: sibling file, same row order, 128×int8/track.

## Build order (de-risk)

0. **PC embedding pipeline FIRST** (CLAP → PCA 128 → int8 → embeddings.bin) —
   the device is born with a soul.
1. SD → MP3 decode → A2DP source → earbuds (biggest risk: verify no stutter,
   check CPU headroom; fallback pre-decode to 128kbps).
2. Index + embeddings load on device ("I know 4,000 songs").
3. Taste model + selection mix + skip detection (watch weights move).
4. Foraging + PC sync pass.
5. Polish (buttons: skip/ban/love, LED, boot chime).

## Pitfalls

- MP3 decode + A2DP on one LX6 core is proven but verify at 320kbps.
- SRAM budget (~320KB usable): decode ~60KB, WiFi ~50KB (only while
  foraging), A2DP ~10KB, scoring scratch ~8KB. Never hold full index in RAM.
- mbedTLS to Jamendo needs ~40KB heap — keep connections short, release
  before playback starts.
- Jamendo `audioformat` values differ (32kbps preview vs full-quality mp3
  URLs) — verify at build time.
