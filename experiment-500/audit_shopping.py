"""Parse product JSON-LD from a saved merchant page."""

import gzip
import hashlib
import io
from html.parser import HTMLParser


class Records(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.capture = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.scripts.append("")
            self.capture = True

    def handle_endtag(self, tag):
        if tag == "script":
            self.capture = False

    def handle_data(self, value):
        if self.capture:
            self.scripts[-1] += value


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def parse(path):
    data = path.read_bytes()
    page = Records()
    if data.startswith(b"\x1f\x8b"):
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as response:
            html = response.read(32 * 1024 * 1024 + 1)
        if len(html) > 32 * 1024 * 1024:
            raise ValueError(f"Decompressed retail response exceeded audit limit: {path}")
    else:
        html = data
    page.feed(html.decode(errors="replace"))
    return page, hashlib.sha256(data).hexdigest()
