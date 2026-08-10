#!/usr/bin/env python3
"""Fetch a URL and print its readable text content to stdout.

Standard-library only (no pip dependencies). Identifies as a normal browser
so it isn't dropped by naive user-agent sniffing (blocking bare `curl`/
`python-requests` UAs is extremely common even on sites with no real
anti-scraping policy). This does NOT attempt to defeat JS-challenge or
CAPTCHA-based bot detection (e.g. Cloudflare's managed challenge) — that is
out of scope by design, not a missing feature.
"""
import argparse
import gzip
import re
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
import zlib
from html.parser import HTMLParser
from urllib.parse import urlparse

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

SKIP_TAGS = {"script", "style", "noscript", "template", "svg", "nav", "footer", "header", "aside"}
BLOCK_TAGS = {
    "p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
    "section", "article", "blockquote", "pre",
}


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.in_title = False
        self.chunks = []
        self.title_chunks = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        if tag == "title":
            self.in_title = True
        if tag in BLOCK_TAGS:
            self.chunks.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skip_depth > 0:
            self.skip_depth -= 1
        if tag == "title":
            self.in_title = False
        if tag in BLOCK_TAGS:
            self.chunks.append("\n")

    def handle_data(self, data):
        if self.skip_depth:
            return
        if self.in_title:
            self.title_chunks.append(data)
            return
        self.chunks.append(data)

    def get_text(self):
        text = "".join(self.chunks)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def get_title(self):
        return "".join(self.title_chunks).strip()


def check_robots_allowed(url, user_agent, timeout=10):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        req = urllib.request.Request(robots_url, headers={"User-Agent": user_agent})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        rp.parse(raw.splitlines())
    except Exception:
        # No robots.txt, or it's unreachable — default to allowed rather
        # than blocking on an absent file.
        return True
    return rp.can_fetch(user_agent, url)


def fetch(url, timeout=15, retries=2):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    }
    last_err = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                encoding = (resp.headers.get("Content-Encoding") or "").lower()
                if encoding == "gzip":
                    raw = gzip.decompress(raw)
                elif encoding == "deflate":
                    try:
                        raw = zlib.decompress(raw)
                    except zlib.error:
                        raw = zlib.decompress(raw, -zlib.MAX_WBITS)
                content_type = resp.headers.get("Content-Type", "")
                charset_match = re.search(r"charset=([\w-]+)", content_type)
                charset = charset_match.group(1) if charset_match else "utf-8"
                return raw.decode(charset, errors="replace"), content_type, resp.geturl()
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500:
                raise RuntimeError(f"HTTP {e.code} {e.reason} for {url} (client error, not retrying)")
            last_err = e
        except (urllib.error.URLError, OSError) as e:
            last_err = e
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url} after {retries + 1} attempt(s): {last_err}")


def main():
    parser = argparse.ArgumentParser(description="Extract readable text from a URL.")
    parser.add_argument("url")
    parser.add_argument("--max-chars", type=int, default=20000, help="Truncate output (0 = no limit). Default 20000.")
    parser.add_argument("--ignore-robots", action="store_true", help="Skip the robots.txt allow-check. Use only with a specific reason.")
    args = parser.parse_args()

    if not args.ignore_robots and not check_robots_allowed(args.url, USER_AGENT):
        print(f"BLOCKED: robots.txt disallows this path for our user-agent — not fetching {args.url}", file=sys.stderr)
        sys.exit(2)

    try:
        html, content_type, final_url = fetch(args.url)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if content_type and "html" not in content_type and "xml" not in content_type:
        text, title = html, ""
    else:
        extractor = TextExtractor()
        extractor.feed(html)
        text, title = extractor.get_text(), extractor.get_title()

    if final_url != args.url:
        print(f"[redirected to: {final_url}]", file=sys.stderr)

    if title:
        print(f"# {title}\n")

    if args.max_chars and len(text) > args.max_chars:
        total = len(text)
        text = text[: args.max_chars] + f"\n\n...[truncated at {args.max_chars} chars; total was {total}]"

    print(text)


if __name__ == "__main__":
    main()
