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

ALLOWED_SCHEMES = {"http", "https"}


def require_http_scheme(url):
    """Reject file://, ftp://, data:, etc. — urllib supports all of them by
    default, which turns a bare urlopen(url) into a local-file-disclosure /
    SSRF vector for a script whose whole point is fetching public web pages."""
    scheme = urlparse(url).scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        raise RuntimeError(f"Refusing non-http(s) URL scheme '{scheme}' for {url!r}")


class SchemeSafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """The default redirect handler follows http(s)->ftp redirects, which
    would let a malicious/compromised https:// origin redirect us into
    fetching from an arbitrary ftp:// host after require_http_scheme() has
    already passed on the original input URL. Refuse anything that isn't
    http(s) at every hop, not just the first one."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlparse(newurl).scheme.lower() not in ALLOWED_SCHEMES:
            raise urllib.error.URLError(f"Refusing redirect to non-http(s) URL: {newurl!r}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _safe_opener():
    return urllib.request.build_opener(SchemeSafeRedirectHandler)


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
    """Returns (allowed, reason). reason is None when allowed, otherwise a
    short human-readable explanation — distinguishing an explicit robots.txt
    disallow rule from a fail-closed default when we couldn't verify at all,
    so the caller doesn't tell the user "robots.txt disallows this" when the
    real cause was e.g. a DNS failure or a dead domain."""
    require_http_scheme(url)
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        req = urllib.request.Request(robots_url, headers={"User-Agent": user_agent})
        with _safe_opener().open(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        rp.parse(raw.splitlines())
    except urllib.error.HTTPError as e:
        if 400 <= e.code < 500:
            # RFC 9309 §2.3.1.3 "Unavailable": ANY 4xx (401/403/404/429/...)
            # means no robots.txt policy is being enforced — crawlers may
            # access freely. Not just 404.
            return True, None
        # 5xx / "Unreachable": assume complete disallow per the same RFC —
        # a server error fetching robots.txt is a reason to hold off, not
        # a reason to assume no policy exists.
        return False, f"couldn't verify robots.txt (HTTP {e.code} fetching it) — failing closed rather than assuming no policy exists"
    except Exception as e:
        # DNS failure, timeout, connection reset, etc. — can't tell
        # whether a policy exists. Same fail-closed reasoning as 5xx above.
        return False, f"couldn't verify robots.txt ({type(e).__name__}) — failing closed rather than assuming no policy exists"
    if rp.can_fetch(user_agent, url):
        return True, None
    return False, "robots.txt explicitly disallows this path for our user-agent"


def fetch(url, timeout=15, retries=2):
    require_http_scheme(url)
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
            with _safe_opener().open(req, timeout=timeout) as resp:
                raw = resp.read()
                encoding = (resp.headers.get("Content-Encoding") or "").lower()
                if encoding in ("", "identity"):
                    pass
                elif encoding == "gzip":
                    raw = gzip.decompress(raw)
                elif encoding == "deflate":
                    try:
                        raw = zlib.decompress(raw)
                    except zlib.error:
                        raw = zlib.decompress(raw, -zlib.MAX_WBITS)
                else:
                    # We only ever advertise gzip/deflate in Accept-Encoding;
                    # a server sending anything else (e.g. brotli) is either
                    # non-compliant or being proxied unexpectedly. Fail loud
                    # rather than decode compressed bytes as if they were text.
                    raise RuntimeError(f"Unsupported Content-Encoding '{encoding}' for {url}")
                content_type = resp.headers.get("Content-Type", "")
                charset_match = re.search(r'charset=["\']?([\w-]+)', content_type, re.IGNORECASE)
                charset = charset_match.group(1) if charset_match else "utf-8"
                try:
                    text = raw.decode(charset, errors="replace")
                except LookupError:
                    # Server declared a charset name Python doesn't recognize
                    # — fall back to the most broadly compatible default
                    # rather than crashing on a server misconfiguration.
                    text = raw.decode("utf-8", errors="replace")
                return text, content_type, resp.geturl()
        except zlib.error as e:
            # Both the direct and raw-deflate decompress attempts failed —
            # not retryable, the response body itself is bad.
            raise RuntimeError(f"Failed to decompress deflate response from {url}: {e}")
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500:
                raise RuntimeError(f"HTTP {e.code} {e.reason} for {url} (client error, not retrying)")
            last_err = e
        except ValueError as e:
            # Malformed URL (e.g. missing scheme entirely) — retrying won't
            # fix it.
            raise RuntimeError(f"Invalid URL {url!r}: {e}")
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

    # Everything from here on — fetch AND extraction/output — is covered by
    # one safety net. A prior version of this fix only wrapped the fetch
    # call, which left UnicodeEncodeError (e.g. an emoji/non-ASCII title
    # printed where stdout isn't UTF-8 — a real, reproducible crash, not
    # hypothetical) and any HTMLParser failure free to crash with a raw
    # traceback. sys.exit() raises SystemExit, which subclasses
    # BaseException rather than Exception, so it still passes through
    # `except Exception` untouched below.
    try:
        if not args.ignore_robots:
            allowed, reason = check_robots_allowed(args.url, USER_AGENT)
            if not allowed:
                print(f"BLOCKED: {reason} — not fetching {args.url}", file=sys.stderr)
                sys.exit(2)
        html, content_type, final_url = fetch(args.url)

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
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Safety net: no exception type should ever escape as a raw
        # traceback — the documented contract is "stderr explains why,
        # non-zero exit," full stop.
        print(f"ERROR: unexpected {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
