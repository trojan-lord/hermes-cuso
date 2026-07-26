# Touch Control Templates

## Complete Working Touch Overlay

This is the verified, tested touch control system for single-file HTML canvas games.
It was built and debugged during the Kenshin action game (July 2026).

### HTML Structure

```html
<div id="wrap">
  <canvas id="game" width="800" height="480"></canvas>
  
  <!-- Overlays for title/win/lose (z-index: 30) -->
  <div id="title" class="ov">
    <h1>GAME TITLE</h1>
    <button id="startBtn">START</button>
  </div>
  
  <!-- Touch controls (z-index: 20, BELOW overlays but ABOVE canvas) -->
  <div id="touchLayer">
    <div id="bL" class="tb">◀</div>
    <div id="bR" class="tb">▶</div>
    <div id="bJ" class="tb">JUMP</div>
    <div id="bA" class="tb">ATK</div>
    <div id="bS" class="tb">SP</div>
    <div id="bP" class="tb">❚❚</div>
  </div>
</div>
```

### CSS (critical parts)

```css
#wrap {
  position: relative;
  overflow: hidden;
  width: min(800px, 100vw);
  aspect-ratio: 800/480;
}

#touchLayer {
  position: absolute;
  inset: 0;
  z-index: 20;
  pointer-events: none;
  display: none;
}

/* Show on touch devices ONLY */
@media(hover:none) and (pointer:coarse) {
  #touchLayer { display: block; }
}

.tb {
  position: absolute;
  pointer-events: auto;     /* CRITICAL: overrides parent pointer-events:none */
  border-radius: 10px;
  touch-action: manipulation;
  -webkit-user-select: none;
  user-select: none;
  -webkit-touch-callout: none;
  color: rgba(155,188,15,.75);
  background: rgba(48,98,48,.4);
  border: 2px solid rgba(155,188,15,.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.tb.on {
  background: rgba(155,188,15,.45);
  border-color: rgba(155,188,15,.6);
}

/* Button positions - percentage-based for scaling */
#bL { left: 8px; bottom: 8px; width: 22%; height: 28%; font-size: 20px; }
#bR { left: calc(22% + 16px); bottom: 8px; width: 22%; height: 28%; font-size: 20px; }
#bJ { right: 8px; bottom: calc(28% + 16px); width: 22%; height: 22%; font-size: 12px; }
#bA { right: calc(22% + 16px); bottom: calc(28% + 16px); width: 22%; height: 22%; font-size: 12px; }
#bS { right: 8px; bottom: 8px; width: 22%; height: 28%; font-size: 11px; }
#bP { right: 8px; top: 8px; width: 40px; height: 36px; font-size: 18px; border-radius: 6px; }
```

### JavaScript Input System

```js
var keys = {};
var tch = {left: false, right: false, jump: false, attack: false, special: false};

// Keyboard
window.addEventListener('keydown', function(e) {
  if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].indexOf(e.key) !== -1)
    e.preventDefault();
  var k = e.key.toLowerCase();
  if (!keys[k]) {
    // Fire-once actions (only on first press)
    if (k === ' ' || k === 'w' || k === 'arrowup') doJump();
    if (k === 'z' || k === 'j') doAttack();
    if (k === 'x' || k === 'k') doSpecial();
    if (k === 'enter') handleStart();
    if (k === 'p') doPause();
  }
  keys[k] = true;
});
window.addEventListener('keyup', function(e) { keys[e.key.toLowerCase()] = false; });

// Touch - each button independent for multi-touch
function bindTouch(id, key, onFn) {
  var el = document.getElementById(id);
  if (!el) return;
  function onStart(e) {
    e.preventDefault();
    e.stopPropagation();
    tch[key] = true;
    el.classList.add('on');
    if (onFn) onFn();  // fire action on press
  }
  function onEnd(e) {
    e.preventDefault();
    e.stopPropagation();
    tch[key] = false;
    el.classList.remove('on');
  }
  el.addEventListener('touchstart', onStart, {passive: false});
  el.addEventListener('touchend', onEnd, {passive: false});
  el.addEventListener('touchcancel', onEnd);
  el.addEventListener('mousedown', onStart);
  el.addEventListener('mouseup', onEnd);
  el.addEventListener('mouseleave', onEnd);
}

// Bind controls
bindTouch('bL', 'left', null);       // continuous (held)
bindTouch('bR', 'right', null);      // continuous (held)
bindTouch('bJ', 'jump', doJump);     // fire-on-press
bindTouch('bA', 'attack', doAttack); // fire-on-press
bindTouch('bS', 'special', doSpecial); // fire-on-press
bindTouch('bP', 'pause', doPause);   // fire-on-press

// Unified input queries
function isLeft()  { return keys['a'] || keys['arrowleft']  || tch.left; }
function isRight() { return keys['d'] || keys['arrowright'] || tch.right; }
```

## Why This Works (and Previous Approaches Failed)

### Failed approach: Canvas touch events
```js
// WRONG: canvas swallows all touches, buttons never receive them
cv.addEventListener('touchstart', e => {
  e.preventDefault();  // THIS KILLS EVERYTHING BELOW
  // ... game logic
}, {passive: false});
```

### Failed approach: Buttons inside canvas parent with no z-index
```css
/* WRONG: buttons exist but canvas sits on top */
#touch { position: absolute; bottom: 0; height: 150px; }
canvas { /* no z-index, but rendered on top due to DOM order */ }
```

### Working approach: Separate overlay with pointer-events:none
```css
/* Parent blocks touches to canvas */
#touchLayer { pointer-events: none; z-index: 20; }
/* Each button re-enables touches for itself */
.tb { pointer-events: auto; }
```
