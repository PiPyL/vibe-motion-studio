"""Print snapshot times from data/timeline.json.

One time just after each scene cut, one just before the next cut, every word
anchor, and a frame near the end. The list stays inside the timeline, so a
30–60 s video is not sampled at 120 s or 148 s.

Usage: python scripts/snapshot-times.py <project dir>
"""
import json
import sys
from pathlib import Path

from audio_gates import snapshot_times


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    timeline = json.loads((root / "data" / "timeline.json").read_text(encoding="utf-8"))
    print(",".join(f"{time:.2f}" for time in snapshot_times(timeline)))


if __name__ == "__main__":
    main()
