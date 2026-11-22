import { channel } from "node:diagnostics_channel";
import { appendFileSync, readFileSync } from "node:fs";

const outstanding = new WeakMap();
const allowedFields = ["model", "reasoning_effort", "thinking", "temperature", "top_p", "stream", "max_tokens", "max_completion_tokens"];
const destination = process.env.LOCAL_REQUEST_OBSERVATION;

function isCerebrasCompletion(request) {
  return destination &&
    request.method === "POST" &&
    String(request.origin) === "https://api.cerebras.ai" &&
    request.path === "/v1/chat/completions";
}

channel("undici:request:bodyChunkSent").subscribe(({ request, chunk }) => {
  if (!isCerebrasCompletion(request)) return;
  const chunks = outstanding.get(request) ?? [];
  chunks.push(Buffer.from(chunk));
  outstanding.set(request, chunks);
});

channel("undici:request:bodySent").subscribe(({ request }) => {
  if (!isCerebrasCompletion(request)) return;
  const chunks = outstanding.get(request);
  outstanding.delete(request);
  if (!chunks) return;
  try {
    const body = JSON.parse(Buffer.concat(chunks).toString("utf8"));
    const fields = Object.fromEntries(
      allowedFields.filter((key) => Object.hasOwn(body, key)).map((key) => [key, body[key]]),
    );
    const task = readFileSync(destination.replace("request-observations.jsonl", "prompt.txt"), "utf8").trim();
    const userMessages = (body.messages ?? []).filter((msg) => msg.role === "user");
    const promptCopies = userMessages.reduce((sum, msg) => {
      const texts = Array.isArray(msg.content) ? msg.content.map(part => part.text ?? "") : [msg.content ?? ""];
      return sum + texts.reduce((count, text) => count + (task ? text.split(task).length - 1 : 0), 0);
    }, 0);
    const observation = {
      promptCopies,
      ...fields,
      tools: (body.tools ?? []).map((tool) => tool.function?.name),
      toolParameters: (body.tools ?? []).map((tool) => Object.keys(tool.function?.parameters?.properties ?? {})),
      messageRoles: (body.messages ?? []).map((message) => message.role),
      at: new Date().toISOString(),
    };
    appendFileSync(destination, JSON.stringify(observation) + "\n", { mode: 0o600 });
  } catch {
    // Diagnostics must never interrupt a request, even if the body is unavailable.
  }
});

channel("undici:request:error").subscribe(({ request }) => {
  outstanding.delete(request);
});

const limits = new Set(["retry-after", "x-ratelimit-limit-requests", "x-ratelimit-remaining-requests",
  "x-ratelimit-limit-tokens", "x-ratelimit-remaining-tokens", "x-ratelimit-reset-requests",
  "x-ratelimit-reset-tokens"]);
channel("undici:request:headers").subscribe(({ request, response }) => {
  if (!isCerebrasCompletion(request)) return;
  try {
    const metadata = { status: response.statusCode, at: new Date().toISOString() };
    for (let index = 0; index + 1 < response.headers.length; index += 2) {
      const name = String(response.headers[index]).toLowerCase();
      if (limits.has(name)) metadata[name] = String(response.headers[index + 1]);
    }
    appendFileSync(destination.replace("request-observations.jsonl", "response-status.jsonl"),
      JSON.stringify(metadata) + "\n", { mode: 0o600 });
  } catch {
    // Missing optional response metadata must never interrupt inference.
  }
});

const completionStreams = new WeakMap();
const numericFields = (record, names) => Object.fromEntries(names
  .filter((key) => Number.isFinite(record?.[key])).map((key) => [key, record[key]]));

channel("undici:request:headers").subscribe(({ request, response }) => {
  if (!isCerebrasCompletion(request) || response.statusCode !== 200) return;
  completionStreams.set(request, { decoder: new TextDecoder(), pending: "", receipt: {},
    headersAt: new Date().toISOString() });
});

channel("undici:request:bodyChunkReceived").subscribe(({ request, chunk }) => {
  const stream = completionStreams.get(request);
  if (!stream) return;
  try {
    const lines = (stream.pending + stream.decoder.decode(chunk, { stream: true })).split("\n");
    stream.pending = lines.pop();
    if (stream.pending.length > 100_000) completionStreams.delete(request);
    for (const line of lines) {
      if (!line.startsWith("data:")) continue;
      const data = line.slice(5).trim();
      if (data === "[DONE]") stream.receipt.done = true;
      if (!/"(?:system_fingerprint|time_info|usage)"\s*:/.test(data)) continue;
      const frame = JSON.parse(data);
      if (typeof frame.system_fingerprint === "string" && /^[\w.-]{1,100}$/.test(frame.system_fingerprint)) {
        stream.receipt.system_fingerprint = frame.system_fingerprint;
      }
      const timing = numericFields(frame.time_info ?? frame.x_groq?.time_info,
        ["queue_time", "prompt_time", "completion_time", "total_time"]);
      if (Object.keys(timing).length) stream.receipt.time_info = timing;
      if (Object.keys(timing).length && !stream.timingWritten) {
        appendFileSync(destination.replace("request-observations.jsonl", "provider-stream-receipts.jsonl"),
          JSON.stringify({ event: "timing-frame", ...stream.receipt, headersAt: stream.headersAt,
            observedAt: new Date().toISOString() }) + "\n", { mode: 0o600 });
        stream.timingWritten = true;
      }
      const usage = numericFields(frame.usage,
        ["prompt_tokens", "completion_tokens", "total_tokens"]);
      if (Object.keys(usage).length) stream.receipt.usage = usage;
    }
  } catch {
    // A malformed frame or compressed stream must not affect benchmark execution.
  }
});

channel("undici:request:trailers").subscribe(({ request }) => {
  const stream = completionStreams.get(request);
  if (!stream) return;
  completionStreams.delete(request);
  try {
    appendFileSync(destination.replace("request-observations.jsonl", "provider-stream-receipts.jsonl"),
      JSON.stringify({ ...stream.receipt, headersAt: stream.headersAt, completedAt: new Date().toISOString() }) + "\n",
      { mode: 0o600 });
  } catch {
    // The optional observer is read-only with respect to model transport and timing.
  }
});
