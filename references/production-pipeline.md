# Production pipeline

The end-to-end flow that produced both reference videos. Each step feeds a file
to the next, so run them in this order. Paths are relative to the project dir
(e.g. `assets/videos/<slug>/`) and written `./scripts/...` for the project's
copies; `<skill>` is this skill's directory.

## 0. Scaffold

```text
<project>/
  index.html                 composition (start from <skill>/assets/templates/index-skeleton.html)
  hyperframes.json           copy <skill>/assets/templates/hyperframes.json
  data/                      script.json, sfx.json, cues.json, music-plan.json, outro-plan.json, music-arrangement.json
   scripts/                   copy <skill>/assets/templates/scripts/ (the .mjs files, generate-vo-vieneu.py, and lib/)
                        and <skill>/scripts/fit-beat-grid.py
  assets/fonts/              local TTF files (OFL/Apache fonts from Google Fonts)
  assets/images/             baked texture tiles (PNG)
  assets/audio/{vo,sfx,music}/
  renders/
```

Start the data files from `<skill>/assets/templates/data/*.example.json`.
Keep one project per video; a restyle of an existing video is a new project dir
so the first edition stays untouched.

## 1. Facts and script

- Collect facts only from primary sources (release notes, repo docs, code). Every
  on-screen label must trace to one; write the evidence into a short report
  under `plans/reports/` before scripting.
- `data/script.json`: `voice` (model, voice, style, `spokenLang`), `outroStyle`,
  `scenes[]`. `spokenLang` is `en` or `vi`. English is the default: Gemini reads
  `say` or `en`, and `vi` is the caption. Vietnamese VO, including the VieNeu
  fallback, reads `vi` and that text is the transcript for alignment, captions
  and word anchors. Each scene has `id` (`sNN-slug`, used as the VO file name
  and the timing key), optional `outro: true`, and `lines[]` with `en`,
  optional `say` (pronunciation, e.g. "three point thirty-four"), and `vi`.
  Keep one idea per line: lines are the unit of placement.
- Budget: ~150 words of VO per minute at TEMPO 1.08. The references are 144 s and
  151 s with 16 scenes (cover, stats, 12 features, stability, outro).

## 2. Generate audio (multix)

```bash
node ./scripts/generate-audio-assets.mjs vo      # Gemini TTS, one WAV per scene
node ./scripts/generate-audio-assets.mjs sfx     # ElevenLabs SFX from data/sfx.json
node ./scripts/generate-audio-assets.mjs music   # ElevenLabs Music from music-plan.json + outro-plan.json
```

Quota exhausted (Gemini/ElevenLabs)? Fall back to on-device VieNeu-TTS for VO
only (details in `audio-and-beat-sync.md`):

```bash
python ./scripts/generate-vo-vieneu.py --voice "Hải Đăng"   # copy from <skill>/assets/templates/scripts/
```

`--force` regenerates, `--only=id1,id2` limits to some scenes/SFX. The script runs
multix in a temp dir because multix drops copies into `./multix-output`.
Spoken text is an argument array, not a shell command, so a price like `$29`
is read aloud instead of being expanded. Credentials come from multix's own
config; never print or copy key values. Voice generation writes
`data/vo-spoken.json`. Alignment and the timeline read that file. Reusing
WAVs from the other language fails until `--force` regenerates every existing
clip. `--only` does not leave the other scenes on the old language.
Music details, the arrangement and the mix are in `audio-and-beat-sync.md`.

## 3. Align the voice

```bash
node ./scripts/align-voiceover.mjs        # ElevenLabs forced alignment -> data/vo-lines.json
```

The mapper uses the language in `data/vo-spoken.json` (otherwise
`voice.spokenLang`, otherwise `en`). A token mismatch exits 1 and does not
write `vo-lines.json`. That used to be a warning, and the mix then cut the
WAV with the short timestamps, so speech after the last mapped word was lost.
Fix the transcript or re-generate the scene and re-align with `--force`.
Do not continue past a non-zero exit.

## 4. Beat grid and music arrangement

```bash
python ./scripts/fit-beat-grid.py ./assets/audio/music/bgm-raw.mp3 --min-bpm 100 --max-bpm 130
# edit data/music-arrangement.json (bpm, beat0, segments) from the bar table
node ./scripts/arrange-music.mjs          # -> ./assets/audio/music/bgm.flac
python <skill>/scripts/verify-arrangement.py .   # every segment lag within +-2 ms
```

## 5. Timeline and mix

Edit the `EDIT` block of `./scripts/build-timeline.mjs` (KICK ranges, DROPS,
OUTRO_BED, DURATION, ANCHORS), then:

```bash
node ./scripts/build-timeline.mjs --dry       # schedule only: scene starts (with beat numbers) and line spans
node ./scripts/build-timeline.mjs             # + captions, SFX cues, audio mix, voice envelope, TIMING injection
node ./scripts/build-timeline.mjs --no-audio  # timing only (keeps the existing mix and envelope)
node ./scripts/build-timeline.mjs --stems     # also writes stems for the balance check
python <skill>/scripts/measure-mix-balance.py .
python <skill>/scripts/verify-delivery.py .
```

`measure-mix-balance.py` exits 1 when the music stem is short, silent after
the last spoken word, more than 10 dB under the voice, or louder than the
voice. The target is still about 4–6 dB under speech. `verify-delivery.py`
also fails when a caption highlight sits outside its frame. Both look for
stems in the directory `build-timeline.mjs --stems` prints (`stems -> ...`,
`<temp>/<project name>-mix`). Pass `--stems-dir` with that path if the
project folder name is not the temp folder's prefix.

Read every warning: `clips the previous voice`, `overlaps previous line`,
`voice runs past its scene end`, `cue: "word" #n not found`. Each one is a
visible or audible defect. A cue word has to be in the spoken transcript:
English words when `spokenLang` is `en`, Vietnamese words when it is `vi`.

## 6. Composition

Author `index.html` against `composition-contract.md` and one style reference.
Choreograph each scene with `W(sid, "word")` so reveals land on the spoken word.

## 7. Validate

```bash
npx --yes hyperframes@0.7.99 lint
npx --yes hyperframes@0.7.99 check
AT=$(python <skill>/scripts/snapshot-times.py .)
npx --yes hyperframes@0.7.99 snapshot --at "$AT" --describe false
```

`check` flags overlaps and contrast; use `data-layout-allow-overlap` only on
intentional overlaps (stacked cards, mascots over panels). Snapshots are large
PNGs: downscale to JPEG before viewing them if the tool context is limited.
The times come from this timeline: just after each cut, just before the next
cut, and on each word anchor. A 30–60 s video is not sampled at 120 s or 148 s.
Look at every scene's busiest moment and the caption band, then play the full
render and judge pace, pronunciation and the ending. Snapshots do not replace
that playback.

## 8. Render, restore the mix, verify

```bash
npx --yes hyperframes@0.7.99 render -q high -f 30 --strict -o renders/<slug>.mp4
ffmpeg -y -i renders/<slug>.mp4 -i ./assets/audio/mix.m4a -map 0:v:0 -map 1:a:0 -c copy -movflags +faststart renders/out.mp4
# replace renders/<slug>.mp4 with renders/out.mp4
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate,channels -show_entries format=duration renders/<slug>.mp4
ffmpeg -i renders/<slug>.mp4 -af ebur128=peak=true -f null -          # ~ -14 LUFS, peak <= -1 dBFS
ffmpeg -i renders/<slug>.mp4 -vf blackdetect=d=0.1:pix_th=0.05 -an -f null -   # no black segments except the fades
```

The remux matters: the renderer re-encodes AAC and pushed the true peak to
0.0 dBFS in the first edition; copying the untouched `mix.m4a` keeps −14 LUFS /
−1.5 dBTP.

## 9. Social encode

```bash
ffmpeg -y -i renders/<slug>.mp4 -c:v libx264 -preset slow -crf 21 -maxrate 6M -bufsize 12M \
  -pix_fmt yuv420p -profile:v high -level 4.1 -g 60 -c:a copy \
  -movflags +faststart renders/<slug>-social.mp4
python <skill>/scripts/verify-delivery.py . --social renders/<slug>-social.mp4 --master renders/<slug>.mp4
```

Copy the audio. Re-encoding AAC here pushed a mastered file off its true-peak
target, and a measurement taken before this step does not describe the file
you deliver. `verify-delivery.py` measures the social file itself and exits 1
when loudness is outside about −14 LUFS (−16 to −12), true peak is above
−1 dBFS, or the duration does not match the master.

Result on the comic edition: 406 MB → 101.6 MB, SSIM 0.977. Check with
`ffmpeg -i social.mp4 -i master.mp4 -lavfi ssim -f null -` when quality matters.
SSIM scores the picture only.

## 9b. Vertical edition (9:16)

A vertical video is a separate project dir starting from
`<skill>/assets/templates/index-skeleton-vertical.html` plus the style
reference's `## Vertical` section. Steps 1–7 are identical (same audio, TIMING
and mix); only composition, render and verify differ:

```bash
npx --yes hyperframes@0.7.99 render -q high -f 30 --strict -o renders/<slug>-vertical.mp4
ffmpeg -y -i renders/<slug>-vertical.mp4 -i ./assets/audio/mix.m4a -map 0:v:0 -map 1:a:0 -c copy -movflags +faststart renders/out-vertical.mp4
# replace renders/<slug>-vertical.mp4 with renders/out-vertical.mp4
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate,channels -show_entries format=duration renders/<slug>-vertical.mp4
# expect width=1080 height=1920; same ebur128 (~-14 LUFS, peak <= -1 dBFS) and blackdetect gates
ffmpeg -y -i renders/<slug>-vertical.mp4 -c:v libx264 -preset slow -crf 21 -maxrate 6M -bufsize 12M \
  -pix_fmt yuv420p -profile:v high -level 4.1 -g 60 -c:a copy \
  -movflags +faststart renders/<slug>-vertical-social.mp4
python <skill>/scripts/verify-delivery.py . --social renders/<slug>-vertical-social.mp4 --master renders/<slug>-vertical.mp4
```

The portrait report includes caption size and bottom inset scaled to a 360 px
wide phone. Read it. It does not say how much of a platform's controls cover
the frame; check that against the actual post UI.

## 10. Studio preview

```bash
npx --yes hyperframes@0.7.99 preview --port 3002 --no-open .
```

Run it as a tracked background process, reuse it if the port is already held
by this project, and stop it when the session ends.

## Rebuild cheatsheet

| Changed | Re-run |
|---|---|
| Script text, same spoken language | `generate-audio-assets vo --only=<id> --force` (or `generate-vo-vieneu.py --only=<id> --force` on fallback) → `align-voiceover --force` → `build-timeline` |
| Spoken language | Regenerate every existing clip with `--force` (no leftover `--only` scenes), retarget cue words and `W()` calls, then `align-voiceover --force` → `build-timeline` |
| Music track | `fit-beat-grid` → edit arrangement → `arrange-music` → `verify-arrangement` → `build-timeline` |
| Anchors / cues | `build-timeline` (audio changes) or `--no-audio` (captions/timing only) |
| Visuals only | `lint` → `check` → `render` → remux |
