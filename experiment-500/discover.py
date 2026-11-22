"""Select a live in-stock product and check its merchant product page."""
from argparse import ArgumentParser
from datetime import datetime, timezone
from decimal import Decimal
from html import unescape
from html.parser import HTMLParser
import json
import re
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

MERCHANT = "https://aisynthesis.com"
CATEGORIES = ("filter", "mixer", "oscillator", "echo", "cable")


def catalog_url(category):
    query = urlencode({
        "search": category, "per_page": 1, "stock_status": "instock",
        "_fields": "name,permalink,is_in_stock",
    })
    return f"{MERCHANT}/wp-json/wc/store/v1/products?{query}"


def fetch(url, destination, accept):
    request = Request(url, headers={"Accept": accept, "User-Agent": "Mozilla/5.0",
                                    "Accept-Encoding": "identity"})
    with urlopen(request, timeout=9) as response:
        final_url = urlsplit(response.geturl())
        if final_url.scheme != "https" or final_url.hostname != "aisynthesis.com":
            raise ValueError("Unexpected redirect")
        data = response.read(4 * 1024 * 1024 + 1)
        if len(data) > 4 * 1024 * 1024:
            raise ValueError("Retail page is too large")
        destination.write_bytes(data)
        return response.status


class ProductPage(HTMLParser):
    """Read titles directly from merchant markup."""
    def __init__(self):
        super().__init__()
        self.titles = []
        self.heading = None

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if tag == "meta" and fields.get("property") == "og:title":
            self.titles.append(fields.get("content", ""))
        if tag == "h1":
            self.heading = []

    def handle_data(self, data):
        if self.heading is not None:
            self.heading.append(data)

    def handle_endtag(self, tag):
        if tag == "h1" and self.heading is not None:
            self.titles.append("".join(self.heading))
            self.heading = None


def normalized_name(value):
    return " ".join(unescape(value).casefold().split())


def matching_page(path, name):
    page = ProductPage()
    page.feed(path.read_text(errors="replace"))
    expected = normalized_name(name)
    return any(expected == normalized_name(title) or normalized_name(title).startswith(expected + " - ")
               for title in page.titles)


def page_offer(path, name):
    from audit_shopping import objects, parse

    page, _ = parse(path)
    for script in page.scripts:
        try:
            nodes = list(objects(json.loads(script)))
        except json.JSONDecodeError:
            continue
        for node in nodes:
            if node.get("@type") != "Product" or normalized_name(node.get("name", "")) != normalized_name(name):
                continue
            for offer in objects(node.get("offers")):
                price = offer.get("price", offer.get("lowPrice"))
                currency = offer.get("priceCurrency")
                if price is not None and currency and str(offer.get("availability")).endswith("/InStock"):
                    return str(Decimal(str(price))), currency
    return None


def markdown_results(reply):
    items = []
    for line in reply.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"- \[([^\[\]]+)\]\((https://[^\s()]+)\)", line.strip())
        if match is None:
            return {}
        name, url = match.groups()
        items.append((url, name))
    result = dict(items)
    return result if len(items) == len(result) == 5 else {}
