// Forced-aligns every voice-over clip against its spoken text (ElevenLabs align via multix)
// and writes data/vo-lines.json: per scene, per line start/end in clip-local seconds.
// Usage: node scripts/align-voiceover.mjs [--force]
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import os from "node:os";
import { spawnArgv } from "./lib/spawn-argv.mjs";
import { lineSpoken, mapAlignmentToLines } from "./lib/spoken.mjs";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const script = JSON.parse(readFileSync(join(root, "data/script.json"), "utf8"));
const force = process.argv.includes("--force");
const alignDir = join(root, "data/align");
const workDir = join(os.tmpdir(), `${basename(root)}-multix`);
mkdirSync(alignDir, { recursive: true });
mkdirSync(workDir, { recursive: true });

const run = (argv) => spawnArgv("multix", argv, { cwd: workDir });

function spokenLang() {
  const sidecar = join(root, "data/vo-spoken.json");
  if (existsSync(sidecar)) return JSON.parse(readFileSync(sidecar, "utf8")).lang;
  return script.voice?.spokenLang || "en";
}

const lang = spokenLang();
console.log(`align language: ${lang}`);

const queue = [...script.scenes];
await Promise.all(
  Array.from({ length: 4 }, async () => {
    while (queue.length) {
      const s = queue.shift();
      const out = join(alignDir, `${s.id}.json`);
      if (existsSync(out) && !force) continue;
      const text = s.lines.map((line) => lineSpoken(line, lang)).join(" ");
      await run(["elevenlabs", "align", "--input", join(root, `assets/audio/vo/${s.id}.wav`), "--text", text, "--output", out]);
      console.log(`aligned ${s.id}`);
    }
  }),
);

// Map aligned words back onto the same transcript that was spoken.
const result = {};
const errors = [];
for (const s of script.scenes) {
  try {
    const align = JSON.parse(readFileSync(join(alignDir, `${s.id}.json`), "utf8"));
    const lines = mapAlignmentToLines(s.lines, align.words, lang);
    result[s.id] = { speechStart: lines[0].start, speechEnd: lines[lines.length - 1].end, lines };
  } catch (err) {
    errors.push(`${s.id}: ${err.message}`);
  }
}
if (errors.length) {
  for (const error of errors) console.error(error);
  process.exit(1);
}
writeFileSync(join(root, "data/vo-lines.json"), JSON.stringify(result, null, 1));
for (const [id, v] of Object.entries(result)) console.log(id, v.speechStart.toFixed(2), v.speechEnd.toFixed(2), v.lines.map((l) => `${l.start.toFixed(2)}-${l.end.toFixed(2)}`).join(" | "));
