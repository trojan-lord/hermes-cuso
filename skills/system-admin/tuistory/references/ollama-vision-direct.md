# Vision via Direct Ollama API

When the Hermes vision tool isn't configured or needs a gateway restart, hit Ollama's REST API directly.

## Python One-Shot

```python
import base64, json, urllib.request

path = '/path/to/image.png'
with open(path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()

payload = json.dumps({
    'model': 'gemma3:4b',  # or any vision model
    'prompt': 'Describe this image in detail...',
    'images': [b64],
    'stream': False
}).encode()

req = urllib.request.Request(
    'http://localhost:11434/api/generate',
    data=payload,
    headers={'Content-Type': 'application/json'}
)
resp = urllib.request.urlopen(req, timeout=180)
result = json.loads(resp.read())
print(result['response'])
```

## Batch Multiple Images

Loop over a list of image paths, send each to the same model. Set generous timeout (180s) — cold model loads can be slow.

## When to Use

- Hermes vision tool not configured yet (needs `auxiliary.vision` config + gateway restart)
- Need image analysis before session restart
- Vision tool hitting wrong provider
- Debugging what a vision model actually sees

## Pitfalls

- First call to a cold model: 30+ seconds. Subsequent calls: ~1-2s per image.
- Large PNGs (2MB+) take longer than compressed JPEGs
- Model must support vision (gemma3:4b, llava, etc.) — text-only models will ignore the image
- `stream: False` returns complete response. `stream: True` returns chunks (useful for long outputs).
