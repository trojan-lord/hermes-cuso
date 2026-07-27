---
name: voice-cloning-pipeline
description: "End-to-end voice cloning pipeline: YouTube source acquisition, audio extraction, caption parsing, Qwen3 TTS model setup (GGUF + PyTorch), voice clone prompt creation, and speech generation."
tags: [tts, voice-cloning, qwen3, gguf, youtube, audio-processing, cuda]
related_skills: [model-advisory, linux-cli-toolbox, youtube-content, marshall-speech-patterns]
---

# Voice Cloning Pipeline

Complete workflow for cloning a voice from source audio and generating speech with Qwen3 TTS.

**Trigger:** User wants to clone a voice, set up TTS with voice reference, download audio from YouTube for voice training, or compare TTS model variants.

---

## Hardware Requirements

- NVIDIA GPU with CUDA support
- Check VRAM: `nvidia-smi --query-gpu=name,memory.total --format=csv,noheader`
- Qwen3-TTS 0.6B Q8_0: ~1.5 GB VRAM (fits 4GB+, fastest option)
- Qwen3-TTS 1.7B Q8_0: ~2.3 GB VRAM (fits 4GB+, best quality)
- Qwen3-TTS 1.7B Q4_K_M: ~1.45 GB VRAM (fits 4GB+, best speed/quality tradeoff on bandwidth-limited GPUs)

## Step 1: Install Qwen3 TTS

### PyTorch Path (easier, supports 0.6B natively)

```bash
python3 -m venv ~/qwen3-tts-env
source ~/qwen3-tts-env/bin/activate
pip install -U qwen-tts
sudo pacman -S --noconfirm sox  # required dependency
```

**Pitfall:** The import is `from qwen_tts import Qwen3TTSModel` — NOT `QwenTTS`.
**Pitfall:** `from_pretrained` uses `device_map='cuda:0'` — NOT `device='cuda'`.

### GGUF Path (best for 1.7B on low VRAM)

```bash
# Build qwentts.cpp with CUDA
cd ~
git clone --recurse-submodules https://github.com/ServeurpersoCom/qwentts.cpp.git
cd qwentts.cpp

# Install CUDA toolkit if nvcc not found
sudo pacman -S --noconfirm cuda

# Build
mkdir build && cd build
cmake .. -DGGML_CUDA=ON -DCMAKE_CUDA_COMPILER=/opt/cuda/bin/nvcc
cmake --build . --config Release -j $(nproc)

# Download GGUF models
source ~/qwen3-tts-env/bin/activate
huggingface-cli download Serveurperso/Qwen3-TTS-GGUF \
    qwen-talker-1.7b-base-Q8_0.gguf \
    qwen-tokenizer-12hz-Q4_K_M.gguf \
    --local-dir ~/qwentts.cpp/models
```

**Pitfall:** nvcc is at `/opt/cuda/bin/nvcc` on CachyOS, not `/usr/local/cuda/bin/nvcc`.
**Pitfall:** Build takes ~15-20 minutes with 12 cores (mostly CUDA kernel compilation).

## Step 1b: Vocal Separation with Demucs + Whisper Transcription

Before extracting reference clips from multi-character content (TV shows, movies), run Demucs to separate vocals from background music and sound effects, then Whisper to generate transcripts. This dramatically improves reference clip quality for voice cloning.

### Setup

```bash
python3 -m venv ~/demucs-env
source ~/demucs-env/bin/activate
pip install demucs          # v4.1.0, installs PyTorch + CUDA deps
pip install openai-whisper  # one-time, for transcript generation
```

**Pitfall:** CachyOS (Arch-based) requires a venv -- `pip install` fails with "externally-managed-environment" system-wide.

### Demucs Pitfalls

**Demucs treats a DIRECTORY path as a single audio file.** If you pass `demucs -o out dir/`, it tries to load `dir/` as an audio file and crashes with `LoadAudioError: unsupported feature: core (probe): no suitable format reader found`. Always pass individual files via glob:
```bash
# WRONG — crashes
demucs -n htdemucs --out "$OUT" ~/pipeline/raw/
# CORRECT — expands to individual file paths
cd ~/pipeline/raw && demucs -n htdemucs --out "$OUT" *.mp3 *.wav
```

**Whisper base model produces NaN logits on CUDA with GTX 1650 Ti.** The error is `ValueError: Expected parameter logits ... to satisfy ... but found invalid values: tensor([[nan, nan, nan]], device='cuda:0')`. This is NOT a memory issue -- it happens even with plenty of free VRAM. Fix: always use `device='cpu'` for Whisper on this GPU. CPU is slower (~2-3 min/clip for base model) but reliable.

**Demucs model runs fine on GTX 1650 Ti GPU.** The htdemucs model (~2GB VRAM) processes tracks at ~18 chunks/second on GPU. No CPU offloading needed for this model on 4GB cards.

### Demucs Model Selection

| Model | VRAM | Quality | Notes |
|-------|------|---------|-------|
| htdemucs | ~2 GB | Good | Default. Use `--two-stems vocals` for faster vocal-only separation |
| htdemucs_ft | ~2 GB | Better | Fine-tuned variant, slightly slower |
| htdemucs_6s | ~4 GB | Best | 6-stem separation, tight on 4GB GPU |

**GTX 1650 Ti (4GB):** htdemucs runs fine on GPU (~30-60s per track). htdemucs_6s may need CPU offloading.

### Complete Pipeline Script

```bash
#!/bin/bash
set -e
source ~/demucs-env/bin/activate

PLAYLIST="https://youtube.com/playlist?list=PLAYLIST_ID"
BASE_DIR="$HOME/voice-pipeline"
RAW_DIR="$BASE_DIR/raw"
DEMUCS_DIR="$BASE_DIR/demucs"
TRANSCRIPT_DIR="$BASE_DIR/transcripts"

mkdir -p "$RAW_DIR" "$DEMUCS_DIR" "$TRANSCRIPT_DIR"

# Phase 1: Download all audio
cd "$RAW_DIR"
yt-dlp --flat-playlist --print "%(id)s" "$PLAYLIST" | while read -r VID; do
    [ -f "$RAW_DIR/${VID}.mp3" ] && continue
    yt-dlp -x --audio-format mp3 --audio-quality 0 \
        -o "${VID}.%(ext)s" \
        "https://www.youtube.com/watch?v=${VID}" 2>/dev/null || echo "FAILED: $VID"
done

# Phase 2: Demucs vocal separation (GPU, with CPU fallback)
for f in "$RAW_DIR"/*.mp3; do
    BASENAME=$(basename "$f" .mp3)
    [ -f "$DEMUCS_DIR/htdemucs/$BASENAME/vocals.wav" ] && continue
    echo "Demucs: $BASENAME"
    demucs -n htdemucs --two-stems vocals -o "$DEMUCS_DIR" "$f" 2>/dev/null || {
        echo "GPU failed, trying CPU..."
        demucs -n htdemucs --two-stems vocals -o "$DEMUCS_DIR" -d cpu "$f"
    }
done

# Phase 3: Whisper transcription (CPU -- avoids CUDA NaN on small GPUs)
find "$DEMUCS_DIR" -name "vocals.wav" | while read f; do
    BASENAME=$(basename "$(dirname "$f")")
    [ -f "$TRANSCRIPT_DIR/${BASENAME}.txt" ] && continue
    echo "Whisper: $BASENAME"
    python3 -c "
import whisper
model = whisper.load_model('base', device='cpu')
result = model.transcribe('$f')
with open('$TRANSCRIPT_DIR/${BASENAME}.txt', 'w') as fh:
    fh.write(result['text'])
"
done
```

### Performance (GTX 1650 Ti, 18 tracks)

| Task | Time | Notes |
|------|------|-------|
| Demucs htdemucs (GPU) | ~10 min total | ~30-60s per track |
| Whisper base (CPU) | ~30-40 min total | ~2-3 min per clip |
| Whisper base (CUDA) | FAILS | NaN logits on this GPU |

### After Demucs

Clean vocal tracks are dramatically better for reference clip selection. Use the iterative user-guided extraction workflow (Step 3c) on the separated vocals instead of raw mixed audio. The transcripts help identify which tracks contain the target speaker's lines.

**Demucs output structure:** Files go to `<out>/htdemucs/<track_name>/vocals.wav` -- note the extra `htdemucs/` subdirectory. When scripting post-Demucs operations, account for this nesting.

**Sharing clean vocals on Discord:** Demucs WAV vocals are 50-200MB each. Convert to MP3 for sharing:
```bash
ffmpeg -y -i vocals.wav -b:a 128k vocals_sample.mp3
# 128kbps MP3 brings a 92MB WAV down to ~8MB, well under Discord's 25MB limit
```

**Duplicate background process spawning:** When re-running Demucs on new batches, do NOT spawn the same command multiple times. Each `terminal(background=True)` call creates a new process. If the first process is still running and you call it again, you get two identical Demucs instances fighting over the same output directory. Always check `process(action='list')` before spawning, or use a single script that handles everything in one process.

## Step 1d: Speaker Embedding Filtering — REJECTED, DO NOT USE

> **⚠️ PRODUCTION RESULT (2026-07-17):** This entire approach was rejected after testing. The cosine similarity method cannot reliably separate target speaker from other characters. Skip to manual selection from Demucs vocals instead. Kept for reference only.

When Demucs vocals contain multiple speakers (TV shows, movies, interviews), the original plan was to use the ECAPA-TDNN speaker encoder built into Qwen3 TTS to automatically filter down to the target speaker.

### How It Works

The Qwen3 TTS Base model contains an ECAPA-TDNN speaker encoder that produces 2048-dimensional embeddings representing "who is speaking." The `.spk` file from `qwen-codec --talker` IS this embedding. Computing cosine similarity between each chunk's embedding and the target speaker's reference embedding tells us whether that chunk is the target speaker or someone else.

### Recommended Approach: Python API (loads model ONCE)

The C++ binary (`qwen-codec`) loads the full 1.7B model from disk for EVERY chunk -- extremely slow for thousands of chunks. The Python API loads the model once and processes all chunks in batch. **Use the Python API.**

```python
from qwen_tts import Qwen3TTSModel
model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    device_map="cpu",  # or "cuda:0"
    dtype=torch.float32,
)
# Key: speaker encoder is at model.model.speaker_encoder
# The extract method takes NUMPY, not tensor:
inner_model = model.model
emb = inner_model.extract_speaker_embedding(audio_numpy, 24000)
```

**Gotchas:**
- `model.model.speaker_encoder` -- the Qwen3TTSModel is a wrapper; the actual model is at `.model`
- `extract_speaker_embedding(audio, sr)` expects a numpy array, NOT a torch tensor. Passing a tensor causes `TypeError: expected np.ndarray (got Tensor)`
- The model does NOT have an `eval()` method -- it's a custom wrapper, not a raw nn.Module
- Full working script: `~/.hermes/skills/qwen-voice-cloning/scripts/extract_speaker.py`

### Benchmark Results (GTX 1650 Ti, 28 Demucs tracks, 5+ hours audio)

| Metric | Value |
|--------|-------|
| Total chunks | ~3500 |
| Matches (threshold 0.80) | 3705 |
| After dedup | 1658 segments |
| Total audio | ~118 min |
| >= 0.95 similarity | 695 segments (46 min) |
| >= 0.90 similarity | 1241 segments (83 min) |
| Median similarity | 0.94 |
| Processing time (CPU) | 149 seconds |
| Model load time | ~25 seconds |

**Total pipeline time: ~3 minutes for all 28 tracks on CPU.** No GPU needed for filtering.

### Why This Matters for Fine-Tuning

The official fine-tuning JSONL format needs `{audio, text, ref_audio}`. This pipeline produces exactly what fine-tuning needs: long, clean, target-speaker-only audio with transcripts. Instead of manually curating 10-20 reference clips, you get hours of filtered audio automatically.

**Minimum for fine-tuning:** 10+ minutes of clean target-speaker audio. This pipeline can extract that from any multi-speaker source material.

### Threshold Tuning — REJECTED IN PRODUCTION (2026-07-17)

**The automated cosine similarity approach was rejected by the user after extensive testing.** Do NOT use this pipeline for speaker filtering — go manual instead.

**Test history:**
- **0.80 threshold:** 1658 segments, 118 min — user called it "really bad,"大量 other speakers mixed in
- **0.95 threshold:** 695 segments, 46 min — still rejected, quality not good enough
- **0.98 threshold:** 15 segments, 64 seconds — technically clean but only caught near-exact duplicates of the reference clip from the same scene
- **0.98 was the hard ceiling:** Only 23 raw matches from 3500+ chunks. The ECAPA-TDNN embeddings are not discriminative enough for multi-character content where voices share similar tonal qualities.

**User's exact words:** "Ya man this is not working we gotta ditch this cosine matching bs and go manual. Ill do it from the dmucs clips by myself"

**Root cause:** The ECAPA-TDNN speaker encoder (2048-dim) captures vocal timbre but not enough prosodic/linguistic context to reliably distinguish between characters who speak in similar ranges. At 0.80-0.95, other characters bleed in. At 0.98, you only get exact duplicates of the reference scene. There is no threshold that produces a clean, diverse set of target-speaker segments.

**What to do instead:** Manual selection from Demucs-separated vocals. The user listens to the clean vocal tracks and picks the target speaker's segments by ear. This is slower but produces actual clean training data. The Demucs output is already high quality — the bottleneck was always the filtering step, not the separation.

**Rule:** When working with multi-character content, skip Step 1d entirely. Go directly to manual clip selection from Demucs vocals.

## Step 2: Source Audio Acquisition

### YouTube Download

```bash
mkdir -p ~/voice-project/audio ~/voice-project/captions

# Search for clips
yt-dlp --flat-playlist -j "ytsearch10:character name show speaking" | \
  python3 -c "import json,sys; [print(f'{json.loads(l)[\"id\"]} | {json.loads(l).get(\"duration_string\",\"?\")} | {json.loads(l).get(\"title\",\"?\")[:80]}') for l in sys.stdin]"

# Download audio (24kHz mono WAV -- Qwen3 native format)
yt-dlp -x --audio-format wav --audio-quality 0 \
  --postprocessor-args "-ar 24000 -ac 1" \
  -o "audio/%(id)s.%(ext)s" \
  "https://www.youtube.com/watch?v=$VIDEO_ID"

# Download auto-generated captions
yt-dlp --write-auto-sub --sub-lang en --skip-download \
  --sub-format vtt \
  -o "captions/%(id)s.%(ext)s" \
  "https://www.youtube.com/watch?v=$VIDEO_ID"
```

### Verify Audio Format

```bash
ffprobe -v error -show_entries stream=sample_rate,channels -of csv=p=0 audio/VIDEO_ID.wav
# Should output: 24000,1
```

### Batch Download from Playlist

```bash
# Download all videos from a YouTube playlist as audio
yt-dlp --flat-playlist --print "%(id)s" "$PLAYLIST_URL" | while read -r VID; do
    [ -f "audio/${VID}.wav" ] && continue
    yt-dlp -x --audio-format wav --audio-quality 0 \
        --postprocessor-args "-ar 24000 -ac 1" \
        -o "audio/%(id)s.%(ext)s" \
        "https://www.youtube.com/watch?v=${VID}" 2>/dev/null
done
```

## Step 3: Caption Processing

### Clean VTT to Plain Text

```python
import re
def clean_vtt(filepath):
    with open(filepath) as f:
        content = f.read()
    content = re.sub(r'WEBVTT\n\n', '', content)
    content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}\n', '', content)
    content = re.sub(r'^\d+\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'<[^>]+>', '', content)
    return '\n'.join(l.strip() for l in content.split('\n') if l.strip())
```

### Extract Long Uncut Blocks (NOT tiny clips)

**CRITICAL: Do NOT slice audio into short clips based on auto-captions.** Auto-captions don't distinguish speakers, so caption-based cutting produces mixed-speaker fragments that ruin voice cloning.

Correct workflow for multi-character content (TV shows, movies):

```python
# Split source audio into 30-second uncut blocks
block_size = 30  # seconds
t = 0
while t < total_duration:
    end = min(t + block_size, total_duration)
    # Extract block — NO chopping, NO caption-based splitting
    ffmpeg -y -i audio.wav -ss t -to end -ar 24000 -ac 1 block_N.wav
    t = end
```

1. Extract 30-second uncut blocks from each source video
2. **Send blocks to user for manual speaker identification** — "which of these have clean TargetSpeaker?"
3. User identifies clean blocks
4. THEN extract precise segments from verified blocks

**Pitfall:** Auto-captions include ALL speakers + background noise. Never trust captions for speaker identification — manual review is the only reliable method.
**Pitfall:** Cutting clips to 8-10 seconds based on captions chops speakers mid-sentence. Always extract long uncut blocks first, then refine.
**Pitfall:** YouTube auto-captions often duplicate text (same phrase repeated 2-3x). Always deduplicate after parsing — check if second half of word list matches first half.

## Step 3c: Iterative User-Guided Extraction (Recommended for Multi-Speaker Content)

For content with multiple speakers (TV shows, movies, interviews), the most reliable workflow is **concatenate → user listens → timestamps → extract from originals**:

### 1. Concatenate all source audio into one file
```bash
# Create concat list
ls audio/*.wav | sort > /tmp/audio_list.txt

# Concatenate (preserves original quality)
ffmpeg -y -f concat -safe 0 -i /tmp/audio_list.txt \
    -ar 24000 -ac 1 marshall_full.wav
```

### 2. Compress for sharing (Discord bot limit = 25MB)
```bash
# WAV is too large — compress to MP3 for sharing
ffmpeg -y -i marshall_full.wav -codec:a libmp3lame -b:a 64k -ar 24000 -ac 1 marshall_full.mp3

# If still over 25MB, split into parts
# Part 1 covers 0:00-10:52, Part 2 covers 10:52-21:43, etc.
```

### 3. User listens and provides timestamps
User gives timestamps like: `1:32-1:36, 2:38-2:50, 4:23-4:28`

### 4. Convert timestamps to source file positions
```python
# Map combined-file timestamps to individual source files
video_starts = {
    "G2qRtRn5XcA": 0,      # 0:00
    "Q4uG1-XQoTE": 262,    # 4:22
    "_y478zwBIYo": 460,     # 7:40
    # ... etc
}

def map_timestamp(combined_seconds, video_starts):
    """Map a timestamp in the combined file to (source_file, source_seconds)."""
    for vid, start in sorted(video_starts.items(), key=lambda x: -x[1]):
        if combined_seconds >= start:
            return vid, combined_seconds - start
    return None, combined_seconds
```

### 5. Extract from ORIGINAL quality files (not the compressed MP3)
```python
# Use the source WAV files, not the compressed MP3
src_start, src_end = map_timestamp(user_start), map_timestamp(user_end)
ffmpeg -y -i f"audio/{source_file}.wav" \
    -ss {src_start} -to {src_end} \
    -ar 24000 -ac 1 selected/clip_NN.wav
```

**Pitfall:** Never extract final clips from the compressed MP3 used for sharing. Always go back to the original WAV files.
**Pitfall:** Timestamp mapping errors are common — verify that mapped positions are positive and within source file duration.
**Pitfall:** Discord bot file upload limit is 25MB. WAV files for 30+ minutes will exceed this. Compress to MP3 (64kbps) for sharing, but extract final clips from originals.

## Step 3b: Character Voice Gathering (YouTube)

When cloning a fictional character's voice, search for official clips where the character speaks heavily:

```bash
# Search for character clips — use show name + character name + "speaking"
yt-dlp --flat-playlist -j "ytsearch20:Character Name Show speaking" | \
  python3 -c "import json,sys; [print(f'{json.loads(l)[\"id\"]} | {json.loads(l).get(\"duration_string\",\"?\")} | {json.loads(l).get(\"title\",\"?\")[:80]}') for l in sys.stdin]"

# Pick videos where target character is the primary speaker
# Download audio + auto-captions in batch
for vid in "${VIDEOS[@]}"; do
  yt-dlp -x --audio-format wav --audio-quality 0 \
    --postprocessor-args "-ar 24000 -ac 1" \
    -o "audio/%(id)s.%(ext)s" \
    "https://www.youtube.com/watch?v=$vid"
  yt-dlp --write-auto-sub --sub-lang en --skip-download \
    --sub-format vtt \
    -o "captions/%(id)s.%(ext)s" \
    "https://www.youtube.com/watch?v=$vid"
done
```

Target: 10+ minutes of clean character speech across multiple clips.

## VoiceBox (jamiepine/voicebox) — GUI Alternative

**jamiepine/voicebox** (40.9k ⭐) is an open-source AI voice studio wrapping Qwen3-TTS + 6 other engines in a Tauri GUI. Features: voice cloning, 23 languages, post-processing effects, MCP server. For CLI-based workflows, redundant — we have Qwen3 TTS directly.

## Step 4: Voice Clone Generation

### Using PyTorch (0.6B or 1.7B with device_map)

**Use `create_voice_clone_prompt()` for production.** It builds the clone prompt once and caches it. Subsequent `generate_voice_clone()` calls skip reference re-extraction. The GGUF CLI path regenerates features every invocation.

```python
from qwen_tts import Qwen3TTSModel
import soundfile as sf

model = Qwen3TTSModel.from_pretrained(
    'Qwen/Qwen3-TTS-12Hz-1.7B-Base',  # or 0.6B-Base
    device_map='cuda:0'
)

# Build reusable clone prompt (one-time extraction)
voice_clone_prompt = model.create_voice_clone_prompt(
    ref_audio_path="reference-clip.wav",
    ref_text="What the reference audio says",
    x_vector_only_mode=False,  # False = ICL mode (better quality)
)

# Reuse for multiple generations without re-extraction
wavs, sr = model.generate_voice_clone(
    text="First sentence",
    language="en",
    voice_clone_prompt=voice_clone_prompt,
)
sf.write("output_1.wav", wavs[0], sr)

wavs, sr = model.generate_voice_clone(
    text="Second sentence",
    language="en",
    voice_clone_prompt=voice_clone_prompt,
)
sf.write("output_2.wav", wavs[0], sr)

# Or batch generate
wavs, sr = model.generate_voice_clone(
    text=["Sentence A.", "Sentence B."],
    language=["en", "en"],
    voice_clone_prompt=voice_clone_prompt,
)
```

**`x_vector_only_mode=True`** uses only the speaker embedding (no transcript needed, lower quality). **`x_vector_only_mode=False`** (default when ref_text provided) uses ICL with full audio tokens (better prosody). See [references/qwen3-tts-architecture.md](references/qwen3-tts-architecture.md) for the full Mode A vs Mode B explanation.

### Using GGUF (qwentts.cpp)

```bash
# Direct voice clone (use --ref-wav for simple mode)
echo "Text to speak" | ~/qwentts.cpp/build/qwen-tts \
    --model ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    --codec ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --ref-wav reference-clip.wav \
    -o output.wav

# Extract speaker embedding first (reusable)
# Note: qwen-codec uses --model for codec GGUF and --talker for talker GGUF
~/qwentts.cpp/build/qwen-codec \
    --model ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --talker ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    -i reference-clip.wav
# Writes .rvq + .spk files next to input

# Then use embedding (no need for reference audio again)
echo "Text to speak" | ~/qwentts.cpp/build/qwen-tts \
    --model ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    --codec ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --ref-spk reference-clip.spk \
    -o output.wav
```

**Pitfall: `qwen-codec` flags are `--model` (codec GGUF) and `--talker` (talker GGUF).** There is NO `--codec` flag on `qwen-codec`. The `--codec` flag only exists on `qwen-tts`. Using `--codec` on `qwen-codec` gives `ERROR: unknown arg: --codec`.

## Step 5: Transcription (Whisper)

YouTube auto-captions are unreliable for speaker identification and contain duplicated text. Use Whisper for clean transcriptions of extracted clips:

```bash
source ~/qwen3-tts-env/bin/activate
pip install openai-whisper  # one-time

# Transcribe a clip (CPU — avoids VRAM conflicts with loaded TTS model)
python3 -c "
import whisper
model = whisper.load_model('base', device='cpu')
result = model.transcribe('clip.wav', language='en')
print(result['text'].strip())
"
```

**Pitfall:** Whisper on CUDA may fail with NaN errors if GPU memory is occupied. Always use `device='cpu'` when TTS models are also using the GPU.
**Pitfall:** Whisper `base` model is sufficient for clean speech. `small` or `medium` for noisy/multi-speaker audio.

### Upgrading STT Quality

The `base` Whisper model is the second-smallest — fast but misses a lot. For better transcription accuracy:

- **Cloud (best quality):** Switch to Deepgram Nova-3 ($0.29/hr, $200 free credit) or AssemblyAI Universal-3.5 Pro ($0.21/hr, best accuracy)
- **Local (best for 4GB VRAM):** Use Faster-Whisper with Whisper turbo INT8 (~1.5GB VRAM, ~10x more accurate than base)
- **Maximum local accuracy:** Try Faster-Whisper large-v3 INT8 (~2.9GB, tight on 3.64GB card)

See [references/stt-research-2026.md](references/stt-research-2026.md) for full comparison tables and setup instructions.

### Current Setup (as of July 2026)

Faster-Whisper with Whisper turbo INT8 is installed and configured as primary STT:

```bash
pip install faster-whisper  # v1.2.1, already installed
```

Config in `~/.hermes/config.yaml`:
```yaml
stt:
  enabled: true
  local:
    model: large-v3-turbo  # Was "base" — upgraded July 2026
  openai:
    model: whisper-1  # Cloud fallback
```

The turbo model (809M params, ~1.5GB VRAM) downloads automatically on first use from HuggingFace (`mobiuslabsgmbh/faster-whisper-large-v3-turbo`). ~10x more accurate than the old base model. Gateway restart required for config changes to take effect.

## Step 6: Reference Audio Preparation

### For Single-Clip References (Simple)

```bash
# Direct clone — reference audio + transcript
~/qwen3-clone.sh -t "Text to speak" -r reference.wav -R "What reference says" -o output.wav

# Extract speaker embedding once, reuse forever
~/qwen3-clone.sh -e reference.wav -o voice.spk
~/qwen3-clone.sh -t "Any text" -s voice.spk -o output.wav
```

### For Multi-Clip References (Better Quality)

Combine multiple clean clips into one reference file:

```python
# Create concat list from curated clips
with open('/tmp/ref_concat.txt', 'w') as f:
    for clip in ['clip_01.wav', 'clip_03.wav', 'clip_07.wav']:
        f.write(f"file '/absolute/path/{clip}'\n")

# Concatenate
ffmpeg -y -f concat -safe 0 -i /tmp/ref_concat.txt \
    -ar 24000 -ac 1 combined_ref.wav

# Combine transcripts
echo "transcript clip 1. transcript clip 2. transcript clip 3." > combined_ref.txt
```

### Critical: ICL Mode vs Speaker Embedding Mode

**Three TTS modes** (determined by which GGUF model you load):

| Mode | GGUF suffix | What it does | Flags needed |
|------|-------------|--------------|-------------|
| **Base** | `base` | Default voice + voice cloning via reference audio | `--ref-wav` or `--ref-spk`/`--ref-rvq` |
| **CustomVoice** | `customvoice` | Named speaker library (Eric, Dylan, etc.) | `--speaker <name>` |
| **VoiceDesign** | `voicedesign` | Describe voice in text, model synthesizes it | `--instruct "young male, deep pitch..."` |

VoiceDesign is 1.7B only. Base is the only mode with a built-in speaker encoder (needed for cloning).

**Two sizes:** 0.6B (fast, ~1.5GB VRAM) and 1.7B (better quality, ~2.1GB VRAM). VoiceDesign is exclusive to 1.7B.

**Two cloning approaches within Base mode:**

| Approach | Flags | How it works | Best for |
|----------|-------|-------------|----------|
| **Mode A: Zero-shot** | `--ref-wav ref.wav --ref-text ref.txt` | Model extracts speaker embedding on-the-fly from reference WAV | Quick testing, single reference |
| **Mode B: ICL (pre-encoded)** | `--ref-rvq ref.rvq --ref-spk ref.spk --ref-text ref.txt` | Pre-extracted latents from `qwen-codec --talker`, reused across generations | Production (faster per-generation, no re-encoding) |

Mode B = ICL (In-Context Learning). The reference audio tokens are prepended to the model's context, and it generates speech matching that voice pattern. ICL is better for prosody because it captures the reference's speaking patterns, not just the voice print.

**ICL context budget:** 4096 frames total (at 12 Hz). ICL prefix ~250 frames/8s. Output cap (default 2048, typically `--max-new 500` = ~42s). Sweet spot: 10-20s reference.

**Other tools:** `qwen-codec` (WAV to/from RVQ codes, extracts .spk + .rvq), `tts-server` (OpenAI-compatible HTTP API with voice registry, keeps model warm in VRAM).

**Default:** When no reference is provided, Base mode uses its built-in default voice. No cloning, no design.

**11 languages** supported (English, Mandarin, etc.). Language auto-detected from text or set with `--lang`.

## Sampling Parameters (Intonation Tuning)

The default sampling settings produce decent results, but intonation can be improved by tuning:

```bash
# Default (temp 0.9, top-k 50, top-p 1.0, rep-pen 1.05)
echo "$TEXT" | ~/qwentts.cpp/build/qwen-tts --model ... --ref-spk ... -o out.wav

# Lower temperature — more stable, less random, better intonation
echo "$TEXT" | ~/qwentts.cpp/build/qwen-tts --model ... --ref-spk ... \
    --temp 0.6 --top-k 30 --top-p 0.85 --rep-pen 1.1 \
    -o out.wav
```

| Parameter | Default | Tuned | Effect |
|---|---|---|---|
| `--temp` | 0.9 | 0.6 | Lower = more stable intonation, less variability |
| `--top-k` | 50 | 30 | Lower = fewer random choices, more deterministic |
| `--top-p` | 1.0 | 0.85 | Lower = nucleus sampling tighter, more focused |
| `--rep-pen` | 1.05 | 1.1 | Higher = less repetition, more natural flow |
| `--sub-temp` | 0.9 | 0.7 | Sub-talker temperature (codebook prediction) |

**User preference: default temp 0.9 sounds better than lower settings.** After A/B testing the same brief at temp 0.9 vs 0.6, the user preferred the default — it has more natural variation and expressiveness. Lower temp (0.6) sounded more stable but flatter. Only drop temp if the output is genuinely erratic.

**ICL mode** (`--ref-wav` + `--ref-text`): Uses both speaker embedding AND reference speech codes. Better intonation/prosody because it captures the reference's speaking patterns. But **much more VRAM** — needs ~2.5GB free for codec encoder.

**Speaker embedding mode** (`--ref-spk`): Uses only the speaker vector. Less VRAM, still good quality.

**Pitfall: ICL mode OOM with long references.** 30+ seconds of reference audio in ICL mode will OOM on 4GB VRAM. The codec encoder needs to process all reference audio into speech codes, which requires allocating large CUDA buffers.

**Solution 1: Extract speaker embedding first, use that instead**
```bash
# Extract embedding from combined reference
~/qwentts.cpp/build/qwen-codec \
    --model ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --talker ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    -i combined_ref.wav
# Creates combined_ref.spk

# Generate with embedding (no VRAM spike)
echo "Text to speak" | ~/qwentts.cpp/build/qwen-tts \
    --model ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    --codec ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --ref-spk combined_ref.spk \
    -o output.wav
```

**Solution 2: Use `--codec-chunk-dur` for ICL mode**
```bash
# Decode in 8-second chunks (prevents OOM during codec decode)
echo "Text to speak" | ~/qwentts.cpp/build/qwen-tts \
    --model ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    --codec ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --ref-spk voice.spk \
    --codec-chunk-dur 8.0 \
    -o output.wav
```

**Solution 3: Pre-encode reference, use ref-rvq mode (avoids OOM entirely)**
```bash
# Step 1: Extract .rvq + .spk from reference (one-time)
~/qwentts.cpp/build/qwen-codec \
    --model ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --talker ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    -i reference.wav
# Creates reference.rvq + reference.spk

# Step 2: Generate with pre-encoded reference (ICL mode, no codec encoder OOM)
echo "Text to speak" | ~/qwentts.cpp/build/qwen-tts \
    --model ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    --codec ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --ref-rvq reference.rvq \
    --ref-spk reference.spk \
    --ref-text reference_transcript.txt \
    --max-new 500 \
    -o output.wav
```

**Pitfall:** ref-rvq mode needs a transcript file (`--ref-text`) with what the reference audio says. Without it, you get `FATAL: cannot open`.
**Pitfall:** The transcript MUST accurately match the reference audio. Wrong transcript = gibberish output (speaker sounds tongue-tied, unintelligible). Use Whisper on the exact reference clip to get an accurate transcript, or use a clip where you already know the exact words spoken.
**Pitfall:** ICL mode can generate indefinitely (hits `--max-new` limit of 2048 frames). Add `--max-new 500` to cap output length.

**Solution 4: Keep ICL references under 15 seconds**
```bash
# Short ICL reference (under 15s works reliably)
~/qwen3-clone.sh -t "Text" -r short_ref.wav -R "Transcript" -o output.wav
```

## Model Selection

**User preference: use 1.7B Q8_0 for both embedding extraction AND TTS generation.** After A/B comparison, the 1.7B model produces noticeably better intonation and naturalness than 0.6B. The 0.6B is available as a fallback if VRAM is tight.

| Task | Model | Why |
|---|---|---|
| Speaker embedding extraction | 1.7B Q8_0 (GGUF) | Larger model captures richer voice characteristics |
| TTS generation | 1.7B Q8_0 (GGUF) | Better intonation, preferred by user after comparison |
| TTS fallback (low VRAM) | 0.6B Q8_0 (GGUF) | Lighter, more VRAM headroom, acceptable quality |

The 1.7B model produces 2048-dimensional speaker embeddings. The 0.6B model expects 1024-dimensional embeddings. **You MUST extract embeddings with the same model you generate with, or re-extract with the correct model.**

**Pitfall: Embedding dimension mismatch.** If you extract with 1.7B (2048-dim) and try to generate with 0.6B (1024-dim), you get: `ref_spk_dim 2048 mismatches talker hidden 1024`. Fix: re-extract with the target model's talker GGUF.

```bash
# Extract embedding with 0.6B (for use with 0.6B generation)
~/qwentts.cpp/build/qwen-codec \
    --model ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --talker ~/qwentts.cpp/models/qwen-talker-0.6b-base-Q8_0.gguf \
    -i reference.wav
# Creates reference.spk (1024-dim)

# Extract embedding with 1.7B (for use with 1.7B generation)
~/qwentts.cpp/build/qwen-codec \
    --model ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --talker ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    -i reference.wav
# Creates reference.spk (2048-dim)
```

### GGUF Models Available

| Model | Talker Size | Total w/ Q4 tokenizer | VRAM | Use For |
|---|---|---|---|---|
| 0.6B Q8_0 | ~993 MB | ~1.2 GB | ~1.5 GB | TTS fallback (low VRAM) |
| 0.6B Q4_K_M | ~629 MB | ~884 MB | ~1 GB | Fastest option, acceptable quality |
| 1.7B Q8_0 | ~2.1 GB | ~2.3 GB | ~2.1 GB | Best quality (preferred for voice cloning) |
| 1.7B Q4_K_M | ~1.2 GB | ~1.45 GB | ~1.2 GB | Best speed/quality tradeoff on 4GB GPU |

Download from: `https://huggingface.co/Serveurperso/Qwen3-TTS-GGUF`

**Quantization speed impact**: Q4_K_M uses ~50% fewer bytes per weight vs Q8_0. On bandwidth-limited GPUs (GTX 1650 Ti etc.), this translates to **~20-40% faster inference** since memory bandwidth is the bottleneck. RVQ codebooks and speaker encoder stay F32 in every variant — only the talker LM weights are quantized. See [references/optimization.md](references/optimization.md) for detailed benchmarks and RTF estimates.

**See model-advisory skill for quantization analysis methodology.**

## Long Text Handling

Qwen3 TTS generates ~12.5 frames/second. At 500 characters, that's ~340 frames (~27 seconds), which can OOM even with chunked decoding on4GB VRAM.

**User preference: Split long responses into 2 parts for seamless transitions and to avoid model crashes.** The split should happen at natural sentence boundaries so the listener doesn't notice the break.

With auto-splitting script: Set `max_text_length: 2000` in Hermes config — the provider script handles splitting at all punctuation boundaries (max 350 chars per chunk, `--max-new 500` per chunk). The script splits at `.`, `!`, `?`, `;`, `—`, `,`, `…` with different pause durations for each. Without auto-splitting, limit to 200 chars for 1.7B, 400 for 0.6B.

The production script (`~/marshall-voice/tts-provider.sh`) implements Python-based sentence splitting and ffmpeg concatenation with 0.8s silence between chunks. See `references/tts-provider-script.md` for the full implementation. For manual generation, split at period/exclamation/question marks.

## Direct CLI Usage (no wrapper script needed)

```bash
# Clone voice from reference audio (use echo pipe, NOT <<<)
echo "Hello world" | ~/qwentts.cpp/build/qwen-tts \
    --model ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    --codec ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --ref-wav reference.wav \
    -o hello.wav

# With reference transcript (ICL mode, better quality, needs <15s reference)
echo "Hello" | ~/qwentts.cpp/build/qwen-tts \
    --model ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    --codec ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --ref-rvq reference.rvq \
    --ref-spk reference.spk \
    --ref-text reference_transcript.txt \
    --max-new 500 \
    -o hello.wav

# Extract speaker embedding once, reuse forever
~/qwentts.cpp/build/qwen-codec \
    --model ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --talker ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    -i reference.wav
# Creates reference.rvq + reference.spk
```

**`--codec-chunk-dur`**: Only affects the buffered decode path (one-shot WAV output). Default 24.0s is fine for sentence-level chunks (< 24s of audio). Only reduce if total audio exceeds chunk duration and causes OOM. The streaming path (tts-server PCM output) ignores this parameter entirely — it uses stateful frame-by-frame decode.

**`--no-fa`**: Flash attention is **on by default** and should stay on. It provides O(n) memory vs O(n²) for the 28-layer talker and 5-layer predictor attention. Works on Turing (sm_75) and later. Only disable for debugging.

## Real-Time Conversation

The `tts-server` binary in qwentts.cpp provides an OpenAI-compatible HTTP API with a cloned voice registry. **This is the recommended production path** — the model stays loaded in GPU memory between requests, eliminating the 1-3 second model load overhead per chunk.

```bash
# Start TTS server (model stays warm in GPU memory)
~/qwentts.cpp/build/tts-server \
    --model ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    --codec ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --host 127.0.0.1 --port 8080

# Register a cloned voice (one-time, extracts speaker embedding server-side)
curl -X POST http://127.0.0.1:8080/v1/voices \
  -H "Content-Type: application/json" \
  -d '{"name": "marshall", "ref_text": "transcript of reference", "spk_b64": "'$(base64 -w0 voice.spk)'", "rvq_b64": "'$(base64 -w0 voice.rvq)'"}'

# Generate speech (streaming PCM — audio starts arriving in ~83ms)
curl -s -X POST http://127.0.0.1:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello world", "voice": "marshall", "response_format": "wav"}' \
  --output speech.wav
```

**response_format "pcm"**: Streams s16le 24 kHz mono chunked as generated (lowest latency — first audio fires ~83ms after first frame).
**response_format "wav"**: Returns a one-shot RIFF file after full generation.

**Note:** Inference takes ~3-5 seconds per response (RTF ~0.4-0.6 with warm model). The streaming PCM path delivers audio incrementally for faster perceived response.

## Hermes TTS Integration

Wire the voice clone into Hermes so it speaks in the cloned voice automatically.

### Config

Add to `~/.hermes/config.yaml`:

```yaml
tts:
  provider: marshall  # MUST be lowercase
  providers:
    marshall:  # dict key MUST match provider name (lowercase)
      type: command
      command: "/path/to/tts-provider.sh {input_path} {output_path}"
      output_format: ogg       # Required: Hermes passes .ogg path to provider
      voice_compatible: true   # Required: emits [[audio_as_voice]] for Discord/Telegram voice delivery
      max_text_length: 2000    # 0.6B can handle ~400; 1.7B needs ~200 without auto-splitting
```

### Provider Wrapper Script

Create `~/marshall-voice/tts-provider.sh` (or equivalent for your voice).

**Use ICL mode (ref-rvq) for best quality** — it captures prosody from the reference audio, not just the voice print. Requires pre-encoding the reference with `qwen-codec --talker` and an accurate transcript file.

The script splits at ALL punctuation: `.`, `!`, `?`, `;`, `—`, `,`, `…`. Each has a different pause duration: `,` → 0.3s, `;` → 0.5s, `—` → 0.5s, `.` → 0.8s, `!` → 0.8s, `?` → 0.8s, `…` → 0.5s. The LAST punctuation of a chunk determines its pause. Chunks are merged if under 350 characters. Final output is 4% slower via ffmpeg atempo=0.96.

```bash
#!/bin/bash
INPUT_PATH="$1"
OUTPUT_PATH="$2"
# CRITICAL: use echo pipe, NOT <<< heredoc (bash escapes apostrophes)
echo "$TEXT" | ~/qwentts.cpp/build/qwen-tts \
    --model ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    --codec ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --ref-rvq ~/marshall-voice/selected/clip_07_trimmed_precise.rvq \
    --ref-spk ~/marshall-voice/selected/clip_07_trimmed_precise.spk \
    --ref-text ~/marshall-voice/selected/clip_07_trimmed_precise.txt \
    --max-new 500 \
    -o "${OUTPUT_PATH%.ogg}.wav" \
    2>/dev/null

# Convert to OGG/Opus for Discord + Telegram voice delivery
ffmpeg -y -i "${OUTPUT_PATH%.ogg}.wav" -af atempo=0.96 -codec:a libopus -b:a 64k "$OUTPUT_PATH" 2>/dev/null
rm -f "${OUTPUT_PATH%.ogg}.wav"
```

**Pre-encode reference (one-time setup for ICL mode):**
```bash
~/qwentts.cpp/build/qwen-codec \
    --model ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --talker ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    -i reference_clip.wav
# Creates reference_clip.rvq + reference_clip.spk
```

**Use the 1.7B model for TTS generation** — better intonation than 0.6B after A/B comparison. The 0.6B is available as fallback if VRAM is tight.

**Best ICL reference clips:** Single clean clip, accurate transcript, longer = better (up to ~15s). Current production reference is `clip_07_trimmed_precise` (7.7s). Switched back from clip_07_trimmed_start (8.0s) on 2026-07-17 because the 7.7s clip ends cleanly and is confirmed clean by the user. Transcript: "Do you think there's any way you could get me something called tetrodotoxin, it's extracted from pufferfish, and..." (Whisper-verified). Rule: trim only if you can afford to lose that segment; never trim below ~7.5s. ALWAYS run Whisper on any new/trimmed clip to verify the transcript matches the audio exactly. ALWAYS use the same reference clip everywhere (tts-provider, extraction pipeline, ICL generation).

**Pitfall: ICL reference length directly affects prosody quality.** Trimming a 9s reference to 7s (1s off each end to remove artifacts) produced noticeably more robotic output — the model didn't have enough speech pattern data to learn natural intonation. However, trimming just the FIRST second (8s total) worked fine and removed the artifact without prosody loss. Trimming 0.3s from the end (7.7s) also worked. Rule: if trimming artifacts, only trim from one end, and keep at least 7.5s.

### Reference Clip Length vs VRAM

The model has no hard limit on reference clip length — it's a few-shot cloning model that works with as little as 3 seconds. The constraint is VRAM, not the model itself. Longer clips capture more of the speaker's patterns, intonation, and rhythm, improving voice quality.

**VRAM scaling (approximate):**

| GPU | VRAM | Comfortable Max Clip | Sweet Spot |
|-----|------|---------------------|------------|
| GTX 1650 Ti | 3.64 GB | ~10-12s | 7-8s |
| RTX 2060 Super | 8 GB | ~20-30s | 10-20s |
| RTX 3070 Ti | 8 GB | ~20-30s | 10-20s |
| RTX 3090 | 24 GB | 60s+ | 15-30s |

The model's transformer receptive field (8 layers x window 72) exceeds any reference length, so the full prime is exact regardless of clip length. The VRAM cost comes from the KV cache growing with reference frames and the codec encoder processing all reference frames during priming.

A 33-second stitched clip was tested on 3.64GB VRAM and worked, but used significantly more VRAM. With 8GB (RTX 2060 Super), 15-20 seconds is comfortable, and 30 seconds is feasible.

**Sweet spot:** 10-20 seconds gives enough speech pattern data to capture personality without excessive VRAM usage.

**Reference clip trimming is iterative.** User will ask for small trims (0.5s, 0.4s, 0.3s, 0.2s) and compare each version. Send each trimmed version as a voice memo for comparison. After the user picks a version, regenerate ICL files (.rvq, .spk, .txt) and run Whisper on the new clip to verify the transcript matches the actual audio content. Trimming changes what words are present (e.g., removing the first second may cut off the first word, trimming the end may remove the last word). The transcript file MUST match the actual audio — wrong transcript = gibberish output.

**Placeholder:** `{input_path}` = temp file with text, `{output_path}` = where audio goes.

### ICL Context Budget (qwentts.cpp)

**TWO DIFFERENT LIMITS — don't confuse them:**

1. **Reference clip length** (how long the ICL reference audio can be)
2. **Output generation length** (how long the generated speech can be)

Both share the same **4096-frame KV cache** (at 12.5 Hz = ~328 seconds total budget).

#### Reference Clip Length

- The ICL reference occupies a prefix in the talker's KV cache
- Tested in production: up to ~250 frames (~20 seconds) — source code comment: "longest ICL prompt observed is ~250"
- **No hard cap in code** — the 4096-frame budget theoretically allows ~328 seconds of reference
- But the model was **trained** on references up to ~20 seconds; beyond that is unvalidated territory
- **Practical sweet spot: 10-20 seconds of clean, isolated speech**
- Longer references introduce more variability (emotions, pacing, mic distance) which dilutes the voice signal
- One perfect 15-second clip > one messy 60-second clip

#### Output Generation Length

- Default `--max-new` is 2048 frames (~164 seconds)
- Production setting: `--max-new 500` (~42 seconds per chunk)
- Voice quality degrades further from the reference — the model "gets tired" after ~50-60 seconds
- Split long text at sentence boundaries, generate each chunk separately, concatenate with ffmpeg

#### Budget Example

Current production: clip_07_trimmed_precise = 7.7s (~250 frames) + output cap 500 frames = 750 / 4096 = 18%. Massive headroom.

#### Alternative Models

**Kokoro** (Helium, 82M params): Supports multi-reference ICL natively (no concatenation needed), but much smaller than Qwen (1.7B = 21x larger). Voice cloning quality scales with model size, so Kokoro's cloning is noticeably worse. Not recommended when Qwen is available.

**Why Demucs-cleaned audio helps ICL more than raw audio:** Clean vocal separation removes background noise that adds "junk" tokens to the reference. With raw audio, the model sees the character's voice mixed with music, SFX, and other speakers -- each of those noise tokens consumes context budget without helping voice matching. Clean audio means every frame of reference carries useful voice information, so shorter references can achieve the same or better quality.

### Expanding ICL References (Cherry-Pick + Concatenate)

The qwentts.cpp `--ref-rvq` flag accepts **ONE reference file**. You cannot pass multiple clips directly. To use multiple clean clips:

1. Go through Demucs-separated tracks
2. Find the best 10-20 second Marshall lines (clear speech, good emotion, isolated vocals)
3. **Concatenate them into one combined reference file:**
   ```bash
   # Create concat list from cherry-picked clips
   echo "file '/path/to/best_clip_1.wav'" > /tmp/ref_concat.txt
   echo "file '/path/to/best_clip_2.wav'" >> /tmp/ref_concat.txt
   echo "file '/path/to/best_clip_3.wav'" >> /tmp/ref_concat.txt
   # Concatenate
   ffmpeg -y -f concat -safe 0 -i /tmp/ref_concat.txt -ar 24000 -ac 1 combined_ref.wav
   # Combine transcripts (must match the concatenated audio order)
   echo "transcript of clip 1. transcript of clip 2. transcript of clip 3." > combined_ref.txt
   # Extract ICL files
   ~/qwentts.cpp/build/qwen-codec \
       --model ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
       --talker ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
       -i combined_ref.wav
   ```
4. Use the combined .rvq + .spk + .txt as the single ICL reference

**Why this works:** The model sees a wider variety of the same voice across different contexts (emotional range, sentence structures, pacing). This produces more robust voice matching than a single long clip from one scene. The concatenated reference still must fit within the 4096-frame context budget alongside the output.

**Pitfall: transcript must match concatenated audio exactly.** If you concatenate clips A, B, C in that order, the transcript file must be "transcript_A. transcript_B. transcript_C." Wrong order or wrong transcript = gibberish output.

### Video ID Lookup Shortcut

YouTube download filenames ARE the video IDs. When you need to look up which video a track came from:
```bash
# The filename IS the video ID
basename ~/marshall-voice-pipeline/raw/0KplMSkEZJA.mp3 .mp3
# Output: 0KplMSkEZJA → https://youtube.com/watch?v=0KplMSkEZJA
```
**Pitfall:** Do NOT re-run Whisper or search through transcripts to figure out which video a clip came from. The filename is the video ID. YouTube URL = `https://youtube.com/watch?v=<filename>`.
**Restart required:** Gateway must restart for TTS config to take effect (`hermes gateway restart`).

### Speech Pacing (Calm, Relaxed Speed)

**User preference: speech should sound like a relaxed person talking, not rushed.**

The Qwen3 TTS model generates at a fixed pace — there's no speed parameter in the CLI. Two approaches to slow things down:

**DO: Longer pauses between chunks (0.8s silence)**
```bash
# In tts-provider.sh, the silence padding between chunks controls pacing
ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t 0.8 "$SILENCE"
# 0.3s = rushed, 0.8s = relaxed, 1.2s = very deliberate
```

**DON'T: Sox tempo effect**
```bash
# WRONG — sounds artificial, like a recording played back slower
sox input.wav output.wav tempo 0.85
```

Sox `tempo` changes playback speed without pitch correction, which sounds unnatural — like the audio file itself is being slowed down. The user explicitly rejected this approach.

**Better approach: Write prompts with natural pauses built in.** Use commas, periods, and ellipses in the text to create breathing room. The model generates natural breaks at punctuation.

```
# RUSHED (no pauses in text)
"Okay so we set up the voice cloning and it works pretty well now"

# RELAXED (commas and periods create natural breaks)
"Okay so, we set up the voice cloning. And, uh, it works pretty well now."
```

**Silence duration guide:**
- 0.3s: Fast, urgent (news broadcast pace)
- 0.5s: Normal conversation
- 0.8s: Relaxed, calm (preferred for Marshall voice)
- 1.2s: Very deliberate, professorial

**Punctuation-aware splitting.** The production script splits at ALL punctuation (`.`, `!`, `?`, `;`, `—`, `,`, `…`) with different pause durations for each. Commas get 0.3s, semicolons/em dashes get 0.5s, periods get 0.8s, ellipses get 0.5s. Chunks are merged if under 350 chars. Final output is 4% slower via ffmpeg atempo=0.96.

```
# The script splits at all punctuation:
"Okay so, here's the thing; the mushroom heals everything. And I mean everything — you don't need money, you don't need insurance."
#               ^ 0.3s pause    ^ 0.5s pause        ^ 0.8s pause          ^ 0.5s pause              ^ 0.3s pause
```

The production script implements this via Python-based splitting that outputs one chunk per line, with a single 0.8s silence file for concatenation. Final output is 4% slower via ffmpeg atempo=0.96. See `references/tts-provider-script.md` for the full implementation.

### Audio-First Responses

When the cloned voice is active in a thread, **prefer voice memos for all responses**. Use text only when:
- Code blocks or formatted output that audio can't convey
- Long lists or tables
- The user explicitly asks for text

This makes the conversation feel like talking to the character, not just reading their words.

- **Discord MEDIA: tag silently dropped:** When the agent responds with BOTH text AND a `MEDIA:<path>` tag in the same message, the Discord adapter sends the text but **silently drops the audio file**. The agent must respond with ONLY the `MEDIA:<path>` tag — no accompanying text, no explanation, no sign-off — for the audio to be delivered as a voice memo. If you need to convey non-audio information (code, tables, links), send it as a separate text message before or after the voice memo.

```
# WRONG — text + MEDIA tag in same message → audio dropped
Here's the system report. MEDIA:/path/to/audio.mp3

# CORRECT — MEDIA tag only → audio delivered as voice memo
MEDIA:/path/to/audio.mp3
```

- **Voice prompt quality — avoid mechanical/template feel:** User reported that voice memos sound like "picking words from a pre-approved set." The marshall-speech-patterns skill's fillers and sentence starters, when applied too rigidly, produce prompts that feel scripted rather than natural. Fix: write prompts that sound like someone thinking in real time, not someone filling a template. Vary the fillers. Let some sentences start without a filler. Use false starts and mid-sentence corrections more than standardized openers. The goal is organic speech, not a formula with slots.

### Voice Memo Writing Style (MANDATORY — User Preference)

**Every voice memo MUST follow the character's speech patterns from SOUL.md. No exceptions.** This is not optional — user explicitly hardwired this requirement.

**Load the `marshall-speech-patterns` skill BEFORE writing any voice prompt.** It contains the fillers, sentence starters, rhythm, and checklist. See that skill for the complete writing guide.

When writing text for voice memos, follow the character's speech patterns from SOUL.md:
- Use fillers from SOUL.md only: "um", "uh", "like", "I mean", "okay so", "look", "yeah", "well"
- Marshall stammers when nervous/excited
- Starts sentences with "Yeah," "Okay," "So," "Look," "Well"
- Shifts from casual to intense on technical topics
- No random fillers — follow the character's speech patterns
- Auto-split long text at sentence boundaries (max ~350 chars per chunk) to avoid truncation

### Command Provider Placeholders

Hermes supports these placeholders in the command template:
- `{input_path}` / `{text_path}` — temp file containing the text to speak
- `{output_path}` — path where the audio file must be written
- `{format}` — output format (mp3, ogg)
- `{voice}` — voice name from config
- `{model}` — model name from config
- `{speed}` — speed setting

**Pitfall:** The command provider writes text to a temp file, not stdin. Read from `{input_path}`, not stdin.
**Pitfall: Discord voice messages REQUIRE OGG/Opus format.** Discord's `send_voice` method sends audio as a native voice message (flags=8192) with `filename: "voice-message.ogg"` and `content_type: "audio/ogg"`. If the actual data is MP3, Discord rejects the format mismatch silently — the file never arrives, and the gateway logs `response_delivery_dropped`. The fallback `channel.send(file=file)` also fails because the Discord API expects OGG for voice-flagged messages.

**Fix:** Output OGG/Opus from the provider script:
```bash
# In tts-provider.sh — final conversion step
ffmpeg -y -i "$FULL_WAV" -af atempo=0.96 -codec:a libopus -b:a 64k "$OUTPUT_PATH"
**Output format:** Voice memos are OGG/Opus (`.ogg`), not MP3. The TTS provider outputs OGG for Discord/Telegram voice message compatibility. Always reference `.ogg` files in MEDIA: tags.

**Required config in ~/.hermes/config.yaml:**
```yaml
tts:
  providers:
    marshall:
      command: /home/h2/marshall-voice/tts-provider.sh {input_path} {output_path}
      output_format: ogg       # Hermes passes .ogg path to provider
      voice_compatible: true   # Routes audio to send_voice (voice message flag)
      max_text_length: 2000
      type: command
```

**context_file_max_chars:** Do NOT set this explicitly. Hermes dynamically calculates it as 6% of the model's context window (floor 20K, ceiling 500K). For big-pickle (200K context), this yields ~48K chars. An explicit override in config.yaml bypasses this scaling and breaks when switching models. Removed `context_file_max_chars: 50000` from config on 2026-07-27.

Without `output_format: ogg`, Hermes passes a `.mp3` path and the Opus codec fails (`Invalid audio stream. Exactly one MP3 audio stream is required`).
Without `voice_compatible: true`, the `[[audio_as_voice]]` directive is not emitted, and the file is sent as a regular attachment instead of a voice message.

**context_file_max_chars:** Do NOT set this explicitly in config.yaml. Hermes dynamically calculates it as 6% of the model's context window (floor 20K, ceiling 500K). For big-pickle (200K context via models.dev), this yields ~48K chars. An explicit override bypasses this scaling and breaks when switching models. Removed `context_file_max_chars: 50000` from config on 2026-07-27.

**Telegram** needs opus (.ogg) too — same format works for both platforms.

**Pitfall: Long text OOM even with chunked decoding.** On 4GB VRAM, the 1.7B Q8_0 model can generate 300+ frames before the codec decoder OOMs during `pipeline_codec_decode`. The `--codec-chunk-dur` parameter splits decoding into chunks but the codec weights + intermediates still need ~1.5GB VRAM.

**Fix (1.7B):** With auto-splitting, set `max_text_length: 2000` in Hermes config — the script handles the real limit (350 chars per chunk, `--max-new 500`). Without auto-splitting, limit to 200 chars.
**Fix (0.6B):** Set `max_text_length: 400` — the 0.6B model uses less VRAM for the talker, leaving more for the codec decoder.

For longer responses, split into multiple TTS calls and concatenate with silence padding between chunks.

### CRITICAL: Config Key Case Sensitivity

**`tts.providers.<name>` dict keys MUST be lowercase.** The `_get_provider()` function lowercases the provider name before lookup:

```python
def _get_provider(tts_config):
    return (tts_config.get("provider") or DEFAULT_PROVIDER).lower().strip()
```

So `provider: Marshall` becomes `"marshall"`, then `providers.get("marshall")` is called. If your config has `Marshall` (capital M) as the dict key, the lookup silently fails and falls through to Edge TTS.

```yaml
# WRONG — capital M dict key, won't match lowercased lookup
tts:
  provider: Marshall
  providers:
    Marshall:
      type: command
      command: "..."

# CORRECT — all lowercase
tts:
  provider: marshall
  providers:
    marshall:
      type: command
      command: "..."
```

**Fix:** Run `hermes config set tts.provider marshall` and ensure the providers dict key matches.

## Step 7: Persona Integration (SOUL.md)

When cloning a specific character's voice, update SOUL.md so the agent's personality matches the voice. This makes text and audio responses feel like the same person.

### Workflow

1. **Research the character** — search fan wikis, episode transcripts, reviews, Reddit
2. **Extract key traits** — personality, speaking style, worldview, quirks, relationships
3. **Update SOUL.md** — add character-specific identity, speech patterns, humor, worldview
4. **Test** — generate a few voice clones with character-appropriate text

### What to capture in SOUL.md

- **Identity** — who they are, their background, their central conflict
- **Speech patterns** — actual quotes, filler words, sentence starters, how they shift between casual/intense
- **Worldview** — their beliefs, philosophy, what they care about
- **Humor** — their style of humor (dry? dark? self-deprecating?)
- **Relationships** — key relationships and how they interact with others
- **Quirks** — physical habits, possessions, routines

**See references/marshall-cuso-persona.md for a worked example.**
**See references/tts-provider-script.md for the production TTS provider script and config.**
**See references/clip-replacement-workflow.md for the step-by-step clip replacement procedure.**
**See references/qwen3-tts-architecture.md for condensed Qwen3 TTS architecture: modes, ICL limits, emotion control, Kokoro comparison, and concatenation strategy.**

## Fine-Tuning the Base Model (Best Path for Persistent Voice Cloning)

**User preference: ICL for immediate use, fine-tuning for long-term. RVC explicitly rejected.**

The Qwen3-TTS repo has official single-speaker fine-tuning. After fine-tuning, the voice is baked into the model weights — no reference audio at inference, no ICL. The model IS the voice. And CustomVoice mode supports `instruct` parameter for emotion control ("speak in a panicked tone"), which was the original reason RVC was being considered.

### Workflow
1. Prepare JSONL with `{"audio": "path.wav", "text": "transcript", "ref_audio": "ref.wav"}`
2. Run `prepare_data.py` (needs tokenizer + GPU, lightweight — ~244MB VRAM)
3. Run `sft_12hz.py` (full training — needs ~13GB for 1.7B, ~5-6GB for 0.6B)
4. Output checkpoint loads as CustomVoice speaker with `generate_custom_voice()`

### What Happens at Checkpoint Save
The script changes model type from "base" to "custom_voice", drops the entire speaker encoder, and bakes the speaker embedding into `codec_embedding.weight[3000]`. No encoder needed at inference.

### Hardware on 4GB GPU
- 1.7B full fine-tune: ~13GB. Does NOT fit.
- 0.6B full fine-tune: ~5-6GB. Tight with CPU offloading.
- **LoRA:** Only trains ~20MB adapter matrices. Frozen 1.7B in bf16. Would fit.
- **CPU-only:** Dead slow but guaranteed to work.
- **`prepare_data.py` is lightweight** (~244MB VRAM) — only needs the tokenizer, not the full TTS.

See [references/qwen3-tts-architecture.md](references/qwen3-tts-architecture.md) for full fine-tuning details and the Voice Design then Clone workflow.

## Emotion Control and Voice Conversion

**Qwen3 TTS does NOT support emotion tags.** Writing `[Angry]`, `[Happy]`, or `[Whisper]` in the prompt will either be ignored or read aloud as literal text. The Base model clones voice timbre from the reference, but the emotional delivery (prosody, energy, pacing) is largely fixed to whatever the reference clip sounds like.

**VoiceDesign mode** takes text descriptions of voice characteristics (age, gender, pitch, accent) — but NOT emotions. It controls voice quality, not delivery style.

### User's Chosen Path: Fine-Tuning for Emotion Control

**RVC has been explicitly rejected by the user** ("Fk rvc i am not interested in it at all"). The user prefers the fine-tuning path over voice conversion.

After fine-tuning the Base model, the output is a CustomVoice checkpoint. CustomVoice mode supports an `instruct` parameter that accepts natural language emotion/style instructions:
- `"speak in a panicked tone"`
- `"slow down and sound uncertain"`
- `"angry, speaking fast"`
- `"whispering, conspiratorial"`

This is the emotion control the user wants — built into the model natively, not bolted on via voice conversion. Requires fine-tuning first (see "Fine-Tuning the Base Model" above).

### Community Implementations (Qwen3 TTS + RVC)

For reference only — user has rejected RVC path in favor of fine-tuning:
- **MimikaStudio** (639 stars): macOS app, Qwen3-TTS + RVC
- **TTS-Audio-Suite** (1,096 stars): ComfyUI node, multi-engine
- **RVCBench**: Referenced as academic benchmark. UNVERIFIED — treat citation with skepticism.

Community consensus: Qwen and RVC complement, not replace. But fine-tuning is the superior path when you have enough clean training data (which we have via Demucs + speaker embedding filtering).

### Demucs Version Info

**Installed:** Demucs 4.1.0 (released 2026-07-11, 6 days ago — latest version)
**Model:** htdemucs (Hybrid Transformer Demucs), 42M parameters, 44100 Hz, 4 stems (drums, bass, other, vocals)

**Main competitor:** BS-RoFormer — slightly better benchmarks on tricky audio (heavy reverb, background noise), but harder to set up and no clean CLI. Multiple tools (UVR, 25K stars) integrate both Demucs and BS-RoFormer. For our use case (vocal extraction for TTS), htdemucs quality is already excellent — switching not recommended unless output quality issues arise.

## Post-Setup Cleanup

After the voice pipeline is working, aggressively remove intermediate files:

```bash
cd ~/voice-project
# Remove: auto-extracted clips, long blocks, clean_clips, transcripts, captions,
# concatenated audio, split parts, old reference files, test outputs, unused scripts
rm -rf clips/ long_clips/ clean_clips/ transcripts/ captions/
rm -f marshall_full.* marshall_part*.mp3 marshall_ref*.* marshall_voice.spk segments.json
rm -f tts_generate.py qwen3-tts.py qwen3-tts-dual.py qwen3-clone.sh
# In selected/: keep only the active reference clip and its derivatives
```

Keep: `audio/` (original source WAVs), `selected/` (active reference only), `tts-provider.sh`.
Delete everything else. The source WAVs are needed if you want to extract new clips later.

## Performance Optimization

**The biggest win: use tts-server instead of per-chunk CLI invocations.** Each `qwen-tts` CLI call loads ~2GB of GGUF from disk (~1-3s), allocates KV cache, builds graphs. The tts-server loads once and stays warm, saving 1.5-4 seconds per chunk. For 10-sentence text, that's 15-40 seconds saved.

**⚠️ 4GB VRAM warning:** tts-server only works for short phrases (<2s audio) on 4GB. Medium+ text OOMs during codec decode because model (2GB) + KV cache (896MB) leaves no room for the ~590MB codec decode buffer. CLI per-chunk is the only viable approach on 4GB. The tts-server also causes CUDA memory fragmentation — after running it, CLI calls to qwen-tts may OOM even on short text until system reboot. See [references/optimization.md](references/optimization.md) for details.

**Quantization for speed**: Q4_K_M talker is ~20-40% faster than Q8_0 on bandwidth-limited GPUs (like GTX 1650 Ti) because it reads ~50% fewer bytes per weight. Quality is maintained since RVQ codebooks stay at F32. Download Q4_K_M talker variants from HuggingFace.

**Flash attention**: Always on by default — never pass `--no-fa`. Provides O(n) memory for the 28-layer talker (ctx 32768) and 5-layer predictor (ctx 65536). Works on Turing (sm_75) via WMMA kernels.

**Expected RTF on GTX 1650 Ti**:
| Config | RTF | Notes |
|--------|-----|-------|
| 1.7B Q8_0, CLI per chunk | 0.7-0.9 | Model load overhead per chunk |
| 1.7B Q4_K_M, CLI per chunk | 0.5-0.7 | Bandwidth savings |
| 1.7B Q4_K_M, tts-server warm | 0.4-0.6 | No model load, CUDA graph replay |
| 0.6B Q8_0, tts-server warm | 0.2-0.4 | Fastest option |
**RTF < 1.0 means faster than real-time.** The engine logs `[Perf]` lines with detailed breakdown (prefill, talker decode, predictor, codec decode, total, RTF).

**Batch/parallel generation**: Not possible. Single GPU context, autoregressive model, serialized FIFO. See [references/optimization.md](references/optimization.md) for full analysis.

## HyperFrames Narration Integration

When embedding TTS output in a HyperFrames video composition:

1. Generate per-scene audio via `bash ~/marshall-voice/tts-provider.sh /tmp/scene.txt output.mp3`
2. Measure durations with ffprobe: `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 file.mp3`
3. Concatenate with 1s silence gaps: `ffmpeg -f concat -safe 0 -i concat.txt -c copy narration_full.mp3`
4. Embed in composition: `<audio id="narration" src="./audio/narration_full.mp3" data-track-index="0" data-start="0" data-duration="TOTAL">`
5. Every `<audio>` MUST have `id`, `data-start`, and `data-duration` — HyperFrames lint errors without them
6. Text limit: keep each scene under 1800 characters (TTS provider truncates silently at 2000)

Full reference: `hyperframes-design-presets` → `references/tts-narration-pipeline.md`

## Pitfalls

- **Demucs directory path crash**: Demucs treats a directory argument as a single audio file, causing `LoadAudioError`. Always pass individual files via glob (`*.mp3 *.wav`), never a directory path.
- **Whisper NaN on CUDA (GTX 1650 Ti)**: Whisper base model produces NaN logits on this GPU even with free VRAM. Always use `device='cpu'`. Confirmed error: `ValueError: Expected parameter logits ... tensor([[nan, nan, nan]], device='cuda:0')`.
- **Duplicate background process spawning**: Each `terminal(background=True)` creates a new process. Never spawn the same long-running command twice -- check `process(action='list')` first. Multiple Demucs instances writing to the same output directory cause conflicts.
- **Embedding dimension mismatch**: 1.7B produces 2048-dim embeddings, 0.6B expects 1024-dim. If you extract with one model and generate with another, you get `ref_spk_dim 2048 mismatches talker hidden 1024`. Always extract embeddings with the same model you generate with.
- **Wrong model for generation**: User prefers 1.7B for TTS generation (better intonation). Use 0.6B only as fallback if VRAM is tight.
- **ICL mode OOM:** `--ref-text` mode encodes entire reference through codec encoder. References >15s will OOM on 4GB VRAM. Use speaker embedding extraction, `--codec-chunk-dur`, or pre-encode with `qwen-codec` and use `--ref-rvq` mode.
- **ref-rvq mode workaround:** Pre-encode reference audio with `qwen-codec --talker` to get `.rvq` + `.spk` files, then use `--ref-rvq` + `--ref-spk` + `--ref-text` for ICL mode without the codec encoder OOM. Requires a transcript file.
- **ICL mode runaway generation:** Without `--max-new`, ICL mode generates until 2048 frames (~164s). Add `--max-new 500` to cap at ~40s. The auto-splitting script uses `--max-new 500` per chunk.
- **Auto-splitting truncation:** If a single sentence exceeds MAX_CHARS (350), it will still generate and may truncate. Break very long sentences manually.
- **Codec decode OOM**: Even with speaker embedding, long output text can OOM during decode. Fix: `--codec-chunk-dur 8.0`.
- **VRAM OOM**: 1.7B BF16 (~3.9 GB) won't fit on 4GB GPU. Use GGUF Q8_0 or PyTorch with `device_map='auto'` + `max_memory` for CPU offloading.
- **Wrong import**: `from qwen_tts import Qwen3TTSModel` (not QwenTTS)
- **Wrong device param**: Use `device_map='cuda:0'` (not `device='cuda'`)
- **sox dependency**: `pip install qwen-tts` needs system `sox` package: `sudo pacman -S sox`
- **flash-attn warning**: Non-fatal. Model runs in manual PyTorch mode without it — slower but functional.
- **Auto-captions quality**: YouTube auto-captions have errors, include all speakers, and duplicate text. Use Whisper for clean transcription of extracted clips.
- **Whisper CUDA conflicts**: Whisper on CUDA may fail if GPU memory is occupied by TTS model. Use `device='cpu'`.
- **Discord file limit**: Bot upload limit is 25MB. WAV for 30+ minutes exceeds this. Compress to MP3 (64kbps) for sharing, extract final clips from original WAVs.
- **Hermes command provider case sensitivity**: Config dict keys MUST be lowercase. `_get_provider()` lowercases the name before dict lookup. `providers.Marshall` won't match `"marshall"`. See "CRITICAL: Config Key Case Sensitivity" above.
- **Discord MEDIA: tag silently dropped**: When the agent responds with BOTH text AND a `MEDIA:<path>` tag in the same message, the Discord adapter sends the text but drops the audio. Respond with ONLY the `MEDIA:<path>` tag for voice memos. Send any accompanying text as a separate message. See "Audio-First Responses" above.
- **Gateway restart from inside gateway**: Cannot run `hermes gateway restart` or `systemctl --user restart hermes-gateway` from within the gateway process — SIGTERM propagates to child processes. Use a separate shell (tmux session, SSH, or `systemctl --user restart hermes-gateway` from a non-gateway process). Note: `hermes config set` writes to disk immediately; many tools reload config on each call, so restart is only needed for config loaded at import time.
- **Bash `<<<` heredoc escapes apostrophes**: When using `<<< "$VAR"` to pipe text to qwen-tts, bash escapes single quotes in the variable (e.g., `it's` becomes `it'\\''s`). This corrupts the text and causes the TTS model to crash with a core dump (OOM-like abort). The same command works fine when run directly in terminal but fails inside a script due to heredoc escaping. Fix: use `echo "$VAR" |` pipe instead of `<<< "$VAR"`. Discovered 2026-07-13 when tts-provider.sh crashed on text containing "it's".
- **`--codec-chunk-dur` is only for buffered path**: This parameter only affects one-shot WAV decode, not streaming PCM. For sentence-level chunks (<24s audio), the default 24.0s already covers the full utterance and chunking never activates. Don't reduce it expecting per-sentence performance gains — it won't help.
- **Q4_K_M segfaults on GTX 1650 Ti:** The 1.7B Q4_K_M model crashes with a segfault in `get_rows_cuda` during inference. This appears to be a CUDA architecture compatibility issue with this specific build of qwentts.cpp. The Q8_0 variant works fine. Do not use Q4_K_M talker on this hardware.
- **tts-server OOM on 4GB VRAM:** The tts-server keeps the model loaded in VRAM, but on 4GB there's no room left for the ~590MB codec decode buffer. Short phrases (<2s audio) work, but anything longer OOMs. CLI per-chunk is the only viable approach on 4GB VRAM.
- **stream-by-line OOM on 4GB VRAM:** The `--stream-by-line` flag with `-o -` OOMs on the second line for both Q8_0 and Q4_K_M models. The streaming path allocates additional KV cache for each line, exceeding 4GB.
- **`--codec-chunk-dur` is critical for 4GB VRAM:** Even with CLI per-chunk, longer text (80+ frames) can OOM during codec decode. Setting `--codec-chunk-dur 2.0` splits the decode into smaller chunks, preventing the OOM. The default 24.0s works for short text but fails for longer outputs.
- **Rollback when changes break things:** If optimization changes break the TTS pipeline, rollback to the last known working commit (`git checkout <commit> -- tts-provider.sh`). The user explicitly asked for this when our optimization experiments broke the working pipeline. Don't try to fix forward — revert first, then investigate.
