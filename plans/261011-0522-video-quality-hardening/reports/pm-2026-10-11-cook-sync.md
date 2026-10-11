# Cook sync — video quality hardening

Status: in-progress. Checkbox progress stays 0/16 because the phase files are still the empty template (Requirement A/B, Task A/B). Those items do not describe the review, so none were checked.

Delivered in the repo, unmapped to a phase checkbox:

- Sidechain voice bus padded to the timeline before `sidechaincompress`.
- TTS and alignment spawn an argument array with the shell off.
- One spoken transcript (`data/vo-spoken.json`). A language change must regenerate every existing clip. Token mismatch exits 1 before `vo-lines.json`.
- Caption highlights stay inside the caption frame or the build fails. Headlines keep emphasis and line breaks. Clay body text is `#242b35` on `#ff8a65`.
- Mix, caption, resource and social gates exit 1. Snapshot times come from the timeline. Social encode copies the mastered audio and the delivered file is measured.

Not started: brief → storyboard → sample frames → animatic, and the benchmark video set. The installed skill at `~/.agents/skills/vibe-motion-studio/` was not updated. No commit.

Verification: `python3 -m unittest discover -s scripts/tests` — 17 tests OK.
