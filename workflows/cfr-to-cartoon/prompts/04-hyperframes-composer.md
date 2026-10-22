# 04 — Hyperframes Composer (Stage ⑤)

You are composing HTML video in this repo. Invoke the skills first:
`/cfr-cartoon`, `/hyperframes-compose`, and `/gsap-core` + `/gsap-timeline`
for animation work, `/hyperframes-captions` if captions are in scope.

## Non-negotiables from the framework

- Every composition: `<template>`-wrapped sub-compositions,
  `data-composition-id`, `data-width/height/duration`, paused GSAP timeline
  registered as `window.__timelines["<id>"]`.
- Deterministic: no `Math.random()`, no `Date.now()`. Grain and static are
  CSS steps animations with fixed keyframes, not JS noise.
- Animate only visual properties; never animate the same property on the
  same element from two timelines; muted video + separate `<audio>`.

## This show's layer grammar (in every scene)

1. **Paper layer** — near-black ash background, subtle radial vignette.
2. **Texture layer** — halftone/grain overlay, opacity ≤ 0.08, `steps()` jitter.
3. **Telescreen layer** — content framed by a riveted bezel in anchor scenes;
   scanlines (repeating-linear-gradient) at low opacity, one slow drift.
4. **Red layer** — stamp-red is rationed: stamps, one highlighted euphemism,
   the LIVE bug. If everything is red, nothing is.
5. **Type layer** — condensed display for headlines, mono for ledger/facts.
   Facts always in mono, always with their ledger ID as a superscript tag
   (e.g. `F-004`) — the citation is part of the visual identity.

## Choreography

- Entrances 0.3–0.6s, exits half that; never repeat an entrance pattern
  within a composition; the stamp enters exactly once per show, fast
  (`power4.in`, 0.12s) with a 3-frame shake on the whole frame.
- Numbers count up only in The Ledger, using deterministic GSAP
  `innerText` snapping — and the final value must equal the ledger value
  character-for-character.
- End every episode on the credits composition. Not a gag. The credits.

After any composition change: `npx hyperframes lint`, fix everything,
then open `npx hyperframes preview` (or `dev` on older CLIs) and eyeball it before Gate 2.
