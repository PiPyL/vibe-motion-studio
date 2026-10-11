# Source evidence — 2026-10-11

Baseline: `570248a`, branch `main`. Source kiểm tra lại khi lập kế hoạch; không có sửa implementation. Các đoạn dưới xác minh điểm neo hiện hữu, không chứng minh proposed implementation đã tồn tại.

40 điểm neo / 4 phase; mỗi điểm kiểm tra bằng khớp chuỗi trực tiếp trong source hiện tại.

## Phase 1

| Source | Điểm neo đã xác minh |
|---|---|
| [assets/templates/scripts/generate-audio-assets.mjs:29](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/scripts/generate-audio-assets.mjs:29) | `shell: true` |
| [assets/templates/scripts/align-voiceover.mjs:21](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/scripts/align-voiceover.mjs:21) | `shell: true` |
| [assets/templates/scripts/align-voiceover.mjs:28](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/scripts/align-voiceover.mjs:28) | `line.say &#124;&#124; line.en` |
| [assets/templates/scripts/align-voiceover.mjs:53](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/scripts/align-voiceover.mjs:53) | `words.slice(i, i + n)` |
| [assets/templates/scripts/generate-vo-vieneu.py:57](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/scripts/generate-vo-vieneu.py:57) | `default="vi"` |
| [assets/templates/scripts/build-timeline.mjs:215](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/scripts/build-timeline.mjs:215) | `sidechaincompress=` |
| [assets/templates/scripts/build-timeline.mjs:247](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/scripts/build-timeline.mjs:247) | `pcm_s16le` |
| [assets/templates/scripts/build-timeline.mjs:123](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/scripts/build-timeline.mjs:123) | `const MAX_CHUNK` |
| [assets/templates/index-skeleton.html:84](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/index-skeleton.html:84) | `h.textContent.trim()` |
| [references/style-soft-tactile-clay.md:18](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/references/style-soft-tactile-clay.md:18) | `--peach: #ff8a65` |

## Phase 2

| Source | Điểm neo đã xác minh |
|---|---|
| [scripts/measure-mix-balance.py:47](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/scripts/measure-mix-balance.py:47) | `n = min(len(m), len(v))` |
| [scripts/measure-mix-balance.py:1](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/scripts/measure-mix-balance.py:1) | `music sits` |
| [scripts/verify-arrangement.py:29](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/scripts/verify-arrangement.py:29) | `span=2.0` |
| [scripts/verify-arrangement.py:54](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/scripts/verify-arrangement.py:54) | `sys.exit(1 if bad else 0)` |
| [scripts/fit-beat-grid.py:39](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/scripts/fit-beat-grid.py:39) | `def fit_grid` |
| [assets/templates/scripts/build-timeline.mjs:19](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/scripts/build-timeline.mjs:19) | `const noAudio` |
| [assets/templates/scripts/build-timeline.mjs:298](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/scripts/build-timeline.mjs:298) | `TIMING:BEGIN` |
| [references/production-pipeline.md:105](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/references/production-pipeline.md:105) | `snapshot --at` |
| [references/production-pipeline.md:132](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/references/production-pipeline.md:132) | `-c:a aac` |
| [SKILL.md:86](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/SKILL.md:86) | `ebur128` |

## Phase 3

| Source | Điểm neo đã xác minh |
|---|---|
| [SKILL.md:55](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/SKILL.md:55) | `Pin the outcome` |
| [references/production-pipeline.md:29](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/references/production-pipeline.md:29) | `Collect facts only` |
| [references/composition-contract.md:43](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/references/composition-contract.md:43) | `## Helpers` |
| [references/composition-contract.md:20](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/references/composition-contract.md:20) | `## Determinism` |
| [assets/templates/index-skeleton-vertical.html:29](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/index-skeleton-vertical.html:29) | `bottom: 64px` |
| [references/style-glass-keynote.md:69](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/references/style-glass-keynote.md:69) | `## Vertical` |
| [references/style-comic-spiderverse.md:83](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/references/style-comic-spiderverse.md:83) | `## Vertical` |
| [references/style-cyberpunk-hud.md:65](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/references/style-cyberpunk-hud.md:65) | `## Scene choreography` |
| [references/style-swiss-editorial.md:93](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/references/style-swiss-editorial.md:93) | `## Scene choreography` |
| [references/style-soft-tactile-clay.md:96](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/references/style-soft-tactile-clay.md:96) | `## Scene choreography` |

## Phase 4

| Source | Điểm neo đã xác minh |
|---|---|
| [scripts/tests/test_audio_tools.py:49](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/scripts/tests/test_audio_tools.py:49) | `def test_recovers_tempo_and_phase` |
| [scripts/tests/test_audio_tools.py:81](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/scripts/tests/test_audio_tools.py:81) | `def test_aligned_splice_passes` |
| [scripts/tests/test_audio_tools.py:86](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/scripts/tests/test_audio_tools.py:86) | `def test_drifted_splice_fails` |
| [README.md:28](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/README.md:28) | `## Install` |
| [SKILL.md:10](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/SKILL.md:10) | `version: "1.1.0"` |
| [assets/templates/scripts/build-timeline.mjs:39](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/scripts/build-timeline.mjs:39) | `const DURATION = 151` |
| [assets/templates/data/script.example.json:5](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/data/script.example.json:5) | `gemini-3.8-flash-tts` |
| [references/production-pipeline.md:103](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/references/production-pipeline.md:103) | `hyperframes@0.7.99` |
| [assets/templates/index-skeleton.html:13](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/assets/templates/index-skeleton.html:13) | `gsap@3.14.2` |
| [SKILL.md:48](/Users/mac/Desktop/AutoWork-Project/vibe-motion-studio/SKILL.md:48) | `Generative text-to-video footage` |

## Bằng chứng chạy từ lượt review ngay trước kế hoạch

- 3/3 unittest pass; 4 script MJS qua `node --check`. Source không đổi nên không chạy lại chỉ để lập kế hoạch.
- Full mix fixture 151s: music stem 2.333250s; silence từ 2.564729s tới151s; build exit0. Audio tổng hợp dùng chứng minh lifecycle, không đại diện chất lượng giọng AI.
- Stub multix ghi argv: `Costs $29. Say $(printf altered).` thành `Costs 9. Say altered.`; không gọi provider.
- VI alignment8tokens / EN4tokens: map mất `Hẹn gặp lại nhé`, chỉ warning, exit0.
- Caption fixture: chunk end1.020s nhưng last-word onset1.110s; exit0 không warning.
- Balance fixture: music thấp hơnvoice67.4dB; measurement exit0.
- DOM offline: `<em>`/pill bị xóa, `<br>` làm `workflowsfor`; white/peach contrast2.314:1.
- Premix PCM16 clipping: nguy cơ từ source, chưa có full-pipeline repro; kế hoạch phải xác minh trước khi tuyên bố đã xảy ra.
- Chưa có benchmark video hoàn chỉnh, chưa gọi TTS/music/align thật trong lượt review.

## Dependency evidence

- [Google Gemini TTS](https://ai.google.dev/gemini-api/docs/speech-generation): đọc ở lượt review 2026-10-11, có `gemini-3.8-flash-tts`. Phải tra lại docs chính thức trước khi implement thay đổi Google AI.
- Local multix0.7.0 `generate-speech --help` hỗ trợ model/style/text/voice/output; help không chứng minh paid API hoạt động.
- HyperFrames0.7.99 và GSAP3.14.2 là pin trong source; chưa chạy full render trong review.
- Bản repo và `/Users/mac/.agents/skills/vibe-motion-studio/` có khác README/skeleton/style/contract/prompts nhưng cùng SKILL1.1.0; không tự cập nhật bản installed.
