"""Verify the replay ledger offline. Pass --zip to also verify the released videos."""
import argparse
import hashlib
import json
import math
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from html import unescape
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECIPE = HERE.parent / "experiment-500"
sys.path.insert(0, str(RECIPE))
from discover import CATEGORIES, catalog_url, normalized_name


def require(ok, message):
    if not ok:
        raise ValueError(message)


def hashed(stream):
    digest = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(block)
    return digest.hexdigest()


def verify_products(messages, pages):
    calls = {c["id"]: c["url"] for m in messages for c in m.get("toolCalls", [])}
    catalogs = {m["url"]: m["catalog"] for m in messages if m["role"] == "toolResult"
                and m["http_status"] == 200 and not m["cached"] and calls.get(m["toolCallId"]) == m["url"]}
    answers = next((m.get("finalProducts", []) for m in reversed(messages)
                    if m.get("stopReason") == "stop"), [])
    final = {p["url"]: p["name"] for p in answers}
    matched = set()
    for page in pages:
        schema = page["product_json_ld_excerpt"]
        offer = schema["offers"]
        name, url, category = page["name"], page["url"], page["category"]
        if not (category in CATEGORIES and final.get(url) == name and page["http_status"] == 200
                and schema["@type"] == "Product" and normalized_name(schema["name"]) == normalized_name(name)
                and offer["availability"].endswith("/InStock") and offer["priceCurrency"]
                and (offer.get("price") is not None or offer.get("lowPrice") is not None)):
            continue
        if any(r["permalink"] == url and unescape(r["name"]) == name and r["is_in_stock"] is True
               for r in catalogs.get(catalog_url(category), [])):
            matched.add(url)
    return matched


def verify_attempt(attempt, tmp, reference):
    rid = attempt["id"]
    packet = json.loads((HERE / attempt["evidence"]).read_text())
    messages = packet["messages"]
    timed = [m for m in messages if m.get("serverGeneration")]
    require(len(timed) == attempt["timed_calls"], f"{rid}: call count")
    if timed:
        with tmp.open("w") as f:
            for m in messages:
                f.write(json.dumps({"message": m}) + "\n")
        score = json.loads(subprocess.check_output(
            ["node", "--no-warnings", RECIPE / "score.mjs", tmp], text=True))
        require(math.isclose(score["meanTokensPerSecond"], attempt["observed_mean_tps"]), f"{rid}: mean")
        if attempt["official_score"] is not None:
            for key in ("meanTokensPerSecond", "p90TokensPerSecond", "outputTokens", "generationMs", "calls"):
                require(math.isclose(score[key], attempt["official_score"][key]), f"{rid}: {key}")
        if attempt["final_call_tps"] is not None:
            g = timed[-1]["serverGeneration"]
            require(timed[-1]["stopReason"] == "stop" and
                    math.isclose(g["outputTokens"] * 1000 / g["completionMs"], attempt["final_call_tps"]),
                    f"{rid}: final-call TPS")
    else:
        require(attempt["observed_mean_tps"] is None and attempt["final_call_tps"] is None,
                f"{rid}: absent timings must stay absent")
    matched = verify_products(messages, packet["retail_pages"])
    require(len(matched) == attempt["verified_products"], f"{rid}: product count")
    if attempt["status"] == "qualified":
        require(matched == reference and attempt["official_score"] is not None
                and attempt["final_call_tps"] is not None, f"{rid}: qualifying evidence")
    if attempt.get("milestone"):
        directory = HERE / attempt["milestone_receipts"]
        for name in ("official-speed.json", "response-status.jsonl", "provider-stream-receipts.jsonl"):
            with (directory / name).open("rb") as src:
                require(hashed(src) == attempt["source_hashes"][name], f"{rid}: altered raw receipt {name}")
        raw_score = json.loads((directory / "official-speed.json").read_text())
        require(raw_score == attempt["official_score"], f"{rid}: official receipt differs")
        raw_frames = [json.loads(line) for line in (directory / "provider-stream-receipts.jsonl").read_text().splitlines()]
        frames = [frame for frame in raw_frames if frame.get("event") == "timing-frame"]
        require(frames == packet["provider_timing_frames"], f"{rid}: published provider frames differ")
        require(all(r["status"] == 200 for r in map(json.loads,(directory/"response-status.jsonl").read_text().splitlines())), f"{rid}: HTTP status")
        for frame in raw_frames:
            if frame.get("done") and "usage" in frame and frame["headersAt"] == frames[-1]["headersAt"]:
                require(frame["usage"]["completion_tokens"] == timed[-1]["usageOutput"], f"{rid}: final provider token count")
        require(attempt["source_hashes"]["prompt.txt"] == hashlib.sha256((RECIPE / "prompt.txt").read_bytes()).hexdigest(),
                f"{rid}: prompt differs from the replay recipe")
        require(len(timed) == len(frames) == 2, f"{rid}: two provider timing frames required")
        require(packet["observed_http_statuses"] == [200, 200], f"{rid}: expected HTTP 200 twice")
        require(any(m.get("original_prompt") for m in messages) and matched == reference, f"{rid}: task")
        for m, f in zip(timed, frames):
            g = m["serverGeneration"]
            require(g["outputTokens"] == m["usageOutput"] and
                    math.isclose(g["completionMs"], f["time_info"]["completion_time"] * 1000),
                    f"{rid}: transcript and provider timing disagree")


def verify_videos(videos, attempts, archive):
    by_id = {a["id"]: a for a in attempts}
    ids = {v["id"] for v in videos}
    require(len(videos) == len(ids), "Duplicate recording IDs")
    assets = {}
    for video in videos:
        if video["attempt"] is not None:
            require(video["id"] in by_id[video["attempt"]]["recordings"], "Unlinked recording")
        for key in ("original", "playback", "dashboard_hold_copy"):
            asset = video.get(key)
            if asset:
                require(asset["path"] not in assets, "Duplicate asset path")
                assets[asset["path"]] = asset
    for attempt in attempts:
        require(set(attempt["recordings"]) == {v["id"] for v in videos if v["attempt"] == attempt["id"]},
                f"{attempt['id']}: recording links")
    if archive:
        with zipfile.ZipFile(archive) as z:
            require(set(z.namelist()) == set(assets) and len(z.namelist()) == len(assets),
                    "Recording ZIP inventory mismatch")
            for path, asset in assets.items():
                require(z.getinfo(path).file_size == asset["bytes"], f"{path}: size")
                with z.open(path) as content:
                    require(hashed(content) == asset["sha256"], f"{path}: SHA-256")
        print(f"Verified {len(assets)} files in {archive.name}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, help="Path to the recordings ZIP from GitHub Releases")
    args = parser.parse_args()
    attempts = json.loads((HERE / "attempts.json").read_text())
    recordings = json.loads((HERE / "recordings.json").read_text())
    reference = {p["url"] for p in json.loads((RECIPE / "evidence/product-pages.json").read_text())}
    require(len({a["id"] for a in attempts}) == len(attempts), "Duplicate attempt IDs")
    with tempfile.TemporaryDirectory() as work:
        for a in attempts:
            verify_attempt(a, Path(work)/"events.jsonl", reference)
    verify_videos(recordings, attempts, args.zip)
    for a in attempts:
        if a.get("milestone"):
            print(f"{a['milestone']}: {a['observed_mean_tps']:,.2f} mean TPS, "
                  f"{a['final_call_tps']:,.2f} final-call TPS, {a['verified_products']} products.")
    print(f"{len(attempts)} ledger entries, {len(recordings)} recordings. "
          f"Outcomes: {dict(Counter(a['status'] for a in attempts))}")


if __name__ == "__main__":
    main()
