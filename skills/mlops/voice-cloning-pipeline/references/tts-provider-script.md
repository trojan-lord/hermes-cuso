# TTS Provider Script — Production Reference

## Current Production Script

Location: `~/marshall-voice/tts-provider.sh`

Uses ICL mode (ref-rvq + ref-spk + ref-text) with clip_07_trimmed_start as the reference.
1.7B Q8_0 model for both speaker embedding and TTS generation.
Splits text at ALL punctuation: `.`, `!`, `?`, `;`, `—`, `,`, `…`.
Each punctuation type has a different pause duration (0.3s–0.8s).
Chunks merged if under 350 chars. LAST punctuation of chunk determines pause.
Final output 4% slower via ffmpeg atempo=0.96.

**CRITICAL: Use `echo |` pipe, NOT `<<<` heredoc.** Bash escapes apostrophes in heredocs, causing TTS crash.

## How Splitting Works

The Python splitter breaks text at ALL punctuation: `.`, `!`, `?`, `;`, `—`, `,`, `…`.
Each punctuation type has a different pause duration (see header comment in script).
Short sentences are merged into chunks under MAX_CHARS (350).
The LAST punctuation mark of each chunk determines its pause duration.

Example: "The mushroom heals everything, and I mean everything." → splits at comma (0.3s) then period (0.8s)
Example: "It works; we can keep tweaking." → splits at semicolon (0.5s) then period (0.8s)

## Hermes Config

```yaml
tts:
  provider: marshall
  providers:
    marshall:
      type: command
      command: "/home/h2/marshall-voice/tts-provider.sh {input_path} {output_path}"
      output_format: ogg       # Required: Hermes passes .ogg path to provider
      voice_compatible: true   # Required: emits [[audio_as_voice]] for voice delivery
      max_text_length: 2000
```

## Reference Clip

### clip_07_trimmed_start (8.0s) — CURRENT PRODUCTION REFERENCE
- Duration: 8.0 seconds (first 1s trimmed from original clip_07)
- Transcript: "Do you think there's any way you could get me something called tetrodotoxin? It's extracted from pufferfish and I would"
- Source: G2qRtRn5XcA (Marshall Survives The Assassin), ~232-240s
- Files: `~/marshall-voice/selected/clip_07_trimmed_start.{wav,rvq,spk,txt}`
- **ACTIVE in tts-provider.sh** — switched from clip_07_trimmed_precise on 2026-07-17
- Transcript verified with Whisper, ICL files re-extracted same day

### clip_07_trimmed_precise (7.7s) — BACKUP
- Duration: 7.7 seconds (first 1s + last 0.3s removed)
- Transcript: "Do you think there's any way you could get me something called tetrodotoxin, it's extracted from pufferfish and"
- Files: `~/marshall-voice/selected/clip_07_trimmed_precise.{wav,rvq,spk,txt}`

### clip_07 (9.0s) — BACKUP (full original clip)
- Duration: 9.0 seconds (untrimmed, starts with "Listen,")
- Transcript: "Listen, do you think there's any way you could get me something called tetrodotoxin? It's extracted from pufferfish and I would"
- Files: `~/marshall-voice/selected/clip_07.{wav,rvq,spk,txt}`

### Why clip_07_trimmed_start over clip_07_trimmed_precise
- 8.0s vs 7.7s — more voice pattern data for the model
- Ends at a more natural point ("and I would" — trailing off) vs the old clip's abrupt "and..."
- clip_07_trimmed_precise had transcript mismatch: .txt said "pufferfish, and..." but audio actually said "pufferfish and" (no comma, no ellipsis). ICL mode uses text-audio alignment — wrong transcript = learning from misaligned data.
- clip_07 (9s) includes "Listen," at start which is characteristic Marshall speech, but the extra 1s at the start may include a breath/mic artifact

### Post-Setup Cleanup
Keep: `audio/` (original source WAVs), `selected/` (active reference + backups), `tts-provider.sh`.
Delete everything else.

## Troubleshooting

- **Speech sounds rushed:** Increase silence between chunks. Do NOT use sox tempo — it sounds artificial. Write prompts with commas and periods for natural breaks.
- **Gibberish output:** Wrong transcript — ICL mode needs exact words from reference audio. ALWAYS verify transcript with Whisper after any clip change. Transcript mismatch (even comma/ellipsis differences) causes the model to learn from misaligned data.
- **Wrong voice:** Check that config key is lowercase "marshall" not "Marshall"
- **Bash heredoc crash:** Use `echo "$VAR" |` pipe, NOT `<<< "$VAR"` heredoc. Bash escapes apostrophes in heredocs, corrupting text and crashing TTS.
- **Discord MEDIA: tag silently dropped:** Respond with ONLY the `MEDIA:<path>` tag — no accompanying text.
- **Discord voice message not delivered (MP3 format):** Discord's send_voice wraps audio as `voice-message.ogg` with content_type `audio/ogg`. If actual data is MP3, Discord rejects it silently. Fix: output OGG/Opus from provider (`codec:a libopus`), set `output_format: ogg` and `voice_compatible: true` in config. Gateway logs `response_delivery_dropped` when this happens.
- **TTS provider exits code 1 (Invalid audio stream):** Happens when Hermes passes `.mp3` output path but provider uses libopus codec. FFmpeg can't write Opus into MP3 container. Fix: set `output_format: ogg` in config so Hermes passes `.ogg` path.
- **ICL transcript mismatch:** If the .txt file doesn't match what the audio actually says (even punctuation differences like "and..." vs "and"), the model learns from misaligned data. Run Whisper on the exact clip and use that output verbatim. Punctuation in the transcript matters because ICL aligns text tokens to audio frames.
- **VRAM contention:** Other GPU applications (Dota 2, browsers with GPU accel, etc.) can eat VRAM needed for TTS. Check `nvidia-smi` before debugging TTS failures.
- **Rollback when broken:** If changes break TTS, `git checkout <last-working-commit> -- tts-provider.sh` to revert. Don't try to fix forward — revert first.
- **Q4_K_M segfaults on GTX 1650 Ti:** The 1.7B Q4_K_M model crashes with a segfault. Use Q8_0 instead.
- **tts-server OOM on 4GB:** Keeps model loaded but no room for codec decode. CLI per-chunk is the only viable approach on 4GB VRAM. Also causes CUDA memory fragmentation.
- **stream-by-line OOM on 4GB:** Allocates additional KV cache per line, exceeding 4GB.
- **Sending multiple audio files to Discord:** Concatenate with ffmpeg into one file, send as single MEDIA: tag. See discord-media-send skill.
