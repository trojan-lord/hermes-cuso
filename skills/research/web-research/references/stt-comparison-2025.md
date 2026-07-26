# STT Solutions Comparison (July 2026)

Quick-reference knowledge bank for Speech-to-Text technology evaluation.

## Cloud APIs (sorted by value)

| Provider | Model | $/hr | Accuracy | Languages | Streaming |
|----------|-------|------|----------|-----------|-----------|
| AssemblyAI | Universal-2 | $0.15 | ★★★★ | 99 | Yes |
| AssemblyAI | Universal-3.5 Pro | $0.21 | ★★★★★ | 18 | Yes |
| Deepgram | Nova-3 Monolingual | $0.29 | ★★★★ | 45+ | Yes |
| Deepgram | Nova-3 Multilingual | $0.35 | ★★★★ | 45+ | Yes |
| OpenAI | whisper-1 | $0.36 | ★★★ | 99 | No |
| Google | Standard Dynamic | $0.18 | ★★★ | 125+ | Yes |
| Google | Chirp V2 Standard | $0.96 | ★★★★ | 100+ | Yes |
| Azure | Real-time | $1.00 | ★★★★ | 100+ | Yes |

**Key findings**: AssemblyAI and Deepgram dominate on price+accuracy. OpenAI whisper-1 is aging (no streaming, higher price, lower accuracy). Google/Excel are enterprise-priced.

## Local Models (GPU VRAM requirements)

| Model | Params | FP16 VRAM | INT8 VRAM | Speed vs large-v3 |
|-------|--------|-----------|-----------|-------------------|
| Whisper tiny | 39M | ~150MB | ~100MB | N/A |
| Whisper base | 74M | ~300MB | ~200MB | N/A |
| Whisper small | 244M | ~1GB | ~500MB | N/A |
| Whisper medium | 769M | ~2.5GB | ~1.5GB | N/A |
| Whisper large-v3 | 1.55B | ~4.5GB | ~3GB | 1x (baseline) |
| Whisper turbo | 809M | ~3GB | ~2GB | ~8x faster |
| distil-large-v3 | 756M | ~2.5GB | ~1.5GB | ~6x faster |
| SenseVoiceSmall | 200M | ~500MB | ~235MB GGUF q8 | ~15x faster |

**Faster-Whisper benchmarks** (13 min audio, RTX 3070 Ti):
- large-v3 FP16: 1m03s, 4525MB
- large-v3 INT8: 59s, 2926MB
- large-v3 INT8 batch=8: 16s, 4500MB
- base INT8: 1m42s, 1477MB (CPU)

## Key Projects

- **Faster-Whisper**: github.com/SYSTRAN/faster-whisper — 4x faster than openai/whisper, CTranslate2 backend, 24k stars
- **SenseVoiceSmall**: github.com/FunAudioLLM/SenseVoice — GGUF via llama.cpp (June 2026), q8 is 235MB, supports ZH/EN/JA/KO/Cantonese
- **Whisper.cpp**: github.com/ggerganov/whisper.cpp — C/C++ implementation, edge/embedded
- **distil-whisper**: huggingface.co/distil-whisper/distil-large-v3 — English-optimized distillation

## For 3-4GB VRAM Cards

Best local options (GTX 1650 Ti class):
1. **Faster-Whisper + turbo INT8** (~1.5GB) — safe, good accuracy
2. **Faster-Whisper + large-v3 INT8** (~2.9GB) — tight fit, best accuracy
3. **SenseVoiceSmall GGUF q8** (~235MB) — if CJK languages needed
4. **Faster-Whisper + medium FP16** (~2.5GB) — conservative middle ground
