# qwentts.cpp Performance Optimization Reference

Research findings from codebase analysis (commit d17c33d, 2026-07-12).

## Architecture Summary

Qwen3-TTS 12 Hz is a two-stage autoregressive system:
1. **Talker LM** (Qwen3 0.6B/1.7B): generates semantic codebook 0, one frame at a time
2. **Code Predictor MTP head** (5-layer, hidden 1024): expands c0 into 15 acoustic codes per frame
3. **Audio Codec** (SEANet + DAC v2): converts 12.5 Hz codes → 24 kHz mono audio

Key constants: 12.5 frames/sec, 1920 samples/frame, 16 codebooks (1 semantic + 15 acoustic).

## Quantization Impact on Speed

The talker backbone is what gets quantized (Q4_K_M or Q8_0). The codec (tokenizer) weights stay F32 for RVQ codebooks — nearest-neighbor lookup is sensitive to per-row noise.

**Why Q4_K_M is faster on bandwidth-limited GPUs:**
- Matrix multiply memory bandwidth: Q4_K_M reads ~50% fewer bytes per weight vs Q8_0
- On GPUs where memory bandwidth > compute (all consumer GPUs), this directly translates to faster inference
- Estimated 20-40% speedup on GTX 1650 Ti (320 GB/s bandwidth)
- RVQ codebook lookups stay at F32 regardless, so audio quality floor is maintained

**Quantizer variant details (from tools/quantize.cpp):**
- Q4_K_M: base Q4_K, bump Q6_K for important tensors (first+last+every 3rd layer), embed Q6_K
- Q8_0: no bumps, no mixing — uniform Q8_0 everywhere except F32 special tensors
- Both keep RVQ codebooks, speaker encoder, biases, norms, snake params at F32

## Flash Attention

Flash attention is **on by default** in qwentts.cpp. The `--no-fa` flag disables it.

- `src/pipeline-tts.cpp:126`: `pt->use_flash_attn = use_fa && bp.has_gpu;`
- ggml has flash attention kernels for Turing (sm_75): `fattn-wmma-f16` and `fattn-vec` paths
- Provides O(n) memory vs O(n²) for manual attention — critical for 28-layer talker (ctx 32768) and 5-layer predictor (ctx 65536)
- On Turing: uses WMMA-based flash kernels, not the Ampere MMA path, but still significantly faster than manual attention
- **Recommendation: never pass `--no-fa`** unless debugging

## --codec-chunk-dur Analysis

This parameter controls the **buffered decode path only** (one-shot WAV output). The streaming path (PCM output, on_chunk callback) ignores it entirely.

- Default: 24.0 seconds (300 frames at 12.5 Hz)
- **For sentence-level chunks (3-5 seconds of audio), this parameter is effectively a no-op** — the total audio never exceeds the chunk duration, so chunking never activates
- The chunking only matters when total audio > codec_chunk_sec, to bound VRAM during codec decode
- For the streaming path (tts-server with PCM), there is no chunking at all — stateful frame-by-frame decode with CUDA graph replay
- **Removed from production tts-provider.sh** — was set to 4.0 but had no effect on sentence-level chunks

## --max-new Analysis

Default: 2048 frames (~164 seconds of audio). At 12.5 Hz:
- 200 frames = 16 seconds
- 500 frames = 40 seconds
- 2048 frames = 164 seconds (maximum)

For 350-char sentence chunks: model generates ~30-50 frames (2.5-4 seconds). `--max-new 300` is a safe cap (~24 seconds). Production script uses 300.

## tts-server vs CLI Per-Chunk

**The biggest optimization opportunity.** 

CLI per-chunk (`qwen-tts` invoked each time):
- Loads 2+ GB GGUF from disk every call (~1-3 seconds depending on cache)
- Allocates KV cache, builds graphs, runs prefill
- Total overhead per chunk: model load (1-3s) + graph build (0.5-1s) + prefill (0.1-0.5s)

tts-server (warm model):
- Loads model once at startup, stays GPU-resident
- Each synthesis skips load/alloc, goes straight to prefill + generate
- Saves 1.5-4 seconds per chunk
- For 10-sentence text: saves 15-40 seconds total

**tts-server features:**
- OpenAI-compatible HTTP API
- Streaming (PCM) and one-shot (wav) modes
- Voice cloning via POST /v1/voices (register once, use by name)
- Sampling overrides per request (seed, temperature, top_k, etc.)
- CUDA graph replay for steady-state frame decode

**Streaming path advantages (PCM response_format):**
- First audio callback fires ~83ms after first frame generated
- Stateful frame-by-frame decode with persistent conv contexts + KV ring
- Adaptive chunk ramp: T=1 → 2 → 4 → 8, then steady at 8
- CUDA graph cache: constant topology → pure replay after first capture
- No re-decoded context, no chunk seams

## RTF (Real-Time Factor)

RTF = processing_time / audio_duration. RTF < 1.0 means faster than real-time.

The engine logs detailed perf metrics (src/pipeline-tts.cpp:425-440):
```
[Perf] Prefill X.X ms (T_ctx prefill)
[Perf] TTFA X.X ms (first frame codes)
[Perf] TalkerDecode X.X ms (N frames, X.XX ms/frame)
[Perf] CodePredictor X.X ms (X.XX ms/frame)
[Perf] CodecDecode X.X ms
[Perf] Total X.X ms (N frames, X.XX ms/frame AR, audio X.XX s, RTF X.XXX)
```

## 4GB VRAM Hard Limits (Verified 2026-07-14)

Tested on GTX 1650 Ti (4GB VRAM, Turing sm_75). These optimizations **do not work** on4GB:

### tts-server: OOM on medium+ text
- Model (2.0GB) + KV cache (896MB) = ~3GB allocated at startup
- Short phrases (<2s audio, ~30 frames) work fine
- Medium text (~5s audio, ~60+ frames) OOMs during codec decode (needs ~590MB, can't find contiguous block)
- **Root cause:** Codec decode allocates large CUDA buffers that don't fit alongside model + KV cache
- **Fix:** None on 4GB. CLI per-chunk is the only viable approach (frees VRAM between calls)

### Q4_K_M quantization: segfaults
- Downloads fine (1.2GB), loads partially, then crashes in `get_rows_cuda` during inference
- Same crash in both normal mode and stream-by-line mode
- **Root cause:** Likely CUDA architecture compatibility issue with this qwentts.cpp build
- **Fix:** Would need rebuild with different CUDA arch flags, or wait for upstream fix

### stream-by-line: OOM on second line
- First line generates successfully
- Second line OOMs because model stays loaded + new KV cache allocation needed
- **Root cause:** Same as tts-server — can't fit model + KV + codec decode on 4GB

### CUDA memory pool fragmentation
- After running tts-server, CLI invocations may start segfaulting during codec decode
- Error: `ggml_cuda_pool_alloc<half>::alloc` fails to find contiguous block
- **Fix:** Reboot clears GPU state and restores normal operation
- **Prevention:** Avoid running tts-server on 4GB VRAM — it corrupts CUDA memory pool state

### `|| true` after qwen-tts command
- On 4GB, qwen-tts sometimes segfaults during process cleanup AFTER writing the output file
- The file is valid (correct audio, correct duration) but exit code is 139 (SIGSEGV)
- **Fix:** Add `|| true` after the qwen-tts command in scripts, then check file existence separately
- The tts-provider.sh already has this: `2>> "$LOG" || true`

## Expected RTF by configuration (GTX 1650 Ti):
| Config | Estimated RTF | Notes |
|--------|--------------|-------|
| 1.7B Q8_0, CLI per chunk | 0.7-0.9 | Model load overhead included |
| 1.7B Q4_K_M, CLI per chunk | 0.5-0.7 | Bandwidth savings, no load overhead |
| 1.7B Q4_K_M, tts-server warm | 0.4-0.6 | No model load, CUDA graph replay |
| 0.6B Q8_0, tts-server warm | 0.2-0.4 | Smaller model, fastest option |

## Batch / Parallel Generation

Not possible with current architecture:
- Single GPU context serialized by g_synth_mutex
- KV cache and hidden bridge are single-instance tensors
- Model is autoregressive (frames depend on previous hidden state)
- 4GB VRAM cannot support multiple GPU contexts
- Inter-chunk parallelism impossible with one talker instance

## Model Size Comparison

| Model | Talker File | Talker+Tokenizer | Hidden | FFN | Layers | Speed Factor |
|-------|------------|------------------|--------|-----|--------|-------------|
| 1.7B Q8_0 | 2.0 GB | 2.3 GB | 2048 | 6144 | 28 | 1.0x (baseline) |
| 1.7B Q4_K_M | 1.2 GB | 1.45 GB | 2048 | 6144 | 28 | ~1.3-1.4x |
| 0.6B Q8_0 | 993 MB | 1.2 GB | 1024 | 3072 | 28 | ~2.0-2.5x |
| 0.6B Q4_K_M | 629 MB | 884 MB | 1024 | 3072 | 28 | ~2.5-3.0x |

The 0.6B is ~2.8x smaller in parameter count (width halved) and runs roughly 2-3x faster.
Note: 0.6B has identity mtp_proj (1024→1024), 1.7B has learned linear (2048→1024).
