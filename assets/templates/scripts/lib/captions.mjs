// Caption times stay inside the on-screen chunk.
// Vietnamese speech uses the alignment timestamps.
// English speech with a Vietnamese subtitle is placed by clause, then rejected
// when the words cannot fit in the spoken window at a readable gap.
import { contentTokens } from "./spoken.mjs";

const MIN_GAP = 0.07;
const MAX_CHUNK = 9;

const round = (value, digits = 3) => Math.round(value * 10 ** digits) / 10 ** digits;

function splitClauses(text) {
  const parts = String(text).trim().split(/(?<=[,.:;?!…])\s+/u).map((part) => part.trim()).filter(Boolean);
  return parts.length ? parts : [String(text).trim()];
}

function paceError(count, span) {
  const need = MIN_GAP * Math.max(0, count - 1);
  const error = new Error(
    `caption pace: ${count} words need ${need.toFixed(3)}s at ${Math.round(MIN_GAP * 1000)}ms gaps but the spoken window is ${span.toFixed(3)}s`,
  );
  error.code = "CAPTION_PACE";
  return error;
}

function placeLinear(tokens, start, end) {
  const count = tokens.length;
  if (!count) return [];
  const lastAt = end - 0.04;
  const span = lastAt - start;
  if (!(span > 0)) throw paceError(count, Math.max(0, end - start));
  const need = MIN_GAP * Math.max(0, count - 1);
  if (need > span + 1e-6) throw paceError(count, span);
  const step = count === 1 ? 0 : span / (count - 1);
  return tokens.map((token, index) => ({ t: token, s: round(start + step * index) }));
}

function timesFromAlignment(line) {
  const tokens = contentTokens(line.vi);
  if (tokens.length !== line.words.length) {
    throw new Error(`caption/alignment mismatch: "${line.vi}" has ${tokens.length} tokens, alignment has ${line.words.length}`);
  }
  return tokens.map((token, index) => ({ t: token, s: line.words[index][1] }));
}

function clauseGroups(line) {
  const spokenClauses = splitClauses(line.spoken);
  const captionClauses = splitClauses(line.vi);
  if (spokenClauses.length !== captionClauses.length) return null;
  const groups = [];
  let index = 0;
  for (const clause of spokenClauses) {
    const count = contentTokens(clause).length;
    const segment = line.words.slice(index, index + count);
    index += count;
    if (segment.length !== count || !segment.length) return null;
    groups.push(segment);
  }
  if (index !== line.words.length) return null;
  return { spoken: groups, captions: captionClauses };
}

function timesFromTranslation(line) {
  const grouped = clauseGroups(line);
  if (!grouped) {
    const tokens = contentTokens(line.vi);
    const start = line.words[0][1];
    const end = Math.min(line.off, line.words[line.words.length - 1][2]);
    return placeLinear(tokens, start, end);
  }
  const placed = [];
  grouped.captions.forEach((clause, index) => {
    const segment = grouped.spoken[index];
    const start = segment[0][1];
    const end = Math.min(line.off, segment[segment.length - 1][2]);
    placed.push(...placeLinear(contentTokens(clause), start, end));
  });
  return placed;
}

function chunkWords(words, line) {
  const chunks = [];
  let current = [];
  const flush = () => {
    if (current.length) chunks.push({ scene: line.scene, lineOff: line.off, words: current });
    current = [];
  };
  words.forEach((word, index) => {
    current.push(word);
    const left = words.length - index - 1;
    const punctuated = /[,.:;?!…]$/.test(word.t);
    if (left === 0) return;
    if ((punctuated && current.length >= 3 && left >= 2 && words.length > MAX_CHUNK) || current.length >= MAX_CHUNK) flush();
  });
  flush();
  return chunks;
}

function windowError(word, end) {
  const error = new Error(`caption window: "${word.t}" at ${word.s.toFixed(3)}s is outside the caption ending at ${end.toFixed(3)}s`);
  error.code = "CAPTION_WINDOW";
  return error;
}

function finalize(chunks) {
  chunks.forEach((chunk, index) => {
    const next = chunks[index + 1];
    const first = chunk.words[0].s;
    const last = chunk.words[chunk.words.length - 1].s;
    chunk.start = round(first - 0.12);
    let end = chunk.lineOff + 0.5;
    if (next) {
      const natural = next.lineOff === chunk.lineOff ? next.words[0].s - 0.12 : chunk.lineOff + 0.5;
      end = Math.min(end, natural, next.words[0].s - 0.16);
    }
    if (end <= last) {
      const extended = last + 0.08;
      const limit = next ? next.words[0].s - 0.04 : extended;
      if (extended <= limit + 1e-9) end = extended;
      else throw windowError(chunk.words[chunk.words.length - 1], end);
    }
    chunk.end = round(end);
    if (chunk.end <= last) chunk.end = round(last + 0.04);
    for (const word of chunk.words) {
      if (word.s < chunk.start - 1e-6 || word.s >= chunk.end) throw windowError(word, chunk.end);
    }
  });
  return chunks;
}

export function buildCaptions(lines, lang) {
  if (lang !== "en" && lang !== "vi") throw new Error(`spoken lang must be en or vi, got ${lang}`);
  const chunks = [];
  for (const line of lines) {
    if (!line.vi || !String(line.vi).trim()) throw new Error("caption: line is missing `vi` text");
    if (!line.words?.length) throw new Error("caption: line has no aligned words");
    const timed = lang === "vi" ? timesFromAlignment(line) : timesFromTranslation(line);
    chunks.push(...chunkWords(timed, line));
  }
  return finalize(chunks).map((chunk) => ({
    scene: chunk.scene,
    start: chunk.start,
    end: chunk.end,
    words: chunk.words.map((word) => ({ t: word.t, s: word.s })),
  }));
}
