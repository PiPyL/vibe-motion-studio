// One spoken transcript for TTS, forced alignment, captions and word anchors.
// `en` reads `say` or `en`. `vi` reads `vi`. Mixing them slices the WAV short.

export function spokenRecord(lang) {
  if (lang !== "en" && lang !== "vi") throw new Error(`spoken lang must be en or vi, got ${lang}`);
  return { lang, field: lang === "vi" ? "vi" : "say-or-en" };
}

export function lineSpoken(line, lang) {
  const record = spokenRecord(lang);
  const text = record.field === "vi" ? line.vi : line.say || line.en;
  if (!text || !String(text).trim()) {
    throw new Error(record.field === "vi" ? "line is missing `vi` text" : "line is missing `say` and `en` text");
  }
  return String(text);
}

export function contentTokens(text) {
  return String(text).split(/\s+/).filter((token) => /[\p{L}\p{N}]/u.test(token));
}

// Existing WAVs stay on the language that produced them. A new language
// requires --force, otherwise alignment would time the wrong transcript.
export function assertSpokenReuse(previous, lang, keptExisting) {
  if (previous && previous.lang && previous.lang !== lang && keptExisting) {
    throw new Error(
      `existing voice-over is ${previous.lang} but this run is ${lang}. Re-run with --force and regenerate every existing clip so speech and alignment use one transcript.`,
    );
  }
}

// True when a clip from the previous language would survive this run.
export function keepsForeignClips(existingIds, selectedIds, force) {
  const selected = new Set(selectedIds);
  return existingIds.some((id) => !(force && selected.has(id)));
}

export function mapAlignmentToLines(lines, words, lang) {
  const aligned = words.filter((word) => /[\p{L}\p{N}]/u.test(word.text));
  let index = 0;
  const mapped = lines.map((line) => {
    const expected = contentTokens(lineSpoken(line, lang));
    const segment = aligned.slice(index, index + expected.length);
    index += expected.length;
    if (segment.length !== expected.length) {
      throw new Error(`alignment shortfall: need ${expected.length} tokens, got ${segment.length}`);
    }
    return {
      start: segment[0].start,
      end: segment[segment.length - 1].end,
      words: segment.map((word) => ({ t: word.text, s: word.start, e: word.end })),
    };
  });
  if (index !== aligned.length) {
    const leftover = aligned.slice(index).map((word) => word.text).join(" ");
    throw new Error(`${aligned.length} aligned words vs ${index} script tokens; leftover: ${leftover}`);
  }
  return mapped;
}
