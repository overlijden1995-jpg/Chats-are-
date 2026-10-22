---
name: cfr-cartoon
description: Turn a Council on Foreign Relations (CFR) conflict article into a grimdark Orwellian satirical animated cartoon with the cfr-to-cartoon workflow. Use when asked for a political satire cartoon, a CFR-based explainer animation, a "Ministry of Peace" episode, or any fact-checked satirical video built from a news article.
---

# CFR → Cartoon (The Ministry of Peace)

A seven-stage pipeline that converts one CFR conflict article into a
45–90 second black-comedy animated episode rendered by Hyperframes. The whole
system lives in `workflows/cfr-to-cartoon/`. Read its `README.md` and
`WORKFLOW.md` before starting.

## The one rule

**Facts cited; jokes invented. Never the reverse.** Every number, date, and
quote on screen must come from a confirmed `fact-ledger.json` entry, and every
scene must cite the fact IDs it uses. `scripts/validate_script.py` enforces
this mechanically. Never weaken it to make a joke fit.

## When to use

- "Make a satirical cartoon from this CFR article"
- "Turn this conflict article into a dark animated explainer"
- "Build a Ministry of Peace episode from these statistics"
- Any request that pairs real conflict reporting with animation and satire

## Procedure

1. **Read the bibles first** — `templates/visual-style.md` (palette,
   typography, motion, prohibitions) and `templates/characters.md` (fictional
   cast only). Do not invent a new look.
2. **Ingest** — `python3 workflows/cfr-to-cartoon/scripts/fetch_cfr.py
   --url <cfr-url> --out episodes/<slug>/source` (or `--file` with saved text).
3. **Ledger** — run `scripts/extract_stats.py`, curate candidates, then stop
   for **Gate 1**: the human confirms every fact. Never self-confirm.
4. **Script** — follow `prompts/02-satire-scriptwriter.md`; write
   `data/script.json` against `schemas/script.schema.json`.
5. **Validate** — `scripts/validate_script.py --script … --ledger …` must
   pass with zero errors.
6. **Build** — `scripts/build_episode.py --script … --ledger … --out episodes/<slug>`.
   Then enrich compositions per `prompts/04-hyperframes-composer.md`.
7. **Voice & captions** — `prompts/05-voice-and-captions.md`: Piper TTS
   (MIT), whisper.cpp captions, FFmpeg-synthesised SFX. No proprietary API.
8. **QC & render** — `prompts/06-fact-check-and-qc.md`, then
   `npx hyperframes lint` and `npx hyperframes render`. Stop for **Gate 2**:
   the human watches the cut before anything is published.

## Hard requirements

- Fictional cast only (The Anchor, The Clerk, The Map, The Ledger). Real
  people never appear except as documented, attributed on-screen quotes.
- Punch at institutions, euphemisms, procedures, arithmetic — never at
  victims, named private individuals, or protected groups.
- The disclaimer "SATIRE. FACTS CITED; JOKES INVENTED." stays on screen in
  the cold open and the credits. Credits must cite CFR title, URL, retrieval
  date, and every fact ID used.
- Deterministic Hyperframes only: paused GSAP timelines registered on
  `window.__timelines`, no randomness, no wall-clock CSS animation.
- The Agent never publishes, uploads, or posts. That is the human's Gate 2 act.

## Useful commands

```bash
# Sample episode, end to end (clearly labelled SAMPLE data)
python3 workflows/cfr-to-cartoon/scripts/validate_script.py \
  --script workflows/cfr-to-cartoon/examples/sample-input/script.sample.json \
  --ledger workflows/cfr-to-cartoon/examples/sample-input/fact-ledger.sample.json

python3 workflows/cfr-to-cartoon/scripts/build_episode.py \
  --script workflows/cfr-to-cartoon/examples/sample-input/script.sample.json \
  --ledger workflows/cfr-to-cartoon/examples/sample-input/fact-ledger.sample.json \
  --out workflows/cfr-to-cartoon/episodes/the-ceasefire-that-wasnt
```

Preview and render from the built project directory. Newer CLI releases
expose the studio as `npx hyperframes preview`; this repo's docs use
`npx hyperframes dev`. Both open the same studio.

## Failure modes

| Symptom | Fix |
|---|---|
| Validator: uncited number | Use the ledger value verbatim, or add the rounding as its own confirmed entry |
| Scene has no facts | Mark it `pure_satire: true` and remove all digits, years, and quotes |
| "Joke isn't landing" | Put the euphemism and the fact in the same scene, fact within 2s |
| Lint: `font_family_without_font_face` | Stick to the two bible families, or add `@font-face` |
| Agent wants a real voice or likeness | Refuse — fictional cast only |
