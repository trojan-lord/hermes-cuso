---
name: model-advisory
description: "Advise on model variant selection: quantized vs full-precision, smaller vs larger, task-specific tradeoff analysis for LLMs, TTS, audio, and multimodal models."
version: 1.0.0
author: Hermes
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Model Selection, Quantization, GGUF, Tradeoff Analysis, TTS, LLM, Benchmarking, Voice Cloning]
---

# Model Advisory — Selection & Quantization Analysis

When a user asks "which model variant should I use?", "is the quantized version good enough?", or "smaller model BF16 vs larger model Q4?", use this skill.

## When to use

- Comparing model sizes (0.6B vs 1.7B vs 7B) for a specific task
- Deciding whether quantization (Q4_K_M, Q8_0, etc.) is acceptable
- "Should I use the smaller model at full precision or the larger model quantized?" — THE canonical question this skill answers
- Evaluating TTS, audio generation, multimodal, or embedding models where standard LLM perplexity doesn't apply

## When NOT to use

- Standard LLM benchmarking with lm-eval-harness (use `evaluating-llms-harness`)
- Running GGUF models with llama.cpp (use `llama-cpp`)
- General model discovery on HuggingFace (use `huggingface-hub`)

## 5-Step Analysis Framework

### Step 1: Compute Information Content Ratio

```
info = params × bits_per_param

0.6B @ BF16:  0.9B × 16 = 14.4 Gbit  (1.8 GB file)
1.7B @ Q4_K_M: 2.0B × 4.88 = 9.76 Gbit  (1.2 GB file)
Ratio: 14.4 / 9.76 = 1.47× advantage to smaller BF16
```

**Thresholds:**
- Ratio ≥ 1.3×: Smaller BF16 likely wins — verify with Steps 2-4
- Ratio 1.0-1.3×: Close call — Steps 2-4 are critical
- Ratio < 1.0×: Larger quantized model has more information — probably wins

### Step 2: Find Paper's Own Benchmarks

Check the model's technical report (arXiv) for side-by-side model-size comparisons.

**Critical question:** How much does the larger model actually outperform the smaller one at full precision for the specific metric that matters?

- If the gap is tiny (< 5% relative), quantization will likely erase it
- If the gap is large (> 15%), the larger model may survive moderate quantization
- For voice cloning specifically: speaker similarity scores are often nearly identical between sizes

### Step 3: Check Community GGUF Converter Notes

Search HuggingFace for community GGUF conversions of the same model:
- `Serveurperso/<model>-GGUF` (general GGML port)
- `cstr/<model>-GGUF` (CrispASR port for TTS)
- `mlx-community/<model>-*` (MLX ports for Apple Silicon)

Look for:
- The labeled "recommended" quant level (often Q8_0, not Q4)
- Warnings about lower quants being "experimental" or "not numerically faithful"
- Whether specific tensors (encoders, codebooks) get special treatment

### Step 4: Architecture-Specific Degradation

Different model types lose different things under quantization:

| Model type | What degrades | Sensitivity |
|---|---|---|
| Text LLM (chat) | Perplexity ~1.7% at Q4_K_M | Low |
| Autoregressive TTS | Speaker similarity, content fidelity | **High** (errors compound) |
| Speaker/voice encoder | Fine speaker identity | **Very high** (small-weight patterns) |
| Audio codec/decoder | Affects all outputs equally | Medium |
| Embedding model | Retrieval accuracy | Medium-high |

**TTS-specific pitfalls:**
- Autoregressive codebook prediction: error at step t feeds into step t+1
- Speaker encoder: identity lives in subtle weight patterns that Q4 destroys
- Paper benchmarks are at BF16 — they do NOT predict quantized performance

### Step 5: Recommend Quant Level

For **non-LLM specialized models** (TTS, audio, multimodal), use a more conservative ladder than for text LLMs:

| Quant | Safe for | Risk level |
|---|---|---|
| BF16/F16 | Reference baseline | None |
| Q8_0 | Nearly all tasks | Very low |
| Q6_K | Most tasks, test carefully | Low-medium |
| Q5_K_M | Acceptable for non-critical use | Medium |
| Q4_K_M | Memory-constrained only | **High** — treat as experimental |
| Q3 and below | Not recommended | Very high |

For **text LLMs**, Q4_K_M remains the standard recommendation.

## Research Sources

When investigating a specific model comparison:

1. **HuggingFace model cards**: Param counts, tensor types, benchmark tables
2. **ArXiv technical report**: Paper's own size-vs-quality comparisons
3. **GGUF converter repos**: Community quantization notes and recommendations
4. **GitHub issues**: Quality reports from users who tested different quant levels
5. **Information content ratio**: Sanity check calculation

## References

- [non-llm-quantization.md](references/non-llm-quantization.md) — Detailed methodology and Qwen3-TTS case study with actual benchmark data
