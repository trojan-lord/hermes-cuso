# XTTS-v2 (Coqui) — Verified Fact Sheet & Qwen3 Comparison

Research date: 2026-08-02. Every claim below was verified against primary sources at research
time (HF API, GitHub API, PyPI API, arXiv, readthedocs). Re-verify dates/versions if stale.
Relevant when: evaluating TTS engines for voice cloning on the 4 GB GTX 1650 Ti, or answering
"XTTS vs Qwen3" / "can I use XTTS commercially".

## Verified hard numbers

- **Params: ~467M total.** GPT-2-style AR transformer **443M** + VQ-VAE (DVAE) **13M** + latent
  diffusion decoder **26M** (paper: arXiv 2406.04904, builds on Tortoise). Cross-checked by fp32
  checkpoint arithmetic: `model.pth` = 1,867,929,118 B ÷ 4 = 466,982,280 params.
- **Config** (config.json): 30 layers, 1024 hidden, 16 heads; 6681 text tokens / 1026 audio tokens;
  perceiver resampler; `kv_cache=True` default; sampling temp 0.75 / top_k 50 / top_p 0.85 /
  repetition_penalty 5.0; `gpt_cond_len` 30 (max reference conditioning, seconds); `max_ref_len` 10;
  output 24 kHz. **Text caps: `gpt_max_text_tokens` 402 / `gpt_max_audio_tokens` 605 → long text
  MUST be chunked (~250–400 chars/pass is the practical sweet spot); inter-chunk prosody is the
  known weak spot.**
- **VRAM:** weights fp32 ≈ 2.1 GB (+0.21 GB dvae.pth) ≈ 4.5–5.5 GB runtime; **fp16 ≈ 2–3 GB runtime
  → fits 4 GB GTX 1650 Ti** via `.half()` and/or `load_checkpoint(use_deepspeed=True)`
  (docs recommend `deepspeed==0.10.3`). Community sources: gigagpu "~2 GB at FP16"; AtmosCompute
  "from 4 GB VRAM (fp16)".
- **CPU-only:** feasible but SLOW — community report of ~30 s delay (idiap discussion #507);
  ~0.2–0.5× real-time on a desktop CPU (estimate, no authoritative benchmark). Compare: Qwen3 GGUF
  on same machine ≈ 1.4× RT. On GPU (T4): real-time 120–150 wpm (Baseten).
- **Reference clip:** model card claims **6 s**; docs mention 3 s minimum; 6–8 s is the sweet spot.
  v2 supports multiple speaker references + interpolation; cross-language cloning (clone EN voice →
  speak any of 17 languages).
- **Emotion/prosody:** no emotion tags or per-line control — emotion/style transfer ONLY via the
  reference clip. Good prosody when reference delivery matches the desired tone.
- **Streaming:** native `inference_stream()` / `synthesize_stream()` (stream_chunk_size=20); official
  claim **<200 ms time-to-first-chunk**; streaming trades total throughput for first-audio latency.

## License — the dealbreaker

- **WEIGHTS = CPML 1.0.0 (Coqui Public Model License) = NON-COMMERCIAL ONLY.** Verbatim: "This
  license allows only non-commercial use of a machine learning model and its outputs." Commercial
  entities may use it for internal testing/evaluation/non-commercial R&D; **training other models
  for commercial use is explicitly NOT non-commercial**; any revenue-generating use is excluded.
- **CODE = MPL-2.0** (separate from weights; verified via GitHub API).
- `coqui.ai/cpml` link is dead (HTTP 404). No one left to enforce, but the license still binds.
- **Consequence for a commercial character voice: XTTS-v2 weights are off-limits.** Permissive
  alternatives: F5-TTS, Kokoro, or permissively-licensed XTTS derivatives (verify each model card).

## Ecosystem status (2026-08)

- Coqui the company shut down ~Jan 2024: coqui.ai 404s; HF space `coqui/xtts` last updated
  2024-01-15; original `coqui-ai/TTS` repo last commit 2024-02-10; community issue #3778.
- **Maintained fork: `idiap/coqui-ai-TTS`** (Idiap Research Institute): 2.3k★, 290 forks, last
  commit 2026-06-10, default branch `dev`, MPL-2.0. Docs live at tts.readthedocs.io.
- **PyPI `coqui-tts` still released: v0.27.5 (2026-01-26)**, Python >=3.10,<3.15. 65 dependencies
  incl. torch>=2.2, torchaudio, transformers>=4.57, coqpit-config, librosa, numba, scipy.
  `pip install coqui-tts[cuda]` style extras for torch.
- Wrappers: AllTalk (erew123/alltalk_tts) actively maintained, bundles XTTSv2, has low-VRAM mode.

## Known quirks

- Autoregressive GPT = slow on CPU; cache `get_conditioning_latents()` for repeated calls.
- Artifacts: repetition/stutter (mitigated by the unusually high repetition_penalty 5.0), "um/uh"
  insertions (community reports — no formal citation).
- 17 languages (model card) / 16 (paper); quality uneven — EN/ES/FR/DE/PT/PL/TR strong,
  zh/ja/ko/hi/ar weaker. 24 kHz output only.
- Setup heavier than a single C++ binary: 65 pip deps, ~2 GB auto-download from HF, Python pinned
  3.10–3.14, torch/numba version alignment gotchas.

## XTTS-v2 vs Qwen3-TTS (user's pipeline) — bottom line

| Criterion | XTTS-v2 | Qwen3-TTS (pipeline default) |
|---|---|---|
| Clone fidelity / prosody | **Wins** — purpose-built zero-shot cloning, 6 s ref | Good (ICL 10–20 s ref), fine-tune path available |
| Fits 4 GB 1650 Ti | Yes, fp16 ~2–3 GB | Yes, Q8_0 ~1.5–2.3 GB |
| CPU-only speed | ~0.2–0.5× RT (bad) | ~1.4× RT (good) |
| Streaming | Native, <200 ms first chunk | tts-server PCM ~83 ms |
| License | **CPML non-commercial** | Apache-2.0 family (verify per model card) |
| Maintenance | Fork-maintained (active) | Active upstream |

## Source URLs

- Model card: https://huggingface.co/coqui/XTTS-v2
- License text: https://huggingface.co/coqui/XTTS-v2/raw/main/LICENSE.txt
- Config: https://huggingface.co/coqui/XTTS-v2/raw/main/config.json
- Paper: https://arxiv.org/abs/2406.04904
- Docs (streaming/params): https://tts.readthedocs.io/en/latest/models/xtts.html
- Fork: https://github.com/idiap/coqui-ai-TTS · API: https://api.github.com/repos/idiap/coqui-ai-TTS
- CPU speed discussion: https://github.com/idiap/coqui-ai-TTS/discussions/507
- PyPI: https://pypi.org/pypi/coqui-tts/json
- Streaming benchmark: https://www.baseten.co/blog/streaming-real-time-text-to-speech-with-xtts-v2/
- VRAM (community): https://gigagpu.com/xtts-v2-vram-requirements/ · https://atmoscompute.com/models/xtts-v2
- AllTalk: https://github.com/erew123/alltalk_tts
- Shutdown issue: https://github.com/coqui-ai/TTS/issues/3778

## Verification method (reusable for any model fact-check)

- **Param count:** fp32 checkpoint bytes ÷ 4 (1,867,929,118 B → 466,982,280 ≈ 467M). Works for any
  fp32 .pth/.bin/.safetensors (÷4 for fp32; GGUF needs the metadata).
- **HF metadata:** GET `https://huggingface.co/api/models/{id}` → cardData.license_name,
  downloads, lastModified; GET `.../tree/main` → per-file sizes; `.../raw/main/README.md` and
  `.../raw/main/LICENSE.txt` for card + license text.
- **Fork liveness:** GitHub API repo fields `archived`, `pushed_at`, `stargazers_count` +
  `GET /repos/{owner}/{repo}/commits?per_page=1` for last commit date. **Follow 301s with `curl -L`**
  (idiap/coqui-tts redirects to idiap/coqui-ai-TTS).
- **PyPI liveness:** GET `https://pypi.org/pypi/{pkg}/json` → info.version, info.requires_dist,
  releases[ver][0].upload_time for release dates.
- **Paper claims:** arXiv export API (`export.arxiv.org/api/query?id_list=...`) for abstract, then
  `pdftotext` for full text (param breakdowns, architecture).
- **Dead-link check:** `curl -sI` to confirm 404s (coqui.ai/cpml was dead).
- DuckDuckGo html endpoint (`html.duckduckgo.com/html/?q=`) works for community data but rate-limits
  hard — space queries out or use it sparingly.
