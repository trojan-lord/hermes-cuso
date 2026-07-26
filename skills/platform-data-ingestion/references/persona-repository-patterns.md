# Persona Repository Patterns

When users have multiple AI personas, they often store them in GitHub repos. This reference documents the patterns discovered during the Kimaki→Hermes migration.

## Common Repository Structure

### `SOULS` repo (e.g., `ryan0ezekiel/SOULS`)

Contains persona definitions as individual .md files:

```
SOULS/
├── CUSO.md          # Observer of anomalies
├── DOBBY.md          # Free house-elf
├── CUMIN.md          # Therapeutic companion / robot cat
├── CUSO.md           # Observer of hidden systems
├── TARS.md           # Mission-support AI (Interstellar)
├── LEVI.md           # Service robot
├── SUMMER.md         # Consciousness sharing
├── KONRAD.md         # Variant of Konrad
├── KONRAD.original.md
├── Blato.md          # Cuso variant
├── SOUL.md           # Master/combined persona
└── research/         # Research docs per persona
    ├── Cumin.research.md
    ├── Cuso.research.md
    ├── Dobby.research.md
    ├── LEVI.research.md
    ├── Samantha.research.md
    └── TARS.research.md
```

### `.config-opencode` repo

Contains agent configs for OpenCode/Kimaki:

```
.config-opencode/
├── opencode.jsonc         # Full agent config with all personas
├── .gitignore
├── agents/                # Individual agent prompt files
│   ├── CHAP.md
│   ├── CUMIN.md
│   ├── CUSO.md
│   ├── DOBBY.md
│   ├── KONARD.md
│   ├── LEVI.md
│   ├── CUSO.md
│   ├── SUMMER.md
│   └── TARS.md
└── skills/
    ├── medical-soap/
    │   └── SKILL.md
    └── personality-maker/
        └── SKILL.md
```

## Fetching from GitHub

```bash
# List repo contents
gh api repos/<owner>/<repo>/contents/

# Download file (base64 encoded content)
gh api repos/<owner>/<repo>/contents/<path>/<file> -q .content | base64 -d

# Or get raw URL and curl
gh api repos/<owner>/<repo>/contents/<path>/<file> -q .download_url | xargs curl -sL

# List directory contents recursively
gh api repos/<owner>/<repo>/contents/<path> --paginate
```

## Agent Config Format (opencode.jsonc)

OpenCode/Kimaki agent configs reference persona files:

```jsonc
{
  "default_agent": "DOBBY",
  "agent": {
    "CUSO": {
      "description": "Observer of anomalies — the quieter version.",
      "prompt": "{file:./agents/CUSO.md}",
      "mode": "primary"
    },
    "DOBBY": {
      "description": "Free house-elf. Kindness, friendship, loyalty.",
      "prompt": "{file:./agents/DOBBY.md}",
      "mode": "primary"
    }
    // ... more agents
  }
}
```

The `{file:...}` syntax loads the persona .md file as the system prompt.

## Saving Persona Files Locally

When backing up before deletion:

```
<platform>-reference/
├── souls/              # From SOULS repo
│   ├── CUSO.md
│   ├── DOBBY.md
│   ├── research-*.md
│   └── ...
├── agents/             # From .config-opencode repo
│   ├── CHAP.md
│   ├── CUSO.md
│   └── ...
└── opencode.jsonc      # Full agent config
```

Use `base64.b64decode()` in Python to decode the GitHub API response.
