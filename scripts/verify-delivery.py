"""Fail a project whose timeline, captions, resources, stems or social file miss the bar.

Usage:
  python scripts/verify-delivery.py <project>
  python scripts/verify-delivery.py <project> --stems-dir DIR
  python scripts/verify-delivery.py <project> --social renders/slug-social.mp4 --master renders/slug.mp4
  python scripts/verify-delivery.py <project> --report data/delivery-report.json

A skipped artifact is reported and does not fail. An artifact named with a flag,
or a stem pair already on disk, fails the run when it misses the gate.
Portrait compositions also report caption size and bottom inset scaled to a
360 px wide phone. That report does not guess how much of a platform UI covers
the frame.
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

from audio_gates import (
    caption_errors,
    decode_mono,
    evaluate_mix,
    local_refs,
    measure_loudness,
    media_duration,
    social_errors,
    timeline_errors,
    vertical_metrics,
)


def artifact(name, status, detail=""):
    return {"name": name, "status": status, "detail": detail}


def check_stems(timeline, stems_dir, required):
    music = stems_dir / "stem-music.wav"
    voice = stems_dir / "stem-voice.wav"
    if not music.exists() or not voice.exists():
        if required:
            return artifact("stems", "fail", f"missing stems in {stems_dir}")
        return artifact("stems", "skip", "no stem files")
    result = evaluate_mix(decode_mono(music), decode_mono(voice), timeline)
    if result["failures"]:
        return artifact("stems", "fail", "; ".join(result["failures"]))
    return artifact("stems", "pass", f"music sits {result['delta']:.1f} dB under the voice")


def check_resources(root, timeline):
    html_path = root / "index.html"
    problems = []
    if not html_path.exists():
        return artifact("resources", "skip", "no index.html")
    html = html_path.read_text(encoding="utf-8")
    for ref in local_refs(html):
        if not (root / ref).exists():
            problems.append(f"missing {ref}")
    vo_dir = root / "assets" / "audio" / "vo"
    if vo_dir.exists():
        for scene_id in timeline.get("scenes", {}):
            wav = vo_dir / f"{scene_id}.wav"
            if not wav.exists():
                problems.append(f"missing {wav.relative_to(root)}")
    if problems:
        return artifact("resources", "fail", "; ".join(problems))
    return artifact("resources", "pass", "local files exist")


def check_social(social, master):
    if not social.exists():
        return artifact("social", "fail", f"missing {social}")
    integrated, peak = measure_loudness(social)
    duration = media_duration(social)
    master_duration = media_duration(master) if master else None
    errors = social_errors(integrated, peak, duration, master_duration)
    detail = f"{integrated:.1f} LUFS, peak {peak:.1f} dBFS, {duration:.3f}s"
    if errors:
        return artifact("social", "fail", detail + "; " + "; ".join(errors))
    return artifact("social", "pass", detail)


def build_report(root, stems_dir=None, social=None, master=None):
    timeline_path = root / "data" / "timeline.json"
    if not timeline_path.exists():
        return [artifact("timeline", "fail", "missing data/timeline.json")]
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    structure = timeline_errors(timeline)
    captions = caption_errors(timeline)
    artifacts = [
        artifact("timeline", "fail" if structure else "pass", "; ".join(structure)),
        artifact("captions", "fail" if captions else "pass", "; ".join(captions)),
        check_resources(root, timeline),
    ]
    default_stems = Path(tempfile.gettempdir()) / f"{root.name}-mix"
    stems = Path(stems_dir) if stems_dir else default_stems
    artifacts.append(check_stems(timeline, stems, stems_dir is not None))
    if social:
        artifacts.append(check_social(Path(social), Path(master) if master else None))
    else:
        artifacts.append(artifact("social", "skip", "pass --social to measure the delivered file"))
    html_path = root / "index.html"
    if html_path.exists():
        metrics = vertical_metrics(html_path.read_text(encoding="utf-8"))
        if metrics:
            artifacts.append(artifact(
                "vertical-readability",
                "info",
                f"caption {metrics['caption_px_at_360']}px and bottom inset {metrics['bottom_px_at_360']}px at 360px wide",
            ))
    return artifacts


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root")
    ap.add_argument("--stems-dir")
    ap.add_argument("--social")
    ap.add_argument("--master")
    ap.add_argument("--report", help="write the artifact report as JSON")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    artifacts = build_report(root, args.stems_dir, args.social, args.master)
    for item in artifacts:
        print(f"{item['name']:<22} {item['status']:<6} {item['detail']}")
    if args.report:
        report_path = Path(args.report)
        if not report_path.is_absolute():
            report_path = root / report_path
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps({"artifacts": artifacts}, indent=2) + "\n", encoding="utf-8")
        print(f"report {report_path}")
    if any(item["status"] == "fail" for item in artifacts):
        sys.exit(1)


if __name__ == "__main__":
    main()
