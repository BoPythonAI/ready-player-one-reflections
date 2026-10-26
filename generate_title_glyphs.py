"""Extract the article title as portable SVG outlines from ZCOOL KuaiLe.

Usage: python generate_title_glyphs.py path/to/ZCOOLKuaiLe-Regular.ttf
Source: https://github.com/google/fonts/tree/main/ofl/zcoolkuaile
Requires fonttools only when updating the title or font; build.py uses the saved outlines.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont


ROOT = Path(__file__).parent
parser = argparse.ArgumentParser()
parser.add_argument("font", type=Path)
args = parser.parse_args()

title = (ROOT / "article.md").read_text(encoding="utf-8").splitlines()[0].removeprefix("# ")
font = TTFont(args.font)
glyph_set = font.getGlyphSet()
cmap = font.getBestCmap()
glyphs = []
for char in title:
    glyph_name = cmap.get(ord(char))
    if glyph_name is None:
        raise ValueError(f"Font lacks title character: {char}")
    pen = SVGPathPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    glyphs.append({
        "char": char,
        "advance": font["hmtx"][glyph_name][0],
        "path": pen.getCommands(),
    })

data = {
    "title": title,
    "font": "ZCOOL KuaiLe",
    "font_sha256": sha256(args.font.read_bytes()).hexdigest(),
    "units_per_em": font["head"].unitsPerEm,
    "glyphs": glyphs,
}
output = ROOT / "assets" / "cartoon-title-glyphs.json"
output.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
print(f"Wrote {output} ({len(glyphs)} glyphs)")
