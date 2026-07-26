# Curated Linux CLI Tools for AI Agents

System admin, monitoring, and automation tools. All verified on CachyOS (Arch) + Niri (Wayland).

---

## 1. System Monitoring (htop alternatives)

| Tool | ⭐ | What it does | Install | URL |
|------|-----|-------------|---------|-----|
| **btop** | 33.5k | Resource monitor: CPU/RAM/disk/network graphs, tree view, mouse support. Best htop replacement. C++. | `pacman -S btop` | https://github.com/aristocratos/btop |
| **bottom (btm)** | 13.7k | Cross-platform graphical process/system monitor. Widgets for CPU, memory, disk, network, temp. Rust. | `pacman -S bottom` or `cargo install bottom` | https://github.com/ClementTsang/bottom |
| **glances** | 33k | Python system monitor. Web UI, REST API, plugins, CSV/JSON/InfluxDB export. Great for agent automation. | `pacman -S glances` | https://github.com/nicolargo/glances |
| **gotop** | 3k | Terminal graphical activity monitor (Go). | `yay -S gotop` | https://github.com/xxxserxxx/gotop |
| **procs** | 6k | Modern `ps` replacement (Rust). Colorized, tree view, keyword search, JSON output. | `cargo install procs` | https://github.com/dalance/procs |
| **dust** | 12k | Intuitive disk usage analyzer (`du` replacement, Rust). Visual bar charts. | `pacman -S dust` | https://github.com/bootandy/dust |
| **duf** | 15.2k | Better `df` alternative. Colorized, grouped output. | `pacman -S duf` | https://github.com/muesli/duf |
| **ncdu** | — | Ncurses disk usage analyzer. Interactive TUI for exploring disk usage. | `pacman -S ncdu` | https://dev.yorhel.nl/ncdu |
| **hyperfine** | — | Command-line benchmarking. Statistical analysis of command runtimes. | `pacman -S hyperfine` | https://github.com/sharkdp/hyperfine |

## 2. Network Tools

| Tool | ⭐ | What it does | Install | URL |
|------|-----|-------------|---------|-----|
| **bandwhich** | 11.9k | Terminal bandwidth utilization per-process. | `cargo install bandwhich` | https://github.com/imsnif/bandwhich |
| **nethogs** | 3.7k | Linux 'net top' — groups bandwidth by process. | `pacman -S nethogs` | https://github.com/raboof/nethogs |
| **gping** | 12.6k | `ping` with a graph. Visualize latency over time. | `pacman -S gping` | https://github.com/orf/gping |
| **doggo** | 4.4k | DNS client for humans. `dig` on steroids. Supports DoH, DoT. | `go install mrkaran/doggo@latest` | https://github.com/mr-karan/doggo |
| **httpie** | 38.3k | Modern HTTP client. JSON, colors, sessions, plugins. | `pacman -S httpie` | https://github.com/httpie/cli |
| **xh** | 7.9k | Fast, friendly HTTP client (HTTPie clone, Rust). | `cargo install xh` | https://github.com/ducaale/xh |

## 3. File Management (CLI)

| Tool | ⭐ | What it does | Install | URL |
|------|-----|-------------|---------|-----|
| **eza** | 22.6k | Modern `ls` replacement. Icons, Git status, tree view, themes. | `pacman -S eza` | https://github.com/eza-community/eza |
| **bat** | 59.7k | `cat` clone with syntax highlighting, Git integration, auto-paging. | `pacman -S bat` | https://github.com/sharkdp/bat |
| **fd** | 43.7k | Fast, user-friendly `find` alternative. Regex, colorized, respects .gitignore. | `pacman -S fd` | https://github.com/sharkdp/fd |
| **ripgrep (rg)** | 66.1k | Blazing fast `grep`. Respects .gitignore, regex, colorized. | `pacman -S ripgrep` | https://github.com/BurntSushi/ripgrep |
| **fzf** | 81.7k | General-purpose fuzzy finder. Integrates with everything. | `pacman -S fzf` | https://github.com/junegunn/fzf |
| **ranger** | 17.3k | VIM-inspired file manager for the console. Tabs, bookmarks, rifle opener. | `pacman -S ranger` | https://github.com/ranger/ranger |
| **lf** | 9.4k | Terminal file manager (Go). Faster ranger alternative. | `pacman -S lf` | https://github.com/gokcehan/lf |
| **nnn** | 21.7k | Fastest terminal file manager. Plugins, disk usage, batch rename. | `pacman -S nnn` | https://github.com/jarun/nnn |
| **lsd** | 16.1k | Next-gen `ls` with icons, colors, tree view. | `pacman -S lsd` | https://github.com/Peltoche/lsd |
| **sd** | — | Intuitive find & replace CLI (`sed` alternative). | `cargo install sd` | https://github.com/chmln/sd |
| **zoxide** | 38k | Smarter `cd`. Learns habits, frecency-based jumping. | `pacman -S zoxide` | https://github.com/ajeetdsouza/zoxide |
| **broot** | — | Directory tree viewer with preview, search, fuzzy matching. | `pacman -S broot` | https://github.com/Canop/broot |
| **rclone** | — | "rsync for cloud storage." Sync/mount 40+ cloud providers. | `pacman -S rclone` | https://rclone.org |
| **just** | 34.7k | Command runner (better `make`). Justfile task automation. | `pacman -S just` | https://github.com/casey/just |

## 4. Notification Systems

| Tool | ⭐ | What it does | Install | URL |
|------|-----|-------------|---------|-----|
| **dunst** | 5.5k | Lightweight, customizable notification daemon. X11 + Wayland. | `pacman -S dunst` | https://github.com/dunst-project/dunst |
| **mako** | 3.2k | Lightweight Wayland notification daemon. Sway developer. CSS styling. | `pacman -S mako` | https://github.com/emersion/mako |

**Agent tip:** For headless agents, `dunstify` (bundled with dunst) or `notify-send` push desktop notifications. On Wayland/Niri, `mako` is the native choice.

## 5. Clipboard Management (Wayland)

| Tool | ⭐ | What it does | Install | URL |
|------|-----|-------------|---------|-----|
| **wl-clipboard** | 2.4k | Command-line copy/paste for Wayland (`wl-copy`/`wl-paste`). Essential for agent↔desktop interaction. | `pacman -S wl-clipboard` | https://github.com/bugaevc/wl-clipboard |

```bash
echo "text" | wl-copy           # copy to clipboard
wl-paste                       # paste from clipboard
wl-paste --type image/png > x.png  # grab image from clipboard
```

## 6. Screenshot / Screen Capture (Wayland)

| Tool | ⭐ | What it does | Install | URL |
|------|-----|-------------|---------|-----|
| **grim** | 1k | Screenshot utility for Wayland. Full output or region. | `pacman -S grim` | https://github.com/emersion/grim |
| **slurp** | 1.3k | Select a region in a Wayland compositor. Pipe output to grim. | `pacman -S slurp` | https://github.com/emersion/slurp |
| **Satty** | 2.2k | Modern screenshot annotation tool (Rust/GTK4). Wayland native. | `yay -S satty-git` (AUR) | https://github.com/Satty-org/Satty |
| **grimblast** | — | Screenshot helper for Hyprland/Niri. grim+slurp+clipboard. | `yay -S grimblast-git` (AUR) | https://github.com/hyprwm/grimblast |
| **swaybg** | 0.8k | Wallpaper tool for Wayland compositors (Niri compatible). | `pacman -S swaybg` | https://github.com/swaywm/swaybg |

```bash
grim ~/screenshot.png                    # full screen
grim -g "$(slurp)" ~/region.png          # region selection
grim -g "$(slurp)" - | wl-copy -t image/png  # region → clipboard
```

## 7. Process Supervision

| Tool | ⭐ | What it does | Install | URL |
|------|-----|-------------|---------|-----|
| **overmind** | 3.7k | Process manager for Procfile + tmux. Auto-restart, log management. Simpler than supervisord. | `yay -S overmind` (AUR) | https://github.com/DarthSim/overmind |
| **hivemind** | — | Process manager for Procfile apps. Minimal, no dependencies. | `yay -S hivemind-bin` (AUR) | https://github.com/DarthSim/hivemind |
| **s6** | 1k | Industrial-strength process supervision. Complex but extremely reliable. | `pacman -S s6` | https://skarnet.org/software/s6/ |
| **aware** | — | Simple process supervisor (Rust). Lightweight. | `cargo install aware` | https://github.com/nicokosi/aware |

```bash
# Procfile example
worker: python worker.py
server: node server.js
watcher: cargo watch -x run

# Then:
overmind start    # or hivemind
```

## 8. Desktop Interaction (Wayland/Niri)

Tools for querying and controlling the desktop from terminal. All verified on Niri + Noctalia.

| Tool | What it does | Install | Notes |
|------|-------------|---------|-------|
| **niri msg** | Full compositor control: windows, workspaces, actions, screenshots. JSON output. | Built into niri | Requires `NIRI_SOCKET` env var (see `linux-desktop` skill for discovery) |
| **brightnessctl** | Screen brightness control. | `pacman -S brightnessctl` | `brightnessctl get` / `brightnessctl set +5%` |
| **wpctl** | Audio/volume control (WirePlumber/PipeWire). | `pacman -S wireplumber` | `wpctl get-volume @DEFAULT_AUDIO_SINK@` |
| **playerctl** | Media player control. Play/pause/next/metadata. | `pacman -S playerctl` | `playerctl metadata --format "{{artist}} - {{title}}"` |
| **gammastep** | Screen color temperature (night light). | `pacman -S gammastep` | `gammastep -m manual -t 4000:4000` (warm) |
| **ydotool** | Desktop automation: mouse clicks, keyboard input. Wayland-native. | `pacman -S ydotool` | Requires `ydotoold` daemon: `sudo systemctl enable --now ydotoold` |
| **notify-send** | Desktop notifications. Works with Noctalia shell. | `pacman -S libnotify` | `notify-send "Title" "Body"` |

**Agent tip:** From systemd (Linger=yes), `niri msg` needs socket discovery and `notify-send` may timeout if shell isn't running. See `linux-desktop` skill for workarounds.

## 9. Local AI Tools (Voice, Text Gen, Image Gen, Terminal Bridges)

All tools run locally with no cloud dependency. Verified on CachyOS + GTX 1650 Ti (4GB VRAM) + 14GB RAM.

### Speech-to-Text (STT)

| Tool | What it does | Install | Resources |
|------|-------------|---------|-----------|
| **whisper-cpp** | C/C++ Whisper port. Fast local STT. tiny/base/small/medium/large models. | `pacman -S whisper-cpp` | tiny: ~1GB RAM; small: ~2GB; medium: ~5GB. Vulkan/CUDA for GPU. |
| **faster-whisper** | Python wrapper (CTranslate2). 4x faster than original Whisper. INT8 quantization. | `paru -S python-faster-whisper` | ~1.5GB RAM for small model. Best Python API. |
| **python-openai-whisper** | Original Python implementation. Full-featured but slower. | `pacman -S python-openai-whisper` | Needs PyTorch (~2GB extra). Base ~1GB. |
| **vosk** | Lightweight streaming STT. ~50MB models. Great for real-time. | `pip install vosk` | ~50MB-2GB. Best for low-resource/real-time. |
| **gst-plugin-whisper** | GStreamer Whisper plugin — pipe mic to Whisper for live transcription. | `pacman -S gst-plugin-whisper` | Same as whisper-cpp |

### Text-to-Speech (TTS)

| Tool | What it does | Install | Resources |
|------|-------------|---------|-----------|
| **Qwen3 TTS** | State-of-the-art voice cloning from 3-sec audio. 10 languages. Apache 2.0. GGUF for low VRAM. | `pip install qwen-tts` (use venv) | 0.6B Q4_K_M: ~884MB. 1.7B Q4_K_M: ~1.5GB. **Best voice cloning TTS (2026).** |
| **GPT-SoVITS** | Voice cloning from 5-sec zero-shot or 1-min fine-tuning. MIT. 59.7k ⭐. | `install.sh --device CU126` (conda) | Works on 4GB VRAM. CPU fallback. Best community/ecoystem. |
| **piper-tts** | Fast neural TTS. 50+ languages. Real-time on CPU. No voice cloning. | `paru -S piper-tts piper-voices-en-us` | <200MB RAM. Best non-cloning TTS. |
| **espeak-ng** | Robust parametric TTS. Robotic voice. Many languages. | `pacman -S espeak-ng` | ~10MB RAM. |
| **edge-tts** | Microsoft Edge neural voices. Excellent quality but cloud. | `pip install edge-tts` | Needs internet. |

**Pitfall:** Coqui XTTS v2 was previously popular but Coqui.ai went bankrupt in 2024 — dead project, no updates. Use Qwen3 TTS or GPT-SoVITS instead.

### Image Generation (CLI)

| Tool | What it does | Install | Resources |
|------|-------------|---------|-----------|
| **stable-diffusion.cpp (Vulkan)** | C/C++ SD/SDXL/Flux inference. CLI-native. | `paru -S stable-diffusion.cpp-vulkan-git` | 4GB VRAM: SD 1.5/quantized SDXL. **Best CLI option.** |
| **ComfyUI** | Node-based GUI + API. Powerful workflows. | `paru -S comfyui` | 4GB: SD 1.5. SDXL needs `--lowvram`. ~2GB/model disk. |
| **A1111 (sd-webui)** | Classic AUTOMATIC1111. CLI args + web UI. | `paru -S stable-diffusion-webui` | 4GB: SD 1.5 best. `--medvram` for SDXL. |
| **cmfy** | CLI wrapper for ComfyUI workflows. | `paru -S cmfy-bin` | Same as ComfyUI |

### Local API Servers (LLM)

| Tool | What it does | Install | Resources |
|------|-------------|---------|-----------|
| **Ollama** | Model server, OpenAI-compatible API. Pull/run models. | `pacman -S ollama` | Per-model: tiny ~500MB, 7B ~4GB, 13B ~8GB. |
| **koboldcpp** | GGUF server + KoboldAI API + web UI. | `paru -S koboldcpp-cuda` | Single binary. ~500MB + model. CUDA build for GPU. |
| **llamafile** | Single-file executable: model + server bundled. | `paru -S llamafile-bin` | ~500MB + model. Zero deps. CPU-only default. |
| **local-ai** | All-in-one: LLM + TTS + STT + embeddings + images. | `paru -S local-ai-bin` | ~1GB baseline + per-model. Heaviest option. |
| **GPT4All** | Desktop + local server for GGUF models. | `pacman -S gpt4all-chat` | Qt app. ~500MB + model. |

### Terminal AI Bridges (AI ↔ CLI Workflow)

| Tool | What it does | Install | Resources |
|------|-------------|---------|-----------|
| **aichat-ng** | Multi-provider terminal chat TUI. Ollama/OpenAI/Claude/Gemini. | `paru -S aichat-ng-bin` | ~50MB. Connects to Ollama. |
| **OpenCode** | AI coding agent for terminal. Multi-file refactoring. | `paru -S opencode-bin` | Minimal. Needs ripgrep. |
| **Aider** | AI pair programming. Git-aware editing. Voice mode. | `paru -S aider-chat-bin` | Minimal. Connects to Ollama. |
| **Fabric** | AI pattern library. Extract/summarize/transform content. | `paru -S fabric-ai-bin` | Minimal. Pipeline engine. |
| **Tabby** | Self-hosted Copilot alternative. Code completion + chat. | `paru -S tabbyml-cuda-bin` | ~2GB RAM + model. Heavier. |
| **Open Interpreter** | Run LLM code locally. Terminal access, file ops. | AUR available | Connects to Ollama. ~200MB. |
| **Claude Squad** | Manage multiple AI agents in parallel tmux sessions. | `paru -S claude-squad-bin` | tmux-based. Minimal. |

### Quick-Start Commands (for 4GB VRAM systems)

```bash
# STT
sudo pacman -S whisper-cpp

# TTS with voice cloning (Qwen3 TTS — best available 2026)
python3 -m venv ~/qwen3-tts-env
source ~/qwen3-tts-env/bin/activate
pip install qwen-tts

# TTS without voice cloning (fast, lightweight)
paru -S piper-tts piper-voices-en-us

# Image Gen (4GB VRAM friendly)
paru -S stable-diffusion.cpp-vulkan-git

# API Server (alternative to Ollama)
paru -S koboldcpp-cuda

# Terminal Bridges
paru -S aichat-ng-bin aider-chat-bin fabric-ai-bin
```

---

## Bonus: Recommended Helpers

| Tool | What it does | Install |
|------|-------------|---------|
| **delta** | Beautiful git diff viewer | `cargo install git-delta` |
| **lazygit** | Terminal UI for git | `pacman -S lazygit` |
| **lazydocker** | Terminal UI for docker | `yay -S lazydocker` (AUR) |
| **cheat** | Interactive cheatsheets | `pacman -S cheat` |
| **tldr** | Simplified man pages | `pacman -S tldr` |
| **mcfly** | ML-based shell history search | `pacman -S mcfly` |
| **navi** | Interactive cheatsheet tool (⭐17.3k) | `yay -S navi` (AUR) |

---

## 10. AI-Era CLI Tools (2025-2026)

The biggest new category of CLI tools. AI coding agents, LLM infrastructure, developer tooling for the agentic era.

| Tool | ⭐ | What it does | Install | URL |
|------|-----|-------------|---------|-----|
| **rtk** | 70.6k | CLI proxy that reduces LLM token consumption by 60-90%. Single Rust binary, zero deps. Transparent proxy for Claude Code/Codex/Gemini CLI. | `cargo install rtk` or `curl -fsSL https://rtk.ai/install.sh \| bash` | https://github.com/rtk-ai/rtk |
| **llmfit** | 29.4k | One command to find what LLMs run on your hardware. Benchmarks hundreds of models against your actual GPU/CPU/RAM. | `cargo install llmfit` | https://github.com/AlexsJones/llmfit |
| **DeepSeek-Reasonix** | 26.8k | DeepSeek-native AI coding agent for the terminal. Prefix-cache stability, TUI with real-time tool output. | `npm install -g deepseek-reasonix` | https://github.com/esengine/DeepSeek-Reasonix |
| **herdr** | 15.9k | Agent multiplexer — run and manage multiple coding agents in parallel TUI panels. Like tmux for AI agents. | `cargo install herdr` or `nix run github:ogulcancelik/herdr` | https://github.com/ogulcancelik/herdr |
| **cockpit-tools** | 13.2k | Universal AI IDE account manager. Multi-account switching, quota monitoring for Codex/Copilot/Windsurf/Cursor. | Download from releases (Tauri app) | https://github.com/jlcodes99/cockpit-tools |
| **cocoindex** | 10.7k | Incremental engine for long-horizon agents. Data pipelines with incremental updates for AI agents. | `pip install cocoindex` | https://github.com/cocoindex-io/cocoindex |
| **hunk** | 6.7k | Review-first terminal diff viewer for agentic coders. Accept/reject AI-generated code hunks. | `cargo install hunk` | https://github.com/modem-dev/hunk |
| **rustnet** | 4.7k | Per-process network monitoring with deep packet inspection. TUI, cross-platform, eBPF. | `pacman -S rustnet` (official repos) | https://github.com/domcyrus/rustnet |
| **abtop** | 3.3k | Like htop, but for AI coding agents. Monitor Claude Code & Codex sessions, tokens, context windows, rate limits. | `cargo install abtop` | https://github.com/graykode/abtop |
| **lazyssh** | 3.8k | Terminal SSH manager. 60+ config fields, TUI browse/search/edit/connect. | `go install github.com/Adembc/lazyssh@latest` | https://github.com/Adembc/lazyssh |
| **resterm** | 1.8k | Terminal API client: HTTP/GraphQL/gRPC/WebSocket/SSE/OpenAPI. SSH tunnels, K8s port-forward, headless mode. | `go install github.com/unkn0wn-root/resterm@latest` | https://github.com/unkn0wn-root/resterm |
| **gitlogue** | 4.8k | Cinematic Git commit replay — animated story of your repo history in the terminal. | `cargo install gitlogue` | https://github.com/unhappychoice/gitlogue |
| **tokentap** | 809 | Intercept LLM API traffic, visualize token usage in real-time terminal dashboard. Track costs and debug prompts. | `pip install tokentap` | https://github.com/jmuncor/tokentap |
| **qqqa** | 624 | Stateless shell LLM: `qq` answers questions, `qa` runs commands. OpenAI/Anthropic/Gemini/DeepSeek/local. | `cargo install qqqa` | https://github.com/iagooar/qqqa |
| **nimbus** | 336 | Auto-analyzes routes/validation to build interactive API testing interface. OpenAPI support. | Build from source | https://github.com/sunchayn/nimbus |
| **dashbrew** | 260 | TUI dashboard builder — visualize data from scripts and APIs in console. JSON config. | `go install github.com/rasjonell/dashbrew/cmd/dashbrew@latest` | https://github.com/rasjonell/dashbrew |
| **hw-smi** | 286 | CPU/GPU telemetry with ASCII visualization. NVIDIA+AMD vendor API. | Build from source (`make.sh`) | https://github.com/ProjectPhysX/hw-smi |
| **lazymake** | 197 | TUI for Makefiles — interactive target selection, dependency visualization, command safety analysis. | `cargo install lazymake` | https://github.com/rshelekhov/lazymake |

**Agent tip:** For LLM cost monitoring, combine `tokentap` (proxy dashboard) + `abtop` (agent session monitor) + `rtk` (token compression). This trio covers the full visibility stack.

---

*Source: ibraheemdev/modern-unix + GitHub API verification + GitHub Search API trending discovery. Updated 2026-07-13.*
