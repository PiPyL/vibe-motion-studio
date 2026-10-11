#!/usr/bin/env python3
"""Fallback voice-over generator with VieNeu-TTS (on-device Vietnamese TTS).

Use when Gemini / ElevenLabs quotas are exhausted. Produces the same
per-scene WAV filenames as `generate-audio-assets.mjs vo`. Alignment,
captions and word anchors follow data/vo-spoken.json.

Language comes from --lang, otherwise voice.spokenLang, otherwise `vi`.
Vietnamese is VieNeu's strength; v3 Turbo is bilingual but English comes out
with a Vietnamese accent. The chosen language is written to data/vo-spoken.json
so alignment uses the same transcript.

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
- Writes data/vo-spoken.json. Alignment, captions and word anchors follow
  that language. Vietnamese VO means cues and W() calls must use the
  Vietnamese words. Keep `en`/`say` fields untouched for a later English re-voice.
- Reusing existing WAVs from another language exits until `--force` regenerates every existing clip. `--only` cannot leave the other scenes on the old language.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # project dir (scripts/..)


def spoken_record(lang):
    if lang not in ("en", "vi"):
        sys.exit(f"spoken lang must be en or vi, got {lang}")
    return {"lang": lang, "field": "vi" if lang == "vi" else "say-or-en"}


def reconcile_spoken(previous, lang, kept_existing):
    if previous and previous.get("lang") and previous["lang"] != lang and kept_existing:
        sys.exit(
            f"existing voice-over is {previous['lang']} but this run is {lang}. "
            "Re-run with --force and regenerate every existing clip so speech and alignment use one transcript."
        )
    return spoken_record(lang)


def keeps_foreign_clips(existing_ids, selected_ids, force):
    selected = set(selected_ids)
    return any(not (force and clip_id in selected) for clip_id in existing_ids)


def scene_text(scene, lang):
    if lang == "vi":
        missing = [i for i, line in enumerate(scene["lines"]) if not line.get("vi")]
        if missing:
            sys.exit(f"scene {scene['id']} lines {missing} have no `vi` text (required for --lang vi)")
        return " ".join(line["vi"] for line in scene["lines"])
    missing = [i for i, line in enumerate(scene["lines"]) if not (line.get("say") or line.get("en"))]
    if missing:
        sys.exit(f"scene {scene['id']} lines {missing} have no `say` or `en` text")
    return " ".join(line.get("say") or line["en"] for line in scene["lines"])


def main():
    ap = argparse.ArgumentParser(description="VieNeu-TTS fallback VO generator")
    ap.add_argument("--voice", default="Hải Đăng", help="preset voice name")
    ap.add_argument("--lang", default=None, choices=["vi", "en"],
                    help="vi = read `vi` lines, en = read `say||en`. Default: voice.spokenLang, else vi")
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
    lang = args.lang or script.get("voice", {}).get("spokenLang") or "vi"
    only = [s for s in args.only.split(",") if s]
    vo_dir = ROOT / "assets" / "audio" / "vo"
    vo_dir.mkdir(parents=True, exist_ok=True)
    (ROOT / "data").mkdir(parents=True, exist_ok=True)

    scenes = [s for s in script["scenes"] if not only or s["id"] in only]
    if not scenes:
        sys.exit(f"no scenes match --only={args.only}")

    sidecar = ROOT / "data" / "vo-spoken.json"
    previous = json.loads(sidecar.read_text(encoding="utf-8")) if sidecar.exists() else None
    existing_ids = [s["id"] for s in script["scenes"] if (vo_dir / f"{s['id']}.wav").exists()]
    kept = keeps_foreign_clips(existing_ids, [s["id"] for s in scenes], args.force)
    record = reconcile_spoken(previous, lang, kept)
    sidecar.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    for s in scenes:
        out = vo_dir / f"{s['id']}.wav"
        if out.exists() and not args.force:
            print(f"skip vo {s['id']}")
            continue
        text = scene_text(s, lang)
        kwargs = {"ref_audio": args.ref_audio} if args.ref_audio else {"voice": args.voice}
        audio = tts.infer(text, **kwargs)
        tts.save(audio, str(out))
        dur = len(audio) / 48000
        print(f"vo {s['id']} -> {out} ({dur:.1f}s, lang={lang})")


if __name__ == "__main__":
    main()
