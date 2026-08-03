# Mel — ESP32 taste-learning radio (A2DP + SD + foraging)

Self-feeding music player: plays MP3s from SD over Bluetooth A2DP to earbuds,
learns the listener's taste from listening behavior, and forages Jamendo for
new songs when WiFi is available. It is not a music player — it's a pet.

Repo: `~/mel/` — pushed & PUBLIC at github.com/trojan-lord/mel. Full
blueprint: `~/mel/docs/architecture.md` — this file is the condensed decision
record. Blueprint is **v4**: TWO-TIER brain — 24-dim stats (reflex) +
128-dim CLAP embeddings computed on the PC (understanding); a
**continuous-spectrum taste model** (graded affinity signals, per-track
belief μ/σ, uncertainty-driven bandit selection); and **borrowed
recommender-platform signal design** (session context, duration
normalization, negative cascades, diversity, two-stage funnel, deferred
Thompson sampling, self-taught sequences). No binary like/dislike, no hard
50/30/20 buckets — the user explicitly requested "nothing black and white,
more complex, more sophisticated", then "borrow from YouTube/Instagram/
TikTok" and "make mel teach herself which songs go after which." Model-
selection reasoning (why CLAP, why not Shazam/MERT):
`references/audio-embedding-player.md`. ⚠️ Editing architecture.md (unicode-
heavy): read_file/patch may misdetect it as binary — fix + workaround in the
`unicode-text-editing` skill.

## Decisions that are locked (don't relitigate)
- Brain = ESP32 **classic** (D0WD-V3 DevKit) — user owns one; S3 N16R8 is
  BLE-only, no A2DP (see SKILL.md Bluetooth gotcha). The S3 stays a spare —
  its PSRAM isn't needed, the taste model is tiny.
- Library = microSD in SPI mode: CS=5, SCK=18, MOSI=23, MISO=19, 3.3V.
- Stack: Arduino core v3 + `pschatzmann/ESP32-A2DP` (source) + `libhelix-mp3`.
- FreeRTOS tasks: audio_task on core 0 (decode is the hot path);
  taste/forage/ctrl on core 1.
- **Taste model = continuous spectrum (v3, replaces all binary counters):**
  - Event signal `a ∈ [−1,+1]` per listen: base curve from heard-fraction h
    (steep at front: h 0→0.15 gives −0.9→−0.6; h 0.5→0.97 gives −0.3→+0.3;
    finish ≥0.97 = soft +0.4) + replay-chain bonus (+0.15 each, cap +0.6)
    + explicit love/ban buttons (±1.0, ground truth).
  - Per-track belief: affinity μ (asymmetric EMA — α+ 0.15 slow trust,
    α− 0.35 fast distrust) and confidence σ = 0.9/√(1+0.1·eff_n) where
    eff_n decays with days since last play — old beliefs expire, songs get
    re-explored. Daily decay μ *= 0.98. Q7.8 fixed-point, no floats.
  - Selection = bandit: `score = Σ(w·f)/127 + μ + c·σ + ε·U(−1,1)`.
    Exploration coefficient c adapts to the last-20-events mean signal
    (skipping everything → c rises → Mel gets restless and explores).
    The old 50/30/20 mix EMERGES from this, it is not programmed.
  - Embedding priors: new/foraged tracks seed μ0 = mean affinity of their 10
    nearest embedding neighbors — Mel expects a song before it plays.
- index.bin: 48-byte records (track_id, duration, n_plays, n_updates u8,
  μ int16, last_played, 24 features, path_offset), 4k tracks ≈ 192KB,
  streamed from SD in 4KB pages — classic chip has no PSRAM, never hold full
  index in RAM. σ is derived on the fly, never stored. `events.bin` (ring,
  1000 graded signals) replaces the old play/skip log; taste.bin holds w + c.
- Burial is evidence-based (μ < −0.6 AND n_updates ≥ 5), NOT a 3-strike
  rule; decay lets old burials drift back and get re-explored.
- Foraging: Jamendo API → score candidates with the live model BEFORE download
  (proxy metadata features only) → keep top 5–10 → staging/ → PC sync pass
  (tools/embed.py over WiFi HTTP sync) computes real embeddings, seeds μ0,
  promotes into rotation. Mel plays nothing from staging until embedded.
  Needs free Jamendo client_id; verify `audioformat` params at build time.
- User naming: "mel" = melody, but needs its own name because it's intelligent
  (user names their creations — consistent with their SOUL/embodiment interest).

- **v4 — recommender-platform borrowings (ALL seven added; user picked them):**
  - Session context (§7e): 4 time-of-day buckets × 2 day-type buckets, each a
    24×int8 weight adjustment (144 B in taste.bin), updated at half rate;
    live energy-drift mood match −γ·|energy−ē| (γ≈0.05). "Weekday mornings =
    acoustic, weekend nights = electronic" emerges from the spectrum, no labels.
  - Duration normalization (§7f): completion/replay scaled by
    k_dur = clamp(3/D_min, 0.5, 1.5) — finishing a 2-min song (+0.6) is 3×
    stronger than a 9-min epic (+0.2). Skips unchanged (h-curve handles position).
  - Negative cascades (§7g): a < −0.5 depresses the 10 nearest embedding
    neighbors, μ −= 0.25·|a|·(1−(r−1)/10), per-event cap ≈ −0.6. Mel learns
    the FLAVOR, not the song; runs inside the NN pass, no extra SD reads.
  - Diversity (§7h): score −= λ_g·genre_count[session] − λ_a·artist_count
    (0.15/0.10, int8, reset per session). The mix breathes.
  - Two-stage funnel (§7i): cheap int8 stats pass over all tracks → top 100 →
    full bandit (μ, σ, context, diversity, sequence, embedding similarity
    on ~2 pages only). Room for richer terms later without slowing the loop.
  - Thompson sampling (§7j): DEFERRED — Phase 3.5, optional; needs a fixed-point
    noise table (~256 int16) instead of c·σ. UCB ships in Phase 3 first.
  - Sequence model (§7k) — user's favorite: pairs.bin sparse table,
    1024 × (A u32, B u32, count u16) = 12 KB; records A→B only when both
    earned a ≥ +0.3 with no skip between; evict lowest-count, decay ×0.98/day;
    pick-time bonus λ_seq 0.4 × count(A→B)/max_count(A→*). Mel builds flows —
    playlists that don't exist until she invents them.
  - Build order gained Phase 3.5 (Thompson, optional) and Phase 4.5 (Flows:
    turn on pairs.bin after ~50 h of engaged listening).

## Build order (verify each phase before the next)
1. SD → MP3 → helix decode → A2DP → earbuds (biggest risk; prove the audio path)
2. `tools/feature_extractor.py` (librosa) → index.bin
3. Taste: affinity-signal computation + μ/σ belief + bandit selection +
   embedding priors. Verify: 5s skip slams μ down, replay chain climbs it,
   month-old favorite decays, c rises when everything is skipped.
4. Jamendo foraging loop
5. Polish: buttons (skip/ban/love), LED, boot chime, OLED status

## Risks
- 320kbps CPU headroom on LX6 — fallback: pre-decode to 128kbps.
- TLS to Jamendo needs ~40KB heap — short connections, release before playback.
- Keep SD SPI/DMA traffic off core 0 during playback to avoid audio glitches.
