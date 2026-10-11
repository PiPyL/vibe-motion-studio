import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { buildCaptions } from "./captions.mjs";
import { wrapHeadlineWords } from "./headline-words.mjs";
import { duckedMusicFilters } from "./mix-graph.mjs";
import { spawnArgv } from "./spawn-argv.mjs";
import { assertSpokenReuse, keepsForeignClips, mapAlignmentToLines } from "./spoken.mjs";

const root = new URL("../../../../", import.meta.url);
const read = (path) => readFileSync(new URL(path, root), "utf8");

test("multix arguments are not expanded by a shell", async () => {
  const dir = mkdtempSync(join(tmpdir(), "vibe-argv-"));
  const stub = join(dir, "stub.mjs");
  writeFileSync(stub, "process.stdout.write(JSON.stringify(process.argv.slice(2)));\n");
  const text = "Costs $29. Say $(printf altered).";
  const log = await spawnArgv(process.execPath, [stub, text]);
  assert.deepEqual(JSON.parse(log), [text]);
});

test("spawnArgv refuses a shell", async () => {
  let seen;
  const fake = (command, argv, options) => {
    seen = { command, argv, options };
    return {
      stdout: { on() {} },
      stderr: { on() {} },
      on(event, callback) {
        if (event === "close") callback(0);
      },
    };
  };
  await spawnArgv("multix", ["gemini", "generate-speech", "--text", "Costs $29"], { spawnImpl: fake });
  assert.equal(seen.options.shell, false);
  assert.equal(seen.argv.at(-1), "Costs $29");
});

test("voice scripts do not pass spoken text through a shell", () => {
  for (const file of ["assets/templates/scripts/generate-audio-assets.mjs", "assets/templates/scripts/align-voiceover.mjs"]) {
    const source = read(file);
    assert.doesNotMatch(source, /shell:\s*true/);
    assert.match(source, /spawnArgv/);
  }
  const timeline = read("assets/templates/scripts/build-timeline.mjs");
  assert.match(timeline, /duckedMusicFilters/);
  assert.match(timeline, /buildCaptions/);
  assert.doesNotMatch(timeline, /\[mus\]\[voside\]sidechaincompress/);
});

test("a language switch refuses to reuse old voice files", () => {
  assert.throws(() => assertSpokenReuse({ lang: "en" }, "vi", true), /--force/);
  assert.doesNotThrow(() => assertSpokenReuse({ lang: "en" }, "vi", false));
  assert.equal(keepsForeignClips(["s01", "s02"], ["s01"], true), true);
  assert.equal(keepsForeignClips(["s01", "s02"], ["s01", "s02"], true), false);
  assert.equal(keepsForeignClips(["s01"], ["s01"], false), true);
  assert.equal(keepsForeignClips([], ["s01"], false), false);
});

test("Vietnamese alignment keeps every spoken word", () => {
  const lines = [
    { en: "Hello world", vi: "Xin chào các bạn" },
    { en: "See you", vi: "Hẹn gặp lại nhé" },
  ];
  const words = "Xin chào các bạn Hẹn gặp lại nhé".split(" ").map((text, index) => ({
    text,
    start: index * 0.3,
    end: index * 0.3 + 0.2,
  }));
  assert.throws(() => mapAlignmentToLines(lines, words, "en"), /leftover: Hẹn gặp lại nhé/);
  const mapped = mapAlignmentToLines(lines, words, "vi");
  assert.deepEqual(mapped.map((line) => line.words.map((word) => word.t).join(" ")), [
    "Xin chào các bạn",
    "Hẹn gặp lại nhé",
  ]);
});

test("translated captions stay inside the spoken clause and the caption frame", () => {
  const fitting = buildCaptions([{
    scene: "s1",
    vi: "Xin chào các bạn. Hẹn gặp.",
    spoken: "Hi. Welcome aboard friends today now please.",
    off: 3.2,
    words: [
      ["hi", 0.1, 0.5],
      ["welcome", 1.5, 1.7],
      ["aboard", 1.7, 1.9],
      ["friends", 1.9, 2.1],
      ["today", 2.1, 2.3],
      ["now", 2.3, 2.5],
      ["please", 2.5, 2.8],
    ],
  }], "en");
  const times = fitting.flatMap((chunk) => chunk.words.map((word) => word.s));
  assert.ok(times.slice(0, 4).every((time) => time < 0.55), times.join(","));
  assert.ok(times[4] >= 1.5, times.join(","));
  for (const chunk of fitting) {
    for (const word of chunk.words) assert.ok(word.s >= chunk.start && word.s < chunk.end, `${word.t} ${word.s} not in ${chunk.start}-${chunk.end}`);
  }
});

test("a caption word past the frame fails instead of shipping", () => {
  const lines = [
    {
      scene: "s1",
      vi: "một hai ba bốn năm sáu bảy tám",
      spoken: "one two",
      off: 1.02,
      words: [["one", 0.9, 1.0], ["two", 1.0, 1.02]],
    },
    {
      scene: "s1",
      vi: "tiếp theo đây",
      spoken: "next",
      off: 2.0,
      words: [["next", 1.18, 1.4]],
    },
  ];
  assert.throws(() => buildCaptions(lines, "en"), /caption pace/);
});

test("Vietnamese speech uses alignment times directly", () => {
  const captions = buildCaptions([{
    scene: "s1",
    vi: "Xin chào các bạn",
    spoken: "Xin chào các bạn",
    off: 1.4,
    words: [["xin", 0.2, 0.4], ["chao", 0.4, 0.6], ["cac", 0.6, 0.8], ["ban", 0.8, 1.1]],
  }], "vi");
  assert.deepEqual(captions[0].words.map((word) => word.s), [0.2, 0.4, 0.6, 0.8]);
  for (const word of captions[0].words) assert.ok(word.s < captions[0].end);
});

test("headline wrap keeps emphasis, pills and line breaks", () => {
  const doc = createDocument();
  const root = doc.createElement("div");
  root.append(
    doc.createTextNode("Fast "),
    element(doc, "em", {}, [doc.createTextNode("workflows")]),
    element(doc, "br"),
    doc.createTextNode("for "),
    element(doc, "span", { className: "accent-pill" }, [doc.createTextNode("everyone")]),
  );
  wrapHeadlineWords(root);
  assert.deepEqual(collect(root, "w"), ["Fast", "workflows", "for", "everyone"]);
  assert.equal(root.childNodes.some((node) => node.tag === "br"), true);
  const em = root.childNodes.find((node) => node.tag === "em");
  assert.deepEqual(collect(em, "w"), ["workflows"]);
  const pill = root.childNodes.find((node) => node.className === "accent-pill");
  assert.deepEqual(collect(pill, "w"), ["everyone"]);
  assert.equal(collect(root, "w").includes("workflowsfor"), false);
});

test("both skeletons use the headline walker", () => {
  const source = read("assets/templates/scripts/lib/headline-words.mjs")
    .replace("export function", "function")
    .replace(/\s+/g, " ")
    .trim();
  for (const file of ["assets/templates/index-skeleton.html", "assets/templates/index-skeleton-vertical.html"]) {
    const html = read(file).replace(/\s+/g, " ");
    assert.equal(html.includes(source), true, file);
    assert.equal(html.includes("textContent.trim().split"), false, file);
  }
});

test("music continues after the sidechain voice ends", () => {
  const dir = mkdtempSync(join(tmpdir(), "vibe-duck-"));
  const music = join(dir, "music.wav");
  const voice = join(dir, "voice.wav");
  const stem = join(dir, "stem-music.wav");
  writeTone(music, 4, 220, 0.25);
  writeTone(voice, 0.4, 880, 0.5);
  const graph = [
    "[0:a]aformat=sample_fmts=fltp:channel_layouts=stereo,atrim=0:4[mus]",
    "[1:a]aformat=sample_fmts=fltp:channel_layouts=stereo[voside]",
    ...duckedMusicFilters(4, { stems: true }),
  ].join(";\n");
  const graphFile = join(dir, "graph.txt");
  writeFileSync(graphFile, graph);
  execFileSync("ffmpeg", [
    "-hide_banner", "-nostats", "-y",
    "-i", music, "-i", voice,
    "-/filter_complex", graphFile,
    "-map", "[musstem]", "-c:a", "pcm_s16le", stem,
    "-map", "[musd]", "-f", "null", "-",
  ], { stdio: "ignore" });
  const duration = Number(execFileSync("ffprobe", [
    "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", stem,
  ], { encoding: "utf8" }).trim());
  assert.ok(duration > 3.8, `music stem is ${duration}s`);
  const tail = execFileSync("ffmpeg", [
    "-v", "error", "-ss", "2", "-i", stem, "-ac", "1", "-ar", "8000", "-f", "f32le", "-",
  ]);
  const samples = new Float32Array(tail.buffer, tail.byteOffset, Math.floor(tail.length / 4));
  let sum = 0;
  for (const sample of samples) sum += sample * sample;
  const rms = Math.sqrt(sum / samples.length);
  assert.ok(rms > 0.02, `tail rms ${rms} is silence`);
});

function createDocument() {
  const doc = {};
  const adopt = (node) => {
    node.ownerDocument = doc;
    node.parentNode = null;
    return node;
  };
  doc.createTextNode = (text) => adopt({ nodeType: 3, textContent: text, childNodes: [] });
  doc.createElement = (tag) => {
    const node = adopt({ nodeType: 1, tag, className: "", childNodes: [] });
    node.append = (...children) => {
      for (const child of children) {
        child.parentNode = node;
        node.childNodes.push(child);
      }
    };
    node.replaceChild = (next, prev) => replaceChild(node, next, prev);
    return node;
  };
  doc.createDocumentFragment = () => {
    const node = adopt({ nodeType: 11, childNodes: [] });
    node.appendChild = (child) => {
      child.parentNode = node;
      node.childNodes.push(child);
      return child;
    };
    return node;
  };
  return doc;
}

function element(doc, tag, props, children = []) {
  const node = doc.createElement(tag);
  Object.assign(node, props);
  node.append(...children);
  return node;
}

function replaceChild(parent, next, prev) {
  const index = parent.childNodes.indexOf(prev);
  const inserted = next.nodeType === 11 ? next.childNodes.splice(0) : [next];
  parent.childNodes.splice(index, 1, ...inserted);
  for (const child of inserted) child.parentNode = parent;
}

function collect(node, className, found = []) {
  if (node?.className === className) found.push(node.textContent);
  for (const child of node?.childNodes || []) collect(child, className, found);
  return found;
}

function writeTone(path, seconds, frequency, amplitude, sampleRate = 48000) {
  const count = Math.floor(seconds * sampleRate);
  const data = Buffer.alloc(44 + count * 2);
  data.write("RIFF", 0);
  data.writeUInt32LE(36 + count * 2, 4);
  data.write("WAVE", 8);
  data.write("fmt ", 12);
  data.writeUInt32LE(16, 16);
  data.writeUInt16LE(1, 20);
  data.writeUInt16LE(1, 22);
  data.writeUInt32LE(sampleRate, 24);
  data.writeUInt32LE(sampleRate * 2, 28);
  data.writeUInt16LE(2, 32);
  data.writeUInt16LE(16, 34);
  data.write("data", 36);
  data.writeUInt32LE(count * 2, 40);
  for (let index = 0; index < count; index++) {
    const sample = Math.sin(2 * Math.PI * frequency * (index / sampleRate)) * amplitude;
    data.writeInt16LE(Math.max(-32767, Math.min(32767, Math.round(sample * 32767))), 44 + index * 2);
  }
  writeFileSync(path, data);
}
