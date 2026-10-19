# Small Models Landscape (July 2026)

Current state of sub-4B models suitable for local Hermes Agent use on tight VRAM.

> **Release date note:** Ollama's "Updated" field reflects tag refreshes, not initial release. Qwen 3.5 was released Feb 2026 (verify via HuggingFace `/commits/main`). Gemma 4 released ~Apr 2026. Always verify via HF commit history before quoting timelines.

## Top Picks (Tool-Calling Capable)

| Model | Params | Q4_K_M | Tools | Vision | Thinking | Notes |
|---|---|---|---|---|---|---|
| **qwen3.5:4b** | 4B | ~2.7 GB | ✅ | ✅ | ✅ | Best all-rounder. 15.6M pulls on family. |
| **qwen3.5:2b** | 2B | ~1.5 GB | ✅ | ✅ | ✅ | Lightest with full features. |
| **gemma4:e4b** | 4B | ~2.7 GB | ✅ | ✅ | ✅ | Google's latest small model. |
| **gemma4:e2b** | 2B | ~1.5 GB | ✅ | ✅ | ✅ | Lightest Gemma 4. |

## Also Available (Less Ideal for Hermes)

| Model | Params | Q4_K_M | Tools | Vision | Thinking | Notes |
|---|---|---|---|---|---|---|
| phi-4-mini | 3.8B | ~2.5 GB | ✅ | ❌ | ❌ | Good reasoning, no vision. Microsoft. |
| qwen2.5:3b | 3B | ~2.0 GB | ✅ | ❌ | ❌ | Older gen. Decent fallback. |
| qwen2.5-coder:3b | 3B | ~2.0 GB | ✅ | ❌ | ❌ | Coding-focused. Poor general agent use. |
| gemma3:4b | 4.3B | ~2.8 GB | ❌ | ✅ | ❌ | Vision only. No tool calling. |
| mistral-nemo:12b | 12B | ~7 GB | ✅ | ❌ | ❌ | Too large for 4 GB VRAM. |

## Key Takeaways for Hermes

- **Tool calling is non-negotiable.** A model that can't call tools will fail as a Hermes agent, regardless of intelligence.
- **Coding models (qwen2.5-coder) are poor general agents.** They are trained for code completion, not multi-step reasoning with tool dispatch.
- **Vision + tools + thinking in one model** (qwen3.5, gemma4) means you can consolidate auxiliary + fallback into a single model.
- **Newer generations punch above their weight.** Qwen 3.5 4B outperforms Qwen 2.5 7B on many benchmarks.

## Qwen Version Timeline (as of Jul 2026)

| Version | Release | Small Sizes? | Key Features |
|---------|---------|-------------|--------------|
| qwen2.5 | 2024 | 0.5b-72b | Tools. No vision at small sizes. |
| qwen3 | Apr 2025 | 0.6b-235b | Tools + thinking. No vision at 4b. |
| qwen3-vl | ~May 2025 | 2b-235b | Vision + tools + thinking. |
| **qwen3.5** | **Feb 2026** | 0.8b-122b | **Unified vision+tools+thinking.** Best for small VRAM. |
| qwen3.6 | ~Jun 2026 | 27b/35b only | Too large for <=4GB. |
| qwen3.7 | -- | -- | **Does not exist.** No official release. |

## Ollama Registry Notes

- `ollama.com/search?c=tools` lists verified tool-calling models
- Registry API does not reliably expose download sizes
- Size must be estimated from param count (see main skill VRAM estimation table)
- Pull count on model pages indicates community adoption

## Hermes Config Roles

| Role | Config Key | Purpose |
|---|---|---|
| Primary | `model.default` + `model.provider` | Main conversation model |
| Fallback | `fallback_model` | Auto-route when primary fails |
| Auxiliary | `auxiliary.vision`, etc. | Specialized subtasks |
