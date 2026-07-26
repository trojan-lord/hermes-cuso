# Qwen3 TTS Architecture Reference

Condensed knowledge from source code inspection (qwentts.cpp) and Qwen3 TTS documentation, gathered 2026-07-17.

## Three Modes (determined by GGUF model file)

| Mode | GGUF suffix | Description | Flags |
|------|-------------|-------------|-------|
| **Base** | `base` | Default voice + voice cloning via reference audio. Has built-in speaker encoder. | `--ref-wav` or `--ref-rvq`/`--ref-spk` |
| **CustomVoice** | `customvoice` | Named speaker library (Eric, Dylan, etc.) — preset voices, no cloning. | `--speaker <name>` |
| **VoiceDesign** | `voicedesign` | Describe voice in text, model synthesizes matching voice. 1.7B only. | `--instruct "young male, deep pitch..."` |

**Two model sizes:** 0.6B and 1.7B. VoiceDesign is 1.7B exclusive.

## Three Ways to Use Base Mode (same GGUF)

| Approach | Flags | How it works | Best for |
|----------|-------|-------------|----------|
| **Plain (no ref)** | none | Model uses built-in default voice | Quick tests |
| **Zero-shot** | `--ref-wav ref.wav --ref-text ref.txt` | Model extracts speaker embedding on-the-fly | Quick testing, single reference |
| **ICL (pre-encoded)** | `--ref-rvq ref.rvq --ref-spk ref.spk --ref-text ref.txt` | Pre-extracted latents from `qwen-codec --talker`, reused across generations | Production (faster per-gen, no re-encoding) |

ICL is an optimization of zero-shot: encode once, reuse forever. Same model, same quality, less per-request overhead.

## X-Vector Mode vs ICL Mode (Mode A vs Mode B)

These are NOT the same thing. The Base checkpoint contains two distinct voice cloning mechanisms:

### Mode A: X-Vector Only (zero-shot, no transcript)
- The ECAPA-TDNN speaker encoder compresses the reference audio into a **single 2048-dimensional vector** (the x-vector)
- This vector is placed at position 6 in the codec embedding stream
- The model generates speech conditioned on this fixed vector
- **Flags:** `--ref-wav ref.wav` (without `--ref-text`) or `--ref-spk ref.spk`
- **Python:** `x_vector_only_mode=True` (no ref_text needed)
- **Quality:** Coarse voice identity. Captures "what this person sounds like" but not their speaking patterns

### Mode B: ICL / In-Context Learning (with transcript)
- The model receives the **actual audio tokens** (all 16 RVQ codebooks across every frame) plus the transcript text
- The reference text and codes are prepended to the prompt so the model continues the speaker
- This is few-shot learning on actual audio tokens, not a compressed summary
- **Flags:** `--ref-rvq ref.rvq --ref-spk ref.spk --ref-text ref.txt` (all three required)
- **Python:** default mode when ref_text is provided
- **Quality:** Much better prosody and speaking patterns. The model learns from the actual acoustic patterns, not just a vector summary

**Analogy:** X-vector is like showing someone a photo of a face. ICL is like showing them a video of the person talking and letting them learn the voice from context.

**The official API parameter is `x_vector_only_mode=False`** (default = ICL when ref_text is provided, x-vector only when ref_text is absent).

**RVC is architecturally closer to x-vector** — it extracts speaker features and retrieves similar features from an index. Qwen ICL is structurally different: few-shot learning on actual audio tokens. This is why ICL generally outperforms RVC for voice identity: it has more information at inference time.

## Hardware Implications by Mode

**The modes do NOT meaningfully affect VRAM usage.** The big memory consumers are identical across all modes:
- Talker LM: 0.6B (~993MB Q8_0) or 1.7B (~2.0GB Q8_0)
- Codec GGUF: ~244MB Q4_K_M
- KV cache: 4096 frames (same size regardless of mode)

Differences:
- Base mode: includes speaker encoder tensors (small, part of the Base GGUF). Used for zero-shot and ICL modes.
- CustomVoice: speaker embeddings pre-stored in a table, no encoder needed. GGUF slightly smaller.
- VoiceDesign: no speaker encoder, no speaker table. Conditioning comes from text description via `--instruct`.

All modes consume essentially the same VRAM. Pick based on what you want to do, not hardware.

## ICL Context Budget

**Talker KV cache: 4096 frames total (at 12.5 Hz = ~328 seconds).**

Both the ICL reference prefix and the generated output share this same budget.

### Reference Clip Length
- ICL reference occupies a prefix in the KV cache
- Tested in production: ~250 frames (~20 seconds) — source code comment: "longest ICL prompt observed is ~250"
- **No hard cap in code** — 4096 frames theoretically allows ~328 seconds of reference
- But model was **trained** on references up to ~20 seconds; beyond that is unvalidated
- **Practical sweet spot: 10-20 seconds of clean, isolated speech**
- Longer references introduce more variability that dilutes the voice signal

### Output Generation Length
- Default `--max-new`: 2048 frames (~164 seconds)
- Production: `--max-new 500` (~42 seconds per chunk)
- Voice quality degrades beyond ~50-60 seconds — the model "gets tired"
- Split long text at sentence boundaries, generate each chunk separately

### Budget Example
Current production: clip_07_trimmed_start (8.0s, ~200 frames) + output cap 500 frames = 700 / 4096 = 17%. Massive headroom.

## ICL Transcript Accuracy (Critical)

**The transcript MUST match the reference audio exactly.** ICL mode uses text-audio alignment during the forward pass — it aligns text tokens to audio frames. Wrong text means the model learns from misaligned data.

Real example: our old reference .txt said "pufferfish, and..." but the audio actually said "pufferfish and" (no comma, no ellipsis, abrupt cut). Whisper confirmed the accurate transcript was different from what we had written. Even punctuation differences matter because ICL aligns text tokens to audio frames.

**After ANY clip change:** run Whisper on the exact reference clip and use that output verbatim for the .txt file.

## Emotion Control

**Qwen3 TTS Base mode does NOT support emotion tags.** Writing `[Angry]` in the prompt will either be ignored or read literally as the word "angry." There is no style or emotion conditioning in the Base model.

The model clones **voice timbre** from the reference, but delivery (prosody, energy, emotional tone) is fixed to whatever the reference clip sounds like.

**Fine-tuning with CustomVoice solves this.** After fine-tuning, the `generate_custom_voice()` function supports an `instruct` parameter. You can pass natural language instructions like "speak in a panicked tone" or "slow down and sound uncertain." This is the emotion control we were trying to hack with RVC.

## Voice Design then Clone Workflow

Official workflow from the Qwen3-TTS docs for creating a consistent, reusable character voice:

1. Use **VoiceDesign** model to synthesize a short reference clip matching your target persona
2. Feed that clip into `create_voice_clone_prompt()` to build a reusable prompt
3. Call `generate_voice_clone()` with `voice_clone_prompt` — no re-extraction needed

```python
# Step 1: Design the voice
design_model = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", ...)
ref_wavs, sr = design_model.generate_voice_design(
    text="H-hey! You dropped your... uh... calculus notebook?",
    language="English",
    instruct="Male, 17 years old, tenor range, gaining confidence"
)

# Step 2: Build reusable clone prompt
clone_model = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", ...)
voice_clone_prompt = clone_model.create_voice_clone_prompt(
    ref_audio=(ref_wavs[0], sr),
    ref_text="H-hey! You dropped your... uh... calculus notebook?",
)

# Step 3: Generate with any text, reusing the cached prompt
wavs, sr = clone_model.generate_voice_clone(
    text="New text to speak",
    language="English",
    voice_clone_prompt=voice_clone_prompt,
)
```

**Key insight:** `create_voice_clone_prompt()` builds the clone prompt once and caches it. Subsequent `generate_voice_clone()` calls skip the reference re-extraction. This is what the official API recommends for production use.

**We should be using this in our tts-provider.sh** instead of passing `--ref-rvq`/`--ref-spk`/`--ref-text` every invocation (though the GGUF CLI may not support this caching pattern directly).

## Kokoro vs Qwen3 TTS

**We use Qwen3 TTS 1.7B, NOT Kokoro.**

| Feature | Qwen3 TTS 1.7B | Kokoro 82M |
|---------|---------------|------------|
| Parameters | 1.7B | 82M (21x smaller) |
| Multi-reference ICL | Single `--ref-rvq` only | Native multi-reference |
| Voice cloning quality | Excellent | Mediocre |
| Maintenance | Active | Stalled |
| Company | Qwen/Alibaba | Helium |

Kokoro's multi-reference feature is convenient but the cloning quality is much worse due to the size difference. Qwen with one good reference outperforms Kokoro with multiple references. Voice cloning quality scales with model size.

## Demucs-Cleaned Audio Improves ICL

Clean vocal separation removes background noise that adds "junk" tokens to the reference. With raw audio, the model sees the character's voice mixed with music, SFX, and other speakers — each noise token consumes context budget without helping voice matching. Clean audio means every frame carries useful voice information, so shorter references achieve the same or better quality.

## Concatenation Strategy for Expanded References

qwentts.cpp `--ref-rvq` accepts **ONE reference file**. To use multiple clips:
1. Cherry-pick best 10-20 second lines from Demucs tracks
2. Concatenate into one file: `ffmpeg -f concat -safe 0 -i list.txt -ar 24000 -ac 1 combined_ref.wav`
3. Combine transcripts in matching order
4. Run through `qwen-codec --talker` to get `.rvq` + `.spk`
5. Use as single ICL reference

The model sees a wider variety of the same voice across contexts, producing more robust matching than a single long clip.

**Critical:** transcript must match concatenated audio order exactly. Wrong order = gibberish output.

## Fine-Tuning the Base Model (Official Support)

The Qwen3-TTS repo has official single-speaker fine-tuning. After fine-tuning, the voice is baked into the model weights — no reference audio at inference, no ICL, no RVC. The model IS the voice.

### Fine-Tuning Workflow
1. Prepare JSONL with `{"audio": "path.wav", "text": "transcript", "ref_audio": "ref.wav"}`
2. Run `prepare_data.py` (needs tokenizer + GPU, lightweight — ~244MB VRAM)
3. Run `sft_12hz.py` (full training — needs ~13GB for 1.7B, ~5-6GB for 0.6B)
4. Output checkpoint loads as CustomVoice speaker with `generate_custom_voice()`

### What Happens at Checkpoint Save
At checkpoint save, the script:
- Changes model type from "base" to "custom_voice"
- Drops the entire speaker encoder from weights
- Bakes the speaker embedding into `codec_embedding.weight[3000]`

The fine-tuned model does NOT need the speaker encoder at inference. Voice is part of the weight matrix. Call `generate_custom_voice()` with speaker name, done.

### Fine-Tuning Supports Instruct for Emotion
CustomVoice mode supports the `instruct` parameter. After fine-tuning, you can pass natural language instructions like "speak in a panicked tone" or "slow down and sound uncertain." This is the emotion control we have been trying to hack with RVC.

### Hardware Requirements
- Model weights in bf16: ~3.4 GB (1.7B) or ~1.2 GB (0.6B)
- AdamW optimizer states (2x fp32): ~6.8 GB (1.7B) or ~2.4 GB (0.6B)
- Gradient buffers: ~3.4 GB (1.7B)
- **1.7B total: ~13 GB minimum. Does NOT fit on 4GB.**
- **0.6B total: ~5-6 GB. Tight but possible with CPU offloading.**

### Feasible Options for 4GB GPU
1. **LoRA fine-tuning** — Only trains low-rank adapter matrices (~20 MB). Frozen 1.7B stays in bf16. Would fit comfortably. Not in official script yet but straightforward to add.
2. **Full fine-tune on 0.6B** — With batch_size 1 and CPU offloading of optimizer states. Slow but technically possible.
3. **CPU-only fine-tune** — Dead slow (hours instead of minutes) but guaranteed to work. 0.6B weights fit in system RAM.

### `prepare_data.py` is Lightweight
The data prep step only needs the tokenizer model (~244 MB), not the full TTS. This step works fine on 4GB GPU.

## User's Preferred Path: ICL + Fine-Tuning (No RVC)

The user has explicitly rejected RVC as an approach. The preferred path is:
1. Use ICL mode for immediate voice cloning (current production)
2. Eventually fine-tune the Base model for persistent voice identity with emotion control via instruct

RVC was considered for emotion control but the user determined that fine-tuning with CustomVoice's `instruct` parameter solves this natively. No voice conversion pipeline needed.

## Speaker Embedding Filtering Pipeline (For Multi-Character Demucs Audio)

When Demucs vocals contain multiple speakers (e.g., TV show clips with Marshall + other characters), use the ECAPA-TDNN speaker encoder to filter down to target-speaker-only segments:

1. **Chunk** each Demucs vocal track into 3-second windows with 1-second overlap
2. **Extract speaker embeddings** for every chunk using `qwen-codec --talker` (the same ECAPA-TDNN used for ICL references)
3. **Compare** each chunk's embedding against the target speaker's reference embedding using cosine similarity
4. **Filter** — keep only high-similarity chunks (threshold ~0.85+)
5. **Stitch** filtered chunks into one long Marshall-only audio file
6. **Transcribe** with Whisper to get accurate timestamps and text
7. **Feed into fine-tuning** as the training data

**Why this works:** The ECAPA-TDNN speaker encoder is already part of our Qwen TTS base model. It outputs 2048-dimensional vectors that represent "who is speaking." The reference .spk file we already have IS Marshall's embedding. Computing cosine similarity between each chunk's embedding and Marshall's reference tells us whether that chunk is Marshall or someone else.

**Performance estimate:** 28 Demucs tracks at ~5 hours total → ~9000 three-second chunks → ~15 minutes for embedding extraction on CPU → filter + stitch is instant. No GPU needed for the filtering step.

This eliminates the need for manual speaker identification (the old "concatenate → user listens → timestamps" approach) and scales to any number of source tracks.

## Community Implementations (Qwen3 TTS + RVC)

For reference only — user has rejected RVC path in favor of fine-tuning:
- **MimikaStudio** (639 stars): macOS app, Qwen3-TTS + RVC
- **TTS-Audio-Suite** (1,096 stars): ComfyUI node, multi-engine
- **RVCBench**: Referenced as academic benchmark. UNVERIFIED — treat citation with skepticism.

Community consensus: Qwen and RVC complement, not replace. But fine-tuning is the superior path when you have enough clean training data.

## Max Text Length Config

`max_text_length: 2000` in Hermes config truncates input BEFORE reaching the TTS provider. Long voice memo prompts (500+ chars) get cut off silently. Keep prompts under 1800 characters.
