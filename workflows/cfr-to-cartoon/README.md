# CFR → Cartoon: Grimdark Orwellian Satire, Built Entirely on Open Source

> **Satire. Facts cited; jokes invented.**
> Take a dry, authoritative Council on Foreign Relations (CFR) article about a
> real conflict. Extract every verifiable fact. Then let an agentic AI turn
> *only those facts* into a black-comedy animated cartoon — a Ministry-of-Truth
> news bulletin where the statistics are real and the euphemisms are the joke.

This workflow lives inside the [Hyperframes](../../README.md) monorepo because
Hyperframes is the last mile: HTML + GSAP in, deterministic MP4 out, designed
for AI agents. Everything else in the chain is open source too.

```
CFR article (URL or pasted text)
        │
  ① INGEST ──────── scripts/fetch_cfr.py        (Python stdlib, no deps)
        │            └─ source/article.json + article.md
  ② FACT LEDGER ─── scripts/extract_stats.py    (Python stdlib, no deps)
        │            └─ data/fact-ledger.json   ← every number gets an ID: F-001…
  ③ SATIRE SCRIPT ─ prompts/02-satire-scriptwriter.md   (the agent writes)
        │            └─ data/script.json        ← every joke cites a fact ID
  ④ VALIDATE ────── scripts/validate_script.py  (no fact ID? the build fails)
        │
  ⑤ BUILD EPISODE ─ scripts/build_episode.py    (tokens → Hyperframes project)
        │            └─ episodes/<slug>/index.html + compositions/*.html
  ⑥ VOICE+CARTIONS ─ Piper TTS (MIT) + whisper.cpp (MIT) via Hyperframes
        │
  ⑦ RENDER ──────── npx hyperframes lint && npx hyperframes render
                     └─ out/<slug>.mp4  + burned-in source credits
```

## The one rule that makes the whole thing work

**The comedy may invent anything except facts.**

Every statistic, date, actor, and quoted phrase that appears on screen must
trace to an entry in `fact-ledger.json`, and every beat in `script.json` must
list the fact IDs it is built on. `validate_script.py` enforces this
mechanically — an uncited number fails the build the way a type error fails
compilation. The satire lives in the framing, the euphemisms, the
bureaucracy, and the delivery. Never in the data.

That single constraint is what separates this from "AI makes stuff up about a
war": the cartoon is funnier *because* the numbers are real, and it stays
defensible for the same reason.

## The one prompt you paste

> Read `workflows/cfr-to-cartoon/prompts/00-master-agent-prompt.md` and run it
> end-to-end for this article: **<CFR URL or saved article path>**. Show me the
> fact ledger at Gate 1 and stop.

Everything below is the manual path for when you want to drive the stages
yourself or run them in CI.

## Quickstart

```bash
# 0. From the repo root, once:  pnpm install && pnpm build   (Node 22+, FFmpeg)

# 1. Ingest — give it a CFR URL, or paste text you have the right to use
python3 workflows/cfr-to-cartoon/scripts/fetch_cfr.py \
  --url "https://www.cfr.org/global-conflict-tracker/conflict/…" \
  --out workflows/cfr-to-cartoon/episodes/demo/source
#    …or fully offline, from text you saved yourself:
python3 workflows/cfr-to-cartoon/scripts/fetch_cfr.py \
  --file my-article.txt --out workflows/cfr-to-cartoon/episodes/demo/source

# 2. Draft the fact ledger (candidates — a human/agent confirms each one)
python3 workflows/cfr-to-cartoon/scripts/extract_stats.py \
  --in workflows/cfr-to-cartoon/episodes/demo/source/article.json \
  --out workflows/cfr-to-cartoon/episodes/demo/data/fact-ledger.json

# 3. Hand the repo to your agent with the master prompt
#    (Claude Code / Cursor / Gemini CLI / Codex — see prompts/00)
#    "Read workflows/cfr-to-cartoon/prompts/00-master-agent-prompt.md and run it."

# 4. Validate, build, lint, render
python3 workflows/cfr-to-cartoon/scripts/validate_script.py \
  --script data/script.json --ledger data/fact-ledger.json
python3 workflows/cfr-to-cartoon/scripts/build_episode.py \
  --script data/script.json --ledger data/fact-ledger.json \
  --out episodes/<slug>
cd episodes/<slug> && npx hyperframes lint && npx hyperframes preview   # `dev` on older CLIs
```

No CFR article handy? Run the bundled sample end-to-end (clearly labelled
**SAMPLE** data — invented article, invented numbers, real pipeline):

```bash
cd workflows/cfr-to-cartoon
python3 scripts/build_episode.py \
  --script examples/sample-input/script.sample.json \
  --ledger examples/sample-input/fact-ledger.sample.json \
  --out episodes/the-ceasefire-that-wasnt
# or: ./scripts/run_pipeline.sh --slug <slug> --file <article.txt>
```

## Open-source stack (no proprietary API required at any step)

| Stage | Tool | Licence | Proprietary fallback (optional) |
|---|---|---|---|
| Ingest | `fetch_cfr.py` — Python 3 stdlib only | PSF | — |
| Stat extraction | `extract_stats.py` — Python 3 stdlib only | PSF | any local LLM via Ollama (Apache-2.0) |
| Script / storyboard / composition | Your coding agent + [`skills/cfr-cartoon`](../../skills/cfr-cartoon/SKILL.md) | this repo, MIT | — |
| Animation runtime | [GSAP](https://gsap.com) via Hyperframes frame adapter | GSAP standard (free) | [anime.js](https://animejs.com) (MIT) |
| Voice (TTS) | [Piper](https://github.com/rhasspy/piper) — local, offline voices | MIT | [Coqui XTTS](https://github.com/coqui-ai/TTS) (MPL-2.0), eSpeak NG (GPL-3.0) |
| Captions / transcription | [whisper.cpp](https://github.com/ggerganov/whisper.cpp) via `hyperframes transcribe` | MIT | — |
| Render | Hyperframes engine + producer (Puppeteer + FFmpeg) | MIT / FFmpeg LGPL·GPL | — |
| Everything else | HTML, CSS, SVG — the web platform | — | — |

The pipeline runs fully offline and costs nothing after ingest. Swap any row
for a hosted model if you like — the schemas and validators don't care which
brain wrote the JSON.

## Layout

| Path | What it is |
|---|---|
| [`WORKFLOW.md`](./WORKFLOW.md) | The 7-stage pipeline, gates, and failure modes, in detail |
| [`prompts/00-master-agent-prompt.md`](./prompts/00-master-agent-prompt.md) | **Paste this to the agent.** Orchestrates stages ②–⑦ |
| `prompts/01…06` | One prompt per stage — use standalone or via the master prompt |
| [`templates/visual-style.md`](./templates/visual-style.md) | The grimdark Orwellian art bible (palette, type, grain, telescreens) |
| [`templates/characters.md`](./templates/characters.md) | Recurring cast: The Anchor, The Clerk, The Map, The Ledger, The Chorus |
| `schemas/` | JSON Schemas for the fact ledger and the satire script |
| `scripts/` | Stdlib-only Python: ingest, extract, validate, build |
| `episode-template/` | Tokenised Hyperframes project the builder fills from `script.json` |
| `examples/sample-input/` | A fully worked, clearly-labelled SAMPLE episode input |
| `episodes/` | Generated episodes (the demo episode is committed pre-built) |
| [`../../skills/cfr-cartoon/SKILL.md`](../../skills/cfr-cartoon/SKILL.md) | Agent skill so Claude Code / Cursor / etc. discover this workflow |

## Editorial guardrails (non-negotiable, enforced in prompts + validator)

1. **Facts are cited, jokes are invented — never the reverse.** No statistic,
   date, casualty figure, or quote may appear on screen without a ledger ID.
2. **Punch at systems, never at victims.** Bureaucracies, euphemisms,
   ministries, summits, and communiqués are the targets. Named civilian
   victims, grieving people, and protected characteristics are never the joke.
3. **No invented quotes.** A real person may only "say" a documented quote
   (ledger `kind: "quote"`). Everything else the characters say is obviously
   fictional dialogue from fictional characters (The Anchor, The Clerk…).
4. **Summarise, don't republish.** Ingest extracts facts and short excerpts
   for commentary/satire. It does not mirror the CFR article. Always credit
   CFR with the article title + URL + access date — the credits scene is
   generated automatically and cannot be removed by the template.
5. **A human approves the ledger before the script is written** (Gate 1) and
   **approves the final cut before anything is published** (Gate 2). The
   agent never publishes. Ever.
6. **On-screen disclaimer in every episode:** *"Satire. Facts cited; jokes
   invented."* — in the cold open and the credits.

## Licence & attribution

Workflow code and prompts: MIT, same as this repo. CFR article text remains
© the Council on Foreign Relations — this workflow extracts facts (not
copyrightable) and brief excerpts for criticism/commentary, and links back.
Generated cartoons are your editorial responsibility: check your local rules
on satire, election-period content, and platform disclosure of AI-generated
media before publishing.
