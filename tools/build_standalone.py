#!/usr/bin/env python3
"""Build the standalone clickable site from the prototype sources.

    python3 tools/build_standalone.py

Reads  prototypes/*.dc.html     (the editable screen sources)
       prototypes/assets/        (images; canvas uploads are named by their upload id)
       archive/<version>/        (frozen earlier versions, already built)
Writes docs/                     (plain HTML that runs in any browser; GitHub Pages serves this folder)

Main.dc.html becomes docs/index.html; every other screen keeps its name with .html.
Canvas image links (/_blob/<id>) point to docs/assets/<id>.<ext>.
Each archive folder is copied to docs/<short name>/, e.g. archive/v1-two-prototypes -> docs/v1/.
Edit the sources in prototypes/, then re-run this script. Do not edit docs/ by hand.
"""
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "prototypes"
ASSETS = SRC / "assets"
ARCHIVE = ROOT / "archive"
OUT = ROOT / "docs"

HEAD_INJECT = (
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    "<style>x-dc{display:none}html,body{margin:0;height:100%;overflow:hidden;background:#0B0D0F}</style>\n"
    '<script src="dc-standalone.js"></script>'
)


def out_name(stem: str) -> str:
    return "index.html" if stem == "Main" else f"{stem}.html"


def asset_for(blob_id: str) -> str:
    matches = sorted(ASSETS.glob(f"{blob_id}.*")) if ASSETS.exists() else []
    if not matches:
        raise SystemExit(f"Missing image for /_blob/{blob_id}: save it as prototypes/assets/{blob_id}.<ext>")
    return f"assets/{matches[0].name}"


def convert(text: str) -> str:
    text = text.replace('<script src="./support.js"></script>', HEAD_INJECT, 1)
    # Links between screens: Foo.dc.html -> Foo.html (Main -> index.html)
    text = re.sub(
        r'href="([A-Za-z0-9_][A-Za-z0-9_.-]*?)\.dc\.html"',
        lambda m: f'href="{out_name(m.group(1))}"',
        text,
    )
    # Canvas uploads -> local asset files
    text = re.sub(r"/_blob/([A-Za-z0-9]+)", lambda m: asset_for(m.group(1)), text)
    return text


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(ROOT / "tools" / "dc-standalone.js", OUT / "dc-standalone.js")
    (OUT / ".nojekyll").write_text("")
    if ASSETS.exists():
        shutil.copytree(ASSETS, OUT / "assets")
    count = 0
    for src in sorted(SRC.glob("*.dc.html")):
        stem = src.name[: -len(".dc.html")]
        (OUT / out_name(stem)).write_text(convert(src.read_text(encoding="utf-8")), encoding="utf-8")
        count += 1
    archived = []
    if ARCHIVE.exists():
        for folder in sorted(p for p in ARCHIVE.iterdir() if p.is_dir()):
            short = folder.name.split("-")[0]  # v1-two-prototypes -> v1
            shutil.copytree(folder, OUT / short)
            archived.append(short)
    print(f"Built {count} screens into {OUT.relative_to(ROOT)}/" + (f"; archived versions: {', '.join(archived)}" if archived else ""))


if __name__ == "__main__":
    main()
