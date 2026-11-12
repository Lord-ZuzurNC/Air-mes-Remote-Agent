#!/usr/bin/env python3
"""Render quick-look preview images of an STL from several angles.

No GPU/X11/OpenGL needed — pure matplotlib (Agg backend) + numpy-stl.
Use this instead of OpenSCAD's own PNG export, which needs a working
GLX context this machine doesn't reliably give a headless terminal.

Usage: render_preview.py model.stl out_prefix
Produces out_prefix_top.png, out_prefix_iso.png, out_prefix_bottom.png
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from stl import mesh


def render(stl_path, out_prefix):
    m = mesh.Mesh.from_file(stl_path)
    scale = m.points.flatten()

    views = {
        "iso": (25, -60),
        "top": (89, -90),     # looking straight down (+Z), see the cavity
        "bottom": (-89, -90), # looking straight up (-Z), see the outer face
        "front": (0, -90),    # looking along +Y, a straight-on side view
    }
    for name, (elev, azim) in views.items():
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection="3d")
        coll = Poly3DCollection(
            m.vectors, facecolor="lightsteelblue", edgecolor="k", linewidths=0.15
        )
        ax.add_collection3d(coll)
        ax.auto_scale_xyz(scale, scale, scale)
        ax.view_init(elev=elev, azim=azim)
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.set_zlabel("Z (mm)")
        plt.tight_layout()
        out = f"{out_prefix}_{name}.png"
        plt.savefig(out, dpi=130)
        plt.close(fig)
        print(out)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
