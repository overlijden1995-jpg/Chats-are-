# 05 — Voice & Captions (Stage ⑥, fully open source)

## Voice — Piper TTS (MIT, local, offline)

- Install: `pip install piper-tts` (or the Piper binary release). Voices:
  a low, flat voice for **The Anchor**; a clipped, higher voice for
  **The Clerk**. Download voice models once from the Piper voices repo
  (Hugging Face, open datasets) and pin them under `assets/voices/`.
- Direction is in the text, not the model: short sentences, full stops,
  no exclamation marks (deadpan cannot survive an exclamation mark).
  Generate per-scene files: `assets/voice-<scene-id>.wav`, then place each
  as a separate `<audio>` clip on its scene's timing.
- Fallback if Piper is unavailable: render FFmpeg sine/silence placeholders
  of the right durations, mark the episode `VOICE PENDING` in `meta.json`,
  and tell the human. Never silently call a proprietary TTS API.

## Captions — whisper.cpp via Hyperframes

```bash
npx hyperframes transcribe assets/voice-ministry-anchor.wav --model small.en
```

- English-only episodes: `small.en` is fine for clean TTS; use `medium.en`
  if the Clerk's clipped delivery gets mangled. Import existing SRT/VTT
  with the same command if captions were authored by hand (preferred for
  the Ledger scene — numbers must be perfect, so author them, don't
  transcribe them).
- Style is locked by `templates/visual-style.md`: mono, bone white on
  ash black, current word in stamp-red only when the word is the
  euphemism; fact superscripts (`F-004`) stay on screen for the whole line.

## Sound design without licences

Synthesize everything with FFmpeg (LGPL/GPL): shortwave static
(`anoisesrc` + bandpass, 0.4s), stamp thud (sine burst 90Hz, 0.12s),
pneumatic tube (filtered noise sweep), telescreen hum (50Hz, −30dB).
No music library, no samples of broadcasts, no real-world audio of the
conflict. Ever.
