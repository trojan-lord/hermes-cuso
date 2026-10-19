---
name: local-ollama
description: "Local Ollama patterns — vision API fallback, model management, direct API calls for tasks Hermes tools don't cover."
version: 1.3.0
author: Cuso
tags: [ollama, local-ai, vision, api, fallback]
related_skills: [llama-cpp, hermes-agent]
---

# Local Ollama Patterns

Working with Ollama models running locally — direct API calls, vision fallback, model selection, and management.

## When to Use

- Hermes vision tool isn't configured or needs a gateway restart
- Need to call a local model directly for analysis
- Want to use a vision model that Hermes doesn't route to

## Vision API — Direct Access

When Hermes vision tool isn't working, call Ollama's vision models directly:

```python
import base64, json, urllib.request

with open('/path/to/image.png', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()

payload = json.dumps({
    'model': 'qwen3.5:4b',
    'prompt': 'Describe this image in detail.',
    'images': [b64],
    'stream': False
}).encode()

req = urllib.request.Request(
    'http://localhost:11434/api/generate',
    data=payload,
    headers={'Content-Type': 'application/json'}
)
resp = urllib.request.urlopen(req, timeout=120)
result = json.loads(resp.read())
print(result['response'])
```

### Multi-Image Analysis

Loop and call separately — Ollama doesn't batch vision well. Use specific prompts per image.

### Prompt Tips for Better Descriptions

- "Describe every element: exact text, colors (hex), layout, spacing, icons, fonts, sections"
- "This image contains N separate screenshots — describe each one separately"
- "Include hex color codes where possible"
- "Describe the layout grid, flexbox, columns, and spacing"

### Pitfalls

- Large PNGs (2MB+) take longer — consider resizing first
- `timeout=120` or higher for vision calls
- Model must be loaded in VRAM first call (warm start)
- Ollama must be running (`systemctl status ollama`)
- Not all models support vision — check with `ollama list`
- First call after idle can take 30+ minutes if model needs to load into VRAM

## Model Management

```bash
ollama list                    # List installed models
ollama pull <model>            # Download a model
ollama rm <model>              # Remove a model
ollama show <model>            # Model details
curl http://localhost:11434/api/tags  # List via API
```

## Hermes Integration

### Fallback Model

Hermes has a `fallback_model` config key. If the primary provider fails, it auto-routes to the fallback.

```bash
hermes config set fallback_model.provider ollama
hermes config set fallback_model.model qwen3.5:4b
```

Config YAML equivalent:
```yaml
fallback_model:
  provider: ollama
  model: qwen3.5:4b
```

Supports a list of dicts for fallback chains (each entry needs `provider` + `model`).

### Auxiliary Models (Vision, Compression)

Hermes routes auxiliary tasks (vision, compression) to configured providers. For local Ollama:

```yaml
auxiliary:
  vision:
    model: qwen3.5:4b
    provider: ollama
```

Set via CLI:
```bash
hermes config set auxiliary.vision.provider ollama
hermes config set auxiliary.vision.model qwen3.5:4b
```

### Auditing Model Roles

When the user asks "what are my Ollama models for?", check which are wired into Hermes config:

```bash
# Primary model
grep -A2 '^model:' ~/.hermes/config.yaml

# Fallback
grep -A2 'fallback_model' ~/.hermes/config.yaml

# Auxiliary (vision, etc.)
grep -A2 'auxiliary' ~/.hermes/config.yaml
```

Models not referenced in config are idle — candidates for removal to free VRAM.

### Unifying Roles (Vision + Fallback)

A model with both vision and tool calling (e.g., `qwen3.5:4b`) can serve as **both** auxiliary vision AND fallback main. This halves disk/VRAM vs maintaining separate models:

```bash
hermes config set auxiliary.vision.model qwen3.5:4b
hermes config set auxiliary.vision.provider ollama
hermes config set fallback_model.model qwen3.5:4b
hermes config set fallback_model.provider ollama
```

Only do this when the model genuinely supports both capabilities. Check `ollama show <model>` for the capabilities list (should show `vision` and `tools`).

### Ollama Service Resilience

Ollama runs as a systemd service (`ollama.service`). The default Arch/CachyOS package already includes restart-on-failure:

```
Restart=on-failure
RestartSec=3
RestartPreventExitStatus=1
```

This means: auto-starts on boot (if `enabled`), AND auto-restarts on crash with a 3-second delay. **A separate health check timer is NOT needed** — systemd handles it natively. Verify with: `systemctl cat ollama.service | grep Restart`

If someone previously set up a redundant health check timer, remove it:
```bash
sudo systemctl disable --now ollama-healthcheck.timer
sudo rm /etc/systemd/system/ollama-healthcheck.{service,timer}
sudo systemctl daemon-reload
```

### Model Load Behavior (keep_alive)

Ollama loads models **on demand** — the server can be running with zero models in VRAM. When a request comes in, Ollama loads the model (~10-30s for a 4B model). After 5 minutes of inactivity (default), it unloads to free VRAM.

Check what's currently loaded: `curl -s http://127.0.0.1:11434/api/ps`

**For fallback models:** If the primary provider goes down and Ollama needs to cold-load the model, the first fallback request will be slow. Options:
- Accept the cold-start delay (fine for occasional fallback use)
- Set `keep_alive` parameter on API requests to extend load duration
- The default 5-minute unload is usually fine — model stays loaded during active use

### Pitfalls

- **Ollama running ≠ model loaded.** The health check confirms the server is up, but the model may not be in VRAM. First request after idle triggers a cold load. Check `curl -s http://127.0.0.1:11434/api/ps` to see if anything is loaded.
- `fallback_model` changes need a gateway restart to take effect.
- Small models (≤3B) work as fallbacks for basic tasks but struggle with complex reasoning.
- Check VRAM before adding models: `nvidia-smi`. Each model loaded consumes its full size in VRAM.
- `ollama list` shows disk usage, not active VRAM. A model listed but not recently used may not be loaded.
- **Ollama "Updated" ≠ release date.** The "Updated" field on ollama.com reflects when the Ollama *tags* were last refreshed, not when the model was originally released. A model listed as "Updated 1 month ago" may actually be 5+ months old. To find the real release date, check the HuggingFace commit history (`/commits/main` on the model repo) — the initial commit date is the actual release. Never quote a release timeline to the user without verifying via HuggingFace or the official blog.
- **"Qwen 3.7" does not exist.** Users may ask about it based on clickbait or confusion. As of Jul 2026, the Qwen lineup is: 2.5 → 3 → 3-vl → 3.5 → 3.6. No 3.7 has been released. Always verify via Ollama search before confirming a model exists. See references/small-models-landscape.md for the version timeline.

## Selecting the Best Local Model

When asked "what model should I run locally?" — evaluate in this order:

1. **VRAM budget** — `nvidia-smi` first. Everything else is downstream.
2. **Tool calling support** — Critical for Hermes. Models without it hallucinate tool names, skip calls, break agent workflows. Check [ollama.com/search?c=tools](https://ollama.com/search?c=tools) for verified support.
3. **Parameter count** — Bigger = smarter but more VRAM. Sweet spot for ≤4 GB is 2B-4B.
4. **Generation** — Newer is dramatically better at the same size (Qwen 3.5 > 3.0 > 2.5, Gemma 4 > 3).

### VRAM Estimation

Ollama's registry API doesn't expose download sizes cleanly. Estimate from param count:

| Params | Q4_K_M | Q5_K_M | Q8_0 |
|--------|--------|--------|------|
| 2B | ~1.5 GB | ~1.8 GB | ~2.5 GB |
| 3B | ~2.0 GB | ~2.4 GB | ~3.2 GB |
| 4B | ~2.7 GB | ~3.2 GB | ~4.3 GB |

Add ~200-500 MB for KV cache during inference. A 4B Q4_K_M model at 2.7 GB uses ~3.0-3.2 GB total.

### Research Sources

1. **Ollama tools category** — `ollama.com/search?c=tools` (verified tool calling)
2. **Model family pages** — e.g., `ollama.com/qwen3.5` (available sizes, capabilities)
3. **HuggingFace GGUF repos** — exact quantized file sizes
4. **Community model pages** on Ollama — pull counts = adoption signal

See [references/small-models-landscape.md](references/small-models-landscape.md) for current landscape.

## API Reference

- `POST /api/generate` — single prompt + optional images
- `POST /api/chat` — multi-turn conversation
- `GET /api/tags` — list models
- `POST /api/show` — model info
- Default endpoint: `http://localhost:11434`
