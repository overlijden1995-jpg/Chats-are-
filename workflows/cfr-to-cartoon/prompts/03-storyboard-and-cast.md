# 03 — Storyboard & Cast (between Stage ③ and ⑤)

Translate `script.json` into a shot list before touching HTML. Output a
markdown table the human can skim in 30 seconds, one row per scene:

| # | Scene (composition) | On screen (visual) | Line / caption | Facts | Duration |
|---|---|---|---|---|---|

Casting rules (full bible: `templates/characters.md`):
- **The Anchor** — telescreen head, scanlines, never blinks. Delivers euphemisms.
- **The Clerk** — hands, stamp, forms. Speaks only in form numbers and verdicts.
- **The Map** — borders that creep when nobody is looking at them directly.
- **The Ledger** — not a character but a place: the counting room. Numbers
  arrive by pneumatic tube and are read without inflection.
- **The Chorus** — three identical headline cards that cannot agree.

Visual gags must be drawable with CSS/SVG geometry, type, and texture —
no drawn faces, no photographic victim imagery, no stock photos of real
suffering. Maps are abstract (coastline-free polygons); flags are reduced
to colour bars. If a gag needs a picture of a real place or person, the
gag is wrong — replace it with typography.

Storyboard approval rides along with Gate 2's preview; flag any scene
whose gag depends on a fact the human has not confirmed.
