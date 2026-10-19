# Speech-to-Text Research — July 2026

## Cloud STT APIs (Ranked)

| Rank | Provider | Model | $/hr | Accuracy | Languages | Notes |
|------|----------|-------|------|----------|-----------|-------|
| 1 | Deepgram | Nova-3 | $0.29 | ★★★★☆ | 45+ | $200 free credit, real-time streaming |
| 2 | AssemblyAI | Universal-3.5 Pro | $0.21 | ★★★★★ | 18 | Best accuracy, code-switching support |
| 3 | Google | Chirp V2 | $0.96 | ★★★★☆ | 100+ | Best language coverage |
| 4 | ElevenLabs | Scribe | ~$0.25-0.50 | ★★★★☆ | 30+ | Credit-based pricing |
| 5 | OpenAI | whisper-1 | $0.36 | ★★★☆☆ | 99 | Aging, no streaming |
| 6 | Azure | Real-time | $1.00 | ★★★★☆ | 100+ | Enterprise compliance |

**Recommendation:** Switch from OpenAI whisper-1 → Deepgram Nova-3 (3x cheaper, better) or AssemblyAI Universal-3.5 Pro (best accuracy).

## Local STT Models (for GTX 1650 Ti, 3.64GB VRAM)

| Model | Params | INT8 VRAM | Accuracy | Notes |
|-------|--------|-----------|----------|-------|
| Whisper base | 74M | ~200MB | Fair | Current fallback — too small |
| Whisper small | 244M | ~500MB | Good | Minimum viable upgrade |
| Whisper medium | 769M | ~1.5GB | Good+ | Safe choice |
| **Whisper turbo** | **809M** | **~1.5GB** | **Very Good** | **Best practical choice** |
| distil-large-v3 | 756M | ~1.5GB | Very Good | English-focused |
| Whisper large-v3 | 1.55B | ~2.9GB | Excellent | Tight fit, may OOM |
| SenseVoiceSmall | 200M | ~250MB | Good | Best for CJK languages |

**Recommendation:** Replace whisper base → Faster-Whisper + Whisper turbo INT8 (~1.5GB VRAM, ~10x more accurate than base).

## Faster-Whisper Setup

```bash
pip install faster-whisper
# Uses CTranslate2 backend, 4x faster than openai/whisper
# Same accuracy as original Whisper models
# INT8 quantization halves VRAM with minimal accuracy loss
```

## Key Findings
- OpenAI whisper-1 is outdated — AssemblyAI and Deepgram offer better accuracy AND lower prices
- Whisper turbo (809M params) is the sweet spot for 4GB VRAM — good accuracy, fits comfortably
- Large-v3 INT8 (~2.9GB) is tight on 3.64GB card — try it but have turbo as fallback
- SenseVoiceSmall (235MB GGUF) is excellent for CJK languages if needed
