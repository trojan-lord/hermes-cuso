# Reference Clip Selection Guide

## How to Choose the Best Reference Clip

The reference clip is the foundation of voice cloning quality. A bad reference
means the speaker filtering will fail, and the fine-tuned model will sound wrong.

## Requirements

1. **Duration:** 5-15 seconds optimal
   - Too short (<3s): Not enough voice characteristics
   - Too long (>30s): May include multiple speakers or silence
   
2. **Content:** Natural, clear speech
   - Avoid whispered, shouted, or whispered segments
   - Avoid singing or extreme vocal effects
   - Prefer conversational pace
   
3. **Quality:** Clean audio
   - Minimal background noise
   - No music bleed (after Demucs separation)
   - No clipping or distortion
   
4. **Speaker:** Single speaker only
   - No overlapping voices
   - No other speakers in the segment
   - Ideally the speaker talking for the entire duration

## Extracting a Reference Clip

### From Demucs Output

```bash
# Find a clean segment in the Demucs vocals
# Use ffprobe to check duration
ffprobe -v quiet -show_entries format=duration -of csv=p=0 vocals.wav

# Extract a 10-second clip starting at 30 seconds
ffmpeg -i vocals.wav -ss 30 -t 10 -c copy reference_clip.wav
```

### From Original Video

```bash
# Extract audio segment from video
ffmpeg -i video.mp4 -ss 00:01:30 -t 00:00:10 -vn -acodec pcm_s16le reference.wav

# Then run Demucs on just this clip for cleaner separation
python -m demucs --two-stems=vocals -n htdemucs reference.wav
```

## Generating the Reference Embedding

```bash
# Using qwentts.cpp
cd ~/qwentts.cpp
./build/qwen-codec \
    --model models/qwen-tokenizer-12hz-Q4_K_M.gguf \
    --talker models/qwen-talker-1.7b-base-Q8_0.gguf \
    -i /path/to/reference_clip.wav

# Output files:
#   reference_clip.rvq  (audio codes, needed for ICL mode)
#   reference_clip.spk  (speaker embedding, 2048-dim)
```

## Testing Reference Quality

Before running the full pipeline, test your reference on a small sample:

```python
# Quick test script
import numpy as np
import struct
from extract_speaker import load_spk_embedding, cosine_similarity

# Load your reference
ref = load_spk_embedding("reference.spk")

# Load a known-good clip of the same speaker
known = load_spk_embedding("known_good.spk")

# Should be high similarity
sim = cosine_similarity(ref, known)
print(f"Similarity to known-good: {sim:.4f}")
print(f"  >= 0.90: Excellent reference")
print(f"  0.80-0.90: Acceptable")
print(f"  < 0.80: Try a different reference clip")
```

## Common Issues

### Low similarity despite using the same speaker
- Reference clip may have background noise
- Audio quality too low (sample rate, compression)
- Speaker is using a different vocal register (whispering vs normal)

### High similarity to wrong speakers
- Reference clip may contain multiple speakers
- Reference is too generic (everyone sounds similar at 0.8)
- Try a longer reference with more distinctive vocal characteristics

### Reference from different source quality
- If your Demucs output is 24kHz but reference is 44.1kHz, resample:
  ```bash
  ffmpeg -i reference.wav -ar 24000 reference_24k.wav
  ```

## Marshall Cuso Specific Notes

For the Marshall voice cloning project:
- Best reference: clip_07_trimmed_precise.wav (7.7 seconds)
- Content: "Do you think there's any way you could get me something called tetrodotoxin, it's extracted from pufferfish, and..."
- Quality: Clean Demucs separation, single speaker, natural conversational pace
- Similarity scores: 0.94-0.99 against other Marshall segments
