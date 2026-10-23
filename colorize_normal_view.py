"""Give the baked Normal View a cyan, lavender, and pink display palette.

Run after ``blender -b -t 8 --python make_normal_view.py``. The raw tangent
and object-space normal maps stay untouched; only the display texture embedded
in the Normal View GLB is recolored.
"""

import json
from pathlib import Path
import struct

import numpy as np
from PIL import Image


ASSETS = Path(__file__).resolve().parent / "assets"
RAW = ASSETS / "decorative-plush-horse-normal-view-texture.png"
COLORED = ASSETS / "decorative-plush-horse-normal-view-color.png"
MODEL = ASSETS / "decorative-plush-horse-normal-view.glb"

raw = np.asarray(Image.open(RAW).convert("RGB"), dtype=np.float32)
r, g, b = raw[..., 0], raw[..., 1], raw[..., 2]
colored = np.stack((
    48 + 0.56 * r + 0.12 * b,
    98 + 0.46 * g + 0.22 * b,
    122 + 0.40 * b + 0.15 * r,
), axis=-1)
colored[raw.max(axis=-1) == 0] = 0
Image.fromarray(np.uint8(np.clip(colored, 0, 255)), "RGB").save(COLORED)
png = COLORED.read_bytes()

with MODEL.open("rb") as handle:
    magic, version, _ = struct.unpack("<4sII", handle.read(12))
    assert magic == b"glTF" and version == 2
    json_length, json_type = struct.unpack("<I4s", handle.read(8))
    assert json_type == b"JSON"
    gltf = json.loads(handle.read(json_length))
    bin_length, bin_type = struct.unpack("<I4s", handle.read(8))
    assert bin_type == b"BIN\x00"
    binary = handle.read(bin_length)

assert len(gltf["images"]) == 1
image = gltf["images"][0]
assert image["mimeType"] == "image/png"
view = gltf["bufferViews"][image["bufferView"]]
offset = view["byteOffset"]
assert offset + view["byteLength"] >= len(binary) - 3  # The texture is last.
binary = binary[:offset] + png
binary += b"\x00" * (-len(binary) % 4)
view["byteLength"] = len(png)
gltf["buffers"][0]["byteLength"] = len(binary)
image["name"] = "decorative-plush-horse-normal-view-color"

json_bytes = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
json_bytes += b" " * (-len(json_bytes) % 4)
total_length = 12 + 8 + len(json_bytes) + 8 + len(binary)
temporary = MODEL.with_suffix(".glb.tmp")
with temporary.open("wb") as handle:
    handle.write(struct.pack("<4sII", b"glTF", 2, total_length))
    handle.write(struct.pack("<I4s", len(json_bytes), b"JSON"))
    handle.write(json_bytes)
    handle.write(struct.pack("<I4s", len(binary), b"BIN\x00"))
    handle.write(binary)
temporary.replace(MODEL)
print(f"Wrote {COLORED} and recolored {MODEL}")
