---
name: qwen-voice-cloning
description: >
  End-to-end voice cloning pipeline using Qwen3-TTS. Covers video acquisition,
  vocal separation, speaker filtering, transcription, fine-tuning, and inference.
  Optimized for single-speaker extraction from multi-speaker video content.
category: mlops
tags: [voice, tts, qwen, cloning, demucs, whisper, fine-tuning]
---

# Qwen3-TTS Voice Cloning Pipeline

Complete workflow for cloning a specific speaker's voice from video content using Qwen3-TTS, Demucs, Whisper, and ECAPA-TDNN speaker embeddings.

## Overview

```
Video URLs → yt-dlp → Demucs (vocal separation) → Speaker Filtering (ECAPA-TDNN)
    → Whisper (transcription) → Fine-tuning (Qwen3-TTS) → Custom Voice Model
```

## Hardware Requirements

- **GPU:** 4GB+ VRAM for inference (Qwen3 TTS 1.7B in Q8_0 = ~1.8GB)
- **GPU:** 8GB+ VRAM for fine-tuning (1.7B model + optimizer states)
- **RAM:** 16GB+ recommended for CPU fallback
- **Disk:** ~50GB for models + pipeline output
- **Note:** Speaker filtering runs efficiently on CPU (~150s for 5 hours of audio)

## Prerequisites

```bash
# Create isolated environment
python3 -m venv ~/voice-clone-env
source ~/voice-clone-env/bin/activate

# Core dependencies
pip install torch torchaudio
pip install qwen-tts
pip install librosa soundfile
pip install openai-whisper
pip install yt-dlp

# Demucs (for vocal separation)
pip install demucs

# Optional: FlashAttention for faster inference
pip install flash-attn --no-build-isolation
```

## Step 1: Video Acquisition

Download audio from video sources using yt-dlp.

```bash
# Single video
yt-dlp -x --audio-format wav --audio-quality 0 -o "%(id)s.%(ext)s" <URL>

# Playlist
yt-dlp -x --audio-format wav --audio-quality 0 \
    -o "raw/%(id)s.%(ext)s" <PLAYLIST_URL>

# Batch download from file
while read url; do
    yt-dlp -x --audio-format wav --audio-quality 0 \
        -o "raw/%(id)s.%(ext)s" "$url"
done < urls.txt
```

**Tips:**
- Use `--audio-format wav` to avoid re-encoding losses
- `--audio-quality 0` ensures highest quality
- The `%(id)s` template uses the YouTube video ID as filename

## Step 2: Vocal Separation (Demucs)

Separate vocals from background music/noise using Demucs.

```bash
# Activate environment
source ~/voice-clone-env/bin/activate

# Process single file
python -m demucs --two-stems=vocals -n htdemucs -d cuda:0 input.wav

# Batch process directory
python -m demucs --two-stems=vocals -n htdemucs -d cuda:0 \
    -o output_dir/ input_dir/

# Process with specific output format
python -m demucs --two-stems=vocals -n htdemucs -d cuda:0 \
    --mp3 --mp3-bitrate 320 \
    -o output_dir/ input.wav
```

**Model recommendation:**
- `htdemucs` (Hybrid Transformer): Best quality, ~42M params
- `htdemucs_ft`: Fine-tuned variant, slightly better
- Processing time: ~0.3x real-time on GTX 1650 Ti

**Output structure:**
```
output_dir/
└── htdemucs/
    └── <video_id>/
        ├── vocals.wav    # <- Use this
        └── no_vocals.wav
```

## Step 3: Speaker Filtering (ECAPA-TDNN)

Extract only segments where the target speaker is talking using speaker embeddings and cosine similarity.

### How It Works

1. **Load reference embedding:** Extract speaker embedding from a known clip of the target speaker
2. **Chunk audio:** Split Demucs vocals into overlapping segments (4 seconds, 1.5 second overlap)
3. **Compute embeddings:** Run each chunk through ECAPA-TDNN speaker encoder
4. **Compare:** Calculate cosine similarity against reference
5. **Filter:** Keep chunks above similarity threshold (0.80-0.95)
6. **Stitch:** Concatenate matching segments into single audio file

### Reference Embedding Extraction

```python
# Using qwentts.cpp (C++ binary)
cd ~/qwentts.cpp
./build/qwen-codec \
    --model models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --talker models/qwen-talker-1.7b-base-Q8_0.gguf \
    -i /path/to/reference_clip.wav

# Output: reference_clip.rvq + reference_clip.spk
# The .spk file contains the 2048-dim speaker embedding
```

**Reference clip requirements:**
- 5-15 seconds of clean speech
- Single speaker only (no overlap)
- Minimal background noise
- Natural speaking pace (not whispered or shouted)

### Speaker Filtering Script

```python
#!/usr/bin/env python3
"""extract_speaker.py - Filter audio for target speaker"""

import os
import struct
import numpy as np
import librosa
import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

def load_spk_embedding(path: str) -> np.ndarray:
    """Load .spk file (2048 float32 values)."""
    with open(path, "rb") as f:
        data = f.read()
    return np.array(struct.unpack(f"{len(data)//4}f", data), dtype=np.float32)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm_a, norm_b = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (norm_a * norm_b)) if norm_a and norm_b else 0.0

def extract_embeddings(chunks, model):
    """Extract speaker embeddings using ECAPA-TDNN."""
    inner_model = model.model
    embeddings = []
    for chunk in chunks:
        with torch.no_grad():
            emb = inner_model.extract_speaker_embedding(chunk, 24000)
            embeddings.append(emb.cpu().numpy().flatten())
    return embeddings

def main():
    # Configuration
    REFERENCE_SPK = "path/to/reference.spk"
    INPUT_AUDIO = "path/to/vocals.wav"
    OUTPUT_AUDIO = "path/to/filtered.wav"
    THRESHOLD = 0.85  # Adjust based on quality requirements
    CHUNK_SEC = 4.0
    OVERLAP = 1.5

    # Load reference
    ref_embedding = load_spk_embedding(REFERENCE_SPK)

    # Load model (loads once, processes all chunks)
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        device_map="cpu",  # or "cuda:0" for GPU
        dtype=torch.float32,
    )

    # Chunk audio
    audio, sr = librosa.load(INPUT_AUDIO, sr=24000, mono=True)
    chunk_samples = int(CHUNK_SEC * sr)
    step_samples = int((CHUNK_SEC - OVERLAP) * sr)

    chunks = []
    starts = []
    start = 0
    while start + chunk_samples <= len(audio):
        chunks.append(audio[start:start+chunk_samples])
        starts.append(start / sr)
        start += step_samples

    print(f"Processing {len(chunks)} chunks...")

    # Extract embeddings
    embeddings = extract_embeddings(chunks, model)

    # Filter by similarity
    matches = []
    for i, (emb, start_sec) in enumerate(zip(embeddings, starts)):
        sim = cosine_similarity(ref_embedding, emb)
        if sim >= THRESHOLD:
            matches.append((chunks[i], start_sec, sim))
            print(f"  MATCH [{sim:.4f}] {start_sec:.1f}s")

    print(f"\n{len(matches)}/{len(chunks)} chunks matched")

    # Stitch matches
    if matches:
        silence = np.zeros(int(0.3 * sr), dtype=np.float32)
        segments = []
        for i, (chunk, _, _) in enumerate(sorted(matches, key=lambda x: x[1])):
            segments.append(chunk)
            if i < len(matches) - 1:
                segments.append(silence)

        combined = np.concatenate(segments)
        sf.write(OUTPUT_AUDIO, combined, sr)
        print(f"Stitched: {len(combined)/sr:.1f}s -> {OUTPUT_AUDIO}")

if __name__ == "__main__":
    main()
```

### Threshold Guide

| Threshold | Quality | Use Case |
|-----------|---------|----------|
| >= 0.95 | Highest | Fine-tuning, production use |
| 0.90-0.95 | High | Good for training data |
| 0.85-0.90 | Medium | Acceptable, review recommended |
| 0.80-0.85 | Low | May include other speakers |

### Performance Benchmarks (Real-World)

Tested on 28 Demucs vocal tracks (5+ hours of audio), GTX 1650 Ti CPU:

| Metric | Value |
|--------|-------|
| Total chunks processed | ~3500 |
| Matches at threshold 0.80 | 3705 (overlapping windows) |
| After deduplication | 1658 segments |
| Total extracted audio | ~118 minutes |
| High-confidence (>=0.95) | 695 segments (46 min) |
| Good (>=0.90) | 1241 segments (83 min) |
| Median similarity | 0.94 |
| Processing time (CPU) | 149 seconds |
| Model load time | ~25 seconds |

### Critical API Gotchas

1. **`extract_speaker_embedding()` expects numpy, NOT tensor.** Passing a torch tensor causes `TypeError: expected np.ndarray (got Tensor)`. The audio chunk must be a raw numpy array.

2. **Model hierarchy:** `Qwen3TTSModel` is a wrapper. The actual model is at `model.model`. Speaker encoder is at `model.model.speaker_encoder`.

3. **No `eval()` method:** `Qwen3TTSModel` is not a raw `nn.Module`. Calling `model.eval()` raises `AttributeError`. The model handles eval mode internally.

4. **C++ binary is ~100x slower for batch processing.** `qwen-codec` loads the full 1.7B model from disk for EVERY chunk. The Python API loads once and processes all chunks. Always use the Python API for speaker filtering.

5. **Reference clip consistency:** Use the SAME reference clip everywhere -- tts-provider, extraction pipeline, ICL generation. Changing the reference changes the speaker embedding, which affects filtering results.

## Step 4: Transcription (Whisper)

Transcribe the filtered audio for fine-tuning data preparation.

```python
#!/usr/bin/env python3
"""transcribe_filtered.py - Generate training data from filtered audio"""

import json
import whisper
import soundfile as sf

def main():
    INPUT_AUDIO = "path/to/filtered.wav"
    OUTPUT_JSONL = "path/to/train_raw.jsonl"
    REFERENCE_AUDIO = "path/to/reference.wav"  # Same reference used for filtering

    # Load Whisper model
    model = whisper.load_model("base", device="cpu")

    # Transcribe with word-level timestamps
    result = model.transcribe(
        INPUT_AUDIO,
        language="en",
        fp16=False,
        word_timestamps=True,
    )

    # Save full transcription
    with open("transcription.txt", "w") as f:
        f.write(result["text"].strip())

    # Generate JSONL for fine-tuning
    with open(OUTPUT_JSONL, "w") as f:
        for seg in result["segments"]:
            # Skip very short segments (< 1 second)
            if seg["end"] - seg["start"] < 1.0:
                continue

            entry = {
                "audio": INPUT_AUDIO,
                "text": seg["text"].strip(),
                "ref_audio": REFERENCE_AUDIO,
                "language": "English",
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Transcription: transcription.txt")
    print(f"Training data: {OUTPUT_JSONL}")

if __name__ == "__main__":
    main()
```

## Step 5: Fine-tuning

Fine-tune Qwen3-TTS Base model on the filtered, transcribed audio.

### Data Preparation

```bash
# Clone the official repo
git clone https://github.com/QwenLM/Qwen3-TTS.git
cd Qwen3-TTS/finetuning

# Extract audio codes (needs GPU)
python prepare_data.py \
    --device cuda:0 \
    --tokenizer_model_path Qwen/Qwen3-TTS-Tokenizer-12Hz \
    --input_jsonl /path/to/train_raw.jsonl \
    --output_jsonl train_with_codes.jsonl
```

### Training

```bash
# Fine-tune the model
python sft_12hz.py \
    --init_model_path Qwen/Qwen3-TTS-12Hz-1.7B-Base \
    --output_model_path output \
    --train_jsonl train_with_codes.jsonl \
    --batch_size 2 \
    --lr 2e-5 \
    --num_epochs 3 \
    --speaker_name "target_speaker"
```

**Training tips:**
- Start with `batch_size=2` for 4GB VRAM, increase if memory allows
- `lr=2e-5` is conservative; try `1e-5` if loss oscillates
- 3 epochs is usually sufficient; monitor validation loss
- Checkpoints saved at `output/checkpoint-epoch-{0,1,2}`

### VRAM Optimization

For limited VRAM (4GB):
- Use `batch_size=1`
- Enable gradient accumulation: `accelerate config` → select "DeepSpeed ZeRO Stage 2"
- Or fine-tune the 0.6B model instead of 1.7B

For more VRAM (8GB+):
- `batch_size=4-8`
- Enable mixed precision (default in script)
- FlashAttention recommended

## Step 6: Inference

### Using Python API

```python
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

# Load fine-tuned model
model = Qwen3TTSModel.from_pretrained(
    "output/checkpoint-epoch-2",  # Or your fine-tuned path
    device_map="cuda:0",
    dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",  # Optional, faster
)

# Generate speech
wavs, sr = model.generate_custom_voice(
    text="Hello, this is a test of the cloned voice.",
    language="English",
    speaker="target_speaker",  # Name used during fine-tuning
    instruct="Speak in a calm, natural tone.",  # Optional emotion control
)

sf.write("output.wav", wavs[0], sr)
```

### Using C++ Binary (qwentts.cpp)

```bash
# For fine-tuned models, use the Python API above
# For zero-shot ICL cloning (no fine-tuning):

# First extract reference features
cd ~/qwentts.cpp
./build/qwen-codec \
    --model models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --talker models/qwen-talker-1.7b-base-Q8_0.gguf \
    -i /path/to/reference.wav

# Generate speech
echo "Hello, this is a test." | ./build/qwen-tts \
    --model models/qwen-talker-1.7b-base-Q8_0.gguf \
    --codec models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --ref-rvq /path/to/reference.rvq \
    --ref-spk /path/to/reference.spk \
    --ref-text "Transcript of the reference audio" \
    --max-new 2048 \
    -o output.wav
```

### ICL vs Fine-tuning

| Aspect | ICL (Zero-shot) | Fine-tuning |
|--------|-----------------|-------------|
| Setup time | Minutes | Hours |
| Data required | 5-15s reference | 5-30min audio |
| Voice quality | Good | Excellent |
| Emotion control | Limited | Full (via instruct) |
| VRAM (inference) | ~1.8GB | ~1.8GB |
| VRAM (training) | N/A | ~4-8GB |

## Complete Pipeline Script

```bash
#!/bin/bash
# voice_clone_pipeline.sh - End-to-end voice cloning

set -e

# Configuration
SOURCE_URLS="urls.txt"
REFERENCE_CLIP="reference.wav"
OUTPUT_DIR="output"
THRESHOLD=0.85
SPEAKER_NAME="target_speaker"

# Create directories
mkdir -p "$OUTPUT_DIR"/{raw,demucs,filtered,transcribed,finetuned}

# Step 1: Download videos
echo "[1/6] Downloading videos..."
while read url; do
    yt-dlp -x --audio-format wav --audio-quality 0 \
        -o "$OUTPUT_DIR/raw/%(id)s.%(ext)s" "$url"
done < "$SOURCE_URLS"

# Step 2: Demucs separation
echo "[2/6] Separating vocals..."
python -m demucs --two-stems=vocals -n htdemucs -d cuda:0 \
    -o "$OUTPUT_DIR/demucs/" "$OUTPUT_DIR/raw/"

# Step 3: Speaker filtering
echo "[3/6] Filtering for target speaker..."
python extract_speaker.py \
    --reference "$REFERENCE_CLIP" \
    --input-dir "$OUTPUT_DIR/demucs/htdemucs/" \
    --output "$OUTPUT_DIR/filtered/vocals.wav" \
    --threshold "$THRESHOLD"

# Step 4: Transcription
echo "[4/6] Transcribing..."
python transcribe_filtered.py \
    --input "$OUTPUT_DIR/filtered/vocals.wav" \
    --output "$OUTPUT_DIR/transcribed/train_raw.jsonl" \
    --reference "$REFERENCE_CLIP"

# Step 5: Fine-tuning
echo "[5/6] Fine-tuning..."
cd Qwen3-TTS/finetuning
python prepare_data.py \
    --device cuda:0 \
    --tokenizer_model_path Qwen/Qwen3-TTS-Tokenizer-12Hz \
    --input_jsonl "$OUTPUT_DIR/transcribed/train_raw.jsonl" \
    --output_jsonl train_with_codes.jsonl

python sft_12hz.py \
    --init_model_path Qwen/Qwen3-TTS-12Hz-1.7B-Base \
    --output_model_path "$OUTPUT_DIR/finetuned" \
    --train_jsonl train_with_codes.jsonl \
    --batch_size 2 \
    --lr 2e-5 \
    --num_epochs 3 \
    --speaker_name "$SPEAKER_NAME"

echo "[6/6] Done!"
echo "Model saved to: $OUTPUT_DIR/finetuned/"
```

## Troubleshooting

### Common Issues

**1. "CUDA out of memory" during fine-tuning**
- Reduce `batch_size` to 1
- Use the 0.6B model instead of 1.7B
- Enable gradient checkpointing

**2. Poor voice quality after fine-tuning**
- Check reference audio quality (clean, single speaker)
- Increase training data (more epochs or more audio)
- Adjust learning rate (try `1e-5` for more stability)

**3. Speaker filtering too aggressive/lenient**
- Adjust `THRESHOLD` (0.80-0.95)
- Use longer reference clip (10-15 seconds)
- Ensure reference clip is clean and representative

**4. Demucs leaves artifacts**
- Try `htdemucs_ft` model instead
- Process at higher quality (WAV, not MP3)
- Check input audio quality

**5. Whisper transcription inaccurate**
- Use larger Whisper model (`medium` or `large`)
- Ensure audio is clean (Demucs output)
- Manually verify and correct transcripts

**6. `TypeError: expected np.ndarray (got Tensor)` during speaker filtering**
- `extract_speaker_embedding()` expects a numpy array, not a torch tensor
- Pass `audio_chunk` directly (numpy), not `torch.from_numpy(audio_chunk)`

**7. `AttributeError: 'Qwen3TTSModel' has no attribute 'eval'`**
- Qwen3TTSModel is a wrapper, not a raw nn.Module
- Remove the `model.eval()` call -- the model handles this internally

**8. Whisper NaN on CUDA (GTX 1650 Ti)**
- Whisper produces NaN logits on this GPU even with free VRAM
- Always use `--device cpu --fp16 False` for Whisper on this hardware

## Performance Benchmarks

On GTX 1650 Ti (4GB VRAM):

| Stage | Time | Notes |
|-------|------|-------|
| yt-dlp download | ~30s/video | Depends on length |
| Demucs separation | ~0.3x real-time | GPU accelerated |
| Speaker filtering | ~150s/5hours audio | CPU, batch processing |
| Whisper transcription | ~0.5x real-time | CPU, base model |
| Fine-tuning (3 epochs) | ~2-4 hours | batch_size=2, 30min data |
| Inference | ~1-2s/second audio | GPU, 1.7B model |

## References

- [Qwen3-TTS Official Repo](https://github.com/QwenLM/Qwen3-TTS)
- [Qwen3-TTS Fine-tuning Docs](https://github.com/QwenLM/Qwen3-TTS/tree/main/finetuning)
- [Demucs Documentation](https://github.com/facebookresearch/demucs)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [ECAPA-TDNN Paper](https://arxiv.org/abs/2005.07143)
