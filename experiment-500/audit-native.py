"""Independently verify final links against in-session web_fetch searches."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html import unescape
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

from discover import CATEGORIES, catalog_url, fetch, matching_page, page_offer, markdown_results


def candidate_lists(text):
    """Find complete merchant response arrays in the tool's wrapper."""
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "[":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, list) and value and all(
            isinstance(row, dict) and {"permalink", "name", "is_in_stock"} <= row.keys()
            for row in value
        ):
            yield value


def run_audit(run):
    if not (run / "transcript.jsonl").is_file():
        return
    expected = {catalog_url(category): category for category in CATEGORIES}
    requests, catalogs = {}, {}
    for line in (run / "transcript.jsonl").open():
        event = json.loads(line)
        message = event.get("message") or {}
        content = message.get("content")
        parts = [item for item in content if isinstance(item, dict)] if isinstance(content, list) else []
        for item in parts:
            if item.get("type") == "toolCall" and item.get("name") == "web_fetch":
                url = item.get("arguments", {}).get("url")
                if url in expected:
                    requests[item["id"]] = expected[url]
        category = requests.get(message.get("toolCallId"))
        if message.get("role") != "toolResult" or not category or message.get("isError"):
            continue
        text = "\n".join(item.get("text", "") for item in parts)
        detail = message.get("details")
        if not isinstance(detail, dict) or "status" not in detail:
            try:
                detail = json.loads(text)
            except json.JSONDecodeError:
                continue
        if not isinstance(detail, dict) or detail.get("status") != 200 or detail.get("cached"):
            continue
        body = detail.get("text")
        if detail.get("url") != catalog_url(category) or not isinstance(body, str):
            continue
        for rows in candidate_lists(body):
            catalogs[category] = (rows, json.dumps(detail, ensure_ascii=False))
            break

    try:
        output = json.loads((run / "stdout.json").read_text())
    except json.JSONDecodeError:
        return
    final = output.get("final") or "\n".join(row["text"] for row in output.get("payloads", []) if row.get("text"))
    chosen = markdown_results(final)
    if not chosen:
        return

    def verify_catalog(entry):
        category, (candidates, response) = entry
        slot = run / "workspace" / "retail-evidence" / category
        slot.mkdir(exist_ok=True, parents=True)
        (slot / "catalog.json").write_text(json.dumps(candidates, ensure_ascii=False) + "\n")
        (slot / "web-fetch-response.txt").write_text(response)
        evidence = {"catalog_url": catalog_url(category), "catalog_status": 200, "rows": []}
        for index, row in enumerate(candidates):
            address = row["permalink"]
            name = unescape(row["name"])
            if chosen.get(address) != name or row["is_in_stock"] is not True:
                continue
            parsed = urlsplit(address)
            if (parsed.scheme, parsed.hostname) != ("https", "aisynthesis.com") or not parsed.path.startswith("/product/"):
                continue
            destination = slot / f"product-{index}.html"
            retrieved_at = datetime.now(timezone.utc).isoformat()
            try:
                status = fetch(address, destination, "text/html")
            except (OSError, ValueError):
                continue
            if status != 200 or not matching_page(destination, name):
                continue
            offer = page_offer(destination, name)
            if not offer:
                continue
            price, currency = offer
            evidence["rows"].append({"name": name, "url": address, "price": str(price),
              "currency": currency, "http_status": status,
              "retrieved_at": retrieved_at, "file": destination.name})
        (slot / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(verify_catalog, catalogs.items()))


if __name__ == "__main__":
    run_audit(Path(sys.argv[1]))
