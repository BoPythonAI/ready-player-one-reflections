"""Render a small animated README preview from the original GLB.

Requires Open3D, Pillow, and NumPy. The interactive model remains in GitHub Pages.
"""

from math import cos, pi, sin
from pathlib import Path

# Some notebook-focused Python installs have a broken comm provider that Open3D
# imports indirectly through Dash. The renderer does not use notebook comms.
import comm
comm.create_comm = lambda **kwargs: None

import numpy as np
import open3d as o3d
from PIL import Image


ROOT = Path(__file__).parent
model = o3d.io.read_triangle_mesh(
    str(ROOT / "assets" / "decorative-plush-horse.glb"),
    enable_post_processing=True,
)
viewer = o3d.visualization.Visualizer()
if not viewer.create_window("Horse preview render", 420, 420, visible=False):
    raise RuntimeError("Could not create a hidden Open3D rendering window")

try:
    viewer.add_geometry(model)
    render_options = viewer.get_render_option()
    view = viewer.get_view_control()
    view.set_lookat(model.get_axis_aligned_bounding_box().get_center())
    view.set_up([0, 1, 0])

    frames = []
    frame_count = 24
    for index in range(frame_count):
        angle = 2 * pi * index / frame_count + 0.35
        view.set_front([sin(angle), 0.08, cos(angle)])
        view.set_zoom(0.85)
        viewer.poll_events()
        render_options.background_color = [0, 0, 0]
        viewer.update_renderer()
        on_black = np.asarray(viewer.capture_screen_float_buffer(do_render=True)).copy()
        render_options.background_color = [1, 1, 1]
        viewer.update_renderer()
        on_white = np.asarray(viewer.capture_screen_float_buffer(do_render=True)).copy()

        # The difference between the two renders reveals edge coverage. Remove
        # the background before shrinking so the GIF stays transparent on GitHub.
        alpha = np.clip(1 - np.mean(on_white - on_black, axis=2), 0, 1)
        rgb = np.clip(on_black / np.maximum(alpha[..., None], 0.01), 0, 1)
        rgba = np.dstack((rgb, alpha))
        frame = Image.fromarray(np.uint8(np.clip(rgba * 255, 0, 255)), "RGBA")
        frames.append(frame.resize((300, 300), Image.Resampling.LANCZOS))
finally:
    viewer.destroy_window()

# Keep palette entry zero for transparency, using one palette for all frames.
palette_source = Image.new("RGB", (300, 300 * len(frames)))
for index, frame in enumerate(frames):
    palette_source.paste(frame.convert("RGB"), (0, index * 300))
palette = palette_source.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
colors = [0, 0, 0] + palette.getpalette()[: 255 * 3]
indexed_frames = []
for frame in frames:
    indices = np.asarray(frame.convert("RGB").quantize(palette=palette)).astype(np.uint16) + 1
    indices[np.asarray(frame.getchannel("A")) < 128] = 0
    indexed = Image.fromarray(indices.astype(np.uint8), "P")
    indexed.putpalette(colors)
    indexed_frames.append(indexed)
output = ROOT / "assets" / "horse-turntable-transparent.gif"
indexed_frames[0].save(
    output,
    save_all=True,
    append_images=indexed_frames[1:],
    duration=200,
    loop=0,
    transparency=0,
    optimize=True,
    disposal=2,
)
print(f"Saved {output} ({output.stat().st_size:,} bytes, {len(frames)} frames)")
