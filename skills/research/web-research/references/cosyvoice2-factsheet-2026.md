# CosyVoice family fact sheet (verified 2026-08-02)

Condensed knowledge bank from a full primary-source verification session (GitHub + HF API + arXiv). Full fact sheet on disk: `/home/h2/cosyvoice2_factsheet.md`. Every number below was checked against the cited source on 2026-08-02.

## Repo state / identity (things that WILL trip up future sessions)
- Repo **transferred**: FunAudioLLM/CosyVoice → **QwenAudio/CosyVoice** (old URL redirects, but GitHub issue-search API 422s on the old name — search `repo:QwenAudio/CosyVoice`).
- 22.5k stars / 2.6k forks / 739 open issues; last commit 2026-05-25; Apache-2.0.
- Flagship is now **Fun-CosyVoice3-0.5B-2512** (released Dec 2025) — README explicitly recommends CV3 over CV2. CV2 remains usable; dev energy is on CV3.
- HF `FunAudioLLM/CosyVoice2-0.5B` weights updated 2026-05-31 (ONNX exports added); 4.9k downloads / 83 likes.
- Demo page `funaudiollm.github.io/cosyvoice2` is **404** as of Aug 2026 — its latency / 3–10 s reference-length claims are unverifiable; use the CV3 paper for "3 s prompt" and "150 ms bi-streaming" instead.

## Paper IDs (authoritative source = README bibtex, NOT memory)
- CosyVoice 1: arXiv 2407.05407
- **CosyVoice 2: arXiv 2412.10117** — user-supplied "2504.13180" was an unrelated vision paper (PerceptionLM)
- CosyVoice 3: arXiv 2505.17589
- CV2: arXiv HTML render was truncated to ToC+abstract; full text needed PDF + `pdftotext -layout`

## Architecture & sizes (CosyVoice2-0.5B)
- LM = **Qwen2.5-0.5B** backbone fine-tuned for next-token speech-token prediction; FSQ tokenizer (6561 codes, 25 Hz); chunk-aware causal flow matching → 50 Hz mel; **24 kHz** output; HiFi-GAN vocoder; campplus 192-dim speaker embedding; RAS sampling top_p 0.8 / top_k 25 (all in `cosyvoice2.yaml`).
- fp32 file sizes → param math (÷4 B/param): llm.pt 2,023 MB ≈ **505M** (the "0.5B"), flow.pt 451 MB ≈ 113M, hift.pt 83 MB ≈ 21M, speech_tokenizer_v2.onnx 496 MB ≈ 124M. Full pipeline ≈ **0.64B params**. No larger CV2 variant exists (family: 300M → 0.5B → 0.5B).

## License
- **Apache-2.0 for code AND weights → commercial use OK** (triple-verified: GitHub LICENSE file, GitHub API license key, HF card frontmatter + tags).
- Contrast: F5-TTS = MIT code but **CC-BY-NC weights** (non-commercial); XTTS-v2 = **Coqui Public Model License** (non-commercial, and abandoned — HF last modified Dec 2023, Coqui shut down 2024).

## VRAM / CPU verdicts (the "can it run on 4 GB" question)
- fp16 weights ≈ 1.3 GB (LM 1.0 + flow 0.23 + hift 0.04) ⇒ ~2–3 GB total with activations ⇒ **fits a 4 GB GTX 1650 Ti in fp16** with the ONNX tokenizer pinned to CPU and short text. No first-party VRAM table exists (paper has zero hardware benchmarks); no verified 4 GB success report found — computed-feasible but practically unconfirmed.
- TRT engines add ~4.5 GB (issue #835); `flow_cache` branch OOMs small cards (#1165); VRAM grows in long-running servers (#667).
- **CPU-only: official stack effectively unusable** — hangs on an i9 3.7 GHz (issue #678). Community GGUF route = open PR #1872 (llama-cpp backend; T4: PyTorch fp16 RTF 1.17 → GGUF F16 RTF 0.45), but flow + vocoder stay torch-CPU ⇒ RTF > 1.0 ⇒ worse than qwentts.cpp's 1.4× realtime CPU baseline.
- Top issue class = speed complaints on modest GPUs (#75, #237, #739, #1237, #1262).

## Quality / benchmarks (official README eval table, CV2 row)
- zh CER 1.45 / en WER 2.57; speaker similarity **75.7 zh / 65.9 en** (human 75.5/73.4). Beats F5-TTS (74.1/64.7), trails closed Seed-TTS.
- Zero-shot cloning: CV3 eval uses **3 s prompts** ("cut the first 3 seconds of the audio clip as prompt speech"); 3–10 s is the commonly cited range. Prompt caching via `add_zero_shot_spk`.
- Instruct mode: emotion/rate/dialect/role + `<|endofprompt|>`; fine-grained `[laughter]`, `[breath]`, `<strong>word</strong>` tags. 9 languages, zh strongest; repo ships `CosyVoice-BlankEN` for pure-EN.

## Streaming
- Native single-model stream + offline (chunk-aware flow; 4 attention masks). Paper §2.5 gives latency formula only — no absolute ms. CV3 claims 150 ms bi-streaming.
- Quirk: naive streaming re-processes growing context (A, 2A, 3A…) → can be SLOWER than offline (#755); popping artifacts at chunk boundaries (#341).

## Head-to-head (verified numbers)
| | CV2-0.5B | F5-TTS | XTTS-v2 |
|---|---|---|---|
| Params | ~0.64B total | ~0.3B | ~0.47B |
| License | Apache-2.0 | MIT code / CC-BY-NC weights | CPML (non-commercial) |
| GPU speed | slowest (T4 fp16 RTF ~1.17) | fastest (L20 offline PyTorch RTF 0.147, TRT-LLM 0.040) | ~0.1–0.2 [unverified] |
| Streaming | native | no | no |
| Maintenance | active (QwenAudio, CV3 successor) | active | abandoned |

## Sources
- Raw README: `raw.githubusercontent.com/FunAudioLLM/CosyVoice/main/README.md`
- HF: `huggingface.co/FunAudioLLM/CosyVoice2-0.5B` (+ `/api/models/.../tree/main` for sizes)
- Papers: arxiv.org/abs/2412.10117 · 2407.05407 · 2505.17589
- Issues: #678 (CPU hang) · #755 (streaming context growth) · #835 (TRT VRAM) · #1165 (flow_cache OOM) · #667 (VRAM leak) · #341 (popping) · #140 (length limit ~20 s) · #1872 (llama-cpp PR with T4 RTF table)
