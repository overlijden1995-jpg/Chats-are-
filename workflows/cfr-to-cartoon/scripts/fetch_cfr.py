#!/usr/bin/env python3
"""Ingest a CFR article into source/article.json + article.md (Stage 1).

Stdlib only - no third-party dependencies. Extracts *facts* and brief
excerpts for commentary/satire; it does not republish the article.

Usage:
  fetch_cfr.py --url "https://www.cfr.org/..." --out episodes/<slug>/source
  fetch_cfr.py --file saved-article.txt      --out episodes/<slug>/source
  fetch_cfr.py --file saved-page.html        --out episodes/<slug>/source

Respect robots.txt and the publisher's terms. Prefer --file with text you
saved yourself if you are unsure about automated access.
"""
from __future__ import annotations

import argparse, json, re, sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

SKIP = {"script", "style", "noscript", "nav", "footer", "header", "aside", "form"}


class Extractor(HTMLParser):
    """Collect <title> and paragraph-ish text; skip boilerplate subtrees."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.in_title = False
        self.block: str | None = None
        self.title = ""
        self.paragraphs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        elif not self.skip and tag == "title":
            self.in_title = True
        elif not self.skip and tag in ("p", "h2", "li"):
            self.block = tag
            self.paragraphs.append("")

    def handle_endtag(self, tag):
        if tag in SKIP and self.skip:
            self.skip -= 1
        elif tag == "title":
            self.in_title = False
        elif tag == self.block:
            self.block = None

    def handle_data(self, data):
        text = " ".join(data.split())
        if not text or self.skip:
            return
        if self.in_title:
            self.title = (self.title + " " + text).strip()
        elif self.block and self.paragraphs:
            self.paragraphs[-1] = (self.paragraphs[-1] + " " + text).strip()


def clean(paragraphs: list[str]) -> list[str]:
    out, seen = [], set()
    for p in paragraphs:
        p = p.strip()
        if len(p) < 40 or p in seen:
            continue
        seen.add(p)
        out.append(p)
    return out


def looks_like_html(raw: str) -> bool:
    return "<p" in raw[:5000].lower() or "<html" in raw[:5000].lower()


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest a CFR article (Stage 1).")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--url", help="CFR article URL to fetch")
    src.add_argument("--file", help="Local .txt or .html file you saved yourself")
    ap.add_argument("--out", required=True, help="Output dir, e.g. episodes/<slug>/source")
    ap.add_argument("--title", default="", help="Override title (for plain-text files)")
    args = ap.parse_args()

    if args.url:
        req = Request(args.url, headers={"User-Agent": "cfr-cartoon-ingest/1.0 (satire research; contact via repo)"})
        with urlopen(req, timeout=30) as r:  # noqa: S310 - user-supplied URL, intentional
            raw = r.read().decode("utf-8", errors="replace")
        source_url = args.url
    else:
        raw = Path(args.file).read_text(encoding="utf-8", errors="replace")
        source_url = ""

    if looks_like_html(raw):
        ex = Extractor()
        ex.feed(raw)
        title = args.title or ex.title.split("|")[0].split(" - ")[0].strip()
        paragraphs = clean(ex.paragraphs)
    else:
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        title = args.title or (lines[0] if lines else "Untitled")
        paragraphs = clean(lines[1:] if lines and title == lines[0] else lines)

    if not paragraphs:
        print("ERROR: no paragraphs extracted - page markup may have changed. "
              "Save the article text manually and retry with --file.", file=sys.stderr)
        return 1

    article = {
        "outlet": "Council on Foreign Relations",
        "title": title or "Untitled CFR article",
        "url": source_url,
        "retrieved_at": date.today().isoformat(),
        "paragraph_count": len(paragraphs),
        "paragraphs": paragraphs,
        "text": "\n\n".join(paragraphs),
    }
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "article.json").write_text(json.dumps(article, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = [f"# {article['title']}", "", f"Source: {source_url or '(local file)'}",
          f"Retrieved: {article['retrieved_at']}", "",
          "<!-- Working extraction for fact extraction/commentary. Do not redistribute. -->", ""]
    md += paragraphs
    (out / "article.md").write_text("\n\n".join(md) + "\n", encoding="utf-8")
    print(f"OK  title={article['title']!r}  paragraphs={len(paragraphs)}  -> {out}/article.{{json,md}}")
    if not title:
        print("WARN: empty title - set --title before Gate 1.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
