# Workflow in Detail — CFR Article → Grimdark Animated Satire

Seven stages, two human gates. Each stage consumes a file and produces a
file, so any stage can be re-run, swapped, or done by hand without touching
the others. The agent runs stages ②–⑦ when given
[`prompts/00-master-agent-prompt.md`](./prompts/00-master-agent-prompt.md).

```
article ──▶ article.json ──▶ fact-ledger.json ──▶ script.json ──▶ episode/ ──▶ MP4
  ingest       extract        [GATE 1: human]      validate       voice+render  [GATE 2: human]
```

---

## Stage ① — Ingest (`scripts/fetch_cfr.py`)

**Input:** a CFR URL (`--url`) or a local text/HTML file (`--file`).
**Output:** `source/article.json` + `source/article.md`.

- Stdlib-only (`urllib`, `html.parser`). No API key, no headless browser.
- Extracts: title, byline/date if present, body paragraphs, and the raw text.
- Records `source_url` and `retrieved_at` — these end up in the end credits.
- **Copyright posture:** the script is for extracting *facts* and brief
  excerpts for commentary. Prefer `--file` with text you saved yourself if
  you are unsure about automated access; respect `robots.txt` and CFR's
  terms; never redistribute `article.md` — it is a working file, gitignored
  in generated episodes.
- Failure mode: CFR pages change markup. The parser degrades gracefully to
  "all paragraph text" rather than failing. If the title comes back empty,
  the agent asks the human instead of guessing.

## Stage ② — Fact Ledger (`scripts/extract_stats.py` → human/agent curation)

**Input:** `source/article.json`. **Output:** `data/fact-ledger.json`
(schema: [`schemas/fact-ledger.schema.json`](./schemas/fact-ledger.schema.json)).

- The extractor proposes candidates: every numeric claim (with its sentence),
  dates, named actors/places, and quoted phrases. Each becomes:

```json
{ "id": "F-004", "kind": "statistic", "claim": "…", "value": "…",
  "unit": "…", "as_of": "…", "excerpt": "verbatim sentence from the article",
  "confidence": "candidate | confirmed" }
```

- `kind` ∈ `statistic | date | actor | place | quote | claim`.
- Candidates start as `"candidate"`. **Nothing becomes `"confirmed"` without
  a human (or the agent, explicitly instructed + human spot-check) verifying
  the excerpt actually says that.** This is the cheapest accuracy win in the
  whole pipeline: verifying 15 excerpts takes five minutes and prevents
  every downstream hallucination.

### 🚦 GATE 1 — Human confirms the ledger

The agent presents the ledger as a table (ID, claim, excerpt). The human
deletes, fixes, or confirms. **The pipeline does not proceed on an
unconfirmed ledger** — the master prompt makes the agent stop and ask.

## Stage ③ — Satire Script (`prompts/02-satire-scriptwriter.md`)

**Input:** confirmed ledger (+ visual style + cast bibles).
**Output:** `data/script.json` (schema: [`schemas/script.schema.json`](./schemas/script.schema.json)).

The scriptwriter prompt turns facts into a 45–90 second black-comedy
bulletin using the recurring cast and set grammar:

| Scene (composition) | Job | Typical joke engine |
|---|---|---|
| `cold-open` | Telescreen crackles on; disclaimer | The state notices you noticing |
| `ministry-anchor` | Headline, delivered deadpan | Euphemism vs. fact, side by side |
| `map-room` | Borders redraw themselves | Cartography as wishful thinking |
| `the-ledger` | Real statistics, counted out loud | Bureaucratic arithmetic of horror |
| `the-stamp` | The Clerk approves the punchline | One red stamp: APPROVED / DENIED / PEACE |
| `credits-sources` | Every fact ID + CFR citation | The only scene that never lies |

Hard rules the prompt enforces (and the validator checks):

- Every scene lists `fact_ids`. A scene with zero real facts must be marked
  `"pure_satire": true` and may contain **no** numbers, dates, or quotes.
- Every line of character dialogue is fictional; documented words only via
  `kind: "quote"` ledger entries, shown on screen in quotation marks with
  attribution.
- Target = institutions, euphemisms, procedures. Never victims.
- Structure: setup (euphemism) → ledger (fact) → stamp (verdict). Repeat.
  End on the credits, not on a gag about the dead.

## Stage ④ — Validate (`scripts/validate_script.py`)

Mechanical, no AI involved. Fails the build if:

- any `fact_id` referenced by the script is missing or unconfirmed;
- any scene contains a digit, year, or quotation mark pattern that is not
  traceable to its cited facts (heuristic scan — a tripwire, not a proof);
- a scene exceeds its word budget (≈150 wpm → duration sanity check);
- the credits scene or the disclaimer has been removed;
- schema violations in either JSON file.

## Stage ⑤ — Build Episode (`scripts/build_episode.py`)

Copies `episode-template/`, substitutes `%%TOKENS%%` from `script.json`
(headline, scene lines, stat values, ledger rows, CFR citation), writes
`meta.json`, and copies the ledger beside the compositions so the credits
scene is generated **from the ledger itself** — credits cannot drift from
the facts because they *are* the facts, rendered.

## Stage ⑥ — Voice & Captions (`prompts/05-voice-and-captions.md`)

- **TTS (open source):** Piper, one flat affectless voice for The Anchor
  (deadpan is a direction, not a model setting: slow rate, narrow pitch),
  a second voice for The Clerk. Output `assets/voice-<scene>.wav`.
- **Captions:** `npx hyperframes transcribe assets/voice-*.wav` (whisper.cpp)
  → word-level `transcript.json` → the captions skill renders tone-adaptive
  captions — here locked to the style bible: mono type, bone-on-black,
  the currently-spoken euphemism highlighted in stamp-red.
- Music/SFX: procedurally generated or public-domain only (shortwave static,
  stamp thud, paper shuffle) — see the prompt for FFmpeg synth recipes so no
  asset licence can ever bite.

## Stage ⑦ — Render & QC (`prompts/06-fact-check-and-qc.md`)

```bash
npx hyperframes lint      # structural errors — must be zero
npx hyperframes preview   # human watches the preview   → 🚦 GATE 2
                          # (`npx hyperframes dev` on older CLI builds)
npx hyperframes render    # deterministic MP4
```

QC checklist (agent performs, human signs off): every on-screen number
matches the ledger character-for-character; disclaimer present; credits list
title/URL/date; no victim imagery; audio never jokes over a casualty figure
(the ledger scene plays it straight — that restraint *is* the joke's engine).

### 🚦 GATE 2 — Human watches before anything leaves the machine

The agent stops after `render`. Publishing, posting, and scheduling are
human acts. The workflow intentionally contains no upload code.

---

## Failure modes worth knowing

| Symptom | Likely cause | Fix |
|---|---|---|
| Validator: "uncited number" | Script invented or rounded a stat | Use the ledger value verbatim, or add the rounding as its own confirmed ledger entry |
| Joke "isn't landing" | Euphemism and fact in different scenes | Co-locate them (style bible: fact lands ≤2s after the euphemism) |
| Ledger full of junk candidates | Extractor is deliberately over-inclusive | Curate at Gate 1 — deletion is the job |
| Render looks flat | House-style defaults crept in | Re-apply `templates/visual-style.md` (grain, vignette, scanlines are mandatory) |
| Agent wants a real person's voice/likeness | — | Refuse. Fictional cast only; documented quotes as on-screen text |
