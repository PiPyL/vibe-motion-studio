# Vibe Motion Studio

Beat-synced 1080p motion-graphic videos in HyperFrames (HTML + GSAP): AI voice-over,
Vietnamese karaoke captions, SFX and generated music — scene cuts land on the beat,
reveals land on spoken words.

Forked from `motion-video` with two big upgrades:

1. **Three rebuilt styles** — Cyberpunk Tactical HUD, Swiss Editorial Kinetic and
   Soft Tactile Clay rewritten to the same bar as the Comic / Glass-Keynote editions:
   exact tokens, layer stacks, components, word-anchored choreography, drops, outros,
   captions and renderer limits.
2. **Free voice fallback** — when Gemini / ElevenLabs quotas run out, generate the
   voice-over on-device with [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS)
   (`assets/templates/scripts/generate-vo-vieneu.py`). Same output filenames, so the
   rest of the pipeline is unchanged.

## Five styles

| Style | Feel |
|---|---|
| Comic multiverse | loud, playful, hand-made |
| Glass keynote | premium, calm, clear |
| Cyberpunk tactical HUD | technical, high-precision, intense |
| Swiss editorial kinetic | authoritative, stark, architectural |
| Soft tactile clay | warm, approachable, joyful |

## Install

```bash
git clone https://github.com/PiPyL/vibe-motion-studio.git
```

- **Claude.ai**: zip the folder → Settings > Capabilities > Skills > Upload.
- **Claude Code / AgentKit**: place under your skills directory, e.g.
  `~/.agents/skills/vibe-motion-studio/`.
- Test: ask *“làm video motion graphic giới thiệu release”*.

## Pipeline

```
facts → script → audio (multix, or VieNeu-TTS fallback for VO)
  → forced alignment → beat grid → bar-spliced music
  → timeline + mix → HTML composition → lint/check/snapshot
  → render → remux → social encode
```

See `SKILL.md` for the full workflow and `references/` for the production
pipeline, beat-sync, composition contract and per-style guides.

## License

MIT
