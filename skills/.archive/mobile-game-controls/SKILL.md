---
name: mobile-game-controls
description: "Touch controls and mobile deployment for browser-based games and interactive p5.js projects. Covers on-screen virtual gamepads, multi-touch handling, CSS touch detection, and iOS/Android deployment pitfalls."
tags: [p5js, mobile, touch, gamepad, browser-game, web-game, ios, android]
related_skills: [p5js]
---

# Mobile Game Controls — Touch Interfaces for Browser Games

## When to use

Any interactive browser project (p5.js games, canvas apps, HTML5 games) that needs to work on phones/tablets alongside desktop keyboard controls. Covers on-screen virtual gamepads, multi-touch, and mobile deployment.

## Core principle

Add touch controls ALONGSIDE keyboard controls. Don't replace. The `keysHeld` pattern used for keyboard input should be the shared state layer — touch buttons write to the same object.

## CSS — touch device detection

```css
@media (hover: none) and (pointer: coarse) {
  #touch-controls { display: block; }
}
```

This is the reliable CSS media query for touch-only devices. Shows buttons on phones/tablets, hides on desktop.

## CSS — button styling essentials

```css
#touch-controls {
  display: none;
  position: fixed;
  bottom: 0; left: 0; right: 0;
  height: 140px;
  z-index: 100;
  pointer-events: none;  /* buttons have pointer-events: auto */
}
.ctrl-btn {
  position: absolute;
  pointer-events: auto;
  border-radius: 8px;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;  /* CRITICAL: prevents double-tap zoom on iOS */
  transition: background .06s;
}
.ctrl-btn:active, .ctrl-btn.active {
  background: rgba(155,188,15,.4);
  border-color: rgba(155,188,15,.6);
}
```

### Start/Restart Buttons (HTML overlays)

Always use a dedicated `<button>` element for start/restart in the title/lose overlay. Don't rely solely on canvas tap — mobile users expect visible buttons:

```html
<button id="startBtn" style="
  font-size:20px; padding:16px 48px; margin-top:16px;
  border-radius:6px; border:none;
  background:linear-gradient(180deg,#4a7a3a,#306230);
  box-shadow:0 4px 0 #1a3a14;
  touch-action:manipulation;
  -webkit-tap-highlight-color:transparent;
  font-family:'Courier New',monospace; color:#9bbc0f;
">⚔ ENTER ⚔</button>
```

Wire with both click AND touchend handlers:
```javascript
document.getElementById('startBtn').addEventListener('click', e => {
  e.stopPropagation(); handleStart();
});
document.getElementById('startBtn').addEventListener('touchend', e => {
  e.preventDefault(); e.stopPropagation(); handleStart();
}, {passive:false});
```

The `e.stopPropagation()` prevents the click from reaching the canvas (which might trigger attack). The `touchend` with `preventDefault()` ensures it fires even if iOS tries to synthesize a delayed click.

## JavaScript — multi-touch bridge to keyboard state

Touch buttons directly manipulate the `keysHeld` object. One-shot actions (attack, jump) fire immediately on `touchstart`. Continuous actions (movement) hold state until `touchend`.

```javascript
(function() {
  const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
  if (!isTouchDevice) return;

  function handleTouch(btn, keyCode, isDown) {
    if (isDown) {
      btn.classList.add('active');
      keysHeld[keyCode] = true;
      // One-shot actions fire immediately
      if (keyCode === 32 && player.grounded) { player.vy = JUMP_F; player.grounded = false; }
      if (keyCode === 90 && state === 'playing') player.attack();
      if (keyCode === 88 && state === 'playing') player.specAttack();
      if (keyCode === ENTER && state === 'title') resetGame();
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

  // Wire up each button...
  addTouchEvents(btnLeft, LEFT_ARROW);
  addTouchEvents(btnRight, RIGHT_ARROW);
  addTouchEvents(btnJump, 32);

  // Prevent scroll while playing
  document.addEventListener('touchmove', e => e.preventDefault(), { passive: false });
})();
```

## Pitfalls

1. **`{ passive: false }` is mandatory** on touchstart/touchend/touchcancel. Without it, `e.preventDefault()` is ignored and the page scrolls during gameplay. Chrome warns about this.

2. **Don't use p5's `touchStarted()` for gamepad buttons.** P5's touch callbacks don't distinguish which button was touched. Use DOM `addEventListener` on each button element. P5's `touches[]` is fine for canvas-level interactions.

3. **One-shot vs continuous:** Jump, attack, start = fire once on touchstart. Movement = hold via `keysHeld[keyCode] = true` on start, `false` on end. Mixing these up causes stuck or missed inputs.

4. **`touchcancel` fires when the system intervenes** (phone call, notification, low battery). Always clean up state on touchcancel or buttons get "stuck" held.

5. **`-webkit-tap-highlight-color: transparent`** removes the blue flash on iOS tap. Essential for games.

6. **`touch-action: none`** on `<body>` prevents pull-to-refresh and overscroll on iOS. Without it, swiping down refreshes the page mid-game.

7. **Canvas tap for start/restart:** Add a touchstart listener on the canvas for title and game-over screens. Mobile users tap the screen — they don't look for specific buttons.

8. **Multi-touch requires separate event listeners per button.** A single touchstart handler on a parent element can't distinguish which finger hit which button. Each button needs its own listener.

9. **`touch-action: manipulation` on buttons** prevents iOS double-tap zoom without disabling scroll entirely. Put it on `.ctrl-btn` elements and any tappable UI buttons. The body should use `touch-action: none` for games, but individual buttons benefit from `manipulation` for the zoom prevention.

10. **Start/restart buttons need both click AND touchend handlers.** `e.stopPropagation()` on both prevents the event from reaching the canvas (which might trigger an attack or other game action). Use `{passive:false}` on the touchend handler.

11. **Don't rely solely on canvas tap for start.** Always provide a visible `<button>` in the overlay. Some users don't realize they can tap the canvas. The button is discoverable; the canvas tap is a convenience.

## Button layout template (side-scroller)

| Button | Position | Size | Color | Action |
|--------|----------|------|-------|--------|
| ← → | bottom-left | 60×60px | translucent green | Movement |
| JUMP | bottom-right, upper | 64×64px | translucent light | Jump |
| ATK | bottom-right, lower-right | 64×64px | translucent red | Primary attack |
| SP | bottom-right, lower-left | 64×64px | translucent blue | Special attack |

Adjust for game type. Key constraint: buttons reachable by thumbs in landscape grip.

## References

- `references/kenshin-implementation.md` — Full working touch controls implementation for the Kenshin side-scroller
- `references/ai-game-dev-patterns.md` — Research findings: OpenAI game repos (procgen, neural-mmo), GothicVania Codex demo architecture, Phaser.js patterns, sprite generation tools (sprite-gen), agent skills workflow for AI-assisted game dev

## Mobile deployment

- **iOS HTML files:** Can't open .html from Files app directly into Safari reliably. Share sheet often doesn't show Safari. Workaround: serve via HTTP and access by IP, or use "Open in..." from long-press context menu.
- **Serve with Python:** `python3 -m http.server 8080` in the project directory. Access from mobile on same network via `http://<local-ip>:8080`.
- **Firewall:** Ensure the port is allowed: `sudo ufw allow 8080/tcp`.
- **Tunneling:** cloudflared needs outbound port 7844 (QUIC). ngrok needs auth token. Both may fail on restricted networks.
- **CDN dependencies:** If mobile users may have spotty connectivity, bundle p5.js inline rather than loading from CDN.
