# Style: Cyberpunk Tactical HUD (Sci-Fi Mission Control)

Hyper-technical FUI authority: deep obsidian void, cyan/green telemetry glow,
polar grid + scan sweep, scanlines, corner reticles, descramble headlines and
console logs that type in on spoken words. Think Andor / Oblivion UI, not cheap
neon gamer wallpaper.
Reference edition: target 135–150 s, 122–128 BPM, voice cold tactical officer,
drops at feature reveals + finale.

Choose it for developer tools, cybersecurity, AI models & infra, cloud, Web3
protocols, high-frequency trading — where precision and speed sell.

## Tokens

```css
--bg: #05080f; --bg2: #0a101d; --panel: rgba(10,16,29,0.88);
--ink: #e0f4ff; --dim: #5c7996; --mute: #2a3d52;
--cyan: #00f0ff; --green: #00ff88; --amber: #ffb800; --red: #ff3355; --purple: #8f00ff;
--stroke: rgba(0,240,255,0.28); --stroke-hi: rgba(0,240,255,0.85);
--glow-c: 0 0 18px rgba(0,240,255,0.45); --glow-g: 0 0 18px rgba(0,255,136,0.45);
--grad-c: linear-gradient(135deg,#00f0ff 0%,#0080ff 100%);
--flash-c: rgba(0,240,255,0.9);
```

Fonts (all OFL): Orbitron 800/900 (headlines, uppercase only), JetBrains Mono
400/700 (kickers, telemetry, terminal, HUD), Be Vietnam Pro 600/700 (captions —
full Vietnamese diacritics). Never set body copy in Orbitron.

## Layers (back to front)

`#bg` solid `#05080f` → `#radar-grid` (one inline SVG: cartesian + polar rings,
single 48 s rotating sweep arm via timeline tween, `opacity:0.5`) →
`#scanline` (baked `scanline.png` 2 px tile, `opacity:0.12`, static — no tween) →
`#particles` (max 60 dots from `rng(seed)`, linear drift loops, `opacity:0.6`) →
`#pulse` wrapper → scenes `#sc01…` → `#hud-corners` (fixed `[ + ]` reticles,
`LAT/LON` + frame `F 0000` text updated on kick beats only) →
`#glitch-slices` (3 full-width slice divs, `visibility:hidden` except during
`glitch`) → `#flash` (background `var(--flash-c)`, not white) → `#captions` →
`#vignette` (radial edge darkening + 4 cyan corner brackets) → `#fade`.

Baked textures in project `assets/images/` (live `radial-gradient` + `blur()`
stacks black out the renderer past ~40 nodes): `scanline.png`,
`radar-grid.png`, `noise-digital.png` (fine mono grain, `opacity:0.08`).

Attach the RGB-split SVG filter only while `glitch` runs, then back to `none`.

## Components

- `.hud-panel`: `background:var(--panel)`, `clip-path: polygon(0 0,calc(100% - 16px) 0,100% 16px,100% 100%,16px 100%,0 calc(100% - 16px))`, 1 px `var(--stroke)` border (fake via outer wrapper — `clip-path` clips real borders), `box-shadow:var(--glow-c)`, padding `28px 32px`. Header row: 10 px status dot (blink via timeline `opacity` on kick, never CSS animation) + `ONLINE // ENCRYPTED` 20 px mono `var(--dim)`.
- `.kicker`: 22 px JetBrains Mono 700, `[ SYS::CORE_EXEC_v4 ]` uppercase, `color:var(--cyan)`, plus status pill (`.ok` green / `.warn` amber, 20 px, padding `4px 12px`, radius 999).
- `.h1`: 68–76 px Orbitron 900 uppercase, `letter-spacing:0.04em`, `line-height:0.95`, `color:var(--ink)`. Accent word in `var(--cyan)` with `text-shadow:var(--glow-c)`. Intro = rapid cypher descramble (use `typeIn` + per-letter stagger 0.035), not a plain fade.
- `.metric-tile`: 3-up row, each `hud-panel` + big `odo` number (48 px mono, `var(--green)`, `odo` helper on the spoken number word) + segmented meter `|||||||| 99.4%` (width tween via `draw`) + 120×36 SVG sparkline stroked `var(--cyan)`.
- `.terminal-window`: `hud-panel` + traffic dots (12 px red/amber/green circles) + `.term-line` rows 24 px mono. Each line reveals with `typeIn` at `W(sid,keyword)` onset — never all at once.
- `.reticle`: 120 px SVG corner brackets, `stroke:var(--cyan)` 3 px, scales `1.4→1` + `autoAlpha` via `pop` locked onto the feature callout word (`W()`), rotates 90° on snare (`isKick(n) && n%2`).
- `.alert-banner`: full-width top bar for drops: `background:var(--red)`, black mono 28 px `!! THREAT NEUTRALIZED // 0.02s !!`, slides in with `slideX`.

## Motion language

- Headline intro per scene: kicker `typeIn` at scene start + 0.05, then `.h1` letters descramble stagger 0.035, then panels `rise` stagger 0.07. Choreograph to words: "panel appears on the word *OAuth*", via `W(sid,"oauth")`.
- Transitions (rotate, never repeat neighbours): `glitch` 0.22 s (RGB split + slices), `shutter` (two 960 px blast doors `scaleY` shut 0.14 s, reopen 0.18 s on beat), `wireframe-zoom` (`scale 1.4→1`, `power4.out` 0.35 s), `laser-wipe` (2 px cyan beam `y -540→540` 0.18 s on kick), `fade` outro only. Out: `fadeOut` + `scale:0.98` 0.2 s.
- Beat reactions (texture only): HUD frame counter + hex tag randomise-and-lock on quarter `B(n)` (HUD only, max 4 nodes); `#flash` `0.22` on kick, `0.32` on kick downbeat; `#pulse` `scale 1.01` on kick downbeats (`n%4==0`).
- Drops: 1 beat tension — meters freeze + reticles lock + flash dips to 0. Full hit: flash `0.8` cyan, `shake(1.2)`, all meters spike to 100% (`odo` + meter width), `alert-banner` `slideX` in. Never insert true silence (breaks −14 LUFS target).
- Outro (telemetry shutoff): scenes out, terminal prints `SESSION TERMINATED → ALL SYSTEMS GO → REPOSITORY ACTIVE` each on its word onset, grid sweep slows to stop, `fade` to black 0.4 s.

## Scene choreography (follow, don't invent)

Cover: system boot — grid sweep in, kicker types, H1 descrambles, status `ONLINE`.
Feature: left H1 + right `hud-panel`, reticle locks on keyword.
Stats: 3× `metric-tile`, `odo` counts on spoken numbers.
Terminal/diagram: `terminal-window` lines on `W()` + sparkline `draw`.
Comparison: 2-col matrix, winner row `var(--green)` glow.
Drop/finale: `alert-banner` + meter spike + shake.
Outro: shutdown sequence above.

## Captions

Tactical teletype bar: `background:rgba(5,8,15,0.92)`, left 3 px `var(--cyan)` bar, padding `10px 22px`, 42 px Be Vietnam Pro 600, `color:#b8e6ff`. Active word: `background:rgba(0,240,255,0.18)`, `color:var(--cyan)`, `box-shadow:var(--glow-c)`, brackets via surrounding spans — never pure white on cyan.

## Vertical

Tactical portrait readout — single-column console:

- `.h1`: 40–44 px Orbitron (`0.56 × 68–76 px`), tracking 0.04em kept;
  descramble intro unchanged, stagger 0.035.
- `.hud-panel`: full width minus 64 px margins, clip-path corners 12 px
  instead of 16; header status row unchanged.
- `.metric-tile`: 1 column stacked (never 3-up); each tile full-width,
  `odo` 40 px, sparkline 200×36.
- `.terminal-window`: full-width, `.term-line` 22 px; keep traffic dots.
- `.reticle`: 80 px brackets (down from 120), lock-on `pop` unchanged.
- `.alert-banner`: full-width top bar, 24 px mono — fits without wrapping.
- Radar grid: polar rings recenter to upper third so telemetry doesn't fight
  captions; sweep arm 48 s unchanged. Corner HUD telemetry moves to a single
  top status line (`LAT/LON/F-frame` inline, 18 px mono).
- Transitions `glitch/shutter/wireframe-zoom/laser-wipe` unchanged; laser
  travels the shorter height, keep 0.18 s.

## Audio & Music matching

- BPM 122–128 (dark synthwave, darksynth, industrial techno — four-on-floor kicks for clean `isKick`).
- Voice (Gemini TTS): "Analytical, cold, confident AI tactical officer. Crisp military diction, fast cadence, sharp micro-pauses before technical reveals."
- SFX: relay clicks, keyboard clacks, radar sweep (on scene in), servo hum bed at −24 dB, HV charge riser into each drop.
- Mix per `audio-and-beat-sync.md`: music ~4–6 dB under speech, sidechain only on kicks.

## Renderer limits

One rotating sweep + max 60 particles + max 4 blinking dots. Everything else static or timeline-tweened. Bake scanlines/grids to PNG. No `backdrop-filter`, no per-frame `blur()`.
