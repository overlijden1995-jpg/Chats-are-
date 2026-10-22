# 06 — Fact-Check & QC (Stage ⑦, then Gate 2)

You are now the hostile fact-checker of your own cartoon. Assume the
scriptwriter (also you) cheated somewhere. Prove or refute it.

## Checklist — every box, in order

1. `scripts/validate_script.py` passes on the final files (re-run it; the
   script may have changed since Stage ④).
2. Scrub the rendered MP4 frame by frame through The Ledger scene: every
   digit on screen equals the ledger `value` exactly; every date equals
   its ledger entry; durations/as_of are not silently dropped where they
   change the meaning ("in one province" must not become "nationwide").
3. Every documented quote is verbatim, in quotation marks, attributed,
   and cites a `kind: "quote"` ledger ID.
4. Disclaimer present twice: cold open and credits
   ("Satire. Facts cited; jokes invented.").
5. Credits cite: CFR article title, author/outlet line as ingested,
   source URL, retrieval date, and the list of fact IDs used.
6. Target audit: list every joke's butt. All must be institutions,
   euphemisms, procedures, or arithmetic. Any line laughing at victims,
   a named private individual, or a protected group → cut, re-render.
7. No real person's likeness or voice; no photographic imagery of real
   suffering; maps/flags abstracted per the style bible.
8. `npx hyperframes lint` clean; render is deterministic (two renders,
   same duration and file structure).

## Then stop: Gate 2

Hand the human: MP4 path, `npx hyperframes dev` preview instructions,
the facts-used summary, and the target audit from step 6. State plainly
that you have not published anything and will not. The human publishes,
or nobody does.
