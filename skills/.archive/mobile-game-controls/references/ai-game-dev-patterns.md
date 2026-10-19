# AI-Assisted HTML5 2D Game Development — Research Findings

## OpenAI Game Repos (What Exists)

**No official open-source HTML5/2D game repos from OpenAI.** What they have:

- **openai/procgen** (1,177★) — 16 procedurally-generated gym environments for RL benchmarking. C++, Gym API. Not HTML5, not playable in browser.
- **openai/neural-mmo** (1,651★, archived) — Massively multiagent game environment. Python. Research-only.
- **openai/codex** (101k★) — The Codex CLI coding agent itself. Not a game, but the tool used to build games.

## Gold Standard: GothicVania Codex Demo

The best reference for AI-generated 2D games built with Codex/Claude:

- **Repo:** acatovic/gothicvania-codex-demo (24★)
- **Live:** https://acatovic.github.io/gothicvania-codex-demo/
- **Engine:** Phaser.js
- **Architecture:** Single `main.js` + `index.html`, multi-scene (Boot → Title → Game)
- **Style:** Gothic side-scrolling platformer (Castlevania-inspired)

### Project Structure
```
index.html              # Phaser config, canvas, scaling
main.js                 # All game logic: scenes, physics, input, AI
DESIGN-DOCUMENT.md      # Drives entire build — game spec
PROGRESS.md             # Development log
assets/
  images/backgrounds/   # Parallax layers (far-bg, columns)
  tilemaps/tiles/       # Tileset PNGs
  tilemaps/maps/        # Tiled JSON exports
  spritesheets/         # Character PNGs + JSON atlases
  audio/sfx/            # Sound effects (jump, attack, hurt, kill)
  audio/music/          # Background music
  fonts/                # Pixel fonts
```

### Agent Skills System (How Codex Builds It)
```
.agents/skills/game-dev/
  SKILL.md              # High-level skill map
  WORKFLOW.md           # Implement → test → iterate loop
  GAME-ENGINE.md        # Phaser API reference
  ASSETS.md             # Asset directory conventions
  TESTING.md            # Playwright-based testing
  PREREQUISITES.md      # Environment setup
```

**Key insight:** The game is built entirely by Codex following agent skills. The human writes the DESIGN-DOCUMENT.md; Codex implements it.

## Technical Patterns for Well-Built HTML5 2D Games

### 1. Engine Choice: Phaser.js
- Built-in physics (Arcade), audio, input, scaling, scene management
- Tiled JSON tilemap support
- Spritesheet + JSON atlas animation system
- Single HTML file deployment possible

### 2. Resolution & Scaling
```javascript
const GAME_WIDTH = 336;   // Low-res native (retro/pixel art)
const GAME_HEIGHT = 224;
// Phaser handles scaling to fit screen
```

### 3. Parallax Scrolling (3 Layers)
```javascript
// Far background (slow scroll)
this.background = this.add.tileSprite(0, 0, GAME_WIDTH, GAME_HEIGHT, "background")
  .setOrigin(0, 0).setScrollFactor(0);

// Mid background (medium scroll)  
this.columns = this.add.tileSprite(0, 0, GAME_WIDTH, GAME_HEIGHT, "columns")
  .setOrigin(0, 0).setScrollFactor(0).setAlpha(0.9);

// Foreground (follows camera) — tilemap layer
```

### 4. Spritesheet Animation System
```javascript
// Load spritesheet + JSON atlas
this.load.spritesheet("player", "assets/spritesheets/player.png", {
  frameWidth: 82, frameHeight: 60
});
this.load.json("player-frames", "assets/spritesheets/player.json");

// Parse frame mapping from JSON
function parseFrameIndexMap(frameConfig, frameWidth, frameHeight, columns) {
  const mapping = {};
  Object.entries(frameConfig).forEach(([name, frame]) => {
    const frameX = Math.floor(frame.x / frameWidth);
    const frameY = Math.floor(frame.y / frameHeight);
    mapping[name] = frameY * columns + frameX;
  });
  return mapping;
}

// Create animations from prefix
function animationFramesForPrefix(frameIndexMap, prefix, textureKey) {
  return Object.keys(frameIndexMap)
    .filter((name) => name.startsWith(prefix))
    .sort((a, b) => Number(a.split("-").pop()) - Number(b.split("-").pop()))
    .map((name) => ({ key: textureKey, frame: frameIndexMap[name] }));
}
```

### 5. Tilemap Collision (Tiled JSON)
```javascript
const map = this.make.tilemap({ key: "map" });
const tileset = map.addTilesetImage("tileset", "tiles");
const groundLayer = map.createLayer("ground", tileset, 0, 0);
groundLayer.setCollisionByProperty({ collidable: true });
this.physics.add.collider(player, groundLayer);
```

### 6. Scene Management
```javascript
class BootScene extends Phaser.Scene {
  preload() { /* load all assets */ }
  create() { this.scene.start("TitleScene"); }
}

class TitleScene extends Phaser.Scene {
  create() { /* title screen, parallax bg, flash "press enter" */ }
  update() { if (ENTER.isDown) this.scene.start("GameScene"); }
}

class GameScene extends Phaser.Scene {
  create() { /* player, enemies, physics, input */ }
  update(time, delta) { /* game logic */ }
}
```

### 7. Iterative Workflow (Agent Skills Pattern)
```
1. Read DESIGN-DOCUMENT.md → understand target
2. Pick ONE feature → implement smallest change
3. Update PROGRESS.md → log what works, TODOs, decisions
4. Dry-run game → start local server + Playwright
5. Inspect state → screenshot + eval game state
6. Verify controls → exercise all interactions
7. Check errors → fix console errors
8. Reset between scenarios → clean state
9. Iterate with small deltas → change one variable at a time
```

## Sprite Generation Tools

- **aldegad/sprite-gen** (534★) — AI sprite generation pipeline: component-row → state rows → alpha cleanup → frame extraction → runtime atlases. Works with Codex/Claude Code.
- **MRCalderon3D/everything-game-dev-code** (60★) — Universal scaffold: 42 agents, 51 commands, 86 skills. Multi-engine (Unity, Unreal, Godot, HTML).

## Key Lessons

1. **DESIGN-DOCUMENT.md is the contract** — Write it thoroughly; the AI implements from it.
2. **Agent skills are harness engineering** — Structure files that guide the AI's implementation.
3. **Phaser.js scales well** — Handles physics, audio, input, and scenes without boilerplate.
4. **Low-res pixel art is forgiving** — 336×224 native resolution masks sprite imperfections.
5. **Iterate with screenshots** — Playwright-based visual testing catches issues code review misses.
6. **Assets drive quality** — Good sprite atlases + Tiled tilemaps = professional-looking games.
