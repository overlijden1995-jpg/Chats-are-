#!/usr/bin/env python3
"""Build a Hyperframes episode from script.json + fact-ledger.json (Stage 5).

Fills the tokenised project in ../episode-template with the episode's real
content and writes a self-contained Hyperframes project to --out.

Usage:
  build_episode.py --script data/script.json --ledger data/fact-ledger.json \
                   --out episodes/my-episode [--no-captions] [--ep-no 0002]
"""
from __future__ import annotations

import argparse, html, json, shutil
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "episode-template"

SPEAKER_LABEL = {
    "ANCHOR": "ANCHOR",
    "CLERK": "CLERK",
    "CHORUS": "CHORUS",
    "LEDGER": "LEDGER",
    "NONE": "",
}


def esc(text: str) -> str:
    return html.escape(str(text), quote=False)


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def speaker_span(speaker: str, cls: str) -> str:
    label = SPEAKER_LABEL.get(speaker, speaker)
    return f'<span class="{cls}">{esc(label)}</span>' if label else ""


def render_lines(lines, prefix: str, line_cls: str, speaker_cls: str) -> tuple[str, int]:
    out = []
    for i, line in enumerate(lines, start=1):
        out.append(
            f'        <div class="{line_cls}" id="{prefix}{i}">'
            f'{speaker_span(line.get("speaker", "NONE"), speaker_cls)}{esc(line.get("text", ""))}</div>'
        )
    return "\n".join(out), len(lines)


def render_ledger_rows(facts, limit: int = 5) -> tuple[str, int]:
    rows, used = [], facts[:limit]
    for i, f in enumerate(used, start=1):
        value = f.get("value") or "&mdash;"
        note_bits = [b for b in (f.get("unit"), ("as of " + f["as_of"]) if f.get("as_of") else "") if b]
        note = esc(" \u00b7 ".join(note_bits))
        claim = esc(f.get("claim", ""))
        if len(claim) > 210:
            claim = claim[:207].rsplit(" ", 1)[0] + "\u2026"
        rows.append(
            f'        <div class="ld-row" id="ld-row-{i}">\n'
            f'          <div class="ld-id">{esc(f["id"])}</div>\n'
            f'          <div class="ld-claim">{claim}</div>\n'
            f'          <div class="ld-value">{esc(value)}'
            f'{f"<small>{note}</small>" if note else ""}</div>\n'
            f'        </div>'
        )
    return "\n".join(rows), len(used)


def render_credits_facts(facts) -> str:
    out = []
    for f in facts:
        value = esc(f.get("value", "")).strip()
        claim = esc(f.get("claim", ""))
        if len(claim) > 150:
            claim = claim[:147].rsplit(" ", 1)[0] + "\u2026"
        tail = f" <b>{value}</b>" if value else ""
        out.append(
            f'          <div class="cr-fact"><i>{esc(f["id"])}</i>'
            f'<div>{claim}{tail} <em>[{esc(f.get("kind", "claim"))}]</em></div></div>'
        )
    return "\n".join(out)


def render_caption_cues(script: dict, scenes_with_offsets) -> tuple[str, str, int]:
    """Return (html, js_array, count). Cues are timed within each scene."""
    blocks, cues = [], []
    n = 0
    for scene, start in scenes_with_offsets:
        lines = [ln for ln in scene.get("lines", []) if ln.get("text")]
        if not lines:
            continue
        dur = float(scene["duration_s"])
        weights = [max(3, len(ln["text"].split())) for ln in lines]
        total = sum(weights)
        cursor = start + 0.35
        for line, w in zip(lines, weights):
            slot = max(0.8, (dur - 0.6) * (w / total))
            n += 1
            blocks.append(
                f'      <div class="cap-line" id="cap-line-{n}">'
                f'{speaker_span(line.get("speaker", "NONE"), "cap-speaker")}{esc(line["text"])}</div>'
            )
            cues.append([round(cursor, 2), round(min(cursor + slot, start + dur - 0.08), 2)])
            cursor += slot
    return "\n".join(blocks), json.dumps(cues), n


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a Hyperframes episode from a validated script.")
    ap.add_argument("--script", required=True)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ep-no", default="0001")
    ap.add_argument("--no-captions", action="store_true", help="Skip the burned-in caption overlay")
    args = ap.parse_args()

    script, ledger = load(args.script), load(args.ledger)
    facts = {f["id"]: f for f in ledger["facts"]}
    out = Path(args.out)
    if out.exists():
        # --out is owned by the builder: it is recreated on every build.
        shutil.rmtree(out)
    shutil.copytree(TEMPLATES, out)

    ep = script["episode"]
    scenes = script["scenes"]
    title = ep["title"]
    retrieved = ledger.get("source", {}).get("retrieved_at", "")
    date_line = f"RETRIEVED {retrieved}" if retrieved else "TRANSMISSION UNSTAMPED"

    scene_clips, scene_offsets = [], []
    cursor = 0.0
    for i, scene in enumerate(scenes, start=1):
        comp = scene["composition"]
        dur = float(scene["duration_s"])
        comp_id = f"{comp}-{i}"
        src = TEMPLATES / "compositions" / f"{comp}.html"
        if not src.exists():
            print(f"ERROR: no template for composition '{comp}'")
            return 1
        tpl = src.read_text(encoding="utf-8")
        tokens = {
            "COMP_ID": comp_id,
            "EP_NO": args.ep_no,
            "TITLE": esc(title),
            "DATE_LINE": esc(date_line),
            "SCENE_DURATION": f"{dur:g}",
            "HEADLINE": esc(scene.get("headline") or title),
            "EUPH": esc(scene.get("euphemism") or "\u201cWe are making progress.\u201d"),
            "EUPH_TAG": "",
            "MAP_TITLE": esc(scene.get("headline") or "The Border Has Been Improved"),
            "MAP_CAPTION": "",
            "MAP_LABELS": "",
            "LEDGER_TITLE": esc(scene.get("headline") or "The Numbers, As Recorded"),
            "LEDGER_SUB": esc(scene.get("euphemism") or ""),
            "LEDGER_ROWS": "",
            "ROW_COUNT": "0",
            "STAMP": esc(scene.get("stamp") or "FILED"),
            "STAMP_AT": "1.2",
            "STAMP_SUBJECT": esc(scene.get("headline") or title),
            "STAMP_SINCE": "THE LAST CRISIS",
            "FORM_NO": f"{(i * 7 + 13) % 89:02d}B/{i % 9 + 1}",
            "CLERK_LINES": "",
            "LINE_COUNT": "0",
            "SOURCE_TITLE": esc(ledger.get("source", {}).get("title", "")),
            "SOURCE_URL": esc(ledger.get("source", {}).get("url", "") or "URL NOT RECORDED"),
            "RETRIEVED": esc(retrieved or "DATE NOT RECORDED"),
            "CREDITS_FACTS": "",
        }

        cited = [facts[f] for f in scene.get("fact_ids", []) if f in facts]
        if comp in ("ministry-anchor", "the-stamp"):
            lines_html, count = render_lines(
                scene.get("lines", []),
                "ma-line-" if comp == "ministry-anchor" else "st-line-",
                "ma-line" if comp == "ministry-anchor" else "st-line",
                "ma-speaker" if comp == "ministry-anchor" else "st-speaker",
            )
            tokens["ANCHOR_LINES" if comp == "ministry-anchor" else "CLERK_LINES"] = lines_html
            tokens["LINE_COUNT"] = str(count)
            if comp == "the-stamp":
                tokens["STAMP_AT"] = f"{max(0.9, dur - 1.1):g}"
        elif comp == "the-ledger":
            rows, count = render_ledger_rows(cited)
            tokens["LEDGER_ROWS"], tokens["ROW_COUNT"] = rows, str(count)
        elif comp == "map-room":
            notes = []
            for f in cited[:3]:
                val = esc(f.get("value", "") or f.get("claim", ""))
                notes.append(f'        <div class="mr-note"><b>{esc(f["id"])}</b> {val}</div>')
            tokens["MAP_LABELS"] = "\n".join(notes)
            line0 = next((ln["text"] for ln in scene.get("lines", []) if ln.get("text")), "")
            caption = esc(line0) if line0 else esc(cited[0]["claim"] if cited else "")
            tags = " ".join(f'<span style="color:#a31616">{esc(f["id"])}</span>' for f in cited[:3])
            tokens["MAP_CAPTION"] = f"{caption} {tags}".strip()
        elif comp == "credits-sources":
            seen, unique = set(), []
            for s in scenes:
                for fid in s.get("fact_ids", []):
                    if fid in facts and fid not in seen:
                        seen.add(fid)
                        unique.append(facts[fid])
            tokens["CREDITS_FACTS"] = render_credits_facts(unique)

        rendered = tpl
        for key, value in tokens.items():
            rendered = rendered.replace(f"%%{key}%%", value)
        if "%%" in rendered:
            leftover = sorted({seg.split("%%")[0] for seg in rendered.split("%%")[1::2]})
            print(f"ERROR: scene {comp_id} has unfilled tokens: {leftover}")
            return 1

        # Optional narration: injected only when the voice file already exists.
        for ext in (".wav", ".mp3"):
            voice = out / "assets" / f"voice-{scene['id']}{ext}"
            if voice.exists():
                audio = (
                    f'    <audio id="aud-{comp_id}" src="../assets/voice-{scene["id"]}{ext}" '
                    f'data-start="0" data-duration="{dur:g}" data-track-index="4" data-volume="1"></audio>\n'
                )
                rendered = rendered.replace("    <style>", audio + "    <style>", 1)
                break

        (out / "compositions" / f"{comp_id}.html").write_text(rendered, encoding="utf-8")
        scene_clips.append(
            f'        <div id="{comp_id}" data-composition-id="{comp_id}" '
            f'data-composition-src="compositions/{comp_id}.html" data-start="{cursor:g}" '
            f'data-duration="{dur:g}" data-width="1920" data-height="1080" '
            f'data-track-index="10" style="position:absolute;inset:0;z-index:10"></div>'
        )
        scene_offsets.append((scene, cursor))
        cursor += dur

    total = round(cursor, 2)

    # Remove the unused scene templates from the built project.
    used = {f"{s['composition']}-{i}" for i, s in enumerate(scenes, start=1)}
    for html_file in (out / "compositions").glob("*.html"):
        if html_file.stem not in used:
            html_file.unlink()

    captions_clip = ""
    if not args.no_captions:
        cap_html, cap_cues, cap_count = render_caption_cues(script, scene_offsets)
        cap_tpl = (TEMPLATES / "compositions" / "captions.html").read_text(encoding="utf-8")
        cap_rendered = (
            cap_tpl.replace("%%COMP_ID%%", "captions")
            .replace("%%CAPTION_LINES%%", cap_html)
            .replace("%%CAPTION_CUES%%", cap_cues)
        )
        (out / "compositions" / "captions.html").write_text(cap_rendered, encoding="utf-8")
        captions_clip = (
            f'      <div id="captions" data-composition-id="captions" '
            f'data-timeline-role="captions" data-caption-root="true" data-track-kind="captions" '
            f'data-composition-src="compositions/captions.html" data-start="0" '
            f'data-duration="{total:g}" data-width="1920" data-height="1080" '
            f'data-track-index="50" style="position:absolute;inset:0;z-index:92"></div>'
        )

    index_tpl = (TEMPLATES / "index.html").read_text(encoding="utf-8")
    index = (
        index_tpl.replace("%%TITLE%%", esc(title))
        .replace("%%SCENE_CLIPS%%", "\n".join(scene_clips))
        .replace("%%CAPTIONS_CLIP%%", captions_clip)
        .replace("%%DURATION%%", f"{total:g}")
    )
    (out / "index.html").write_text(index, encoding="utf-8")

    (out / "meta.json").write_text(
        json.dumps(
            {
                "name": title,
                "slug": ep.get("slug", out.name),
                "series": "The Ministry of Peace",
                "episode_no": args.ep_no,
                "duration_s": total,
                "facts_cited": sorted({fid for s in scenes for fid in s.get("fact_ids", [])}),
                "source_title": ledger.get("source", {}).get("title", ""),
                "source_url": ledger.get("source", {}).get("url", ""),
                "retrieved_at": retrieved,
                "voice": "pending" if not (out / "assets").exists() else "check assets/",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    data_dir = out / "data"
    data_dir.mkdir(exist_ok=True)
    shutil.copy(args.script, data_dir / "script.json")
    shutil.copy(args.ledger, data_dir / "fact-ledger.json")

    print(f"OK  built {out}  scenes={len(scenes)}  duration={total:g}s  captions={'off' if args.no_captions else 'on'}")
    print(f"Next: cd {out} && npx hyperframes lint && npx hyperframes dev")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
