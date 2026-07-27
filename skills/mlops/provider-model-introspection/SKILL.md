---
name: provider-model-introspection
description: "Identify what model a proxy/aggregator provider is actually serving behind an alias. Query APIs, probe model self-identification, compare response patterns. Use when user suspects a model swap, wants to know what 'big-pickle' or similar aliases resolve to, or needs to audit provider transparency."
version: 1.0.0
author: Cuso
license: MIT
metadata:
  hermes:
    tags: [mlops, providers, debugging, introspection]
---

# Provider Model Introspection

Some LLM providers (especially free aggregators like OpenCode Zen) serve models under opaque aliases. This skill covers how to identify what's actually running behind those aliases.

## When to Use

- User suspects a model swap or outage caused by a provider change
- User wants to know what a model alias (e.g., `big-pickle`) actually resolves to
- Auditing provider transparency / model provenance
- Debugging unexpected behavior changes in a model

## Core Technique: API Probing

### Step 1: Check the model list endpoint

```bash
curl -s https://<provider>/v1/models -H "Authorization: Bearer <key>" | python3 -m json.tool
```

This lists available model IDs but does NOT reveal what aliases map to.

### Step 2: Ask the model to self-identify

```bash
curl -s https://<provider>/v1/chat/completions \
  -H "Authorization: Bearer <key>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "<alias>",
    "messages": [{"role": "user", "content": "What is your exact model name and version? State your full model identifier exactly."}],
    "max_tokens": 200
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['choices'][0]['message']['content'])"
```

**Caveat:** Model self-identification is based on training data, not runtime metadata. A model may honestly report its identity, or it may confabulate. Cross-reference with other signals.

### Step 3: Inspect response metadata

Check the raw API response for:
- `model` field in the response (often the alias, not the real model)
- `reasoning_tokens` in `usage.completion_tokens_details` (indicates reasoning/thinking model)
- Response headers for infrastructure clues (`cf-placement`, `server` headers)

```bash
curl -s -D - https://<provider>/v1/chat/completions \
  -H "Authorization: Bearer <key>" \
  -H "Content-Type: application/json" \
  -d '{"model":"<alias>","messages":[{"role":"user","content":"Say hi"}],"max_tokens":10}' \
  | head -30
```

### Step 4: Compare aliases

If the provider has multiple aliases, test each:
```bash
for model in "alias-1" "alias-2" "alias-3"; do
  echo "=== $model ==="
  curl -s https://<provider>/v1/chat/completions \
    -H "Authorization: Bearer <key>" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"$model\",\"messages\":[{\"role\":\"user\",\"content\":\"What model are you?\"}],\"max_tokens\":150}" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['choices'][0]['message']['content'])"
done
```

### Step 5: Check Hermes source for known mappings

```bash
grep -rn "<provider_name>" ~/.hermes/hermes-agent/agent/models_dev.py
grep -rn "<provider_name>" ~/.hermes/hermes-agent/agent/auxiliary_client.py
grep -rn "<provider_name>" ~/.hermes/hermes-agent/agent/model_metadata.py
```

These files contain Hermes's internal knowledge of provider→model mappings and context window sizes.

## Context Window Detection & Discrepancies

Aliases on aggregator providers often report different context windows than the underlying model's native specs. Hermes resolves context via a multi-step chain in `model_metadata.py::get_model_context_length()`:

1. Config override (`model.context_length`)
2. Persistent cache (`~/.hermes/context_length_cache.yaml`)
3. Endpoint metadata (`/v1/models`)
4. Provider-specific probes (Nous, Codex OAuth, GMI, Ollama, models.dev)
5. Hardcoded defaults (`DEFAULT_CONTEXT_LENGTHS` in `model_metadata.py`)
6. Fallback: 256K

**Key gotcha:** For aggregated/free providers like OpenCode Zen, the resolution lands at step 4f — `models.dev` registry lookup. The `opencode-zen` provider maps to `opencode` in models.dev (`PROVIDER_TO_MODELS_DEV`), and models.dev reports the *provider's* limit, not the model's native spec.

Example: `big-pickle` resolves to 200K via models.dev, even though the underlying MiMo-V2.5 supports 1M natively. OpenCode Zen caps it at 200K on their proxy.

### Probing context window discrepancies

```python
# Check what models.dev reports for a specific alias
python3 -c "
from agent.models_dev import lookup_models_dev_context
print(lookup_models_dev_context('opencode-zen', 'big-pickle'))
"  # returns 200000

# Check what the hardcoded DEFAULT_CONTEXT_LENGTHS says
python3 -c "
import sys; sys.path.insert(0, '~/.hermes/hermes-agent')
from agent.model_metadata import DEFAULT_CONTEXT_LENGTHS
print(DEFAULT_CONTEXT_LENGTHS.get('mimo-v2.5'))  # returns 1048576
"
```

### Querying models.dev directly

```bash
curl -s "https://models.dev/api.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
models = data.get('<provider>', {}).get('models', {})
entry = models.get('<alias>', {})
print(json.dumps(entry.get('limit', {}), indent=2))
"
```

### Persisted context cache

Hermes caches discovered context lengths in `~/.hermes/context_length_cache.yaml`. If a provider changes its limits, invalidate the cache:
```python
from agent.model_metadata import _invalidate_cached_context_length
_invalidate_cached_context_length('big-pickle', 'https://opencode.ai/zen/v1')
```

## Context File Truncation

Once the context window is known, Hermes uses it to budget how much of SOUL.md and other context files to inject into the system prompt. The dynamic formula (6% of context × 4 chars/token, floor 20K, ceiling 500K) means a 256K-context model gets ~61K chars for context files. See `references/context-file-truncation.md` for the full formula, head/tail truncation ratios (70%/20%), and implications for SOUL.md sizing on different context windows.

## Pitfalls

- **Self-identification is not proof.** Models can misidentify themselves, especially smaller ones. Always cross-reference with architecture clues (context window, reasoning tokens, response style).
- **Providers can swap backends without notice.** The alias stays the same; the underlying model changes. Periodic re-probing is the only way to detect this.
- **models.dev reports provider limits, not native model specs.** An aggregator may cap context well below what the underlying model supports. Always cross-reference the hardcoded `DEFAULT_CONTEXT_LENGTHS` with what models.dev reports — the gap reveals provider-imposed caps.
- **Stale context cache.** If a provider raises limits, the persisted cache holds the old value. Use `_invalidate_cached_context_length()` to force re-resolution.
- **Rate limits.** Probing multiple models rapidly may hit rate limits. Add delays between requests.
- **The `/v1/models/{id}` endpoint often doesn't exist** for aggregator providers. Don't assume it will work.

## Reference Data

- `references/opencode-zen-mimo.md` — OpenCode Zen's `big-pickle` alias and Xiaomi MiMo-V2.5, including the 200K vs 1M context window discrepancy.
- `references/context-file-truncation.md` — How Hermes uses context window size to calculate SOUL.md budgets, truncation ratios, and resolution order.
