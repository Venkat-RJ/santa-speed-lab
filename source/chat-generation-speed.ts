import { html, nothing } from "lit";
import { t } from "../../i18n/index.ts";

/**
 * Generation speed of a response, a run, or a session, from the decode timing
 * Cerebras reports for every model call: `time_info.completion_time` and
 * `usage.completion_tokens` in the stream's last chunk, kept on the assistant
 * message as `serverGeneration`. Each call's rate is its tokens over its decode
 * time, so queueing, prefill, network, and tool time are excluded.
 */
export type GenerationSpeed = {
  /** Mean of the per-call rates: the headline. */
  meanTokensPerSecond: number;
  /** 90th-percentile per-call rate (nearest rank); below 10 calls it is the fastest call. */
  p90TokensPerSecond: number;
  /** Completion tokens and decode time summed over the calls. */
  outputTokens: number;
  generationMs: number;
  calls: number;
};

type CallSpeed = { outputTokens: number; generationMs: number };

function readNumber(record: Record<string, unknown>, key: string): number | undefined {
  const value = record[key];
  return typeof value === "number" && Number.isFinite(value) ? value : undefined;
}

/** One model call's server decode timing, from an assistant message's `serverGeneration`. */
function readCall(message: unknown): CallSpeed | null {
  if (!message || typeof message !== "object") {
    return null;
  }
  const record = message as Record<string, unknown>;
  const server = record.serverGeneration;
  if (record.role !== "assistant" || !server || typeof server !== "object") {
    return null;
  }
  const completionMs = readNumber(server as Record<string, unknown>, "completionMs");
  const outputTokens = readNumber(server as Record<string, unknown>, "outputTokens");
  return completionMs !== undefined &&
    completionMs > 0 &&
    outputTokens !== undefined &&
    outputTokens >= 1
    ? { outputTokens, generationMs: completionMs }
    : null;
}

function callRate(call: CallSpeed): number {
  return call.outputTokens / (call.generationMs / 1000);
}

/** Mean and p90 of the per-call rates over the messages' server-timed model calls; null when there are none. */
export function generationSpeed(messages: readonly unknown[]): GenerationSpeed | null {
  const calls = messages.map(readCall).filter((call): call is CallSpeed => call !== null);
  if (calls.length === 0) {
    return null;
  }
  const rates = calls.map(callRate);
  const sorted = rates.toSorted((a, b) => a - b);
  return {
    meanTokensPerSecond: rates.reduce((sum, rate) => sum + rate, 0) / rates.length,
    p90TokensPerSecond: sorted[Math.max(0, Math.ceil(0.9 * sorted.length) - 1)] ?? 0,
    outputTokens: calls.reduce((sum, call) => sum + call.outputTokens, 0),
    generationMs: calls.reduce((sum, call) => sum + call.generationMs, 0),
    calls: calls.length,
  };
}

export function formatTokensPerSecond(rate: number): string {
  return rate >= 100 ? Math.round(rate).toLocaleString() : rate.toFixed(1);
}

function speedLabel(speed: GenerationSpeed): string {
  return t("chat.messages.generationSpeedPercentilesServer", {
    mean: formatTokensPerSecond(speed.meanTokensPerSecond),
    p90: formatTokensPerSecond(speed.p90TokensPerSecond),
  });
}

function speedDetail(speed: GenerationSpeed): string {
  const calls = String(speed.calls);
  return [
    t("chat.messages.generationSpeedMeanDetail", {
      mean: formatTokensPerSecond(speed.meanTokensPerSecond),
      calls,
    }),
    t("chat.messages.generationSpeedP90Detail", {
      p90: formatTokensPerSecond(speed.p90TokensPerSecond),
      calls,
    }),
    t("chat.messages.generationSpeedServerDetail", {
      tokens: speed.outputTokens.toLocaleString(),
      seconds: (speed.generationMs / 1000).toFixed(1),
      calls,
    }),
  ].join("\n");
}

/** Per-response badge; nothing when no call in the response was server-timed. */
export function renderGenerationSpeedBadge(speed: GenerationSpeed | null) {
  if (!speed) {
    return nothing;
  }
  return html`<span class="chat-gen-speed" title=${speedDetail(speed)}>${speedLabel(speed)}</span>`;
}

/**
 * Live badge in the working indicator: the run's speed over the model calls
 * that have finished so far, updated as each one finishes.
 */
export function renderLiveGenerationSpeed(
  progress: { runSpeed?: GenerationSpeed | null } | null | undefined,
) {
  const run = progress?.runSpeed;
  if (!run) {
    return nothing;
  }
  return html`<span aria-hidden="true">·</span
    ><span class="chat-gen-speed chat-gen-speed--live" title=${speedDetail(run)}
      >${speedLabel(run)}</span
    >`;
}

/** Persistent composer readout over the whole visible session. */
export function renderGenerationSpeedSummary(messages: readonly unknown[] | undefined) {
  const session = messages ? generationSpeed(messages) : null;
  if (!session) {
    return nothing;
  }
  return html`<span class="chat-gen-speed chat-gen-speed--summary" title=${speedDetail(session)}
    >${speedLabel(session)}</span
  >`;
}
