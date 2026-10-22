#!/usr/bin/env python3
"""Validate script.json against fact-ledger.json (Stage 4). Stdlib only.

This is the tripwire that makes "facts cited; jokes invented" mechanical:
  * every cited fact exists and is confirmed;
  * pure-satire scenes contain no digits / years / quotation marks;
  * fact-bearing scenes actually cite facts;
  * heuristic scan: numbers spoken in dialogue must appear in a cited fact;
  * credits + disclaimer scenes are present;
  * word budget roughly fits the scene durations (~150 wpm).

Usage: validate_script.py --script data/script.json --ledger data/fact-ledger.json
Exit code 1 (with a readable report) on any failure.
"""
from __future__ import annotations

import argparse, json, re, sys
from pathlib import Path

DIGITS = re.compile(r"\d")
NUMBERISH = re.compile(r"\$?\d[\d,\.]*\s*(?:million|billion|trillion|percent|%|thousand)?", re.I)
QUOTEY = re.compile(r"[\"“”]")
REQUIRED_SCENES = {"cold-open", "credits-sources"}


def load(p: str) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9%$. ]", "", s.lower()).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate satire script vs fact ledger.")
    ap.add_argument("--script", required=True)
    ap.add_argument("--ledger", required=True)
    args = ap.parse_args()

    script, ledger = load(args.script), load(args.ledger)
    facts = {f["id"]: f for f in ledger.get("facts", [])}
    errors: list[str] = []
    warnings: list[str] = []

    # Ledger sanity
    ids = [f["id"] for f in ledger.get("facts", [])]
    if len(ids) != len(set(ids)):
        errors.append("ledger: duplicate fact IDs")
    for f in ledger.get("facts", []):
        for k in ("id", "kind", "claim", "excerpt", "confidence"):
            if k not in f:
                errors.append(f"ledger {f.get('id','?')}: missing '{k}'")

    # Episode sanity
    scenes = script.get("scenes", [])
    comps = {s.get("composition") for s in scenes}
    for req in REQUIRED_SCENES:
        if req not in comps:
            errors.append(f"script: required scene '{req}' missing (credits/disclaimer are not optional)")

    total_words = 0
    total_dur = 0.0
    for s in scenes:
        sid, comp = s.get("id", "?"), s.get("composition", "?")
        cited = s.get("fact_ids", [])
        pure = s.get("pure_satire", False)
        dur = float(s.get("duration_s", 0))
        total_dur += dur
        words = sum(len(ln.get("text", "").split()) for ln in s.get("lines", []))
        total_words += words
        if dur and words / max(dur, 0.01) * 60 > 190:
            warnings.append(f"scene {sid}: {words} words in {dur}s is too fast for deadpan (>190 wpm)")

        for fid in cited:
            if fid not in facts:
                errors.append(f"scene {sid}: cites unknown fact {fid}")
            elif facts[fid].get("confidence") != "confirmed":
                errors.append(f"scene {sid}: fact {fid} is not 'confirmed' (Gate 1)")

        blob = " ".join(ln.get("text", "") for ln in s.get("lines", []))
        headline = s.get("headline", "") or ""
        if pure:
            if cited:
                errors.append(f"scene {sid}: pure_satire scene must cite no facts")
            if DIGITS.search(blob + headline) or QUOTEY.search(blob):
                errors.append(f"scene {sid}: pure_satire scene contains digits/quotes — facts or fiction, pick one")
        else:
            if comp not in ("cold-open", "credits-sources") and not cited:
                errors.append(f"scene {sid} ({comp}): not pure_satire but cites no facts")

        # Heuristic: every number spoken must be traceable to a cited fact.
        # Ledger IDs (F-004) and fictional form codes (27B/6) are set dressing,
        # not factual claims, so they are exempt from the number scan.
        scan_blob = re.sub(r"F-\d{3,}", " ", blob)
        scan_blob = re.sub(r"\b\d{1,3}B/\d+\b", " ", scan_blob)
        cited_text = norm(" ".join(
            f"{facts[f].get('claim','')} {facts[f].get('value','')} {facts[f].get('excerpt','')}"
            for f in cited if f in facts))
        for m in NUMBERISH.finditer(scan_blob):
            token = norm(m.group(0))
            if token and token not in cited_text:
                errors.append(f"scene {sid}: uncited number '{m.group(0)}' in dialogue — add it to the ledger or cut it")

    target = script.get("episode", {}).get("target_duration_s", 0)
    if target and abs(total_dur - target) > max(10, target * 0.25):
        warnings.append(f"scene durations sum to {total_dur:.0f}s vs target {target}s")

    for w in warnings:
        print(f"WARN  {w}")
    if errors:
        for e in errors:
            print(f"FAIL  {e}")
        print(f"\n{len(errors)} error(s). The build does not proceed on uncited facts.")
        return 1
    print(f"OK  {len(scenes)} scenes, {total_words} words, {total_dur:.0f}s — every number traces to a confirmed fact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
