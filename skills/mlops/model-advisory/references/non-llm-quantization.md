# Non-LLM GGUF Quantization Analysis

Detailed methodology for evaluating quantization tradeoffs on specialized GGUF models (TTS, audio codecs, multimodal) where standard perplexity benchmarks don't apply.

## The Canonical Question

"Should I use the smaller model at full precision (BF16) or the larger model quantized (Q4_K_M)?"

This is the most common model-advisory question. The answer depends on **task-specific** metrics, not perplexity.

## Case Study: Qwen3-TTS Voice Cloning

### Models Compared

| Model | Actual params | BF16 size | Q4_K_M size |
|---|---|---|---|
| Qwen3-TTS-12Hz-0.6B-Base | 0.9B | 1.8 GB | 629 MB |
| Qwen3-TTS-12Hz-1.7B-Base | 2.0B | 3.9 GB | 1.2 GB |

Note: "0.6B" and "1.7B" are model family names — actual param counts differ (0.9B and 2.0B).

### Information Content

```
0.6B BF16:  0.9B × 16 = 14.4 Gbit
1.7B Q4_K_M: 2.0B × 4.88 = 9.76 Gbit
Ratio: 1.47× in favor of 0.6B BF16
```

### Paper Benchmarks (arXiv:2601.15621, Table 4)

Speaker similarity (cosine sim, higher = better, at BF16):

| Language | 0.6B | 1.7B | Winner |
|---|---|---|---|
| Chinese | 0.811 | 0.799 | 0.6B |
| English | 0.829 | 0.775 | 0.6B |
| Japanese | 0.798 | 0.788 | 0.6B |
| Korean | 0.812 | 0.799 | 0.6B |
| German | 0.769 | 0.775 | 1.7B |
| Italian | 0.792 | 0.817 | 1.7B |
| Portuguese | 0.794 | 0.817 | 1.7B |
| Spanish | 0.812 | 0.814 | 1.7B (tiny) |
| French | 0.700 | 0.714 | 1.7B |
| Russian | 0.781 | 0.792 | 1.7B |

Key finding: **0.6B wins speaker similarity in 4/10 languages.** Average gap is ~0.01 — nearly identical.

The 1.7B's real advantage is in **content consistency** (WER):
- Chinese WER: 0.92 (0.6B) vs 0.77 (1.7B) — 17% better
- English WER: 1.32 (0.6B) vs 1.24 (1.7B) — 6% better

### Community GGUF Converter Findings

**Serveurperso/Qwen3-TTS-GGUF** (main GGUF port):
- Q8_0 labeled as "recommended default"
- Q4_K_M labeled as "lowest VRAM"
- Quantization policy: entire talker LM gets standard K-quant; tokenizer stays at F16 for conv kernels

**cstr/qwen3-tts-1.7b-base-GGUF** (CrispASR port):
- Only provides F16 and Q8_0 for the 1.7B
- Explicitly states: "Lower-bit talker quants (q6_k, q5_k, q4_k) can still load but are not numerically faithful to the F16 reference and should be treated as experimental"
- Q8_0 verified to achieve "ASR-roundtrips word-exact" quality on English prompts

### Architecture Details

Both models share:
- Same tokenizer/decoder (Qwen3-TTS-Tokenizer-12Hz, 0.2B params)
- Same 12Hz, 16-layer multi-codebook design
- Same streaming architecture

Differences (LM backbone only):
- 0.6B: hidden=1024
- 1.7B: hidden=2048, plus ECAPA speaker encoder with enc_dim=2048, plus small_to_mtp_projection bridge

Since the tokenizer/decoder is shared, audio reconstruction quality is identical — only code prediction quality differs.

### Conclusion

**For voice cloning (speaker similarity): 0.6B BF16 > 1.7B Q4_K_M**

Reasoning:
1. 0.6B stores 47% more information
2. At BF16, the two models are nearly identical for speaker similarity
3. Q4_K_M is explicitly experimental for this architecture
4. Autoregressive codebook prediction amplifies quantization errors across steps
5. Speaker similarity specifically depends on fine weight patterns that 4-bit quantization degrades disproportionately

**Optimal choice if VRAM allows**: 1.7B Q8_0 (~2.1 GB) — gets both capacity advantage and quantization safety.

## Why LLM Perplexity Tables Don't Transfer

The llama.cpp perplexity table shows Q4_K_M = +1.7% perplexity degradation for text LLMs. This does NOT generalize because:

1. **Perplexity measures text prediction accuracy**, not speaker identity preservation
2. **Speaker similarity depends on fine weight patterns** that are disproportionately affected by block-wise quantization
3. **Autoregressive error accumulation** in TTS codebook prediction is worse than in text next-token prediction (16 codebooks × 12.5 Hz vs 1 codebook × text)
4. **Speaker encoder quantization** corrupts the input conditioning signal before generation starts

## Other Models / Domains

This methodology applies whenever the question is "smaller full-precision vs larger quantized":

- **Music generation** (MusicGen, AudioCraft): melody/key preservation under quantization
- **Speech recognition** (Whisper): WER degradation under quantization
- **Embedding models**: retrieval accuracy degradation
- **Vision-language models**: image understanding fidelity under quantization

Always check: does the model maker provide benchmarks for the specific capability you need, or only general-purpose metrics?
