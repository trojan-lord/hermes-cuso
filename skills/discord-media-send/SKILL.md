---
name: discord-media-send
description: "AUTOMATIC TRIGGER: Any time a MEDIA: tag appears in the response. Prevents Discord file drops."
tags: [discord, media, audio]
---

# Discord Media Send Rule — CRITICAL

When sending a file to Discord using `MEDIA:/path/to/file`:

## RULE: Your ENTIRE response must be ONLY the MEDIA: tag. Nothing else. Period.

- NO text before the MEDIA: tag
- NO text after the MEDIA: tag
- NO explanation, NO context, NO "here you go"
- Your response = exactly `MEDIA:/absolute/path/to/file`

## Why?
Discord drops the file silently if ANY text appears alongside the MEDIA: tag. The file was generated correctly, but the Discord adapter discards it.

## Discord File Size Limits (per-file)
- **Default**: 10 MiB per file for all users
- **Higher with Nitro**: Nitro subscribers and boosted servers get larger limits
- **Bot uploads**: same per-file limit applies; the API rejects (not silently drops) oversized files
- If a file exceeds the limit, the API returns an error — always check `ls -lh` before sending

## How It Works Internally
The Hermes Discord adapter delivers MEDIA: files in two stages:
1. **Streaming phase**: Text is sent via `channel.send(content=...)`. The `MEDIA:` tag is stripped from visible text by `stream_consumer._clean_for_display()`.
2. **Post-stream phase**: `_deliver_media_from_response()` in `gateway/run.py` extracts MEDIA: tags from the original response text, then routes files by type: images → `send_multiple_images()` (batches up to 10 per message), audio → `send_voice()`, everything else → `send_document()` / `_send_file_attachment()`.

The `send_voice()` method attempts native Discord voice message format first (flags=8192, `.ogg` files get waveform/duration), falling back to regular file attachment.

See [references/discord-api-file-limits.md](references/discord-api-file-limits.md) for Discord API source-of-truth details.

## Sending Multiple Audio Files

### Option A: Separate responses (simple, for 2–3 files)
Send each as its own turn with ONLY a MEDIA: tag:

Turn 1: `MEDIA:/path/to/part1.mp3`
Turn 2: `MEDIA:/path/to/part2.mp3`

### Option B: Concatenate into one file (recommended for 3+ files)
Combine all MP3s into a single file before sending. This avoids multiple turns and stays under size limits more easily.

```bash
# 1. Create a concat list file
cat > /tmp/concat_list.txt << 'EOF'
file '/home/h2/audio/part1.mp3'
file '/home/h2/audio/part2.mp3'
file '/home/h2/audio/part3.mp3'
EOF

# 2. Concatenate with ffmpeg
ffmpeg -y -f concat -safe 0 -i /tmp/concat_list.txt -c copy /home/h2/audio/combined.mp3

# 3. Check size before sending
ls -lh /home/h2/audio/combined.mp3

# 4. Send as single MEDIA: tag
MEDIA:/home/h2/audio/combined.mp3
```

**Important**: All input files must have the same codec, sample rate, and channel count for `-c copy` (stream copy) to work. If they differ, re-encode:

```bash
ffmpeg -y -f concat -safe 0 -i /tmp/concat_list.txt \
  -ar 44100 -ac 2 -codec:a libmp3lame -b:a 192k /home/h2/audio/combined.mp3
```

## Downloadable Files

**User preference: send MP3 directly by default. Only zip when user explicitly asks for a downloadable version.** Do NOT preemptively zip files — the user finds it annoying when they just want to listen inline.

When user asks for a downloadable version:
1. Zip the file: `zip output.zip input.mp3`
2. Send the zip: `MEDIA:/path/to/output.zip`
3. Zip forces Discord to offer a download — MP3s sometimes play inline instead.

## Best Practices
- **Always check file size** (`ls -lh`) before sending to Discord
- **Prefer concatenation** over sending 3+ separate files — cleaner UX, fewer turns
- **Keep total size under 25 MB** for reliability across all server types
- **Use `-c copy` first** (fast, lossless); fall back to re-encoding only if codecs differ
- **Clean up temp files** (`/tmp/concat_list.txt`, intermediate audio) after sending
- **Name output files descriptively** — the filename shows in Discord (e.g., `song_full.mp3`, not `combined.mp3`)

## Example
✅ Response: `MEDIA:/home/h2/.hermes/cache/audio/tts_20260714_043025.mp3`
✅ Response (after concatenation): `MEDIA:/home/h2/audio/song_full.mp3`
❌ Response: `Here's the audio: MEDIA:/path/to/file.mp3`
❌ Response: `MEDIA:/path/to/file.mp3 — let me know how it sounds`

## Pitfalls
- **THE #1 MISTAKE: Text alongside MEDIA: tag.** This is the most common and most costly error. Even a single word before or after the MEDIA: tag causes Discord to drop the file silently. The file was generated, the cost was paid, but the user never sees it. If you catch yourself writing ANYTHING other than the bare MEDIA: tag in a message that contains one, DELETE the text before sending.
- **Multiple MEDIA: tags in one message.** Only the last one gets delivered. Use separate messages for separate files, or concatenate into one file with ffmpeg.
- **Forgetting to concatenate multi-part audio.** When generating 3+ parts of a voice memo, always concatenate with ffmpeg into one file before sending. See the concatenation recipe above.
