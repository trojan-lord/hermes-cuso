# Troubleshooting Guide

## Hardware Issues

### "CUDA out of memory" during fine-tuning
```bash
# Check VRAM usage
nvidia-smi

# Reduce batch size
python sft_12hz.py --batch_size 1 ...

# Or use the smaller 0.6B model
python sft_12hz.py --init_model_path Qwen/Qwen3-TTS-12Hz-0.6B-Base ...
```

### GPU not detected
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# If False, reinstall PyTorch with CUDA support
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Slow CPU inference
- Expected: ~1-2 seconds per second of audio on CPU
- If slower, check if other processes are using CPU
- Consider using GPU for inference when available

## Audio Quality Issues

### Demucs leaves artifacts
```bash
# Try the fine-tuned model instead
python -m demucs --two-stems=vocals -n htdemucs_ft -d cuda:0 input.wav

# Or use BS-RoFormer (alternative architecture)
python -m demucs --two-stems=vocals -n mdx_extra_q -d cuda:0 input.wav
```

### Speaker filtering too aggressive
```bash
# Lower the threshold (default 0.85)
python extract_speaker.py --threshold 0.75 ...

# Or use a longer reference clip (10-15 seconds)
```

### Speaker filtering too lenient
```bash
# Raise the threshold
python extract_speaker.py --threshold 0.90 ...

# Or use a more distinctive reference clip
```

### Whisper transcription inaccurate
```bash
# Use a larger model
python transcribe_filtered.py --whisper-model medium ...

# Or manually edit the transcription.txt file
```

## Fine-tuning Issues

### Loss not decreasing
- Check data quality (manual review of transcripts)
- Reduce learning rate: `--lr 1e-5`
- Increase epochs: `--num_epochs 5`

### Model sounds robotic
- Increase training data (more audio)
- Check reference audio quality
- Try different checkpoint (epoch 0 vs epoch 2)

### Model doesn't match speaker
- Reference clip may be poor quality
- Training data may contain other speakers
- Check similarity scores in matches.json

## Pipeline Issues

### yt-dlp download fails
```bash
# Update yt-dlp
pip install -U yt-dlp

# Try different format
yt-dlp -f "bestaudio" -x --audio-format wav <URL>
```

### Demucs fails to start
```bash
# Check ffmpeg is installed
ffmpeg -version

# Reinstall demucs
pip install -U demucs
```

### qwen-tts import errors
```bash
# Check dependencies
pip list | grep -E "torch|transformers|qwen"

# Reinstall if needed
pip install -U qwen-tts
```

## Performance Optimization

### Speed up speaker filtering
- Process on GPU if available: `--device cuda:0`
- Increase chunk size: `--chunk-sec 5.0` (reduces number of chunks)
- Use batch processing (default in script)

### Speed up fine-tuning
- Enable mixed precision (default in script)
- Use FlashAttention: `pip install flash-attn`
- Increase batch size if VRAM allows

### Reduce disk usage
- Delete intermediate files after pipeline completes
- Compress Demucs output: `--mp3 --mp3-bitrate 192`
- Use symlinks for large audio files

## Debug Mode

Enable verbose output:
```bash
# Python scripts
python -u script.py 2>&1 | tee debug.log

# Demucs
python -m demucs -v --two-stems=vocals ...

# Whisper
python -c "import whisper; model = whisper.load_model('base'); result = model.transcribe('audio.wav', verbose=True)"
```

## Getting Help

1. Check the official repos:
   - Qwen3-TTS: https://github.com/QwenLM/Qwen3-TTS
   - Demucs: https://github.com/facebookresearch/demucs
   - Whisper: https://github.com/openai/whisper

2. Search for error messages online

3. Check GPU drivers and CUDA version:
   ```bash
   nvidia-smi
   nvcc --version
   ```

4. Share debug.log when asking for help
