"""Checks that turn a finished motion-graphic project into a pass or a failure.

The mix measurement used to print a number and exit 0. A music stem that ends
with the voice, a highlight outside its caption, or a social file past the
loudness target now fails the process.
"""
import re
import subprocess

import numpy as np

SR = 8000
TAIL_SILENCE_DB = -45.0
TAIL_MIN_SECONDS = 0.75
MUSIC_SHORT_TOLERANCE = 0.25
MAX_UNDER_DB = 10.0
MIN_UNDER_DB = -1.0
LUFS_MIN = -16.0
LUFS_MAX = -12.0
PEAK_MAX = -1.0
DURATION_TOLERANCE = 0.15


def db(samples):
    if len(samples) == 0:
        return float("-inf")
    return float(10 * np.log10(np.mean(np.asarray(samples) ** 2) + 1e-12))


def pad(samples, count):
    samples = np.asarray(samples, dtype=np.float32)
    if len(samples) >= count:
        return samples[:count]
    out = np.zeros(count, np.float32)
    out[: len(samples)] = samples
    return out


def decode_mono(path, sample_rate=SR):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sample_rate), "-f", "f32le", "-"],
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def spoken_spans(timeline):
    return [
        (float(line["on"]), float(line["off"]))
        for scene in timeline.get("scenes", {}).values()
        for line in scene.get("lines", [])
    ]


def evaluate_mix(music, voice, timeline, sample_rate=SR, body=None):
    """Measure music against voice. Do not crop both stems to the shorter one.

    A short music stem is silence for the rest of the timeline, which is how a
    sidechain that ends with the voice used to hide under a padded mix file.
    """
    duration = float(timeline["duration"])
    spans = spoken_spans(timeline)
    music_duration = len(music) / sample_rate
    failures = []
    if music_duration + MUSIC_SHORT_TOLERANCE < duration:
        failures.append(f"music stem is {music_duration:.3f}s but the timeline is {duration:.3f}s")

    count = max(1, int(round(duration * sample_rate)))
    music_full = pad(music, count)
    voice_full = pad(voice, count)
    speech = np.zeros(count, bool)
    for start, end in spans:
        left = max(0, int(start * sample_rate))
        right = min(count, int(end * sample_rate))
        if right > left:
            speech[left:right] = True

    window_start, window_end = body if body else (0.0, duration)
    window = np.zeros(count, bool)
    window[max(0, int(window_start * sample_rate)) : min(count, int(window_end * sample_rate))] = True
    speech_body = speech & window
    if not np.any(speech_body):
        failures.append("no spoken audio inside the measured window")
        under = gaps = voice_level = float("-inf")
        delta = float("inf")
    else:
        under = db(music_full[speech_body])
        gap_mask = window & ~speech
        gaps = db(music_full[gap_mask]) if np.any(gap_mask) else float("-inf")
        voice_level = db(voice_full[speech_body])
        delta = voice_level - under
        if delta > MAX_UNDER_DB:
            failures.append(f"music sits {delta:.1f} dB under the voice (limit {MAX_UNDER_DB:.0f} dB)")
        if delta < MIN_UNDER_DB:
            failures.append(f"music is {-delta:.1f} dB louder than the voice")

    if spans:
        speech_end = max(end for _, end in spans)
        tail = duration - speech_end
        if tail > TAIL_MIN_SECONDS:
            tail_db = db(music_full[min(count, int(speech_end * sample_rate)) :])
            if tail_db < TAIL_SILENCE_DB:
                failures.append(
                    f"music after the last spoken word is {tail_db:.1f} dB (silence) for {tail:.2f}s"
                )

    gap_ratio = float(np.mean(~speech[window])) if np.any(window) else 0.0
    return {
        "under": under,
        "gaps": gaps,
        "voice": voice_level,
        "delta": delta,
        "gap_ratio": gap_ratio,
        "music_duration": music_duration,
        "failures": failures,
    }


def caption_errors(timeline):
    errors = []
    captions = timeline.get("captions") or []
    if spoken_spans(timeline) and not captions:
        errors.append("timeline has spoken lines but no captions")
    for index, caption in enumerate(captions):
        start, end = float(caption["start"]), float(caption["end"])
        if end <= start:
            errors.append(f"caption {index} ends at {end:.3f}s before it starts")
            continue
        for word in caption.get("words", []):
            text, onset = word[0], float(word[1])
            if onset < start - 0.02 or onset >= end:
                errors.append(
                    f'caption {index} word "{text}" at {onset:.3f}s outside [{start:.3f}, {end:.3f})'
                )
    return errors


def timeline_errors(timeline):
    errors = []
    duration = timeline.get("duration")
    if not isinstance(duration, (int, float)) or duration <= 0:
        return ["timeline duration is missing"]
    scenes = list(timeline.get("scenes", {}).values())
    if not scenes:
        errors.append("timeline has no scenes")
    for scene in scenes:
        if float(scene["end"]) <= float(scene["start"]):
            errors.append(f"scene {scene.get('start')} ends before it starts")
    return errors


def snapshot_times(timeline):
    """Sample just after each cut, just before the next cut, and on word anchors."""
    duration = float(timeline["duration"])
    times = set()
    for scene in timeline.get("scenes", {}).values():
        start, end = float(scene["start"]), float(scene["end"])
        times.add(round(min(duration - 0.05, max(0.05, start + 0.2)), 2))
        if end - start > 0.5:
            times.add(round(max(0.05, end - 0.15), 2))
        for line in scene.get("lines", []):
            for word in line.get("words", []):
                times.add(round(float(word[1]), 2))
    times.add(round(min(duration - 0.05, max(0.1, duration - 1.0)), 2))
    return sorted(time for time in times if 0 < time < duration)


def social_errors(integrated, peak, duration, master_duration=None):
    errors = []
    if not LUFS_MIN <= integrated <= LUFS_MAX:
        errors.append(f"social loudness {integrated:.1f} LUFS is outside {LUFS_MIN:.0f} to {LUFS_MAX:.0f}")
    if peak > PEAK_MAX:
        errors.append(f"social true peak {peak:.1f} dBFS is above {PEAK_MAX:.1f} dBFS")
    if master_duration is not None and abs(duration - master_duration) > DURATION_TOLERANCE:
        errors.append(f"social duration {duration:.3f}s differs from master {master_duration:.3f}s")
    return errors


def measure_loudness(path):
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    summary = proc.stderr[proc.stderr.rfind("Summary") :]
    integrated = re.search(r"I:\s+(-?[\d.]+) LUFS", summary)
    peak = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summary)
    if not integrated or not peak:
        raise RuntimeError(f"ebur128 failed for {path}:\n{proc.stderr[-500:]}")
    return float(integrated.group(1)), float(peak.group(1))


def media_duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        text=True,
    )
    return float(out.strip())


def local_refs(html):
    refs = []
    for match in re.finditer(r"""(?:url\(\s*['"]?|src=")([^"')\s]+)""", html, re.I):
        url = match.group(1).strip()
        if url.startswith(("http://", "https://", "data:", "#", "//")):
            continue
        refs.append(url.split("?")[0])
    return refs


def vertical_metrics(html):
    portrait = 'data-resolution="portrait"' in html or 'height="1920"' in html
    if not portrait:
        return None
    width_match = re.search(r'data-width="(\d+)"', html)
    width = int(width_match.group(1)) if width_match else 1080
    font_match = re.search(r"\.cap-box\s*\{[^}]*font:[^;]*?(\d+)px", html)
    bottom_match = re.search(r"\.cap\s*\{[^}]*bottom:\s*(\d+)px", html)
    font = int(font_match.group(1)) if font_match else 40
    bottom = int(bottom_match.group(1)) if bottom_match else 64
    scale = 360 / width
    return {
        "caption_px_at_360": round(font * scale, 1),
        "bottom_px_at_360": round(bottom * scale, 1),
        "frame_width": width,
    }
