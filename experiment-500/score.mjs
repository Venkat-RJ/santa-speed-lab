import { readFileSync } from "node:fs";
import { stripTypeScriptTypes } from "node:module";

const [transcript, scorer = new URL("../source/chat-generation-speed.ts", import.meta.url)] =
  process.argv.slice(2);
if (!transcript) {
  throw new Error("Usage: node experiment-500/score.mjs TRANSCRIPT [OFFICIAL_SCORER]");
}

const source = readFileSync(scorer, "utf8");
const boundary = source.indexOf("export function formatTokensPerSecond");
if (boundary < 0) {
  throw new Error("Could not find the end of the official calculation.");
}
const core = source.slice(0, boundary).replace(/^import .*;\r?\n/gm, "").replace(/\bexport /g, "");
const generationSpeed = new Function(stripTypeScriptTypes(core) + "; return generationSpeed;")();
const messages = readFileSync(transcript, "utf8").trim().split("\n")
  .map((line) => JSON.parse(line).message).filter(Boolean);
const score = generationSpeed(messages);
if (!score) {
  throw new Error("No server-timed assistant calls in the transcript.");
}
console.log(JSON.stringify(score, null, 2));
