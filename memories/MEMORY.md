GPU: GTX 1650 Ti Mobile + AMD Renoir. Ollama: qwen3.5:4b. Demucs htdemucs on GPU (v4.1.0). Gaming: Niri Wayland. HDMI games need gamescope `-b` flag (NOT `-e -f`). DualSense BT controllers. Steam VDF editable via Python `vdf` lib.
§
mumble_monster = 'papa' to Cuso. Pola' Bea' = 'Daddy' / 'Dady big balls'. Two different people, different Discord IDs. Respect the distinction. Daddy is playful/teasing — tests boundaries, laughs when refused. Dynamic is lighthearted.
§
GitHub: trojan-lord. gh auth active. Push only existing repos; ask first. SOUL.md ref rule: never borrow show quotes verbatim, only flavor/patterns.
§
Hermes backup: trojan-lord/hermes-cuso (public, GitHub). Local: ~/hermes-cuso. Sync: bash ~/hermes-cuso/sync.sh. SOUL.md: do NOT trim — set context_file_max_chars: 50000 in config.yaml instead (default 20K truncates middle of 32K SOUL.md). User explicitly wants full personality preserved.
§
TTS: "marshall" provider. Output: OGG/Opus (libopus). Config: output_format: ogg + voice_compatible: true. Provider: ~/marshall-voice/tts-provider.sh. Discord requires OGG — MP3 silently rejected. ICL ref: clip_07_trimmed_precise (7.7s). Voice quality concern: speech-patterns skill too prescriptive.
§
CRITICAL VOICE RULE: Thread 1525642190376931509 = ALL voice memos. MEDIA: tag first, then "Full text: [...]". MUST call skill_view('marshall-speech-patterns') BEFORE EVERY text_to_speech. No exceptions. Every time. Load skill, then write prompt.
§
§ Gateway restart: blocked by terminal tool. Workaround: write cmd to script, tuistory launch. ALWAYS load skills, stay in character, verify tech from source.
§
§ Primary model: big-pickle (opencode-zen). Fallback: deepseek-v4-flash-free → mimo-v2.5-free → north-mini-code-free → ollama qwen3.5:4b. Config: ~/.hermes/config.yaml fallback_model. Intermittent outages on backend.
§
User tests on iPad (Discord client). HTML files can't open from iOS Files into Safari. Serve via HTTP on local network (UFW: port 8080 allowed). Bundle p5.js inline for zero-network builds. Cloudflare tunnel blocked (outbound 7844). Ngrok needs auth.