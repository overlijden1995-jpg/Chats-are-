# 01 — Ingest & Fact Ledger (Stage ①②)

You are preparing the evidentiary foundation for a satirical cartoon. Your
output will be quoted on screen, so accuracy here is the whole ballgame.

## Do

1. Ingest with `scripts/fetch_cfr.py` (URL or local file). Work from
   `source/article.json` only — never from memory of the conflict, never
   from other articles, never from your training data. If a "well-known"
   fact is not in this article, it does not exist for this episode.
2. Run `scripts/extract_stats.py` for candidates, then curate:
   - one fact per entry; split compound sentences;
   - `claim` = one neutral, presenter-tense sentence a fact-checker would sign;
   - `excerpt` = the verbatim sentence from the article, character-exact;
   - `value`/`unit`/`as_of` filled for statistics whenever the text gives them;
   - quotes: `claim` names the speaker, `excerpt` is the exact quoted words.
3. Aim for 8–16 confirmed facts. Prioritise: scale statistics (displaced,
   casualties, spending, percentages), dates of escalations/decisions,
   official euphemisms or programme names (satire gold — kind: `claim`),
   and anything the article itself flags as disputed (note the dispute in
   the claim: "X claims…, Y disputes…").
4. Present the ledger as a table and stop at **Gate 1**.

## Never

- Never round, convert, or "make vivid" a number in the ledger. Conversions
  (e.g. "per day" rates) must be separate entries showing the arithmetic in
  the claim, and still need human confirmation.
- Never confirm your own candidates silently. `confidence` flips to
  `confirmed` only via the human gate.
- Never include graphic detail about identifiable victims. Aggregate
  statistics from the article are the ceiling of specificity.
