#!/usr/bin/env bash
# CFR → Cartoon: run stages 1, 2, 4 and 5 with the bundled Python scripts.
# Stage 3 (writing the satire script) is the agent's job — see prompts/02.
#
# Usage:
#   ./run_pipeline.sh --slug my-episode --url "https://www.cfr.org/..."
#   ./run_pipeline.sh --slug my-episode --file saved-article.txt
#   ./run_pipeline.sh --slug my-episode --file article.txt --script data/script.json --ledger data/fact-ledger.json
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
SLUG=""; URL=""; FILE=""; SCRIPT=""; LEDGER=""; EP_NO="0001"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --slug) SLUG="$2"; shift 2 ;;
    --url) URL="$2"; shift 2 ;;
    --file) FILE="$2"; shift 2 ;;
    --script) SCRIPT="$2"; shift 2 ;;
    --ledger) LEDGER="$2"; shift 2 ;;
    --ep-no) EP_NO="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

[[ -n "$SLUG" ]] || { echo "--slug is required" >&2; exit 2; }
OUT="$ROOT/episodes/$SLUG"

if [[ -n "$URL" || -n "$FILE" ]]; then
  echo "▸ stage 1: ingest"
  if [[ -n "$URL" ]]; then
    python3 "$HERE/fetch_cfr.py" --url "$URL" --out "$OUT/source"
  else
    python3 "$HERE/fetch_cfr.py" --file "$FILE" --out "$OUT/source"
  fi
  echo "▸ stage 2: draft candidate facts"
  python3 "$HERE/extract_stats.py" --in "$OUT/source/article.json" --out "$OUT/data/fact-ledger.json"
  echo
  echo "🚦 GATE 1 — have a human confirm the ledger ($OUT/data/fact-ledger.json),"
  echo "   then write $OUT/data/script.json with prompts/02-satire-scriptwriter.md."
fi

SCRIPT="${SCRIPT:-$OUT/data/script.json}"
LEDGER="${LEDGER:-$OUT/data/fact-ledger.json}"
[[ -f "$SCRIPT" ]] || { echo "missing script: $SCRIPT" >&2; exit 2; }
[[ -f "$LEDGER" ]] || { echo "missing ledger: $LEDGER" >&2; exit 2; }

echo "▸ stage 4: validate"
python3 "$HERE/validate_script.py" --script "$SCRIPT" --ledger "$LEDGER"

echo "▸ stage 5: build"
python3 "$HERE/build_episode.py" --script "$SCRIPT" --ledger "$LEDGER" --out "$OUT" --ep-no "$EP_NO"

echo
echo "Next: cd $OUT && npx hyperframes lint && npx hyperframes preview"
echo "Then render and stop at GATE 2 for human review."
