# Tools Installed 2026-07-13

Session where user asked "find more programs like tuistory to help u function." Three rounds of research, 9 subagent delegations total.

## Installed This Session

| Tool | Install | Purpose |
|---|---|---|
| brightnessctl | `pacman -S brightnessctl` (pre-installed) | Screen brightness control |
| wpctl | `pacman -S wpctl` (pre-installed) | WirePlumber audio/volume control |
| playerctl | `pacman -S playerctl` (pre-installed) | Media player control (MPRIS) |
| gammastep | `pacman -S gammastep` | Night light / color temperature |
| ydotool | `pacman -S ydotool` | Desktop automation (click, type, keys) — Wayland |
| rustnet | `pacman -S rustnet` | Per-process network monitoring TUI |
| resterm | `yay -S resterm-bin` | REST/GraphQL/gRPC API client TUI |
| yt-dlp | `yay -S yt-dlp` | YouTube video/audio download |
| cuda | `pacman -S cuda` | NVIDIA CUDA toolkit (nvcc at /opt/cuda/bin/) |
| sox | `pacman -S sox` | Audio processing (qwen-tts dependency) |

## Installed via pip (in ~/qwen3-tts-env)

| Package | Purpose |
|---|---|
| qwen-tts | Qwen3 TTS Python bindings |
| torch + torchaudio | PyTorch with CUDA |
| soundfile | WAV I/O |

## Built from Source

| Tool | Source | Purpose |
|---|---|---|
| qwentts.cpp | github.com/ServeurpersoCom/qwentts.cpp | GGUF Qwen3 TTS inference (CUDA) |

## System State Tools — Quick Reference

```bash
# Battery
cat /sys/class/power_supply/BAT*/capacity

# Brightness
brightnessctl get / brightnessctl set 50%

# Volume
wpctl get-volume @DEFAULT_AUDIO_SINK@
wpctl set-volume @DEFAULT_AUDIO_SINK@ 0.5

# Media
playerctl metadata --format "{{artist}} - {{title}}"
playerctl play/pause/stop

# Network
rustnet  # TUI monitor

# Notifications
notify-send "Title" "Body"
notify-send -u critical "Title" "Urgent body"
```

## Tool Research Patterns

User preference: **always check for the latest and best available tool before recommending.** The AI/ML landscape moves fast. Verify against current GitHub stars, recent commits, and community comparisons. Don't rely on potentially outdated knowledge.

Three research rounds were done with parallel subagent delegations:
1. TUI/agent tools (tmux, Zellij, WezTerm, asciinema, VHS)
2. System admin CLI tools (brightnessctl, mako, grim, slurp, overmind)
3. Terminal automation (node-pty, pexpect, Textual, pyte)
4. Desktop interaction (ydotool, niri msg, cliphist, wev)
5. Viral new tools 2025-2026 (rtk, llmfit, resterm, rustnet)
6. Local AI tools (whisper-cpp, piper, Coqui, Ollama extensions)
7. Voice cloning comparison (GPT-SoVITS, F5-TTS, Fish Speech, Qwen3 TTS)
8. Qwen3 TTS deep dive
9. VoiceBox (jamiepine) evaluation
