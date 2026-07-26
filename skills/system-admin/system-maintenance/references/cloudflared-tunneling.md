# Cloudflared Quick Tunnel

## What It Is

Cloudflare's free quick tunnel service. Exposes a localhost port to the internet via a random `*.trycloudflare.com` subdomain. No account, no DNS config, no registration.

## Setup (One-Time Download)

```bash
curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /tmp/cloudflared
chmod +x /tmp/cloudflared
```

Binary is ~30MB. Platform-specific: `cloudflared-linux-amd64`, `cloudflared-linux-arm64`, `cloudflared-darwin-amd64`, etc.

## Usage

```bash
/tmp/cloudflared tunnel --url http://localhost:PORT
```

Watch for the URL in output:
```
Your quick Tunnel has been created! Visit it at:
https://random-words.trycloudflare.com
```

## Characteristics

- **No account needed** — anonymous quick tunnel
- **Ephemeral** — URL changes on every restart
- **Process-bound** — dies when the process stops
- **HTTPS** — Cloudflare terminates TLS automatically
- **No bandwidth limits** for light use
- **Subject to Cloudflare ToS** — not for production

## Common Use Cases

- Preview a static site from a local dev server
- Share a web app prototype with someone on another network
- Quick mobile testing of a localhost app
- Demo something without deploying

## Alternatives for Persistent Tunnels

| Tool | Account? | Persistent URL? | Free? |
|------|----------|-----------------|-------|
| Cloudflared quick tunnel | No | No | Yes |
| Cloudflared named tunnel | Yes (Cloudflare) | Yes | Yes |
| ngrok | Yes (free tier) | Yes (paid) | Free tier limited |
| localtunnel | No | Semi (subdomain reserved) | Yes |
| bore | No | No | Yes |

## Pitfalls

- The URL changes every time you restart the tunnel — can't bookmark it
- If the machine is behind a corporate proxy, QUIC may fail (falls back to HTTP/2)
- Large file transfers may be slow — this is meant for preview/light use, not production traffic
- The binary in /tmp won't survive reboot — install properly if you use it regularly:
  ```bash
  sudo cp /tmp/cloudflared /usr/local/bin/cloudflared
  ```
