# Visual Style Bible — "The Ministry of Peace"

Fixed art direction for every episode. The agent must not improvise a new
look; consistency *is* the brand. Overrides the generic Hyperframes house
style wherever they conflict.

## Palette (declare exactly these, reference by name)

| Token | Hex | Use |
|---|---|---|
| `--ash` | `#0B0A08` | Background — near-black warm ash |
| `--paper` | `#14120E` | Panel / telescreen interior |
| `--bone` | `#E8DFC8` | Primary text — aged bone white |
| `--bone-dim` | `#9A917C` | Secondary text, rules, excerpts |
| `--stamp` | `#A31616` | Stamp red — rationed (stamps, LIVE bug, one euphemism) |
| `--telescreen` | `#7A8B7F` | Muted surveillance green-grey — scanlines, map fills |
| `--brass` | `#8C6A2F` | Sparingly: form numbers, the Clerk's furniture |

No blue accent. No pure white, no pure mid-grey. High contrast, low chroma.

## Typography (Google Fonts, loaded per composition)

- **Display / headlines:** `Archivo Black` or `Anton` — condensed, uppercase,
  tight tracking (−0.01em). The state's voice.
- **Facts / ledger / captions:** `IBM Plex Mono` or `Space Mono` — facts are
  *always* mono. If it's in the display face, it's propaganda; if it's in
  mono, it's evidence. This distinction is a running gag and a fact-check
  aid at the same time.
- **Excerpts / credits:** mono at 20–24px, `--bone-dim`, with ledger IDs
  (`F-004`) as stamp-red superscript tags.
- Minimum 20px text at 1920×1080. Headlines 72–140px; scale contrast 3–5×.

## Texture & frame (mandatory layers, every scene)

1. Radial vignette (`radial-gradient`, transparent centre → `--ash` edges).
2. Halftone grain: repeating radial dots or an SVG feTurbulence-free CSS
   pattern at opacity 0.05–0.08, animated with `steps(2)` position jitter
   on a 0.4s loop — fixed keyframes only, deterministic.
3. Scanlines on telescreen content: `repeating-linear-gradient` 3px bands,
   opacity ≤ 0.12, drifting 8px over the scene's duration.
4. Riveted bezel around anchor scenes: 24px `--paper` border, corner bolts
   (8px circles, `--brass` at 40%).

## Motion grammar

- Bureaucracy is slow, verdicts are instant: forms slide in at 0.5s
  `power2.out`; the stamp lands in 0.12s `power4.in` + 3-frame frame shake.
- The Map's borders creep: 6–10s linear drifts, never when the Anchor is
  "looking" (border moves only during Ledger lines).
- Numbers count up in The Ledger only (`snap: 1`, deterministic), then hold
  perfectly still for ≥1s — the audience must be able to read the real figure.
- Captions: hard cuts, no fades. The state does not dissolve.
- Exits are twice as fast as entrances; episodes end on credits, hard cut
  to black after a 1s hold. No zoom-outs, ever. Zooms are for hope.

## Prohibitions

- No photographs of real people, places, casualties, or destruction.
- No realistic maps: abstract polygons, no coastlines, labels as
  `[REDACTED COUNTRY A]`-style ministry designations unless the ledger
  names a place for a *statistic* (then mono text, no geography lesson).
- No flags as imagery — colour bars only.
- No drawn faces (per repo house style): characters are frames, hands,
  stamps, type. See `characters.md`.
- No colour beyond the palette. Hope is not in the palette.
