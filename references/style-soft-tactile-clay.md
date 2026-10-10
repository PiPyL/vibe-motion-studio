# Style: Soft Tactile Clay (3D Claymorphism & Bubbly Toybox)

Warm toybox delight: milk-cream canvas, pastel clay solids with real bevel
depth, 36 px cards, pill buttons that squash on kicks, elastic physics and
pastel confetti that explodes only on drops. Think Pitch / Duolingo / Linear
icons — soft, never flat, never childish-cheap.
Reference edition: target 120–140 s, 112–118 BPM, voice bubbly storyteller,
drops at feature trio + finale.

Choose it for B2C mobile, EdTech, productivity, collab tools, creator apps,
health & wellness — where friendliness converts.

## Tokens

```css
--bg: #faf7f2; --surface: #ffffff;
--ink: #242b35; --soft: #677487; --mute: #9aa5b5;
--peach: #ff8a65; --lav: #9c88ff; --lav-dk: #6d5bff; --mint: #2ed573;
--sky: #38bdf8; --sun: #ffa502; --coral: #ff6b81;
--r-card: 36px; --r-pill: 999px; --r-inner: 24px;
--bd-clay: 2.5px solid rgba(255,255,255,0.85);
--sh-clay: 0 20px 35px rgba(36,43,53,0.07), 0 8px 16px rgba(36,43,53,0.04), inset 0 -5px 8px rgba(36,43,53,0.05), inset 0 4px 8px rgba(255,255,255,0.95);
--sh-hover: 0 26px 45px rgba(36,43,53,0.10), 0 10px 20px rgba(36,43,53,0.05), inset 0 -3px 6px rgba(36,43,53,0.04), inset 0 5px 10px rgba(255,255,255,0.98);
```

Pastel is for fills only — text is always `--ink` on light, white on
`--lav-dk`/`--peach` fills (never white on `--lav` — contrast fails).

Fonts (all OFL): Plus Jakarta Sans or Outfit 800/900 (headlines, rounded),
Poppins 600 / Inter 600 (body/labels), Sniglet 400 (badges/numbers accents),
Be Vietnam Pro 700 (captions — diacritics).

## Layers (back to front)

`#canvas-warm` solid `var(--bg)` → `#pastel-orbs` (3 large radial PNG blobs:
peach/mint/lavender, 40 s sine drift loops, `opacity:0.55` — baked gradients,
no live `blur()`) → `#floating-props` (max 8 clay shapes: spheres/torus/pills
from `clay-*.png`, gentle `y:±8px` `sine.inOut` loops, stagger via `rng`) →
`#pulse` wrapper → scenes `#sc01…` → `#hud-floating` (top-right mascot avatar
80 px circle + level badge `.lvl` + XP bar) → `#confetti-burst` (max 80 DOM
rects/circles from `confetti-pack.png` sprites, `visibility:hidden` except
drops — no canvas, deterministic via `rng(seed)`) → `#captions` → `#fade`.

Baked textures: `clay-sphere.png`, `clay-torus.png`, `clay-pill.png`,
`confetti-pack.png` (pastel stars/circles sheet). Live CSS blobs + blur caused
black frames at 1080p — always use PNGs.

## Components

- `.clay-card`: `background:var(--surface)`, `border-radius:var(--r-card)`,
  `border:var(--bd-clay)`, `box-shadow:var(--sh-clay)`, padding `36px 40px`,
  inner top highlight via `::before` (white 40% line). Intro: squash
  (`scaleY:0.92,scaleX:1.05` 0.12 s) → `elastic.out(1,0.45)` to 1, stagger 0.07
  on keyword `W()`.
- `.h1`: 64–80 px Plus Jakarta 800, `letter-spacing:-0.02em`,
  `line-height:0.95`, `color:var(--ink)`. Accent word in pill
  (`background:var(--peach)` or `var(--lav-dk)`, white text, `radius:999`,
  `padding:4px 20px`). Intro: `elasticWord(.hl .w, W(sid,word))` — back.out(1.8),
  0.5 s, stagger 0.05.
- `.bubbly-pill`: `radius:999`, pastel fill, 24 px Poppins 700, padding
  `14px 28px`, `box-shadow:var(--sh-clay)`. Compresses `scale:0.94` 0.08 s on
   every kick then releases — the characteristic squash-and-release beat feel.
- `.emoji-avatar`: 96 px clay icon circle, `bob y:±8px sine.inOut`, tilts ±6°
  on snare. Max 3 per scene for perf.
- `.toggle`: chunky 120×64 pill track + 52 px knob PNG; knob slides
  `x:0→56` `back.out(2)` 0.3 s exactly on confirmation words
  (`W(sid,"enabled")`, `"fast"`, `"instant"`).
- `.lvl` badge: Sniglet 28 px + XP bar (height 12 px, `radius:999`,
  fill `var(--mint)`, width tween via `odo`/word). Squashes on kick.
- Mascot: chubby clay blob inline SVG via `mascot(uid,acc)` — blinks (eyes
  `scaleY` 0.1 s every ~3 s), squashes on kick (`.m-squash`), talks via
  `envKeys` on `.m-mouth` between line on/off, celebration flip (`rotation:360`)
  on drops. Accessories per scene (cap, glasses, star wand).

## Motion language

- Physics first: `elastic.out(1,0.45)` / `back.out(1.8)` for entrances;
  squash-and-stretch pre-compress on every card entrance. Eases are bouncy,
  never `power4` slams or stepped `on2`.
- Transitions (soft, rotate): `pop-bubble` (from center clay bubble
  `scale:0.2→1` `back.out(2)` 0.5 s), `spring-up` (elements `y:120→0` stagger
  0.05 `back.out(1.7)`), `soft-slide` (rounded curtain `radius:48px` slide +
  `elastic` overshoot 0.15), `fade` outro only. Out: squash down
  `scaleY:0.9` + `fadeOut` 0.22 s.
- Beat reactions: props bob +12 px on quarter `B(n)`; cards micro-bounce
  `scale:1.025→1` 0.18 s on kick; pills compress 0.94 on kick; mascot squash on
  kick downbeat. Keep amplitudes small — cuteness, not seasickness.
- Drops: 1-beat squash (whole `#pulse` `scaleY:0.96`) → explode out
  (`scale:1` `elastic.out`) + full confetti `pop` (80 pieces, `rng` trajectories,
  gravity fall 1.2 s) + mascot flip + `bubbly-pill` flash. Confetti only on
  drops — never ambient.
- Outro (warm goodbye): cream canvas holds, mascot waves (arm rotate ±15°
  ×3), credits `rise` stagger 0.08, confetti mini-pop 24 pcs, `fade` to cream
  0.5 s (not black).

## Scene choreography (follow, don't invent)

Cover: orbs drift in, H1 words pop, mascot peeks + waves on brand word.
Feature: left H1 + right `clay-card`, toggle slides on confirmation word.
Stats: 3× mini clay-cards, `odo` counts + XP bars fill on spoken numbers.
How-it-works: 3 pills in a row, each pops on its keyword, knob toggles.
Comparison: 2 cards — winner lifts (`y:-12`, `sh-hover`) + mint badge.
Drop: trio cards slam + confetti + mascot flip.
Outro: mascot center, `Coming soon` pills rise, cream fade.

## Captions

Milk cloud pill: `background:rgba(255,255,255,0.94)`,
`box-shadow:0 12px 30px rgba(36,43,53,0.08)`, `radius:28px`,
padding `12px 28px`, 40 px Be Vietnam Pro 700, `color:var(--ink)`.
Active word: `background:var(--lav-dk)` (not `--lav` — contrast),
white text, `radius:12px`, `padding:2px 10px`. Bottom band only, max 1400 px.

## Vertical

Toybox tower — one squishy layer at a time:

- `.h1`: 36–44 px Plus Jakarta (`0.56 × 64–80 px`); accent pill
  `padding:4px 16px`, 30 px text.
- `.clay-card`: `radius:28px` (down from 36), padding `26px 28px`, full width
  minus 64 px margins; squash pre-compress + `elastic.out(1,0.45)` unchanged.
- `.bubbly-pill`: 20 px Poppins, kick compress 0.94 kept — pills stack
  vertically with 16 px gaps, never side by side.
- Mascot scales 0.75×, bottom-center above captions (bottom 220 px reserved);
  blink/squash/talk/flip behaviors unchanged.
- Floating props: max 5 (down from 8), smaller radii; confetti 60 pieces
  (down from 80) — narrower frame needs fewer particles for the same density.
- Captions: milk pill 38 px, box up to 960 px, bottom 64 px.

## Audio & Music matching

- BPM 112–118 (upbeat indie pop, marimba chilhop, cheerful future bass with
  guitar strum + bouncy synth chords — 102 BPM drags cuts, 112+ keeps spring).
- Voice (Gemini TTS): "Warm bubbly product storyteller. Smiling throughout,
  cheerful bouncy cadence, encouraging, clear, delightfully friendly."
- SFX: bubble pops (scene in, −12 dB), wooden block clicks (word reveals),
  squish bounce (card squash), toybox chime (toggle), confetti pop (drops).
- Mix per `audio-and-beat-sync.md`: music ~4–6 dB under speech; keep low-end
  light so squash SFX poke through.

## Renderer limits

Max 8 floating props + 3 orbs (PNG) + 80 confetti (drops only,
`visibility`-gated). No `backdrop-filter`, no live `blur()`, no canvas.
All physics are timeline tweens from `TIMING` — deterministic across renders.
