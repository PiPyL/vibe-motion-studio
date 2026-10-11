// sidechaincompress stops when the sidechain stops. A voice bus that ends on
// the last word therefore cuts the music off, and padding the finished mix
// only adds silence. Pad the sidechain to the timeline before the compressor.
const DUCK = "sidechaincompress=threshold=0.03:ratio=3:attack=15:release=350:makeup=1";

export function duckedMusicFilters(duration, { stems = false } = {}) {
  const pad = `[voside]apad=whole_dur=${duration},atrim=0:${duration}[vosidepad]`;
  const compressed = stems
    ? `[mus][vosidepad]${DUCK},asplit=2[musd][musstem]`
    : `[mus][vosidepad]${DUCK}[musd]`;
  return [pad, compressed];
}
