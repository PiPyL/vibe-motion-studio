#!/usr/bin/env python3
"""Fallback voice-over generator with VieNeu-TTS (on-device Vietnamese TTS).

Use when Gemini / ElevenLabs quotas are exhausted. Produces the same
per-scene WAVs as `generate-audio-assets.mjs vo` so the rest of the pipeline
(`align-voiceover`, `build-timeline`) works unchanged.

Default reads the `vi` lines (Vietnamese VO) because VieNeu's strength is
Vietnamese; v3 Turbo is bilingual but English comes out with a Vietnamese
accent. Pass --lang en to keep English VO with that caveat.

Setup (CPU, torch-free, RTF ~0.5):
    pip install vieneu
Preview voices in the Web UI before batch-generating:
    uv run vieneu-web   # http://127.0.0.1:7860, backbone "VieNeu-TTS-v3-Turbo"

Suggested preset voices per style (editors' picks, override with --voice):
    comic / hype ...... Adam bựa, Hải Đăng
    glass keynote ..... Hải Đăng, Mai Anh
    cyberpunk HUD ..... Thiện Minh, Quang Sơn
    swiss editorial ... Thiền Tâm Đức, Ngọc Huyền
    soft clay ......... Mai Anh, Trúc Ly

Usage:
    python scripts/generate-vo-vieneu.py [--voice "Hải Đăng"] [--lang vi|en]
        [--ref-audio my_voice.wav] [--force] [--only=s01-cover,s02-power-01]
        [--list-voices]

Notes:
- v3 Turbo ignores style prompts; character comes from the preset / cloned
  reference voice. Emotion cues [cười], [thở dài], [hắng giọng] work inline.
- Output is 48 kHz WAV, matching the mix target. TEMPO=1.08 speed-up for
  energetic lines still happens later in build-timeline, not here.
- If VO switches to Vietnamese, captions align even better (spoken words ==
  caption words). Keep `en`/`say` fields untouched for future re-voice.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # project dir (scripts/..)


def scene_text(scene, lang):
    if lang == "vi":
        missing = [i for i, l in enumerate(scene["lines"]) if not l.get("vi")]
        if missing:
            sys.exit(f"scene {scene['id']} lines {missing} have no `vi` text (required for --lang vi)")
        return " ".join(l["vi"] for l in scene["lines"])
    return " ".join(l.get("say") or l["en"] for l in scene["lines"])


def main():
    ap = argparse.ArgumentParser(description="VieNeu-TTS fallback VO generator")
    ap.add_argument("--voice", default="Hải Đăng", help="preset voice name")
    ap.add_argument("--lang", default="vi", choices=["vi", "en"],
                    help="vi = read `vi` lines (recommended), en = read `say||en`")
    ap.add_argument("--ref-audio", default=None,
                    help="3-8s reference clip for instant cloning (overrides --voice)")
    ap.add_argument("--force", action="store_true", help="regenerate existing WAVs")
    ap.add_argument("--only", default="", help="comma-separated scene ids")
    ap.add_argument("--list-voices", action="store_true", help="list preset voices and exit")
    args = ap.parse_args()

    try:
        from vieneu import Vieneu
    except ImportError:
        sys.exit("vieneu not installed. Run: pip install vieneu  (GPU: pip install 'vieneu[cuda]')")

    tts = Vieneu()  # default v3 Turbo, 48 kHz; GPU auto-detected
    if args.list_voices:
        for label, vid in tts.list_preset_voices():
            print(f"  - {label} ({vid})")
        return

    script = json.loads((ROOT / "data" / "script.json").read_text(encoding="utf-8"))
    only = [s for s in args.only.split(",") if s]
    vo_dir = ROOT / "assets" / "audio" / "vo"
    vo_dir.mkdir(parents=True, exist_ok=True)

    scenes = [s for s in script["scenes"] if not only or s["id"] in only]
    if not scenes:
        sys.exit(f"no scenes match --only={args.only}")

    for s in scenes:
        out = vo_dir / f"{s['id']}.wav"
        if out.exists() and not args.force:
            print(f"skip vo {s['id']}")
            continue
        text = scene_text(s, args.lang)
        kwargs = {"ref_audio": args.ref_audio} if args.ref_audio else {"voice": args.voice}
        audio = tts.infer(text, **kwargs)
        tts.save(audio, str(out))
        dur = len(audio) / 48000
        print(f"vo {s['id']} -> {out} ({dur:.1f}s, lang={args.lang})")


if __name__ == "__main__":
    main()
