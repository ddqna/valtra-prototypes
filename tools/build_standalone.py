#!/usr/bin/env python3
"""Build the standalone clickable site from the prototype sources.

    python3 tools/build_standalone.py

Reads  prototypes/*.dc.html  (the editable screen sources)
Writes docs/                  (plain HTML that runs in any browser; GitHub Pages serves this folder)

Main.dc.html becomes docs/index.html; every other screen keeps its name with .html.
Edit the sources in prototypes/, then re-run this script. Do not edit docs/ by hand.
"""
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "prototypes"
OUT = ROOT / "docs"

HEAD_INJECT = (
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    "<style>x-dc{display:none}html,body{margin:0;height:100%;overflow:hidden;background:#0B0D0F}</style>\n"
    '<script src="dc-standalone.js"></script>'
)


def out_name(stem: str) -> str:
    return "index.html" if stem == "Main" else f"{stem}.html"


def convert(text: str) -> str:
    text = text.replace('<script src="./support.js"></script>', HEAD_INJECT, 1)
    # Links between screens: Foo.dc.html -> Foo.html (Main -> index.html)
    text = re.sub(
        r'href="([A-Za-z0-9_][A-Za-z0-9_.-]*?)\.dc\.html"',
        lambda m: f'href="{out_name(m.group(1))}"',
        text,
    )
    return text


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(ROOT / "tools" / "dc-standalone.js", OUT / "dc-standalone.js")
    (OUT / ".nojekyll").write_text("")
    count = 0
    for src in sorted(SRC.glob("*.dc.html")):
        stem = src.name[: -len(".dc.html")]
        (OUT / out_name(stem)).write_text(convert(src.read_text(encoding="utf-8")), encoding="utf-8")
        count += 1
    print(f"Built {count} screens into {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
