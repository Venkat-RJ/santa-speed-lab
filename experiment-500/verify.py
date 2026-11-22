"""Verify Experiment #500's published receipts and product evidence offline."""

from collections import Counter
from html import unescape
import hashlib
import json
import math
from pathlib import Path
import subprocess

from discover import CATEGORIES, catalog_url, markdown_results, normalized_name

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def read_json(name):
    return json.loads((EVIDENCE / name).read_text())


def read_jsonl(name):
    return [json.loads(line) for line in (EVIDENCE / name).read_text().splitlines()]


def verify_speed(messages):
    transcript = EVIDENCE / "transcript.jsonl"
    speed = json.loads(subprocess.check_output(
        ["node", "--no-warnings", HERE / "score.mjs", transcript], text=True,
    ))
    require(speed == read_json("official-speed.json"), "Official speed receipt differs.")
    require(speed["calls"] == 2, "Expected two server-timed calls.")
    statuses = read_jsonl("response-status.jsonl")
    requests = read_jsonl("request-observations.jsonl")
    require([row["status"] for row in statuses] == [200, 200] and len(requests) == 2,
            "Expected two successful Cerebras requests.")
    require(all(row["reasoning_effort"] == "low" and row["temperature"] == 0.3
                and row["model"] == "moonshotai-kimi-k3.1-pro-trial"
                and row["stream"] and row["promptCopies"] == 1
                and row["tools"] == ["web_fetch"] for row in requests),
            "Provider request settings differ.")
    frames = read_jsonl("provider-stream-receipts.jsonl")
    frames_by_request = [row for row in frames if row.get("event") == "timing-frame"]
    assistant = [row for row in messages if row["role"] == "assistant"]
    require(len(frames_by_request) == len(assistant) == 2,
            "Each assistant call must have one original provider timing frame.")
    for message, receipt in zip(assistant, frames_by_request):
        recorded = message["serverGeneration"]["completionMs"]
        require(math.isclose(recorded, 1000 * receipt["time_info"]["completion_time"]),
                "Provider decode time differs from the assistant event.")
    require(frames[-1]["usage"]["completion_tokens"] == assistant[-1]["serverGeneration"]["outputTokens"],
            "Final provider token count differs from the assistant event.")
    return speed


def verify_products(messages):
    expected_urls = {catalog_url(category): category for category in CATEGORIES}
    calls = messages[1]["content"]
    require(all(call["type"] == "toolCall" and call["name"] == "web_fetch" for call in calls)
            and Counter(call["arguments"]["url"] for call in calls) == Counter(expected_urls.keys()),
            "The five live catalog searches do not match the recipe.")
    urls_by_id = {call["id"]: call["arguments"]["url"] for call in calls}
    catalogs = {}
    for message in messages[2:-1]:
        detail = message["details"]
        url = urls_by_id.pop(message["toolCallId"], None)
        require(message["role"] == "toolResult" and not message["isError"] and url
                and detail["status"] == 200 and not detail["cached"]
                and detail["url"] == detail["finalUrl"] == url, "Invalid catalog result.")
        catalogs[expected_urls[url]] = detail["catalog"]
    require(not urls_by_id and len(catalogs) == 5, "A live catalog result is missing.")

    final = (EVIDENCE / "final-answer.txt").read_text().strip()
    require(messages[-1]["content"] == [{"type": "text", "text": final}], "Final answer differs.")
    links = markdown_results(final)
    pages = read_json("product-pages.json")
    require(len(links) == len(pages) == 5 and {page["url"] for page in pages} == set(links)
            and {page["category"] for page in pages} == set(CATEGORIES),
            "Expected one distinct final product per category.")
    for page in pages:
        name, url = page["name"], page["url"]
        catalog = catalogs[page["category"]]
        require(any(row["permalink"] == url and unescape(row["name"]) == name
                    and row["is_in_stock"] is True for row in catalog),
                f"Product does not match the in-stock catalog response: {url}")
        schema = page["product_json_ld_excerpt"]
        offer = schema["offers"]
        require(links[url] == name and schema["@type"] == "Product"
                and normalized_name(schema["name"]) == normalized_name(name)
                and offer["availability"].endswith("/InStock") and offer["priceCurrency"]
                and (offer.get("price") is not None or offer.get("lowPrice") is not None)
                and page["http_status"] == 200, f"Product does not match the retail page: {url}")


def main():
    integrity = {
        "prompt.txt": "daeacab054ba8e01c7b290f430d0bfc4621f102bee25a826393213e4d2cf8e99",
        "config.json": "de55336d1c981a598b9fc655ca09c51384076639ca4fbc2c43985df9ba0a0a82",
        "discover.py": "addebabd184e1afc53041c1057b2212e160050a5cba41c7e4f4e9a8448613c7b",
        "retry-context.patch": "fa56fe355685577443da3144a191a109b5bc2c5da15ca91316c1c1400f1fbe0e",
        "observe-request.mjs": "34c5f523c7958bcf3d85dbe6c5c0da08192678727d7277cb3f035549a15ce563",
        "../source/chat-generation-speed.ts": "05354264292d2c1d55a7bc7f44ceb021c6a563aff5aa83cb49fed13947e463fa",
    }
    for name, expected in integrity.items():
        require(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected,
                f"Historical SHA-256 differs: {name}")
    messages = [row["message"] for row in read_jsonl("transcript.jsonl")]
    require([row["role"] for row in messages] == ["user", "assistant", *(["toolResult"] * 5), "assistant"],
            "Unexpected transcript sequence.")
    require(messages[0]["content"].strip() == (HERE / "prompt.txt").read_text().strip(),
            "The transcript prompt differs from the replay prompt.")
    speed = verify_speed(messages)
    verify_products(messages)
    print(f"Experiment #500: {speed['meanTokensPerSecond']:,.2f} mean TPS, "
          f"{speed['p90TokensPerSecond']:,.2f} peak TPS, {speed['calls']} timed calls")
    print("Five distinct in-stock products match the saved catalog and product-page evidence.")


if __name__ == "__main__":
    main()
