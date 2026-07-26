# Reference Clip Replacement Workflow

When the user wants to trim/replace the reference clip, follow this exact sequence:

## Iterative Trimming (User-Guided)

When the user says "trim the first/last X seconds", follow this loop:

1. Trim with ffmpeg
2. Send the trimmed clip to user (MEDIA: tag only, no text)
3. Wait for user feedback — they may want more/less trimmed
4. Repeat until user says "replace everywhere"
5. Then do the full replacement workflow below

User typically trims in small increments (0.2-0.5s at a time) to find the sweet spot.

## Step 1: Trim the audio

```bash
# Trim from start only (preferred — less risk to prosody)
ffmpeg -y -i old_clip.wav -ss <seconds_to_skip> new_clip.wav

# Trim from end only
ffmpeg -y -i old_clip.wav -t <new_duration> new_clip.wav

# Trim from both ends
ffmpeg -y -i old_clip.wav -ss <start_trim> -t <new_duration> new_clip.wav

# Verify duration
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 new_clip.wav
```

**Rules:**
- Never trim below 7.5s — prosody degrades
- Prefer trimming from one end only
- If trimming from both ends, keep total removal under 1.5s

## Step 2: Generate ICL files

```bash
cd /home/h2
~/qwentts.cpp/build/qwen-codec \
    --model ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --talker ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    -i marshall-voice/selected/new_clip.wav
# Creates new_clip.rvq + new_clip.spk
```

**Pitfall:** `qwen-codec` uses `--model` for codec GGUF and `--talker` for talker GGUF. There is NO `--codec` flag on `qwen-codec`.

## Step 3: Verify transcript with Whisper (MANDATORY)

**Trimming changes what words are in the clip.** Removing the first second may cut off the first word. Removing from the end may cut off the last word. ALWAYS run Whisper on the trimmed clip to get the accurate transcript.

```bash
source ~/qwen3-tts-env/bin/activate
CUDA_VISIBLE_DEVICES="" ~/qwen3-tts-env/bin/whisper new_clip.wav \
    --model base --language en --output_format txt --output_dir /tmp/whisper_verify
cat /tmp/whisper_verify/new_clip.txt
```

Then use that exact text for the .txt file:

```bash
cat /tmp/whisper_verify/new_clip.txt > marshall-voice/selected/new_clip.txt
```

**Pitfall:** If the transcript doesn't match the audio, the ICL mode produces gibberish. The model tries to match the speech patterns to the transcript, and a mismatch makes it sound tongue-tied.

## Step 4: Update tts-provider.sh

```bash
sed -i 's|clip_old_name\.rvq|new_clip.rvq|g; s|clip_old_name\.spk|new_clip.spk|g; s|clip_old_name\.txt|new_clip.txt|g' ~/marshall-voice/tts-provider.sh
```

Or use the patch tool to replace the three --ref-rvq/--ref-spk/--ref-text lines.

## Step 5: Test

```bash
echo "Test text to verify the new clip works." > /tmp/test_new.txt
> /tmp/tts-provider.log
~/marshall-voice/tts-provider.sh /tmp/test_new.txt /tmp/test_new.mp3 2>&1 | tail -3
grep -E "Chunk|Done|ERROR" /tmp/tts-provider.log
```

## Step 6: Push and update memory

```bash
cd /home/h2/.hermes-Cuso && cp ~/marshall-voice/tts-provider.sh . && git add -A && git commit -m "TTS: replace reference clip with new_clip" && git push
```

Update memory with new clip name.
