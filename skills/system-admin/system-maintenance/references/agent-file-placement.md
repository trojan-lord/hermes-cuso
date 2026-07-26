# Agent File Placement — Current Directory Structure

As of 2026-07-19, the following convention is in use.

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
└── piezo/
    └── piezo-sketch.html
```

## Active project directories (NOT moved, contain working references)

These stay in ~ because scripts/configs reference them by absolute path:

- `~/marshall-voice/` — voice cloning data and clips
- `~/marshall-voice-pipeline/` — Demucs pipeline output
- `~/qwentts.cpp/` — TTS model build and binaries
- `~/qwen3-tts-env/` — Python venv for Qwen TTS
- `~/demucs-env/` — Python venv for Demucs
- `~/plato-reference/` — Hermes backup

## User-owned directories (never touch)

- `~/akexim/`, `~/ak-exim/` — website projects
- `~/i/` — dotfiles repo
- `~/SteamTools/`, `~/sddm-astronaut-theme/` — user customizations
- Standard dirs: Desktop, Downloads, Games, Music, Pictures, Templates, Videos, Public
