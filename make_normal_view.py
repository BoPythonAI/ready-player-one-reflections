"""Bake a model's shaded normals into a viewable GLB with no lighting dependency.

Run with Blender 5.2+: blender -b -t 8 --python make_normal_view.py
Pass -- --source assets/monkey-king-original.glb --prefix monkey-king for another model.
The tangent normal map is extracted byte-for-byte from the input GLB. The baked
object-space normal texture combines its detail with the mesh surface normals.
"""

import json
from pathlib import Path
import struct
import sys
import argparse

import bpy


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
parser = argparse.ArgumentParser()
parser.add_argument("--source", type=Path, default=ASSETS / "decorative-plush-horse-optimized.glb")
parser.add_argument("--prefix", default="decorative-plush-horse")
parser.add_argument("--preview", action="store_true")
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
SOURCE = args.source if args.source.is_absolute() else ROOT / args.source
VIEW_MAP = ASSETS / f"{args.prefix}-normal-view-texture.png"
VIEW_GLB = ASSETS / f"{args.prefix}-normal-view.glb"


def read_glb(path):
    with path.open("rb") as handle:
        magic, version, total_length = struct.unpack("<4sII", handle.read(12))
        assert magic == b"glTF" and version == 2 and total_length == path.stat().st_size
        json_length, json_type = struct.unpack("<I4s", handle.read(8))
        assert json_type == b"JSON"
        gltf = json.loads(handle.read(json_length))
        binary_length, binary_type = struct.unpack("<I4s", handle.read(8))
        assert binary_type == b"BIN\x00"
        binary = handle.read(binary_length)
    return gltf, binary


def write_glb(path, gltf, binary):
    json_bytes = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    json_bytes += b" " * (-len(json_bytes) % 4)
    binary += b"\x00" * (-len(binary) % 4)
    total_length = 12 + 8 + len(json_bytes) + 8 + len(binary)
    with path.open("wb") as handle:
        handle.write(struct.pack("<4sII", b"glTF", 2, total_length))
        handle.write(struct.pack("<I4s", len(json_bytes), b"JSON"))
        handle.write(json_bytes)
        handle.write(struct.pack("<I4s", len(binary), b"BIN\x00"))
        handle.write(binary)


source_gltf, source_binary = read_glb(SOURCE)
normal_texture = next(material["normalTexture"] for material in source_gltf["materials"] if "normalTexture" in material)
image = source_gltf["images"][source_gltf["textures"][normal_texture["index"]]["source"]]
extension = {"image/png": "png", "image/jpeg": "jpg"}[image["mimeType"]]
TANGENT_MAP = ASSETS / f"{args.prefix}-normal-map.{extension}"
view = source_gltf["bufferViews"][image["bufferView"]]
offset = view.get("byteOffset", 0)
TANGENT_MAP.write_bytes(source_binary[offset:offset + view["byteLength"]])

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
assert len(meshes) == 1 and meshes[0].data.uv_layers
mesh = meshes[0]

if args.preview:
    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.export_scene.gltf(
        filepath=str(ASSETS / f"{args.prefix}-preview.glb"),
        export_format="GLB", use_selection=True,
        export_image_format="AUTO", export_copyright="BoPythonAI",
        export_draco_mesh_compression_enable=True,
    )

# Keep the imported PBR material while baking: its tangent normal map supplies
# fine details that would be absent from geometry normals alone.
image = bpy.data.images.new(f"{args.prefix} Normal View", width=2048, height=2048, alpha=False)
for material in mesh.data.materials:
    target = material.node_tree.nodes.new("ShaderNodeTexImage")
    target.name = "Normal View Bake Target"
    target.image = image
    material.node_tree.nodes.active = target

bpy.ops.object.select_all(action="DESELECT")
mesh.select_set(True)
bpy.context.view_layer.objects.active = mesh
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 1
scene.render.bake.margin = 8
scene.render.bake.normal_space = "OBJECT"
bpy.ops.object.bake(type="NORMAL")
image.filepath_raw = str(VIEW_MAP)
image.file_format = "PNG"
image.save()

# The baked RGB values are a visualization, not a normal map for lighting.
# Put them in base color and mark the exported material KHR_materials_unlit.
material = bpy.data.materials.new("Normal View")
material.use_nodes = True
nodes = material.node_tree.nodes
nodes.clear()
texture_node = nodes.new("ShaderNodeTexImage")
texture_node.image = image
principled = nodes.new("ShaderNodeBsdfPrincipled")
output = nodes.new("ShaderNodeOutputMaterial")
material.node_tree.links.new(texture_node.outputs["Color"], principled.inputs["Base Color"])
material.node_tree.links.new(principled.outputs["BSDF"], output.inputs["Surface"])
mesh.data.materials.clear()
mesh.data.materials.append(material)

bpy.ops.export_scene.gltf(
    filepath=str(VIEW_GLB), export_format="GLB", use_selection=True,
    export_image_format="AUTO", export_copyright="BoPythonAI",
    export_draco_mesh_compression_enable=True,
)
gltf, binary = read_glb(VIEW_GLB)
used = gltf.setdefault("extensionsUsed", [])
if "KHR_materials_unlit" not in used:
    used.append("KHR_materials_unlit")
for material in gltf["materials"]:
    material.setdefault("extensions", {})["KHR_materials_unlit"] = {}
write_glb(VIEW_GLB, gltf, binary)
print(f"Wrote {TANGENT_MAP}, {VIEW_MAP}, {VIEW_GLB}")
