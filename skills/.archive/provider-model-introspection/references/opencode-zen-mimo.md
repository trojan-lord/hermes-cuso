# OpenCode Zen — Model Alias Reference

## Provider Details

- **Base URL:** `https://opencode.ai/zen/v1`
- **API Key:** `public` (free, no card needed)
- **Model list endpoint:** `GET /v1/models` (works, returns all aliases)
- **Per-model endpoint:** Returns HTML 404 (does NOT work)

## Known Alias → Model Mappings (July 2026)

| Alias | Underlying Model | Provider | Native Context | Proxy Limit | Notes |
|-------|-----------------|----------|----------------|-------------|-------|
| `big-pickle` | Xiaomi MiMo-V2.5 | Xiaomi | 1M | **200K** | Reasoning model; models.dev caps at 200K |
| `mimo-v2.5-free` | Xiaomi MiMo-V2.5 | Xiaomi | 1M | **200K** | Same underlying model, different alias |
| `deepseek-v4-flash-free` | DeepSeek V4 Flash | DeepSeek | 1M | **200K** | Empty content on probe; models.dev caps at 200K |
| `north-mini-code-free` | Unknown | Unknown | Unknown | **200K** | Returned "None" content on probe |

**Critical:** The proxy limit (what OpenCode Zen actually serves) is 200K for all free-tier aliases, regardless of the underlying model's native context window. Hermes resolves this via the models.dev registry lookup step in `get_model_context_length()`, NOT from the hardcoded `DEFAULT_CONTEXT_LENGTHS` (which has `mimo-v2.5: 1048576`).

## Xiaomi MiMo-V2.5 Specs

- **Total params:** 1T (v2-pro architecture)
- **Active params:** 42B
- **Native context window:** 1M tokens (on Xiaomi direct API)
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

## models.dev Registry Data for OpenCode Zen

All free-tier models report the same 200K context on models.dev:

```json
"big-pickle": {
  "limit": { "context": 200000, "input": 160000, "output": 32000 }
}
```

Query directly:
```bash
curl -s "https://models.dev/api.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
models = data.get('opencode', {}).get('models', {})
for m in ['big-pickle', 'mimo-v2.5-free', 'deepseek-v4-flash-free']:
    entry = models.get(m, {}).get('limit', {})
    print(f\"{m}: context={entry.get('context', 'N/A')}\")
"
```

## Hermes Resolution Chain for big-pickle

```
get_model_context_length('big-pickle', base_url='https://opencode.ai/zen/v1', provider='opencode-zen')
  → step 0: no config override
  → step 1: no persistent cache
  → step 4f: models.dev lookup via lookup_models_dev_context('opencode-zen', 'big-pickle')
    → PROVIDER_TO_MODELS_DEV maps 'opencode-zen' → 'opencode'
    → fetches https://models.dev/api.json
    → finds big-pickle under opencode.models
    → returns limit.context = 200000
  → result: 200000
```

The hardcoded `mimo-v2.5: 1048576` in `DEFAULT_CONTEXT_LENGTHS` is never reached because the models.dev step fires first.

## Key Behaviors Observed

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

# model_metadata.py — context window sizes (hardcoded, NOT what big-pickle resolves to)
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
