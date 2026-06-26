#!/usr/bin/env python3
"""
Inject Offroad Insight touch overlay into Unity WebGL index.html.
IDEMPOTENT: removes any old injections before adding fresh ones.

v3: Wrapper-based fullscreen — avoids Unity's DOM manipulation entirely.
    Canvas + overlay live inside #oi-wrapper. Fullscreen targets #oi-wrapper,
    so Unity's framework.js never touches our positioning.
"""
import re, sys

HTML_PATH = sys.argv[1] if len(sys.argv) > 1 else 'index.html'

with open(HTML_PATH, 'r') as f:
    html = f.read()

# ── STEP 0: Remove ALL previous injections ──────────────────────────
html = re.sub(r'<style>\s*/\* ===== Offroad Insight Touch Overlay ===== \*/.*?</style>',
              '', html, flags=re.DOTALL)
html = re.sub(r'<!-- Offroad Insight Overlay HTML -->.*?<!-- /Offroad Insight Overlay HTML -->',
              '', html, flags=re.DOTALL)
html = re.sub(r'<script>\s*// ===== Offroad Insight Touch Overlay JS =====.*?</script>',
              '', html, flags=re.DOTALL)
html = re.sub(r'\s*window\.__tuanjieInstance = tuanjieInstance;\s*if \(window\.__oi_init\) window\.__oi_init\(tuanjieInstance\);',
              '', html)
html = re.sub(r'\s*/\* ===== Offroad Insight Wrapper Fullscreen CSS ===== \*/.*?</style>',
              '', html, flags=re.DOTALL)
html = re.sub(r'\n{4,}', '\n\n\n', html)

# Also clean up any wrapper divs left from previous injections
html = html.replace('<div id="oi-wrapper">', '')
html = html.replace('</div><!-- /oi-wrapper -->', '')

# ── STEP 1: Inject CSS into <head> ──────────────────────────────────
CSS = '''<style>
/* ===== Offroad Insight Touch Overlay ===== */

html, body { margin: 0; padding: 0; background: #000; height: 100%; overflow: hidden; }

/* Wrapper — contains canvas + overlay, fullscreened as one unit */
#oi-wrapper {
  position: absolute;
  left: 50%; top: 50%;
  width: 960px; height: 540px;
  overflow: hidden;
  transform: translate(-50%, -50%) scale(1);
}
/* Fullscreen: wrapper fills viewport, canvas stretches */
body.oi-fullscreen #oi-wrapper {
  width: 100vw; height: 100vh;
  left: 0; top: 0;
  transform: none;
}
body.oi-fullscreen #tuanjie-canvas { width: 100% !important; height: 100% !important; }

/* Hide Unity's built-in fullscreen button — we use our own */
#tuanjie-fullscreen-button { display: none !important; }

#oi-overlay {
  display: block;
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  z-index: 10;
  pointer-events: none;
  font-family: system-ui, -apple-system, sans-serif;
  -webkit-user-select: none; user-select: none;
}
#oi-overlay > * { pointer-events: auto; }

.oi-hold-btn, .oi-sm-btn, .oi-go-btn, .oi-brk-btn, .oi-top-btn {
  touch-action: manipulation; -webkit-tap-highlight-color: transparent;
  user-select: none; cursor: pointer; border: none;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  font-weight: bold;
}
.oi-hold-btn:active, .oi-sm-btn:active, .oi-go-btn:active, .oi-brk-btn:active, .oi-top-btn:active,
.oi-hold-btn.pressed, .oi-go-btn.pressed, .oi-brk-btn.pressed {
  background: rgba(50,130,255,0.7) !important; transform: scale(0.93);
}

/* TOP BAR */
#oi-top-bar {
  position: absolute; top: 1vh; left: 2vw; right: 2vw;
  display: flex; align-items: center; justify-content: center;
}
#oi-small-bar { display: flex; gap: clamp(5px, 1.2vw, 10px); }
.oi-top-btn {
  width: clamp(36px, 7vw, 56px); height: clamp(24px, 4.5vw, 38px);
  border-radius: 6px; border: 1px solid rgba(255,255,255,0.16);
  background: rgba(20,20,20,0.5); color: rgba(255,255,255,0.7);
  font-size: 12px; flex-shrink: 0;
}
.oi-menu-btn { background: rgba(150,20,20,0.5) !important; }

/* FULLSCREEN BUTTON */
#oi-btn-fs {
  position: absolute; top: 1vh; right: 2vw;
  width: clamp(34px, 7vw, 48px); height: clamp(34px, 7vw, 48px);
  border-radius: 8px; border: 1px solid rgba(255,255,255,0.18);
  background: rgba(60,40,10,0.45); color: rgba(255,255,255,0.7);
  font-size: 18px; font-weight: bold; cursor: pointer;
  touch-action: manipulation; -webkit-tap-highlight-color: transparent;
  user-select: none;
}
#oi-btn-fs:active { background: rgba(50,130,255,0.6) !important; transform: scale(0.93); }

/* CAMERA DRAG ZONE */
#oi-cam-zone {
  position: absolute;
  top: calc(clamp(24px, 4.5vw, 38px) + 3vh);
  left: 2vw; right: 2vw;
  bottom: calc(28vh + 3vh);
  z-index: 5;
  pointer-events: none;
}

/* BOTTOM BAR */
#oi-bottom-bar {
  position: absolute; left: 0; right: 0; bottom: 0;
  height: 28vh; display: flex;
  z-index: 20;
  padding-bottom: env(safe-area-inset-bottom, 0px);
}

/* STEERING ZONE */
#oi-steer-zone {
  flex: 0 0 50%; height: 100%;
  position: relative;
  display: flex; align-items: center; justify-content: center;
}
#oi-joystick-base {
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,0.05);
  border: 2px solid rgba(255,255,255,0.16);
  width: min(85%, clamp(70px, 26vw, 120px));
  height: min(85%, clamp(70px, 26vw, 120px));
  max-width: 24vh; max-height: 24vh;
  transform: translate(-50%, -50%);
}
#oi-joystick-thumb {
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,0.3);
  width: min(45%, clamp(35px, 12vw, 55px));
  height: min(45%, clamp(35px, 12vw, 55px));
  max-width: 12vh; max-height: 12vh;
  transform: translate(-50%, -50%);
  display: none; pointer-events: none;
}

/* DRIVE ZONE */
#oi-drive-zone {
  flex: 0 0 50%; height: 100%;
  display: flex; align-items: center; justify-content: space-evenly;
}
#oi-drive-left { display: flex; flex-direction: column; align-items: center; gap: 1.5vh; }
#oi-drive-right { display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 1.5vw; }

.oi-sm-btn {
  width: 11vh; height: 11vh; max-width: 68px; max-height: 68px;
  min-width: 36px; min-height: 36px;
  border-radius: 50%; border: 1px solid rgba(255,255,255,0.18);
  background: rgba(20,20,20,0.5); color: rgba(255,255,255,0.7);
  font-size: 12px;
}
.oi-brk-btn {
  width: 15vh; height: 15vh; max-width: 90px; max-height: 90px;
  min-width: 48px; min-height: 48px;
  border-radius: 50%; border: 2px solid rgba(255,255,255,0.22);
  background: rgba(20,20,20,0.55); color: rgba(255,255,255,0.85);
  font-size: 18px;
}
.oi-go-btn {
  width: 18vh; height: 18vh; max-width: 110px; max-height: 110px;
  min-width: 56px; min-height: 56px;
  border-radius: 50%; border: 2px solid rgba(40,200,70,0.45);
  background: rgba(20,140,50,0.5); color: rgba(255,255,255,0.9);
  font-size: 24px;
}
.oi-dlabel { font-size: 0.38em; color: rgba(200,200,200,0.5); margin-top: 2px; }
.oi-sm-btn.active {
  background: rgba(255,200,50,0.45) !important;
  border-color: rgba(255,200,50,0.7) !important;
  color: rgba(255,255,255,0.95) !important;
}
body.oi-kb-active #oi-overlay { display: none !important; }
</style>
'''

html = html.replace('</head>', CSS + '\n</head>', 1)

# ── STEP 2: Wrap canvas + overlay in oi-wrapper ─────────────────────
OVERLAY_HTML = '''
<!-- Offroad Insight Overlay HTML -->
<div id="oi-overlay">

  <div id="oi-top-bar">
    <div id="oi-small-bar">
      <button id="oi-btn-reset" class="oi-top-btn">reset</button>
      <button id="oi-btn-cam"   class="oi-top-btn">view</button>
      <button id="oi-btn-menu"  class="oi-top-btn oi-menu-btn">menu</button>
    </div>
  </div>
  <button id="oi-btn-fs">&#x26F6;</button>

  <div id="oi-cam-zone"></div>

  <div id="oi-bottom-bar">
    <div id="oi-steer-zone">
      <div id="oi-joystick-base"></div>
      <div id="oi-joystick-thumb"></div>
    </div>
    <div id="oi-drive-zone">
      <div id="oi-drive-left">
        <button id="oi-btn-light" class="oi-sm-btn">light</button>
        <button id="oi-btn-hb"    class="oi-sm-btn">HB</button>
      </div>
      <div id="oi-drive-right">
        <button id="oi-btn-brk" class="oi-brk-btn">&#x25BC;<span class="oi-dlabel">BRK</span></button>
        <button id="oi-btn-go"  class="oi-go-btn">&#x25B2;<span class="oi-dlabel">GO</span></button>
      </div>
    </div>
  </div>

</div>
<!-- /Offroad Insight Overlay HTML -->
'''

# ── Wrap everything inside #tuanjie-container in #oi-wrapper ────────
# Structure: <container> <wrapper> <canvas> <overlay> <loading-bar> <footer> </wrapper> </container>
WRAPPER_OPEN = '<div id="oi-wrapper">'
WRAPPER_CLOSE = '</div><!-- /oi-wrapper -->'

canvas_tag = '<canvas id="tuanjie-canvas" width=960 height=540 tabindex="-1"></canvas>'
html = html.replace(canvas_tag, WRAPPER_OPEN + canvas_tag, 1)
html = html.replace(canvas_tag, canvas_tag + '\n' + OVERLAY_HTML, 1)
# Close wrapper just before </div> that closes #tuanjie-container
# The last </div> before the loading scripts is the container close
html = html.replace(
    '</div>\n\t\n\t\n    <script>',
    '\n' + WRAPPER_CLOSE + '\n    </div>\n\t\n\t\n    <script>',
    1
)

# ── STEP 3: Add __oi_init call ──────────────────────────────────────
OLD_CALLBACK = '''.then((tuanjieInstance) => {
                loadingBar.style.display = "none";
                // Unity fullscreen button hidden via CSS — we use oi-btn-fs
              })'''

NEW_CALLBACK = '''.then((tuanjieInstance) => {
                window.__tuanjieInstance = tuanjieInstance;
                if (window.__oi_init) window.__oi_init(tuanjieInstance);
                loadingBar.style.display = "none";
                // Unity fullscreen button hidden via CSS — we use oi-btn-fs
              })'''

html = html.replace(OLD_CALLBACK, NEW_CALLBACK, 1)

# ── STEP 4: Inject JS at end of <body> ──────────────────────────────
JS = '''
<script>
// ===== Offroad Insight Touch Overlay JS =====
(function() {
  var overlayEl = document.getElementById('oi-overlay');
  var wrapperEl = document.getElementById('oi-wrapper');
  var canvasEl  = document.querySelector('#tuanjie-canvas');
  var uInstance = null;

  // ---- SendMessage helper ----
  function sm(method, value) {
    try {
      if (uInstance) uInstance.SendMessage('TouchBridge', method, value);
    } catch(e) {}
  }

  // ---- Continuous buttons (hold) ----
  function bindHold(id, name) {
    var el = document.getElementById(id);
    if (!el) return;
    function down(e) {
      e.preventDefault(); e.stopPropagation();
      el.classList.add('pressed');
      sm('OnTouchDown', name);
      if (canvasEl) canvasEl.focus();
    }
    function up(e) {
      el.classList.remove('pressed');
      sm('OnTouchUp', name);
    }
    el.addEventListener('touchstart', down, {passive: false});
    el.addEventListener('touchend', up);
    el.addEventListener('touchcancel', up);
    el.addEventListener('mousedown', down);
    el.addEventListener('mouseup', up);
    el.addEventListener('mouseleave', up);
  }
  bindHold('oi-btn-go',  'throttle');
  bindHold('oi-btn-brk', 'brake');
  bindHold('oi-btn-hb',  'handbrake');

  // ---- Joystick ----
  // All coordinates in CSS pixels. Touch viewport coords converted via scale factor.
  var joyZone  = document.getElementById('oi-steer-zone');
  var joyBase  = document.getElementById('oi-joystick-base');
  var joyThumb = document.getElementById('oi-joystick-thumb');
  var joyActive = false, joyFingerId = -1, joyCx = 0, joyCy = 0, joyRadius = 60;

  function joyInit() {
    // CSS pixel coords (stable, unaffected by wrapper scale transform)
    joyCx = joyZone.offsetWidth * 0.35;
    joyCy = joyZone.offsetHeight * 0.5;
    joyBase.style.left = joyCx + 'px';
    joyBase.style.top  = joyCy + 'px';
    joyRadius = joyBase.offsetWidth * 0.45;
  }
  function joyShow(cx, cy) {
    joyThumb.style.display = 'block';
    joyThumb.style.left = cx + 'px';
    joyThumb.style.top  = cy + 'px';
    sm('OnSteer', '0');
  }
  function joyMove(cx, cy) {
    var dx = cx - joyCx, dy = cy - joyCy;
    var dist = Math.sqrt(dx*dx + dy*dy);
    var clampDist = Math.min(dist, joyRadius);
    var angle = Math.atan2(dy, dx);
    joyThumb.style.left = (joyCx + Math.cos(angle) * clampDist) + 'px';
    joyThumb.style.top  = (joyCy + Math.sin(angle) * clampDist) + 'px';
    var steer = Math.max(-1, Math.min(1, dx / joyRadius));
    sm('OnSteer', steer.toFixed(2));
  }
  function joyHide() {
    joyActive = false; joyFingerId = -1;
    joyThumb.style.display = 'none';
    sm('OnSteer', '0');
  }
  // Convert viewport touch coords to CSS pixel coords
  function viewportToCSS(clientX, clientY) {
    var zr = joyZone.getBoundingClientRect();
    var scale = zr.width / joyZone.offsetWidth;
    return {
      x: (clientX - zr.left) / scale,
      y: (clientY - zr.top) / scale
    };
  }

  if (joyZone) {
    joyZone.addEventListener('touchstart', function(e) {
      if (joyActive) return;
      var t = e.changedTouches[0];
      joyActive = true; joyFingerId = t.identifier;
      var css = viewportToCSS(t.clientX, t.clientY);
      joyShow(css.x, css.y);
      e.preventDefault();
    }, {passive: false});
    joyZone.addEventListener('touchmove', function(e) {
      if (!joyActive) return;
      for (var i = 0; i < e.changedTouches.length; i++) {
        var t = e.changedTouches[i];
        if (t.identifier === joyFingerId) {
          var css = viewportToCSS(t.clientX, t.clientY);
          joyMove(css.x, css.y);
          break;
        }
      }
      e.preventDefault();
    }, {passive: false});
    joyZone.addEventListener('touchend', function(e) {
      for (var i = 0; i < e.changedTouches.length; i++)
        if (e.changedTouches[i].identifier === joyFingerId) { joyHide(); break; }
    });
    joyZone.addEventListener('touchcancel', joyHide);
    joyZone.addEventListener('mousedown', function(e) {
      if (joyActive) return;
      joyActive = true;
      var css = viewportToCSS(e.clientX, e.clientY);
      joyShow(css.x, css.y);
    });
    document.addEventListener('mousemove', function(e) {
      if (joyActive && joyFingerId < 0 && e.buttons) {
        var css = viewportToCSS(e.clientX, e.clientY);
        joyMove(css.x, css.y);
      }
    });
    document.addEventListener('mouseup', function() { if (joyFingerId < 0) joyHide(); });
  }

  // ---- One-shot buttons ----
  function bindTap(id, name) {
    var el = document.getElementById(id);
    if (!el) return;
    function tap(e) {
      e.preventDefault(); e.stopPropagation();
      sm('OnTap', name);
      if (canvasEl) canvasEl.focus();
    }
    el.addEventListener('touchend', tap);
    el.addEventListener('click', tap);
  }
  bindTap('oi-btn-reset', 'reset');
  bindTap('oi-btn-cam',   'camera');
  bindTap('oi-btn-menu',  'menu');

  // Headlight toggle
  (function() {
    var lightBtn = document.getElementById('oi-btn-light');
    var lightOn = false;
    if (lightBtn) {
      function toggleLight(e) {
        e.preventDefault(); e.stopPropagation();
        lightOn = !lightOn;
        lightBtn.classList.toggle('active', lightOn);
        sm('OnTap', 'headlights');
        if (canvasEl) canvasEl.focus();
      }
      lightBtn.addEventListener('touchend', toggleLight);
      lightBtn.addEventListener('click', toggleLight);
    }
  })();

  // ---- Fullscreen — targets #oi-wrapper, NOT tuanjie-container ----
  // Unity's framework.js fullscreen listeners only fire on the canvas/
  // container. By fullscreening #oi-wrapper (a separate div), we
  // completely bypass Unity's DOM manipulation.
  (function() {
    var btn = document.getElementById('oi-btn-fs');
    if (!btn || !wrapperEl) return;

    var _fsTimer = null;
    function onFSChange() {
      clearTimeout(_fsTimer);
      var fs = !!(document.fullscreenElement || document.webkitFullscreenElement);
      if (!fs) {
        // Exiting fullscreen (ESC or button): delay class toggle to let
        // browser/Unity settle after the synchronous canvas resize.
        // Without this delay, Unity mid-frame resize causes freeze.
        _fsTimer = setTimeout(function() {
          document.body.classList.remove('oi-fullscreen');
          // Refocus canvas so keyboard input continues to work
          if (canvasEl) { canvasEl.focus(); canvasEl.style.display = ''; }
          scaleToFit();
        }, 50);
      } else {
        document.body.classList.add('oi-fullscreen');
        if (canvasEl) canvasEl.focus();
        scaleToFit();
      }
    }
    document.addEventListener('fullscreenchange', onFSChange);
    document.addEventListener('webkitfullscreenchange', onFSChange);

    btn.addEventListener('click', function(e) {
      e.preventDefault(); e.stopPropagation();
      var fs = !!(document.fullscreenElement || document.webkitFullscreenElement);
      if (!fs) {
        if (wrapperEl.requestFullscreen) wrapperEl.requestFullscreen();
        else if (wrapperEl.webkitRequestFullscreen) wrapperEl.webkitRequestFullscreen();
      } else {
        if (document.exitFullscreen) document.exitFullscreen();
        else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
      }
      if (canvasEl) canvasEl.focus();
    });
    btn.addEventListener('touchend', function(e) {
      e.preventDefault(); e.stopPropagation();
      btn.click();
    });
  })();

  // ---- Camera drag zone ----
  var camZone = document.getElementById('oi-cam-zone');
  var camActive = false, camFingerId = -1, camLast = {x:0, y:0};
  if (camZone) {
    camZone.addEventListener('touchstart', function(e) {
      if (camActive || e.touches.length !== 1) return;
      var t = e.changedTouches[0];
      camActive = true; camFingerId = t.identifier;
      camLast = {x: t.clientX, y: t.clientY};
      e.preventDefault();
    }, {passive: false});
    camZone.addEventListener('touchmove', function(e) {
      if (!camActive) return;
      for (var i = 0; i < e.changedTouches.length; i++) {
        var t = e.changedTouches[i];
        if (t.identifier === camFingerId) {
          var dx = t.clientX - camLast.x, dy = t.clientY - camLast.y;
          camLast = {x: t.clientX, y: t.clientY};
          sm('OnCameraDrag', dx.toFixed(1) + ':' + dy.toFixed(1));
          break;
        }
      }
      e.preventDefault();
    }, {passive: false});
    camZone.addEventListener('touchend', function(e) {
      for (var i = 0; i < e.changedTouches.length; i++)
        if (e.changedTouches[i].identifier === camFingerId) { camActive = false; camFingerId = -1; break; }
    });
    camZone.addEventListener('touchcancel', function() { camActive = false; camFingerId = -1; });
    camZone.addEventListener('mousedown', function(e) {
      if (camActive) return;
      camActive = true; camLast = {x: e.clientX, y: e.clientY};
    });
    document.addEventListener('mousemove', function(e) {
      if (camActive && camFingerId < 0 && e.buttons) {
        var dx = e.clientX - camLast.x, dy = e.clientY - camLast.y;
        camLast = {x: e.clientX, y: e.clientY};
        sm('OnCameraDrag', dx.toFixed(1) + ':' + dy.toFixed(1));
      }
    });
    document.addEventListener('mouseup', function() { if (camFingerId < 0) camActive = false; });
  }

  // ---- Visibility: reset held buttons ----
  document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
      document.querySelectorAll('.pressed').forEach(function(el) { el.classList.remove('pressed'); });
      sm('OnTouchUp', 'throttle');
      sm('OnTouchUp', 'brake');
      sm('OnTouchUp', 'handbrake');
    }
  });

  // ---- Keyboard detection ----
  var kbUsed = false;
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Shift' || e.key === 'Control' || e.key === 'Alt' || e.key === 'Meta') return;
    if (!kbUsed) { kbUsed = true; document.body.classList.add('oi-kb-active'); }
  });

  // ---- Auto-scale to fill viewport (non-fullscreen) ----
  function scaleToFit() {
    if (!wrapperEl || !canvasEl) return;
    if (document.fullscreenElement || document.webkitFullscreenElement) {
      return; // CSS handles fullscreen
    }
    var vw = window.innerWidth, vh = window.innerHeight;
    var ASPECT = 960 / 540;
    var w = vw, h = vw / ASPECT;
    if (h > vh) { h = vh; w = vh * ASPECT; }
    var s = w / 960;
    wrapperEl.style.transform = 'translate(-50%, -50%) scale(' + s + ')';
  }
  window.addEventListener('resize', function() { setTimeout(scaleToFit, 100); });
  window.addEventListener('load', scaleToFit);

  // ---- Init ----
  window.__oi_init = function(instance) {
    uInstance = instance;
    scaleToFit();
    if (joyZone && joyBase) joyInit();
  };

  // Called by Unity via Application.ExternalCall when menu/game state changes
  window.oi_set_overlay_visible = function(visible) {
    if (overlayEl) overlayEl.style.display = visible ? 'block' : 'none';
  };
})();
</script>
'''

html = html.replace('</body>', JS + '\n</body>', 1)

with open(HTML_PATH, 'w') as f:
    f.write(html)

print(f"Injected overlay (v3 wrapper) into {HTML_PATH} ({len(html)} bytes)")
