# Agent File Placement — Current Directory Structure

As of 2026-07-28, the following convention is in use.

## ~/Documents/

```
~/Documents/
├── manuscripts/
│   ├── parallel-lines/
│   │   ├── parallel-lines-manuscript.docx
│   │   ├── parallel-lines-manuscript.pdf
│   │   ├── parallel-lines-manuscript-v2.docx
│   │   ├── parallel-lines-manuscript-v2.pdf
│   │   ├── parallel-lines-manuscript-full.docx
│   │   ├── parallel-lines-manuscript-full.pdf
│   │   ├── parallel-lines-ch1-narration.mp3
│   │   └── parallel-lines-ch1-full-narration.mp3
│   ├── seppuku/
│   │   ├── seppuku-manuscript.docx
│   │   ├── seppuku-manuscript.pdf
│   │   ├── seppuku-manuscript-full.docx
│   │   └── seppuku-manuscript-full.pdf
│   ├── books-delivery.zip
│   ├── Voice_Memos_July15.zip
│   ├── Metamorphic_Wings_Explanation.zip
│   ├── Metamorphic_Wings_Simple.zip
│   └── manuscript-formatting-standards.md
├── research/
│   ├── dobby_meta_research.md
│   ├── marshall_cuso_character_research.md
│   ├── marshall_cuso_research.md
│   ├── marshall-cuso-speech-research.md
│   ├── pinecil-firmware-update-SKILL.md
│   ├── research-html5-game-architecture.md
│   ├── linux-cli-tools-for-agents.md
│   ├── terminal-automation-tools.md
│   └── stt-research-2025.md
└── cuso/
    ├── marshall_cuso_character_analysis.md
    └── marshall-cuso.md
```

## ~/Projects/

```
~/Projects/
├── websites/
│   ├── ak-exim/          (git repo — static website)
│   └── akexim/           (git repo — static website, newer version)
├── games/
│   ├── kenshin-action/   (git repo — HTML5 game)
│   └── kenshin-game/     (HTML5 game prototype)
├── astryx/
│   ├── astryx-demo/      (Vite + Node Astryx demo)
│   └── astryx-setup/     (Astryx install test)
├── hardware/
│   └── pinecil-update/   (Pinecil firmware files)
├── marshall-voice/
│   ├── tts-provider/     (TTS audio + tts-provider.sh — hermes config points here)
│   ├── journey/          (HyperFrames voice journey composition)
│   ├── origin/           (HyperFrames origin video project)
│   └── pipeline/         (Python extraction pipeline — 4.5G)
├── reference/            (plato-reference, etc.)
└── piezo/                (piezo-sketch.html)
```

## ~/Videos/

```
~/Videos/
├── marshall-voice-coral.mp4
├── voice-journey.mp4
├── voice-journey-v2.mp4
└── RustDesk/
```

## Active project directories in ~/ (NOT moved, contain working references)

These stay in `~/` because they are large build artifacts or venvs with hardcoded absolute paths:

- `~/qwentts.cpp/` — Qwen TTS C++ project (7.1G, git repo, has cmake build dir)
- `~/qwen3-tts-env/` — Python venv for Qwen TTS (5.6G, hardcoded paths)
- `~/demucs-env/` — Python venv for Demucs (5.6G, hardcoded paths)

## Other dirs in ~/ (user-owned, never touch)

- `~/i/` — dotfiles repo (git)
- `~/hermes-cuso/` — Hermes config backup repo (syncs from ~/.hermes)
- `~/SOULS/` — Character SOUL files (git, public repo on GitHub)
- `~/sddm-astronaut-theme/` — SDDM login theme (git repo)
- `~/plato-reference/` — Reference materials for kimaki/Hermes development
- `~/SteamTools/` — Windows SteamTools.exe (runs via Wine?)
- Standard XDG dirs: Desktop, Downloads, Games, Music, Pictures, Templates, Public

## Hidden dirs (non-standard, in ~/)

- `~/.agents/` — Hermes agent skill lock (auto-managed)
- `~/.claude/` — Claude Code skills + transcripts
- `~/.critique/` — Critique tool license
- `~/.hermes-backup/` — Hermes backup (may duplicate hermes-cuso/)
- `~/.hermes-Cuso/` — Older Cuso profile
- `~/.hyperframes/` — HyperFrames cache
- `~/.opencode/` — OpenCode CLI
- `~/.playwriter/` — Playwright CDP logs (regenerates, safe to delete)
- `~/.sisyphus/` — Sisyphus drafts
- `~/.wine-test/` — Wine test prefix (check if in use)
- `~/.ii-original-dots-backup/` — Old dotfiles backup (28K, safe to delete after verifying)
