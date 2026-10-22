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
    viewer.get_render_option().background_color = [0.04, 0.08, 0.17]
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
        viewer.update_renderer()
        pixels = np.asarray(viewer.capture_screen_float_buffer(do_render=True))
        frame = Image.fromarray(np.uint8(np.clip(pixels * 255, 0, 255)))
        frames.append(frame.resize((300, 300), Image.Resampling.LANCZOS))
finally:
    viewer.destroy_window()

# Use one palette for every frame to avoid color shifts during the loop.
palette_source = Image.new("RGB", (300, 300 * len(frames)))
for index, frame in enumerate(frames):
    palette_source.paste(frame, (0, index * 300))
palette = palette_source.quantize(colors=192, method=Image.Quantize.MEDIANCUT)
indexed_frames = [frame.quantize(palette=palette) for frame in frames]
output = ROOT / "assets" / "horse-turntable.gif"
indexed_frames[0].save(
    output,
    save_all=True,
    append_images=indexed_frames[1:],
    duration=110,
    loop=0,
    optimize=True,
    disposal=2,
)
print(f"Saved {output} ({output.stat().st_size:,} bytes, {len(frames)} frames)")
