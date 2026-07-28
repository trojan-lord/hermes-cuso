---
name: discord-media-send
description: "AUTOMATIC TRIGGER: Any time a file needs to be sent to Discord. Uses direct Discord API via curl -- NEVER uses MEDIA: tags."
tags: [discord, media, audio, file]
---

# Discord File Send — Direct API Method

## RULE: ALWAYS use curl to the Discord API. NEVER use MEDIA: tags.

The Hermes MEDIA: tag adapter is broken/unreliable for Discord. It silently drops files. Do not use it.

## How to Send Files

### Step 1: Get credentials from environment

```bash
# Bot token is in ~/.hermes/.env as DISCORD_BOT_TOKEN
TOKEN=$(grep DISCORD_BOT_TOKEN ~/.hermes/.env | cut -d= -f2)
```

### Step 2: Send via curl

```bash
# For audio files (voice memos, music, etc.)
curl -s -X POST \
  "https://discord.com/api/v10/channels/{CHANNEL_ID}/messages" \
  -H "Authorization: Bot $TOKEN" \
  -F "file=@/absolute/path/to/file.ogg;filename=descriptive_name.ogg"
```

For images, the same approach works — just change the filename extension.

### Step 3: Verify it sent

Pipe the response through a quick check:
```bash
| python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Sent! ID: {d[\"id\"]}' if 'id' in d else f'Error: {d}')"
```

## Channel IDs

The primary channel for voice memos:
- Channel: `1526410959772717106`

Use the channel_id from the current conversation context when available.

## Discord File Size Limits
- **Default**: 10 MiB per file
- **Nitro**: Higher limits for subscribers
- Check with `ls -lh` before sending

## Sending Multiple Files

For 2-3 files, send each in a separate curl call.

For 3+ files, concatenate first:
```bash
# Create concat list
cat > /tmp/concat_list.txt << 'EOF'
file '/path/to/part1.ogg'
file '/path/to/part2.ogg'
EOF

# Concatenate
ffmpeg -y -f concat -safe 0 -i /tmp/concat_list.txt -c copy /path/to/combined.ogg

# Send combined file
curl -s -X POST "https://discord.com/api/v10/channels/{CHANNEL_ID}/messages" \
  -H "Authorization: Bot $TOKEN" \
  -F "file=@/path/to/combined.ogg;filename=combined.ogg"
```

## Voice Message Format (Optional)

To send as a Discord voice message (with waveform UI), add the flags payload:
```bash
-F "payload_json={\"flags\": 8192}"
```
Note: Voice message format requires waveform/duration metadata. If you get error 50161, just send as a regular attachment (omit the payload_json).

## Pitfalls
- **NEVER use MEDIA: tags.** They silently drop files on Discord.
- **Always use the bot token from ~/.hermes/.env**, not hardcoded tokens.
- **Check file size before sending.** Over 10MB may fail.
- **Use descriptive filenames** — they show in Discord.
