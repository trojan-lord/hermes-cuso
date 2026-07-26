# Marshall Cuso Voice Cloning — Session Notes (2026-07-13)

## Source Material
- **Character:** Marshall Cuso from *Common Side Effects* (Adult Swim)
- **Videos downloaded:** 7 clips, ~32.5 minutes total audio
- **Audio format:** 24kHz mono WAV (native Qwen3 format)
- **Location:** `~/marshall-voice/audio/`, `~/marshall-voice/captions/`

## Video IDs
| ID | Title | Duration |
|---|---|---|
| Q4uG1-XQoTE | Marshall Tells Frances About A Secret Miracle Drug | 3:18 |
| k-GKulyZB6E | Marshall Goes To Jail | 2:50 |
| uRh9CyR8UVI | Marshall Tries To Grow Mushrooms | 2:38 |
| yDNvcAKYWlU | Can Mushrooms Cure Dementia? | 4:57 |
| nTVQbulG3Ns | Marshall and Hildy's Relationship | 3:50 |
| _y478zwBIYo | Who's Against Big Pharma? | 10:42 |
| G2qRtRn5XcA | Marshall Survives The Assassin | 4:23 |

## Final Working State

### Files
- `~/marshall-voice/marshall_voice.spk` — speaker embedding (extracted from 33s combined reference)
- `~/marshall-voice/marshall_reference.wav` — 33s source audio (5 stitched clips from user)
- `~/qwen3-clone.sh` — wrapper script (uses Q8_0 + `--codec-chunk-dur 8.0`)
- `~/marshall-voice/tts-provider.sh` — Hermes TTS command provider wrapper
- `~/.hermes/config.yaml` — TTS provider configured as "marshall" (lowercase)

### Models
- `~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf` (2.0 GB)
- `~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf` (244 MB)

### User-Curated Clips (Part 1 only — awaiting Parts 2 & 3)

| Clip | Duration | Source | Source Time |
|---|---|---|---|
| clip_01.wav | 4.0s | G2qRtRn5XcA | 92-96s |
| clip_02.wav | 1.0s | G2qRtRn5XcA | 110-111s |
| clip_03.wav | 12.0s | G2qRtRn5XcA | 158-170s |
| clip_04.wav | 6.0s | G2qRtRn5XcA | 187-193s |
| clip_05.wav | 2.0s | G2qRtRn5XcA | 210-212s |
| clip_06.wav | 8.0s | G2qRtRn5XcA | 221-229s |
| clip_07.wav | 9.0s | G2qRtRn5XcA | 231-240s |
| clip_08.wav | 5.0s | Q4uG1-XQoTE | 1-6s |
| clip_09.wav | 5.0s | Q4uG1-XQoTE | 8-13s |
| clip_10.wav | 3.0s | Q4uG1-XQoTE | 18-21s |

**User stitched 5 clips (33s) → used as final reference.**

## Lessons Learned

- **Concatenate → user listen → timestamps → extract from originals** is the reliable workflow for multi-speaker content.
- **Never trust auto-captions for speaker identification.** They include ALL speakers + background noise.
- **Q4_K_M is worse than 0.6B BF16** for voice cloning despite more params. Q8_0 is the sweet spot.
- **`--codec-chunk-dur 8.0`** is essential for preventing OOM during codec decode.
- **Long text OOM at ~27 seconds output.** Even with `--codec-chunk-dur 8.0`, generating 342 frames (~27s) OOMs. Fix: `max_text_length: 200` in Hermes TTS config. 500 chars → ~27s → OOM. 200 chars → ~10s → fits.
- **ICL mode OOM:** >15s references OOM on 4GB VRAM. Use speaker embedding instead.
- **ref-rvq mode avoids ICL OOM:** Pre-encode reference with `qwen-codec --talker` to get `.rvq` + `.spk`, then use `--ref-rvq` + `--ref-spk` + `--ref-text`. Skips codec encoder entirely. Requires transcript file.
- **ICL mode needs --max-new:** Without it, generates 2048 frames (~164s). Use `--max-new 500` for ~40s max.
- **Whisper base on CPU** works well. Avoid CUDA when GPU is occupied by TTS.
- **Discord bot file limit is 25MB** — compress WAV to MP3 for sharing.
- **jamiepine/voicebox** is a GUI wrapper around Qwen3 TTS — redundant for CLI workflows.
- **Meta VoiceBox** never released code/weights — dead end.
- **VoiceClonePromptItem tensors** are model-family-compatible between 0.6B and 1.7B.
- **Hermes command provider config keys MUST be lowercase.** `_get_provider()` lowercases the name before dict lookup. `providers.Marshall` won't match `"marshall"`. This caused TTS to silently fall through to Edge TTS (generic female voice).
- **Gateway restart cannot run from inside gateway process.** SIGTERM propagates to children. Use tuistory.
- **Hermes config hot-reloads** for most tools — `hermes config set` writes to disk immediately. Gateway restart only needed for config loaded at import time.
- **Reboot via tuistory:** `tuistory launch "sudo reboot" --background -s reboot-system`. `systemctl reboot` and `sudo reboot` are hard-blocked from inside the gateway. tmux is NOT installed — never use it.
- **1.7B preferred over 0.6B for TTS generation** — user A/B tested both and chose 1.7B for better intonation/naturalness.
- **0.6B speaker embedding is 1024-dim, 1.7B is 2048-dim.** Must match model when extracting and generating.
- **Default temp 0.9 preferred over lower settings.** User A/B tested temp 0.9 vs 0.6 on the same brief — preferred default. Lower temp sounded flatter, less expressive.
- **ICL mode transcript accuracy is critical.** Wrong transcript = gibberish (speaker sounds tongue-tied). Clip_07 (9s, "Listen, do you think there's any way you could get me something called tetrodotoxin? It's extracted from pufferfish and I would") is the best ICL reference — longest clean transcript, best prosody transfer. Clip_09 also works but shorter. The stitched 33s reference produced gibberish because the combined transcript didn't match the audio.
- **`--max-new 310`** caps ICL output to ~25 seconds, matching ref-spk output length. Without it, ICL generates 2048 frames (~164s).
- **0.6B Q8_0 GGUF downloaded** to `~/qwentts.cpp/models/qwen-talker-0.6b-base-Q8_0.gguf` (947MB). Available as fallback.
- **Models now stored locally** in `~/qwentts.cpp/models/` — not dependent on HF cache for offline use.
- **Real-time voice chat possible** via `tts-server` binary — OpenAI-compatible HTTP API with voice registry. ~3-5s latency per response.
- **User preference: audio-first responses.** In threads with the cloned voice active, respond with voice memos whenever possible. Text only when necessary (code, long lists, formatting that audio can't convey).
