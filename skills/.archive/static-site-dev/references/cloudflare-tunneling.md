# Cloudflare Quick Tunnels — Local Dev Hosting

Expose local HTTP servers to the internet via Cloudflare's free quick tunnels. No account needed.

## Setup

```bash
# Download cloudflared (one-time)
curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /tmp/cloudflared
chmod +x /tmp/cloudflared
/tmp/cloudflared --version
```

## Host a Site

```bash
# 1. Start HTTP server on a port
cd /path/to/site && python3 -m http.server 8080 &

# 2. Start cloudflared tunnel
/tmp/cloudflared tunnel --url http://localhost:8080

# 3. Wait for URL (appears in output):
# "Your quick Tunnel has been created! Visit it at:
#  https://random-words.trycloudflare.com"
```

## Multiple Sites

Use different ports for each site:

```bash
# Site A
cd /path/to/site-a && python3 -m http.server 8080 &
/tmp/cloudflared tunnel --url http://localhost:8080 &

# Site B
cd /path/to/site-b && python3 -m http.server 8081 &
/tmp/cloudflared tunnel --url http://localhost:8081 &
```

## Key Details

- **Free, no account required** — quick tunnels are temporary
- **URLs are random** — `https://<3-random-words>.trycloudflare.com`
- **URLs change on restart** — not persistent across reboots
- **Port conflicts** — each site needs a unique port
- **Background processes** — use `&` or tuistory for long-running tunnels
- **Tunnel logs** — URL appears in stderr output after ~5-10 seconds

## Finding Tunnel URLs

```bash
# Check running tunnels
ps aux | grep cloudflared | grep -v grep

# Read tunnel output (if using tuistory)
tuistory read -s <session-id>

# Or check process output directly
pgrep -a cloudflared
```

## Limitations

- No custom domains (use named tunnels for that)
- No SSL certificates for custom domains
- URLs are not persistent — restart = new URL
- Cloudflare reserves the right to investigate usage
- Not for production — use named tunnels with a Cloudflare account for that

## Process Management

```bash
# Kill a specific tunnel
kill $(pgrep -f "cloudflared.*8080")

# Kill all tunnels
pkill cloudflared

# Kill all HTTP servers
pkill "python3 -m http.server"
```
