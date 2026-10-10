# Style: Swiss Editorial Kinetic (International Typographic Style)

Architectural typographic authority: warm paper canvas, 12-column hairline
grid, colossal 100–140 px headlines, serif-italic tape accents, brutalist
zero-radius cards, marquee ribbons and single-frame inversions on drops.
Think Stripe Press / design biennale, not a slide deck.
Reference edition: target 130–150 s, 120–126 BPM, voice design curator,
drops at manifesto + finale.

Choose it for design toolkits, creative SaaS, brand repositioning, agencies,
curated releases, executive B2B — where craftsmanship and prestige sell.

## Tokens

```css
--paper: #f5f4ef; --cream: #ebe9e1; --black: #111111; --charcoal: #242424;
--sub: #63625d; --mute: #a19f97;
--blue: #0038ff; --blue-dk: #001f8f; --orange: #ff4500;
--rule: #111111; --rule-soft: rgba(17,17,17,0.16);
--tape: linear-gradient(90deg,#0038ff 0%,#001f8f 100%);
--inv-bg: #111111; --inv-ink: #f5f4ef;
```

No shadows, no gradients except `--tape`, no border-radius except caption pill
4 px. Contrast is the decoration. Inverse scenes swap `--paper`/`--black`.

Fonts (all OFL — PP Neue / Editorial New are commercial, do not reference):
Inter Display 800/900 (headlines, `tracking:-0.05em`), Playfair Display Italic
700 (accent words inside headlines), Space Mono 400/700 or JetBrains Mono
(index stamps, footnotes, 12–14 px uppercase), Be Vietnam Pro 700 (captions).

## Layers (back to front)

`#canvas` solid `var(--paper)` → `#paper-texture` (baked `paper-grain.png`,
`opacity:0.06`, `mix-blend-mode:multiply`, static) → `#grid-columns` (12× 1 px
lines at 10% opacity, static — never tweened) → `#pulse` wrapper → scenes
`#sc01…` → `#marquee-ribbon` (top + bottom tickers, constant-velocity `linear`
tweens built synchronously, `will-change:transform` off) → `#flash-invert`
(full-frame black div, `visibility:hidden` except drops) → `#captions` →
`#editorial-border` (perimeter 1 px hairline + corner tags `VOL.04 // ISSUE 2026`
+ folio numbers) → `#fade`.

Baked textures: `paper-grain.png`, `halftone-fine.png` (micro-dots for callouts
only). No `blur()`, no `backdrop-filter`, no `clip-path` crowds — hairlines are
plain divs/SVG lines for renderer safety.

## Components

- `.headline-giant`: 100–140 px Inter Display 900, `letter-spacing:-0.05em`,
  `line-height:0.88`, `color:var(--black)`, words in tight `overflow:hidden`
  masks. Accent word: Playfair Italic + `background:var(--tape)`, white text,
  `padding:0 12px`. Intro: mask slide-up stagger 0.06 + `scale 2.2→1`
  `power4.out` 0.28 s on the hero word, locked to grid — zero overshoot.
- `.swiss-card`: `border-radius:0`, 1 px solid `var(--black)`, interior either
  pure black (white type) or stark white (black type), padding `32px 36px`.
  No shadow. Reveals with `rise` stagger 0.07 on its keyword `W()`.
- `.index-stamp`: `( 01 )` / `FIG.4A`, Space Mono 700 22 px uppercase,
  bordered square `padding:8px 14px`, absolute top-left of card.
- `.marquee-tape`: full-bleed 64 px band, black bg white 28 px mono uppercase,
  one phrase repeated 8× via `rng` build step, glides `x:-50%→0` linear loop.
  Pause (freeze position) for 1 beat on drops for impact.
- `.comparison-matrix`: strict table, 1 px black cell dividers, header row black
  bg white text, binary badges `YES` (blue tape) / `NO` (outline), numbers
  `0.02s / 4.10s` in mono. Winner row inverts.
- `.hairline-arrow`: SVG 2 px line + crosshair, draws via `draw` exactly on
  kick downbeat `B(n)`, `n%4==0`.
- HUD counter: folio style `04 / 12` + thin progress rule (height 2 px, width
  tween), runs first→last feature scene, hidden on cover/outro — satisfies the
  composition-contract HUD requirement without a mascot.

## Motion language

- Kinetic type first: every scene opens with headline masks sliding up
  (`yPercent:110→0`, `power4.out` 0.4 s, stagger 0.06). Hero numbers punch
  `scale 2.2→1` 0.28 s. All reveals anchored to words via `W(sid,word)`.
- Hairlines draw themselves on kicks (`draw` 0.3 s). Nothing floats; everything
  locks to the column grid.
- Transitions (mechanical, rotate): `invert` (single-frame black/white flip
  0.04 s on snare), `curtain` (solid black or paper wipe `x:-100%→0` 0.3 s
  `power4.inOut`), `column-shutter` (4 vertical strips stagger 0.05 in on beat),
  `hard-cut` (zero-frame, on transient). Out: instant hide except curtain scenes
  (`fadeOut` 0.15 s). No `back.out`, no `elastic`, no smooth `power3` drifts.
- Beat reactions: hairline draws + folio number flips on kick; `#pulse`
  `scale 1.008` on kick downbeats only. Marquee velocity constant — never eased.
- Drops: canvas flips to `--inv-bg`, marquee freezes 1 beat, giant 180 px
  headline slams center with zero overshoot + `flash-invert` 1 frame. Second
  drop adds orange `FIG.` stamp.
- Outro (colophon): paper canvas, stacked credits `rise` stagger 0.08 on word
   onsets (`Design → Type → System → 2026`), border folio `END`, `fade` 0.4 s.

## Scene choreography (follow, don't invent)

Cover: `VOL.` stamp + giant title + hairline rule draws on kick.
Feature: left headline + right `swiss-card`, index stamp counts up.
Stats: 3-col matrix, `odo` numbers on spoken digits, winner inverts on drop word.
Diagram: hairline arrows `draw` + callout labels on `W()`.
Comparison: full matrix, rows reveal stagger 0.07.
Manifesto/drop: inverse black + 180 px slam.
Outro: colophon list above.

## Captions

Brutalist badge: solid white (paper scenes) or solid black (inverse scenes)
with 1 px `var(--black)` / white border, `border-radius:4px`, padding
`10px 20px`, 42 px Be Vietnam Pro 700. Active word: `background:var(--blue)`,
white text, `padding:2px 8px`. Swap theme with scene — never grey-on-grey.
Width caps at 1400 px centered, bottom band only.

## Audio & Music matching

- BPM 120–126 (minimal techno, crisp breakbeats, tight rimshots + double-bass
  stabs — needs hard transients for `hard-cut`/`invert`; NOT lo-fi/chillhop,
  which smears cuts).
- Voice (Gemini TTS): "Sophisticated design curator. Unhurried authority,
  perfect enunciation, measured cadence, intellectual conviction."
- SFX: paper snaps (scene in), typewriter carriage (headline), camera shutter
  (stats lock), soft acoustic thud (drop, −6 dB under voice).
- Mix per `audio-and-beat-sync.md`: music ~4–6 dB under speech.

## Renderer limits

Hairlines + grid are static DOM/SVG — zero per-frame cost. Marquee is 2 linear
tweens only. Invert is `visibility` toggle, never `filter:invert()`. Bake paper
grain. Keeps 1920×1080/30 renders black-frame-free.
