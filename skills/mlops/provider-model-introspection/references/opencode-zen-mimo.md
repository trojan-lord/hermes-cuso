# OpenCode Zen — Model Alias Reference

## Provider Details

- **Base URL:** `https://opencode.ai/zen/v1`
- **API Key:** `public` (free, no card needed)
- **Model list endpoint:** `GET /v1/models` (works, returns all aliases)
- **Per-model endpoint:** Returns HTML 404 (does NOT work)

## Known Alias → Model Mappings (July 2026)

| Alias | Underlying Model | Provider | Notes |
|-------|-----------------|----------|-------|
| `big-pickle` | Xiaomi MiMo-V2.5 | Xiaomi | 1M context, reasoning tokens, free |
| `mimo-v2.5-free` | Xiaomi MiMo-V2.5 | Xiaomi | Same model, different alias |
| `deepseek-v4-flash-free` | DeepSeek V4 Flash | DeepSeek | Returned empty content on probe |
| `north-mini-code-free` | Unknown | Unknown | Returned "None" content on probe |

## Xiaomi MiMo-V2.5 Specs

- **Total params:** 1T (v2-pro architecture)
- **Active params:** 42B
- **Context window:** 1M tokens
- **Max output:** 128K tokens
- **Architecture:** Hybrid attention (7:1 ratio), Multi-Token Prediction
- **Modalities:** Text, image, video, audio understanding
- **License:** MIT (fully open source)
- **HuggingFace:** `XiaomiMiMo/mimo-v25` collection

### Benchmark Position (July 2026)

- Artificial Analysis Intelligence Index: #8 worldwide, #2 in China (per Xiaomi's claim)
- ClawEval: #1 among open-source models
- GDPVal: #1 among open-source models
- Cost per Intelligence Index task: $0.01 (tied #2 most affordable)
- Agent performance: Comparable to Claude Sonnet 4.6 / GPT-5.4 on coding agent tasks

### Pricing (Xiaomi direct API, overseas)

| Model | Input (miss) | Input (cache) | Output |
|-------|-------------|---------------|--------|
| mimo-v2.5-pro | $0.435/M | $0.0036/M | $0.87/M |
| mimo-v2.5 | $0.14/M | $0.0028/M | $0.28/M |
| mimo-v2-flash | $0.10/M | $0.01/M | $0.30/M |

TTS models (mimo-v2.5-tts, voiceclone, voicedesign) are free for a limited time.

### Key Behaviors Observed

- Uses reasoning/thinking tokens (visible in `usage.completion_tokens_details.reasoning_tokens`)
- Responds to identity queries by stating "MiMo-V2.5, developed by Xiaomi LLM Core Team"
- Training data cutoff: late 2024, updated early 2025
- Routed through Cloudflare (`cf-placement: remote-ORD`)

## Hermes Source Mappings

```bash
# models_dev.py — provider name mapping
"opencode-zen": "opencode"

# auxiliary_client.py — default auxiliary model per provider
"opencode-zen": "gemini-3-flash"

# model_metadata.py — context window sizes
"mimo-v2-pro": 1048576
"mimo-v2.5-pro": 1048576
"mimo-v2.5": 1048576
"mimo-v2-omni": 262144
"mimo-v2-flash": 262144
```

## OpenCode Zen Full Model List (July 2026)

Claude: fable-5, opus-4-8/7/6/5/1, sonnet-5/4-6/4-5/4, haiku-4-5
Gemini: 3.6-flash, 3.5-flash-lite, 3.5-flash, 3.1-pro, 3-flash
GPT: 5.6-sol/terra/luna, 5.5/5.5-pro, 5.4/5.4-pro/mini/nano, 5.3-codex-spark/codex, 5.2/5.2-codex, 5.1/codex-max/codex/codex-mini, 5/5-codex/5-nano
Grok: build-0.1, 4.5
DeepSeek: v4-pro, v4-flash
GLM: 5.2, 5.1, 5
MiniMax: m3, m2.7, m2.5
Kimi: k2.7-code, k2.6, k2.5
Qwen: 3.6-plus, 3.5-plus
Free tier: big-pickle, deepseek-v4-flash-free, mimo-v2.5-free, nemotron-3-ultra-free, north-mini-code-free, laguna-s-2.1-free
