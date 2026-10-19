---
name: linux-cli-toolbox
description: "Discover, evaluate, and recommend Linux CLI tools for system administration, monitoring, and automation. Covers tool research, availability checks, and curated picks for Arch/CachyOS + Wayland environments."
tags: [linux, cli, tools, sysadmin, monitoring, wayland, arch, cachyos, recommendations]
related_skills: [system-maintenance, linux-desktop]
---

# Linux CLI Toolbox

Discover, evaluate, and recommend Linux CLI tools for system admin, monitoring, and automation.

**Trigger:** User asks "what tools should I use for X?", "best CLI for Y", "htop alternatives", or any tool recommendation/discovery request on Linux.

---

## Research Technique: Search-Engine-Free Tool Discovery

Browser search engines (Google, DuckDuckGo, Bing) frequently block headless browsers with CAPTCHAs/bot detection. Use these fallbacks in order:

### Fallback 1: Known curated lists via raw.githubusercontent.com

The single best source is **ibraheemdev/modern-unix** — a curated list of modern alternatives to classic Unix tools, maintained with screenshots and GitHub links:

```bash
curl -sL "https://raw.githubusercontent.com/ibraheemdev/modern-unix/master/README.md" | head -500
```

This covers: bat, eza, lsd, delta, dust, duf, broot, fd, ripgrep, fzf, mcfly, choose, jq, sd, cheat, tldr, bottom, glances, gtop, hyperfine, gping, procs, httpie, curlie, xh, zoxide, doggo, lazygit.

### Fallback 2a: GitHub Search API — discover NEW trending repos

Unlike batch queries (2b), this **discovers repos you don't know about yet**:

```bash
# Find hot new Rust CLI tools
curl -s "https://api.github.com/search/repositories?q=created:>2025-01-01+language:rust+stars:>500&sort=stars&order=desc&per_page=30" | \
  jq -r '.items[] | "\(.full_name) ⭐\(.stargazers_count) — \(.description)"'

# Filter by topic tags
curl -s "https://api.github.com/search/repositories?q=created:>2025-01-01+topic:cli+stars:>200&sort=stars&order=desc" | \
  jq -r '.items[] | "\(.full_name) ⭐\(.stargazers_count) — \(.description)"'

# Filter by language + stars threshold
curl -s "https://api.github.com/search/repositories?q=created:>YYYY-MM-DD+topic:tui+stars:>200&sort=stars&order=desc" | \
  jq -r '.items[] | "\(.full_name) ⭐\(.stargazers_count) — \(.description)"'
```

**Pitfall:** Search API and repos API share the same 60 req/hr rate limit. Use search API for discovery (5-10 calls), then switch to batch queries (2b) or browser for verification. Don't burn the whole limit on search.

**Pitfall:** When rate-limited, the search API **returns results but with `null` star counts** — not a 403 error. This is a subtle silent failure. You get results that look valid but have missing data. Detect with: `jq '.items[].stargazers_count' | grep null`. If you see nulls, you're rate-limited — switch to browser verification.

### Fallback 2b: GitHub API batch queries — verify specific repos

Query repo metadata (stars, description) for specific tools you already know about:

```bash
for repo in "user/repo1" "user/repo2"; do
  data=$(curl -sL -H "Accept: application/vnd.github.v3+json" "https://api.github.com/repos/$repo")
  desc=$(echo "$data" | jq -r '.description // "N/A"')
  stars=$(echo "$data" | jq -r '.stargazers_count // "N/A"')
  echo "$repo | ⭐ $stars | $desc"
done
```

**Pitfall:** Unauthenticated GitHub API has a 60 requests/hour rate limit. Batch queries fast. If rate-limited, switch to browser for remaining lookups, or use `gh api` if authenticated.

**Pitfall:** GitHub API frequently returns HTTP 403 to headless environments (Browserbase) even with rate limit remaining — Varnish/bot detection blocks the request entirely. Don't retry. Pivot immediately to Fallback 3b.

### Fallback 2c: Browser fallback for star count verification

When the API returns null stars or 403, verify via browser page visit:

```bash
# browser_navigate to https://github.com/<org>/<repo>
# Read star count from the snapshot — it appears as: "Star 4.7k" or "Star 70.6k"
# GitHub abbreviates large numbers (k suffix), so "4.7k" = 4,700
```

This is slower (one page load per repo) but always works. Use for the top 5-10 most promising tools after API discovery.

### Fallback 3b: AUR RPC API (best for Arch tool discovery)

The AUR search API is excellent for finding tools and returns rich metadata. No auth needed, no bot detection:

```bash
# Search AUR for tools by keyword
curl -s "https://aur.archlinux.org/rpc/v5/search/<query>" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); \
  [print(f'{r[\"Name\"]}: {r[\"Description\"]}') for r in d.get('results',[])]"

# Get package details (depends, URL, etc.)
paru -Si <package-name> | grep -E "^(Name|Description|URL|Depends|OptDepends)"
```

**Why this is powerful:** AUR packages often have CUDA/Vulkan/SYCL variants (e.g., `koboldcpp-cuda`, `stable-diffusion.cpp-vulkan-git`), making it easy to find GPU-accelerated builds. The RPC API also searches official repos.

### Fallback 4: pacman for official repos

```bash
# Search official repos (fast, always works)
pacman -Ss <tool-name>

# Get full package metadata
pacman -Si <package-name> | grep -E "^(Name|Description|URL|Depends)"

# Check what's already installed
pacman -Qs <pattern>
```

On CachyOS, most modern CLI tools are in `extra/` or `cachyos-extra-v3/`.

### Fallback 3: Browser navigation to known pages

Navigate directly to:
- `github.com/<org>/<repo>` — verify stars, description, latest release
- `archlinux.org/packages` or `aur.archlinux.org` — check availability
- Package manager docs (e.g., `pacman -Ss <query>`)

### Avoid: Search engine queries from headless browser

Google, Bing, and DuckDuckGo all trigger bot detection on headless Browserbase sessions. Don't waste time retrying — go straight to fallbacks 1-3.

---

## Availability Check Pattern

After finding a tool, check if it's available:

```bash
# Official repos
pacman -Ss <tool-name>

# AUR (if yay/paru installed)
yay -Ss <tool-name>

# Already installed?
which <binary-name>

# Cargo (Rust tools)
cargo install <crate-name>

# Go
go install <module>@latest
```

On CachyOS, most modern CLI tools are in `extra/` or `cachyos-extra-v3/`. AUR has the rest via `-git` or `-bin` packages.

---

## Image Conversion: Bitmap to SVG (vtracer)

For converting raster images (PNG, JPEG) to vector SVG — logos, illustrations, diagrams, or any image where you need infinite scaling.

```bash
# Install (not in pacman — cargo only)
cargo install vtracer

# High-quality color conversion
vtracer --input input.png --output output.svg --preset photo

# Other presets: --preset bw (black/white), --preset poster (posterized)
# Manual tuning: --colormode color|bw, --hierarchical stacked|cutout, --mode pixel|polygon|spline
```

**Pitfall:** Large images (3840×2160+) will timeout or take extremely long. Downscale first — SVG scales infinitely so output resolution doesn't matter:
```bash
convert input.jpg -resize 1920x1080 scaled.png   # ImageMagick
vtracer --input scaled.png --output output.svg --preset photo
```

**Pitfall:** vtracer works best with PNG input. Convert JPEG first with ImageMagick: `convert input.jpg -quality 100 output.png`

**Note:** `potrace` (in pacman repos) only handles B&W bitmaps. For color images, `vtracer` is the right tool.

---

## Evaluation Criteria for AI Agent Tool Picks

When recommending tools, weight these factors:

1. **Scriptability** — Can it output JSON? Accept stdin? Non-interactive mode? (critical for agent use)
2. **Wayland compatibility** — Does it work on Wayland/Niri, or only X11?
3. **Installation ease** — In pacman repos? Single binary download? Complex build?
4. **Maintenance status** — Last commit date, open issues, release cadence
5. **Stars/adoption** — Proxy for reliability and community support

### For AI/ML tools specifically, also check:

6. **GPU requirements** — What VRAM does the tool need? Does it have CPU-only fallback? What backend (CUDA/Vulkan/SYCL/Metal)?
7. **RAM footprint** — Base RAM + per-model overhead. Is there quantization support (INT8/INT4) to reduce memory?
8. **Model size vs VRAM** — Check `nvidia-smi` for available VRAM. SD 1.5 ~2GB, SDXL ~6GB, Flux ~12GB. LLMs scale with parameter count and quantization.
9. **Disk space** — Models can be 1-15GB each. Check `df -h` and note which drive has space.
10. **Backend variants** — Many AI tools on AUR have `-cuda`, `-vulkan`, `-hipblas`, `-sycl` variants. Match the variant to your GPU (NVIDIA→cuda/vulkan, AMD→hipblas/vulkan, Intel→sycl/vulkan).

**Quick hardware audit before recommending:**
```bash
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader  # or rocm-smi for AMD
free -h | head -2
df -h /home | tail -1
```

**Pitfall:** Don't recommend SDXL/Flux image gen for systems with <6GB VRAM. On 4GB VRAM, recommend SD 1.5 or quantized SDXL via `stable-diffusion.cpp` (Vulkan) rather than ComfyUI/A1111 which are heavier.
**Pitfall:** Whisper medium/large models need >4GB RAM. On low-RAM systems, use whisper-cpp with tiny/base model or faster-whisper with INT8 quantization.
**Pitfall:** ALWAYS check what is already installed before installing something new. User corrected: GUI qBittorrent was already installed with full CLI support (`--save-path`, `--skip-dialog=true`, magnet URLs as positional args), but agent installed qbittorrent-nox separately without checking. Run `pacman -Qi <pkg>` or `which <cmd>` first.

**Pitfall:** URLs containing `&` (magnet links, API URLs with query params) get split by bash even when quoted. The shell interprets `&` as background operators. Use Python `subprocess.Popen()` to pass such URLs as a single argv -- it is the only reliable method. Do NOT try `.magnet` files (qBittorrent tries to bdecode them as torrent data) or `xargs` (does not preserve full URL). See `references/qbittorrent-cli.md` for full patterns including torrent management and cleanup.

**Pitfall:** For package removal, verify cleanup across all dimensions (binary, config, data, cache, processes, systemd, temp). See `references/package-cleanup-verification.md` for the full checklist. Shared config dirs between package variants (e.g. GUI vs headless) need surgical cleanup, not full wipes.

**Pitfall:** ALWAYS check for the latest and best available tool before recommending anything. The AI/ML landscape moves fast — newer models beat older ones regularly. Verify against current benchmarks and recent releases (check GitHub creation date, recent commits, community comparisons) before suggesting a solution. Do not rely on knowledge that may be outdated. User explicitly corrected this: "Next time always make sure the thing u r suggesting is the latest and greatest thing available for us."

**Pitfall:** NEVER assume what provider/model/environment the user is running. Always check the actual config before making recommendations. User corrected: "First of all we r not running on ollama. Figure out what we r actually running on." The system may be using cloud providers, custom endpoints, or configurations that differ from what you expect. Run `cat ~/.hermes/config.yaml` or equivalent to verify before assuming.

**Pitfall:** VRAM is the hard ceiling for local AI tools. A 1.7B parameter model at BF16 needs ~3.9 GB — won't fit on a 4GB GPU even though "1.7B sounds small." Always check `nvidia-smi` for actual available VRAM, not just the model's parameter count. GGUF quantization (Q4_K_M) can reduce a 3.9 GB model to 1.2 GB. When a model doesn't fit at full precision, check if a quantized GGUF variant exists before giving up.

## Desktop Control: niri msg

Full desktop control from terminal via `niri msg`. See `references/niri-msg-desktop-control.md` for full action list.

```bash
# Find socket (required under systemd, changes each boot)
NIRI_SOCKET=$(ls /run/user/$(id -u)/niri.*.sock 2>/dev/null | head -1)
export NIRI_SOCKET="$NIRI_SOCKET"

niri msg -j windows              # list all windows
niri msg action spawn -- app     # launch app
niri msg action close-window     # close focused window
niri msg action toggle-window-floating
```

## Notifications (Noctalia)

`notify-send` works when Noctalia shell is running (provides org.freedesktop.Notifications D-Bus interface):

```bash
notify-send "Title" "Body"
notify-send -u critical "Title" "Urgent body"
```

---

## Curated Tool List

See `references/curated-tools.md` for the full categorized list with:
- System monitoring (htop alternatives)
- Network tools
- File management
- Notification systems
- Clipboard management
- Screenshot/screen capture (Wayland)
- Process supervision
- **Local AI tools** (STT, TTS, image gen, LLM servers, terminal AI bridges)

Updated: 2026-07-13. Re-run the research technique above to refresh.
