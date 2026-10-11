"""Measure how loud the ducked music sits under the voice-over and in the gaps.

Usage: python scripts/measure-mix-balance.py <project dir> [--stems-dir DIR] [--body START END]
Needs the stems written by `node scripts/build-timeline.mjs --stems`
(stem-music.wav and stem-voice.wav) and data/timeline.json.

Exits 1 when the music is more than 10 dB under the voice, louder than the
voice, shorter than the timeline, or silent after the last spoken word.
The target is still about 4–6 dB under speech. Both stems are measured on the
full timeline; a short music stem counts as silence instead of being cropped
away.
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

from audio_gates import SR, decode_mono, evaluate_mix


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root")
    ap.add_argument("--stems-dir", help="defaults to <temp>/<project name>-mix")
    ap.add_argument("--body", nargs=2, type=float, metavar=("START", "END"),
                    help="seconds to measure (default: the whole timeline)")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    stems = Path(args.stems_dir) if args.stems_dir else Path(tempfile.gettempdir()) / f"{root.name}-mix"
    timeline = json.loads((root / "data/timeline.json").read_text(encoding="utf8"))
    music = decode_mono(stems / "stem-music.wav", SR)
    voice = decode_mono(stems / "stem-voice.wav", SR)
    result = evaluate_mix(music, voice, timeline, SR, tuple(args.body) if args.body else None)
    print(
        f"music under speech {result['under']:.1f} dB | "
        f"music in gaps {result['gaps']:.1f} dB | voice {result['voice']:.1f} dB"
    )
    print(
        f"music sits {result['delta']:.1f} dB under the voice; "
        f"gaps are {100 * result['gap_ratio']:.0f}% of the body"
    )
    for failure in result["failures"]:
        print(f"FAIL {failure}")
    if result["failures"]:
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
