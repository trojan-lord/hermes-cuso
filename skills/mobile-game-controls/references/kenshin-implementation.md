# Full Touch Controls Implementation — Kenshin Side-Scroller

## Complete working example (HTML + CSS + JS)

This is a tested, working implementation from the kenshin-game project. Copy and adapt.

### HTML structure

```html
<style>
  * { margin: 0; padding: 0; box-sizing: border-box;
      -webkit-touch-callout: none; -webkit-user-select: none; user-select: none; }
  body { background: #0a0a0a; display: flex; justify-content: center; align-items: center;
         height: 100vh; overflow: hidden; touch-action: none; }
  canvas { display: block; image-rendering: pixelated; }

  #touch-controls { display: none; position: fixed; bottom: 0; left: 0; right: 0;
                     height: 140px; z-index: 100; pointer-events: none; }
  .ctrl-btn { position: absolute; pointer-events: auto; border-radius: 50%;
              display: flex; align-items: center; justify-content: center;
              font-family: monospace; font-weight: bold;
              color: rgba(255,255,255,0.8); text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
              -webkit-tap-highlight-color: transparent; }
  .ctrl-btn:active, .ctrl-btn.active { opacity: 1 !important; transform: scale(0.92); }

  /* D-pad left side */
  #btn-left  { width: 60px; height: 60px; bottom: 30px; left: 20px;
               background: rgba(139,172,15,0.35); border: 2px solid rgba(139,172,15,0.6); font-size: 24px; }
  #btn-right { width: 60px; height: 60px; bottom: 30px; left: 100px;
               background: rgba(139,172,15,0.35); border: 2px solid rgba(139,172,15,0.6); font-size: 24px; }
  /* Action buttons right side */
  #btn-jump { width: 64px; height: 64px; bottom: 70px; right: 100px;
              background: rgba(155,188,15,0.35); border: 2px solid rgba(155,188,15,0.6); font-size: 11px; }
  #btn-atk  { width: 64px; height: 64px; bottom: 20px; right: 20px;
              background: rgba(180,40,30,0.4); border: 2px solid rgba(180,40,30,0.7); font-size: 11px; }
  #btn-spec { width: 64px; height: 64px; bottom: 20px; right: 100px;
              background: rgba(50,70,130,0.4); border: 2px solid rgba(50,70,130,0.7); font-size: 11px; }

  @media (hover: none) and (pointer: coarse) { #touch-controls { display: block; } }
</style>

<!-- Inside body, after canvas -->
<div id="touch-controls">
  <div id="btn-left" class="ctrl-btn">&larr;</div>
  <div id="btn-right" class="ctrl-btn">&rarr;</div>
  <div id="btn-jump" class="ctrl-btn">JUMP</div>
  <div id="btn-atk" class="ctrl-btn">ATK</div>
  <div id="btn-spec" class="ctrl-btn">SP</div>
</div>
```

### JavaScript (runs after p5.js setup)

```javascript
(function() {
  const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
  if (!isTouchDevice) return;

  const btnLeft  = document.getElementById('btn-left');
  const btnRight = document.getElementById('btn-right');
  const btnJump  = document.getElementById('btn-jump');
  const btnAtk   = document.getElementById('btn-atk');
  const btnSpec  = document.getElementById('btn-spec');

  function handleTouch(btn, keyCode, isDown) {
    if (isDown) {
      btn.classList.add('active');
      keysHeld[keyCode] = true;
      if (keyCode === 32 || keyCode === 87 || keyCode === UP_ARROW) {
        if (typeof player !== 'undefined' && player.grounded) {
          player.vy = JUMP_F; player.grounded = false;
        }
      }
      if (keyCode === 90 && typeof player !== 'undefined' && state === 'playing') player.attack();
      if (keyCode === 88 && typeof player !== 'undefined' && state === 'playing') player.specAttack();
      if (keyCode === ENTER) {
        if (state === 'title') resetGame();
        else if (state === 'gameover' && gameOverDelay <= 0) { hiScore = Math.max(hiScore, score); resetGame(); }
      }
    } else {
      btn.classList.remove('active');
      keysHeld[keyCode] = false;
    }
  }

  function addTouchEvents(btn, keyCode) {
    btn.addEventListener('touchstart', e => { e.preventDefault(); handleTouch(btn, keyCode, true); }, { passive: false });
    btn.addEventListener('touchend', e => { e.preventDefault(); handleTouch(btn, keyCode, false); }, { passive: false });
    btn.addEventListener('touchcancel', e => { e.preventDefault(); handleTouch(btn, keyCode, false); }, { passive: false });
  }

  addTouchEvents(btnLeft, LEFT_ARROW);
  addTouchEvents(btnRight, RIGHT_ARROW);
  addTouchEvents(btnJump, 32);
  addTouchEvents(btnAtk, 90);
  addTouchEvents(btnSpec, 88);

  document.querySelector('canvas').addEventListener('touchstart', function() {
    if (state === 'title') resetGame();
    else if (state === 'gameover' && gameOverDelay <= 0) { hiScore = Math.max(hiScore, score); resetGame(); }
  }, { passive: true });

  document.addEventListener('touchmove', e => e.preventDefault(), { passive: false });
})();
```

## Key design decisions in this implementation

1. **`pointer-events: none` on container, `auto` on buttons** — allows taps to pass through to canvas where no button exists (important for title screen tap-to-start).

2. **Separate touchstart/touchend per button** — multi-touch works because each finger triggers independent events on different elements. A single handler on a parent can't do this.

3. **`typeof player !== 'undefined'` guards** — the touch script runs before p5.js creates game objects. Guards prevent crashes during initialization.

4. **Canvas touchstart for start/restart** — uses `passive: true` because we don't need to prevent default (no scroll to block on canvas). Title/game-over screens respond to any tap.

5. **CSS `active` class + JS `keysHeld`** — visual feedback (scale animation) and game state (key held) both update on the same event. No sync issues.
