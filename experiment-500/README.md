# Experiment #500 replay

The recorded run used OpenClaw 2026.10.9, Node.js 24.22.1, pnpm 12.15.0, Python 3, and macOS arm64. It used Kimi K3.1 Pro on Cerebras (model ID `moonshotai-kimi-k3.1-pro-trial`), streaming, low reasoning effort, temperature 0.3, and only OpenClaw’s native `web_fetch` tool. Both Cerebras requests returned HTTP 200. The provider observations show that low reasoning effort reached both requests.

## Verify the saved run

From the repository root, run the offline verifier with Python 3.9+ and Node.js 24.

    python3 experiment-500/verify.py

It runs the original OpenClaw scorer over the two stored `serverGeneration` records, compares the decode times to the provider timing frames, and checks that each final link appears in its own successful in-stock catalog response and has a matching in-stock product offer.

- [Official score](evidence/official-speed.json), [provider timing receipts](evidence/provider-stream-receipts.jsonl), [request settings](evidence/request-observations.jsonl), and [HTTP status records](evidence/response-status.jsonl) are copied from the run. The first provider timing frame contains decode time. The first call’s 474 completion tokens come from the OpenClaw assistant event, since the observer’s provider receipt only retained the final call’s usage.
- [Redacted transcript](evidence/transcript.jsonl) retains the prompt, five tool calls and responses, both timing records, and final answer. Tool IDs were replaced with local labels. The original [final answer](evidence/final-answer.txt) is also included.
- [Product evidence](evidence/product-pages.json) contains selected Product and Offer fields from the five HTML pages fetched during the verification step, along with retrieval times and original HTML SHA-256 digests. The excerpts let readers compare the answer with the saved product records offline. The full HTML and raw session state were kept private.
- [Protected measurement checksums](../source/official-measurement-sha256.json) cover the 25 files in the organizer’s patch. The [offline scorer source](../source/chat-generation-speed.ts) is a byte-for-byte copy of that checkout’s scorer. The [OpenClaw license](../source/OPENCLAW-LICENSE) accompanies the bundled source.

The TPS measure excludes queueing, prefill, network time, and tool execution. The official scorer averages the per-call rates and reports a nearest-rank p90, which equals the fastest call in this two-call run.

## Prepare the source

Run these commands from the root of a clone of this repository. Use Git, Node.js 24.22.1 on your PATH, [Corepack](https://github.com/nodejs/corepack), and Python 3.9+. Use a fresh path for OpenClaw. These commands fetch the public base, import the organizer’s patch and config example, then apply the separate retry change that was present in the recorded run.

    git init ../openclaw-exp500
    git -C ../openclaw-exp500 fetch --no-tags --depth=1 \
      https://github.com/openclaw/openclaw.git 8b18b5578f66eab1501cba4cef2310d88bfb9a41
    git -C ../openclaw-exp500 bundle verify "$PWD/source/openclaw-speed-bounty.bundle"
    git -C ../openclaw-exp500 fetch "$PWD/source/openclaw-speed-bounty.bundle" \
      refs/heads/codex/cerebras-speed-bounty
    git -C ../openclaw-exp500 switch --detach 94043a69f5fc1e1fc1def41b32bce744a2e5add0
    git -C ../openclaw-exp500 apply "$PWD/experiment-500/retry-context.patch"
    (cd ../openclaw-exp500 && corepack pnpm install --frozen-lockfile)

The [source bundle](../source/openclaw-speed-bounty.bundle) includes the organizer’s measurement commit `6156ea29713352f023ab13251c9622b0261c82ea` and its subsequent Cerebras example-config commit `94043a69f5fc1e1fc1def41b32bce744a2e5add0`. The [retry patch](retry-context.patch) preserves settled tool results during same-turn rate-limit recovery. It leaves all 25 protected measurement files byte-for-byte unchanged. The original scored run needed no retry.

## Run with live retail discovery

Make `CEREBRAS_API_KEY` available in your shell environment. Your key must have access to the recorded Cerebras trial model. Use a new run directory for every invocation.

    python3 experiment-500/replay.py ../openclaw-exp500 runs/replay-001

The runner validates the source, sets up an isolated state directory, and calls `corepack pnpm openclaw --profile speed-bounty agent exec` in direct, lean mode. It supplies the exact [prompt](prompt.txt) and [config](config.json), and writes the full command and non-secret settings to `runs/replay-001/command.json`. Add `--prepare` with a new directory to write the command and config without starting a model request.

The runner exports the fresh transcript, computes the official score from it, and verifies the returned links against the live catalog responses and retailer pages. It writes the run locally under `runs/`. Keep the generated state, context trace, or raw transcript private. The runner uses the same 150-second supervisor budget for the model run and gives the subsequent product audit up to 55 seconds. It takes a lock for one benchmark at a time in this checkout.

A fresh run can produce different products, different timings, or a failed audit. Experiment #501 replayed this setup and verified five distinct in-stock gifts at 972.95 mean TPS across two calls, with a 1,319.42 TPS peak.
