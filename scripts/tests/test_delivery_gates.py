"""Regression tests for mix, caption, snapshot and delivery gates.

Run: python -m unittest discover -s scripts/tests
"""
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from audio_gates import (  # noqa: E402
    caption_errors,
    evaluate_mix,
    snapshot_times,
    social_errors,
    vertical_metrics,
)

SR = 8000


def contrast_pair(text_hex, fill_hex):
    def channel(value):
        value = value / 255
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    def luminance(color):
        red, green, blue = (channel(int(color[i : i + 2], 16)) for i in (0, 2, 4))
        return 0.2126 * red + 0.7152 * green + 0.0722 * blue

    dark, light = sorted((luminance(text_hex), luminance(fill_hex)))
    return (light + 0.05) / (dark + 0.05)


def write_wav(path, samples, sr=SR):
    pcm = (np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sr)
        handle.writeframes(pcm.tobytes())


def tone(seconds, amplitude, sr=SR, freq=440):
    times = np.arange(int(seconds * sr)) / sr
    return (amplitude * np.sin(2 * np.pi * freq * times)).astype(np.float32)


def timeline(duration, speech=(0.2, 1.0)):
    return {
        "duration": duration,
        "scenes": {
            "s1": {
                "start": 0,
                "end": duration,
                "lines": [{"on": speech[0], "off": speech[1], "words": [["hello", speech[0], speech[1]]]}],
            }
        },
        "captions": [{"start": speech[0] - 0.1, "end": speech[1] + 0.4, "words": [["xin", speech[0]]]}],
    }


def project(root, data, stems=None):
    (root / "data").mkdir(parents=True)
    (root / "data" / "timeline.json").write_text(json.dumps(data), encoding="utf-8")
    if stems:
        write_wav(root / "stem-music.wav", stems[0])
        write_wav(root / "stem-voice.wav", stems[1])


def run_measure(root, stems):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "measure-mix-balance.py"), str(root), "--stems-dir", str(stems)],
        capture_output=True,
        text=True,
    )


class MixBalanceTest(unittest.TestCase):
    def test_short_music_stem_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "proj"
            speech = (0.1, 0.4)
            project(root, timeline(4, speech), stems=(tone(0.5, 0.112), tone(0.5, 0.2)))
            result = run_measure(root, root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("music stem is", result.stdout)

    def test_silence_after_speech_is_not_cropped_out(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "proj"
            music = np.concatenate([tone(0.4, 0.112), np.zeros(int(3.6 * SR), np.float32)])
            voice = tone(0.5, 0.2)
            project(root, timeline(4, (0.1, 0.4)), stems=(music, voice))
            result = run_measure(root, root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("after the last spoken word", result.stdout)

    def test_music_far_under_voice_fails(self):
        sr = SR
        music = tone(4, 0.112)
        music[int(0.2 * sr) : int(1.0 * sr)] = tone(0.8, 0.00008)
        voice = np.zeros(4 * sr, np.float32)
        voice[int(0.2 * sr) : int(1.0 * sr)] = tone(0.8, 0.2)
        data = timeline(4)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "proj"
            project(root, data, stems=(music, voice))
            result = run_measure(root, root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("under the voice", result.stdout)
            self.assertGreater(float(re.search(r"sits ([\d.]+) dB", result.stdout).group(1)), 10)

    def test_balanced_music_passes(self):
        sr = SR
        music = tone(4, 0.112)
        voice = np.zeros(4 * sr, np.float32)
        voice[int(0.2 * sr) : int(1.0 * sr)] = tone(0.8, 0.2)
        measured = evaluate_mix(music, voice, timeline(4), sr)
        self.assertEqual(measured["failures"], [], measured)
        self.assertAlmostEqual(measured["delta"], 5.0, delta=0.5)


class SnapshotAndCaptionTest(unittest.TestCase):
    def test_snapshot_times_follow_a_short_timeline(self):
        data = {
            "duration": 45,
            "scenes": {
                "s1": {"start": 0, "end": 10, "lines": [{"words": [["hello", 1.25, 1.5]]}]},
                "s2": {"start": 10, "end": 45, "lines": [{"words": [["world", 12.5, 13]]}]},
            },
        }
        times = snapshot_times(data)
        self.assertTrue(all(time < 45 for time in times))
        self.assertNotIn(120, times)
        self.assertNotIn(148, times)
        self.assertIn(1.25, times)
        self.assertIn(12.5, times)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "data" / "timeline.json").write_text(json.dumps(data), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPTS / "snapshot-times.py"), str(root)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("1.25", result.stdout)
            self.assertNotIn("148", result.stdout)

    def test_caption_highlight_outside_the_frame_fails(self):
        errors = caption_errors({
            "scenes": {"s": {"lines": [{"on": 0.2, "off": 1.02}]}},
            "captions": [{"start": 0.2, "end": 1.02, "words": [["mười", 1.11]]}],
        })
        self.assertTrue(any("1.110" in error and "1.020" in error for error in errors), errors)


class DeliveryReportTest(unittest.TestCase):
    def test_bad_caption_fails_and_writes_a_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "proj"
            (root / "data").mkdir(parents=True)
            (root / "data" / "timeline.json").write_text(json.dumps({
                "duration": 4,
                "scenes": {"s1": {"start": 0, "end": 4, "lines": [{"on": 0.2, "off": 1.02, "words": [["one", 0.2, 0.4]]}]}},
                "captions": [{"start": 0.2, "end": 1.02, "words": [["mười", 1.11]]}],
            }), encoding="utf-8")
            report = root / "data" / "delivery-report.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "verify-delivery.py"), str(root), "--report", "data/delivery-report.json"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("captions", result.stdout)
            saved = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(next(item["status"] for item in saved["artifacts"] if item["name"] == "captions"), "fail")

    def test_missing_resource_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "proj"
            (root / "data").mkdir(parents=True)
            (root / "data" / "timeline.json").write_text(json.dumps(timeline(4)), encoding="utf-8")
            (root / "index.html").write_text('<style>@font-face { src: url("assets/fonts/missing.ttf"); }</style>', encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "verify-delivery.py"), str(root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("missing assets/fonts/missing.ttf", result.stdout)

    def test_portrait_size_is_reported_not_guessed(self):
        html = Path(ROOT / "assets/templates/index-skeleton-vertical.html").read_text(encoding="utf-8")
        metrics = vertical_metrics(html)
        self.assertAlmostEqual(metrics["caption_px_at_360"], 13.3, places=1)
        self.assertAlmostEqual(metrics["bottom_px_at_360"], 21.3, places=1)


class SocialLoudnessTest(unittest.TestCase):
    def test_gate_numbers(self):
        self.assertEqual(social_errors(-14.0, -1.5, 8.0, 8.0), [])
        self.assertTrue(social_errors(-30.0, -1.5, 8.0, 8.0))
        self.assertTrue(any("peak" in error for error in social_errors(-14.0, -0.2, 8.0, 8.0)))
        self.assertTrue(any("duration" in error for error in social_errors(-14.0, -1.5, 8.0, 10.0)))

    def test_delivered_aac_is_measured(self):
        from audio_gates import measure_loudness, media_duration

        with tempfile.TemporaryDirectory() as directory:
            hot = Path(directory) / "hot.m4a"
            mastered = Path(directory) / "master.m4a"
            for path, audio_filter in ((hot, "volume=0dB"), (mastered, "loudnorm=I=-14:TP=-1.5:LRA=11")):
                subprocess.run(
                    ["ffmpeg", "-y", "-hide_banner", "-nostats", "-f", "lavfi", "-i", "sine=frequency=440:duration=8",
                     "-af", audio_filter, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(path)],
                    check=True, capture_output=True,
                )
            hot_errors = social_errors(*measure_loudness(hot), media_duration(hot), media_duration(mastered))
            self.assertTrue(hot_errors, hot_errors)
            master_errors = social_errors(*measure_loudness(mastered), media_duration(mastered), media_duration(mastered))
            self.assertEqual(master_errors, [], master_errors)


class ClayContrastTest(unittest.TestCase):
    def test_peach_text_is_ink(self):
        text = (ROOT / "references/style-soft-tactile-clay.md").read_text(encoding="utf-8")
        match = re.search(r"text (#[0-9a-fA-F]{6}) on fill (#[0-9a-fA-F]{6})", text)
        self.assertIsNotNone(match)
        ink, peach = match.group(1)[1:], match.group(2)[1:]
        self.assertEqual(peach.lower(), "ff8a65")
        self.assertNotEqual(ink.lower(), "ffffff")
        self.assertGreaterEqual(contrast_pair(ink, peach), 4.5)
        self.assertLess(contrast_pair("ffffff", peach), 3)
        self.assertNotIn("white on\n`--lav-dk`/`--peach`", text)


class SpokenFallbackTest(unittest.TestCase):
    def test_vieneu_refuses_a_language_change_without_force(self):
        path = ROOT / "assets/templates/scripts/generate-vo-vieneu.py"
        spec = importlib.util.spec_from_file_location("vieneu_vo", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with self.assertRaises(SystemExit):
            module.reconcile_spoken({"lang": "en"}, "vi", True)
        self.assertEqual(module.reconcile_spoken({"lang": "en"}, "vi", False)["lang"], "vi")
        self.assertEqual(module.reconcile_spoken(None, "vi", True)["field"], "vi")
        self.assertTrue(module.keeps_foreign_clips(["s01", "s02"], ["s01"], True))
        self.assertFalse(module.keeps_foreign_clips(["s01", "s02"], ["s01", "s02"], True))
        self.assertTrue(module.keeps_foreign_clips(["s01"], ["s01"], False))
        self.assertFalse(module.keeps_foreign_clips([], ["s01"], False))


class NodePipelineTest(unittest.TestCase):
    def test_node_regressions(self):
        result = subprocess.run(
            ["node", "--test", str(ROOT / "assets/templates/scripts/lib/pipeline.test.mjs")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
