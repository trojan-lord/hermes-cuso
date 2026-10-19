# Qwen3 TTS — Setup & VRAM Reference (2026-07-13)

## Hardware: GTX 1650 Ti (3.64 GB VRAM)

### Model VRAM Requirements

| Model | Precision | VRAM | Fits 4GB GPU? |
|-------|-----------|------|---------------|
| 0.6B-Base | BF16 | ~1.8 GB | ✅ Yes |
| 0.6B-Base | Q8_0 GGUF | ~1.5 GB | ✅ Yes |
| 1.7B-Base | BF16 | ~3.9 GB | ❌ OOM (3.64 GB total) |
| 1.7B-Base | Q8_0 GGUF | ~2.1 GB | ✅ Yes (preferred) |
| 1.7B-Base | Q4_K_M GGUF | ~1.2 GB | ✅ Yes (avoid — worse than 0.6B Q8_0) |

### Primary Method: GGUF via qwentts.cpp

This is the production method. Python scripts were deleted — use GGUF binaries.

```bash
# Build qwentts.cpp with CUDA
cd ~
git clone --recurse-submodules https://github.com/ServeurpersoCom/qwentts.cpp.git
cd qwentts.cpp
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

### Python Setup (for Whisper transcription only)

```bash
python3 -m venv ~/qwen3-tts-env
source ~/qwen3-tts-env/bin/activate
pip install openai-whisper  # for transcription, not TTS
sudo pacman -S sox  # system dependency
```

### Key Binaries

- `~/qwentts.cpp/build/qwen-tts` — TTS generation
- `~/qwentts.cpp/build/qwen-codec` — Speaker embedding extraction
- `~/qwentts.cpp/build/tts-server` — HTTP API server

### Model Selection

**Use 1.7B Q8_0 for everything** — better intonation than 0.6B after A/B comparison. 0.6B is fallback only if VRAM is tight.

| Task | Model | Why |
|------|-------|-----|
| Speaker embedding extraction | 1.7B Q8_0 | Larger model captures richer voice characteristics |
| TTS generation | 1.7B Q8_0 | Better intonation, preferred by user |
| TTS fallback (low VRAM) | 0.6B Q8_0 | Lighter, acceptable quality |

### Embedding Dimension Mismatch

1.7B produces 2048-dim embeddings. 0.6B expects 1024-dim. **Always extract with the same model you generate with.**

```bash
# Extract with 1.7B (for 1.7B generation)
~/qwentts.cpp/build/qwen-codec \
    --model ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --talker ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    -i reference.wav
# Creates reference.spk (2048-dim)

# Extract with 0.6B (for 0.6B generation)
~/qwentts.cpp/build/qwen-codec \
    --model ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --talker ~/qwentts.cpp/models/qwen-talker-0.6b-base-Q8_0.gguf \
    -i reference.wav
# Creates reference.spk (1024-dim)
```

### ICL Mode (Best Quality)

Pre-encode reference offline, then use at inference without codec encoder OOM:

```bash
# Step 1: Extract .rvq + .spk (one-time)
~/qwentts.cpp/build/qwen-codec \
    --model ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --talker ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    -i reference.wav

# Step 2: Generate with pre-encoded reference
echo "Text to speak" | ~/qwentts.cpp/build/qwen-tts \
    --model ~/qwentts.cpp/models/qwen-talker-1.7b-base-Q8_0.gguf \
    --codec ~/qwentts.cpp/models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --ref-rvq reference.rvq \
    --ref-spk reference.spk \
    --ref-text reference_transcript.txt \
    --codec-chunk-dur 4.0 \
    --max-new 500 \
    -o output.wav
```

**Pitfall:** ref-rvq mode needs `--ref-text` with accurate transcript. Wrong transcript = gibberish.
**Pitfall:** Always add `--max-new 500` to cap output length. Without it, generates until 2048 frames.

### Key API Notes

- Tokenizer is model-agnostic: `Qwen3TTSTokenizer()` takes no arguments
- Both 0.6B and 1.7B share the same tokenizer/embedding space
- `--codec-chunk-dur 4.0` prevents OOM during codec decode (mandatory for 1.7B on 4GB GPU)
