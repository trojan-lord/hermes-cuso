# F5-TTS — verified fact sheet (2026-08-02)

All facts verified live against: SWivid/F5-TTS GitHub (API + raw source), HF API/card (`SWivid/F5-TTS`), arXiv:2410.06885v3 (20 May 2025), PyPI `f5-tts`, F5-TTS-ONNX, ComfyUI-F5-TTS. Estimates marked `[est]`.

## Verdict-relevant numbers
- **Fits a 4 GB GTX 1650 Ti**: official code loads **fp16 iff CUDA CC≥7** (Turing 7.5 → fp16), fp32 on CPU/BigVGAN (`src/f5_tts/infer/utils_infer.py` `load_checkpoint`). fp16 weights ≈ 0.67 GB + Vocos (~13M params) → **~1.2–2 GB total** `[est from 1,348 MB fp32 ckpt / 335.8M params]`. No official int8 in PyTorch path; ONNX port ships only `CPU_F32.zip` + `GPU_CUDA_F16.zip`.
- **CPU-only**: feasible (fp32, ~1.34 GB RAM). Paper GPU RTF: **0.15 @16 NFE, 0.31 @32 NFE** (RTX 3090, 10 s speech); L20 PyTorch offline 0.1467, TRT-LLM 0.039–0.040 (README runtime table). Default code = 32 NFE. CPU ≈ 0.4–1.5× real-time mid-range `[est]`; one user report ~3 s per ~360-char chunk (issue #1163).
- **Zero-shot cloning**: prompts 4–10 s in paper eval; ref auto-clipped to ~12 s, <12 s + ~1 s trailing silence recommended. **SIM-o 0.66** (GT 0.754), **WER 2.42 @32 / 2.53 @16 NFE** — mid-pack vs VALL-E 2 (0.643), Voicebox (0.64), NaturalSpeech 3 (0.67), MaskGCT (0.687). No emotion/paralinguistic control (paper).
- **Prosody**: fully non-AR flow matching ⇒ native rhythm; no duration model/alignment. Long text auto-chunked at sentence boundaries (~135 chars, adaptive), chunks in parallel, joined with **0.15 s cross-fade** — replaces manual chunk+silence hacks. Single-gen cap ≈ 30 s incl. ref (gen ≈ 22 s − ref via code formula).
- **Streaming**: chunk-level only (`socket_server.py`, `infer_batch_process(streaming=True)`); first packet ≈ 2 s+ (issue #1225). No token streaming.

## Specs
- 335.8M params: DiT (22 layers, 16 heads, dim 1024, FFN 2048) + ConvNeXt V2 (4 layers, 512/1024). Text padded with filler tokens to mel length (E2-TTS scheme).
- **NO Large/1.6B variant exists** — HF search `F5-TTS` (100 results) + GitHub repo search `F5-TTS-Large` (0) + official HF siblings (only F5TTS_Base, F5TTS_Base_bigvgan, F5TTS_v1_Base, F5TTS_v1_Base_no_zero_init). `F5TTS_Small` config exists, no released checkpoint. "1.6B" rumor likely conflation with Qwen-Talker 1.7B / MaskGCT ~1B.
- v1 Base (2025-03-12): same arch + rms qk-norm + `text_mask_padding`. Checkpoints ~1,348 MB fp32 each (HF API `?blobs=true`).

## License — split
- **Code MIT** (repo LICENSE; PyPI). **Weights CC-BY-NC-4.0** (HF card; README: NC due to Emilia training data). Commercial use of official weights NOT allowed. Community finetunes vary (ONNX export code = Apache-2.0) — check per model.

## Maintenance & ecosystem (2026-08)
- 15,054 stars, 2,186 forks, 57 open issues, v1.1.22 released 2026-07-23, ~monthly cadence, not archived. HF: 689K downloads, 1,187 likes, 30+ Spaces.
- Ports: F5-TTS-ONNX (ONNX Runtime/OpenVINO/DirectML), f5-tts-mlx (Apple), F5_TTS_Faster (TRT-LLM), ComfyUI-F5-TTS, official Docker (ghcr.io/swivid/f5-tts), PyPI `f5-tts` 1.1.22.

## Setup
`pip install f5-tts` (inference) / `pip install -e .` (training). Python ≥ 3.10, conda optional (virtualenv fine), **FFmpeg required** (blank output if missing), **no espeak-ng** (Chinese via jieba+pypinyin). Deps: torch≥2.0, torchaudio, torchcodec, vocos, accelerate, transformers, gradio, librosa, pydub, soundfile, hydra-core, wandb, x_transformers, torchdiffeq, rjieba. CPU users must install CPU torch wheels explicitly.

## Quirks
- Official = English + Chinese only (pinyin tokenizer; numbers need preprocessing to be read in Chinese); other languages need community finetunes (list in `src/f5_tts/infer/SHARED.md`).
- Uppercase spelled letter-by-letter ("K.F.C."); punctuation/spaces control pauses; sentence-final punctuation needs trailing space for chunking.
- Sampling variance — `seed` supported in API.
- Notable bugs: word-skipping (#1197, fixed 2025-10), v1→noise regression in 1.1.9 (#1223, fixed), VRAM creep on long text (#851, fixed 2025-03), flash-attn training instability (#1217, open), finetune-gradio shell injection (#1306, open 2026-07).
