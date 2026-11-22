import { DatabaseSync } from "node:sqlite";
import { zstdDecompressSync } from "node:zlib";

const [database, wantedSession] = process.argv.slice(2);
const db = new DatabaseSync(database, { readOnly: true });
try {
  const session = wantedSession || db.prepare(
    "SELECT session_id FROM transcript_events ORDER BY rowid DESC LIMIT 1",
  ).get()?.session_id;
  if (!session) {
    throw new Error("No session in the isolated run database.");
  }
  const events = db.prepare(
    "SELECT event_json, event_zstd FROM transcript_events WHERE session_id = ? ORDER BY seq",
  ).all(session);
  if (!events.length) {
    throw new Error("Session has no transcript events.");
  }
  for (const event of events) {
    const json = event.event_json || zstdDecompressSync(event.event_zstd).toString("utf8");
    console.log(JSON.stringify(JSON.parse(json)));
  }
} finally {
  db.close();
}
