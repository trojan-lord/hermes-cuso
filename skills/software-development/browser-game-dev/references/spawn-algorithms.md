# Spawn Algorithms for Side-Scrollers

## The Anti-Stacking Pattern

Problem: spawning entities relative to player position + random offset + clamp
causes position convergence when player is near world boundaries.

### Why It Happens

```js
// Player at x=120, world width=3200, spawn range=±300-900
var x = player.x + rnd(300,900) * (Math.random()<0.5?1:-1);
x = clamp(x, 50, WW-100);
// Math.random()<0.5: x = 120 - (300..900) = -180..-780 → clamped to 50
// Math.random()>=0.5: x = 120 + (300..900) = 420..1020 → spread OK
// 50% of enemies hit the clamp → stack at x=50
```

### The Fix: Spawn Ahead + Spread

Always place enemies in front of the player's facing direction, spread apart:

```js
function spawnWave(playerX, waveNum, WW) {
  var n = Math.min(3 + waveNum, 14);
  var types = ['thug','thug','samurai','archer','thug','elite'];
  
  // Determine spawn direction (ahead of player)
  var spawnRight = playerX < WW * 0.4;
  var baseX = spawnRight
    ? Math.max(playerX + rnd(300,600), 480)
    : Math.min(playerX - rnd(300,600), WW - 480);
  baseX = clamp(baseX, 50, WW - 100);
  
  var spawned = [];
  for (var i = 0; i < n; i++) {
    var type = pickType(types, waveNum);
    // Offset each enemy: i * spacing + jitter
    var x = baseX + i * rnd(40, 80) + rnd(-20, 20);
    spawned.push(mkEnemy(type, clamp(x, 50, WW - 100)));
  }
  return spawned;
}
```

### Boss Spawning

```js
// Always spawn ahead of the player, never behind
var dir = playerX > WW * 0.5 ? -1 : 1;
var bossX = clamp(playerX + dir * rnd(200, 400), 200, WW - 200);
```

### Spacing Values

| Scenario | Spacing | Jitter | Notes |
|----------|---------|--------|-------|
| Normal wave | 40-80px | ±20px | Natural-looking spread |
| Boss + minions | 100-150px | ±30px | Minions flank boss |
| Dense wave (high level) | 25-50px | ±15px | Tighter pack |

### Tested Results (Kenshin game)

| Wave | Enemies | Positions | All Spread? |
|------|---------|-----------|-------------|
| Wave 1 | 4 thugs | 228, 287, 388, 446 | ✓ Yes |
| Wave 2 | 5 mixed | 1593, 1694, 1736, 1827, 1889 | ✓ Yes |

Before fix: all 4 enemies at x=50 (stacked).

## Random Direction Spawn (AVOID)

```js
// This ALWAYS stacks when player is near an edge
var x = player.x + rnd(300,900) * (Math.random()<0.5?1:-1);
```

## Ahead-of-Player Spread (USE)

```js
// This always works regardless of player position
var baseX = clamp(player.x + dir * rnd(300,600), 50, WW-100);
var x = baseX + i * rnd(40,80) + rnd(-20,20);
```

## Off-Screen Spawn (for scrolling games)

For games with camera tracking, spawn at the camera edge:

```js
// Spawn just past the right edge of the camera
var spawnX = camX + W + rnd(50, 200);
// Or ahead of player in the direction they're moving
var dir = player.facing || 1;
var spawnX = clamp(player.x + dir * rnd(250, 500), 50, WW - 100);
```
