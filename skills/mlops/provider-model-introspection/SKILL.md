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

## Pitfalls

- **Self-identification is not proof.** Models can misidentify themselves, especially smaller ones. Always cross-reference with architecture clues (context window, reasoning tokens, response style).
- **Providers can swap backends without notice.** The alias stays the same; the underlying model changes. Periodic re-probing is the only way to detect this.
- **Rate limits.** Probing multiple models rapidly may hit rate limits. Add delays between requests if needed.
- **The `/v1/models/{id}` endpoint often doesn't exist** for aggregator providers. Don't assume it will work.

## Reference Data

See `references/opencode-zen-mimo.md` for specific data on OpenCode Zen's `big-pickle` alias and Xiaomi MiMo-V2.5.
