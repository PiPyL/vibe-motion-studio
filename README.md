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

## Auto-install with AI

Copy the prompt below into your coding agent (Claude Code, AgentKit, opencode, …)
and it will install everything for you. No `sudo` is ever run; anything needing
admin rights or API keys is reported back for you to do manually.

```text
Install the vibe-motion-studio skill for me, fully via terminal, and report the result at the end.

1. Clone the skill into the correct skills directory (auto-detect, in this priority order):
   - If ~/.agents/skills/ exists → clone into ~/.agents/skills/vibe-motion-studio
   - Else if ~/.claude/skills/ exists → clone into ~/.claude/skills/vibe-motion-studio
   - If the vibe-motion-studio directory already exists, run git pull inside it instead of cloning.
   Repo: https://github.com/PiPyL/vibe-motion-studio.git
   State the exact directory you installed into in your final report.

2. Verify SKILL.md exists at the root of the cloned directory.

3. Install system dependencies (skip any step that is already satisfied; NEVER use sudo —
   if a step needs admin rights, leave it for me and list it in the final report):
   - Node.js (check: node -v). If missing, do NOT install it yourself — list it as a manual step.
   - ffmpeg (check: ffmpeg -version). If missing: macOS `brew install ffmpeg`, Ubuntu/Debian `apt install -y ffmpeg` (user-space only). On Windows, stop here and point me to the manual install section in the repo README.
   - Python 3.10+ with numpy and scipy: `pip install numpy scipy` (check: `python3 -c "import numpy, scipy"`).
   - VieNeu-TTS for the free voice fallback: `pip install vieneu` (check: `python3 -c "import vieneu"`).

4. Verify: run `python3 -m unittest discover -s scripts/tests` inside the skill directory and confirm 3 tests pass.
   NOTE: do NOT install the multix CLI and do NOT configure any API key — only check `multix --version`.
   If multix is missing, write it clearly in the report so I install it and enter credentials myself (never print keys).

5. Final report must include: the exact skill path installed, the version of each tool
   (node, ffmpeg, python, numpy/scipy, vieneu, multix present/missing), the unit-test result,
   and any remaining manual steps (if any) for me to do myself.
```

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
