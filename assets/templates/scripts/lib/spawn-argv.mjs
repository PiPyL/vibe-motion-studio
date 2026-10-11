// Run a CLI with an argument array. Never use a shell: `$`, backticks and
// command substitution in a voice-over line are text, not commands.
import { spawn } from "node:child_process";

export function spawnArgv(command, argv, { cwd, spawnImpl = spawn } = {}) {
  const args = argv.map((value) => String(value));
  return new Promise((ok, fail) => {
    const child = spawnImpl(command, args, { shell: false, cwd });
    let log = "";
    child.stdout.on("data", (chunk) => (log += chunk));
    child.stderr.on("data", (chunk) => (log += chunk));
    child.on("error", (err) => fail(err));
    child.on("close", (code) => (code === 0 ? ok(log) : fail(new Error(log.slice(-800) || `${command} exited ${code}`))));
  });
}
