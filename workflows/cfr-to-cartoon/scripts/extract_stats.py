#!/usr/bin/env python3
"""Draft candidate facts from article.json (Stage 2). Stdlib only.

Deliberately over-inclusive: Gate 1 (human confirmation) is where facts
are made. Every candidate keeps its verbatim source sentence as `excerpt`.

Usage: extract_stats.py --in source/article.json --out data/fact-ledger.json
"""
from __future__ import annotations

import argparse, json, re
from pathlib import Path

NUM = re.compile(
    r"(?P<num>\$?\d[\d,\.]*\s*(?:million|billion|trillion|percent|%|thousand)?)",
    re.IGNORECASE)
YEAR = re.compile(r"\b(19|20)\d{2}\b")
MONTH_DATE = re.compile(
    r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\b",
    re.IGNORECASE)
QUOTE = re.compile(r"[\"“]([^\"”]{12,180})[\"”]")


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 25]


def main() -> int:
    ap = argparse.ArgumentParser(description="Draft candidate fact ledger (Stage 2).")
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    article = json.loads(Path(args.inp).read_text(encoding="utf-8"))
    facts, seen = [], set()

    def add(kind, claim, excerpt, value=""):
        key = (kind, claim.lower()[:90], value.lower())
        if key in seen:
            return
        seen.add(key)
        facts.append({"id": f"F-{len(facts)+1:03d}", "kind": kind,
                      "claim": claim[:280], "excerpt": excerpt[:500],
                      "confidence": "candidate", **({"value": value} if value else {})})

    for s in sentences(article.get("text", "")):
        # Dates first, so their digits are not re-read as bare statistics.
        without_dates = s
        for m in MONTH_DATE.finditer(s):
            add("date", s, s, m.group(0))
            without_dates = without_dates.replace(m.group(0), " ")
        for m in YEAR.finditer(without_dates):
            add("date", s, s, m.group(0))
            without_dates = without_dates.replace(m.group(0), " ")
        seen_values = set()
        for m in NUM.finditer(without_dates):
            value = m.group("num").strip().rstrip(".,")
            if not value or value in seen_values:
                continue
            seen_values.add(value)
            add("statistic", s, s, value)
        for m in QUOTE.finditer(s):
            add("quote", s, s, m.group(1))

    ledger = {"source": {"outlet": "Council on Foreign Relations",
                         "title": article.get("title", ""),
                         "url": article.get("url", ""),
                         "retrieved_at": article.get("retrieved_at", "")},
              "facts": facts}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK  {len(facts)} candidate facts -> {out}  (all 'candidate': confirm at Gate 1)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
