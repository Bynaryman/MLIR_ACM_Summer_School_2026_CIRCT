#!/usr/bin/env python3
"""Render the SKY130 inverter GDS as a layered 3D PNG.

Run this script with the system Python. It extracts polygons with KLayout's
Python bindings, then invokes Blender to render those exact polygons.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GDS = ROOT / "assets/gds/sky130_fd_sc_hd__inv_1.gds"
DEFAULT_OUTPUT = ROOT / "assets/images/digital-design/sky130-inverter-gds-3d.png"


LAYER_STYLE = {
    # GDS layer/datatype: display name, z origin, thickness, material
    (64, 20): ("nwell", 0.06, 0.055, "nwell"),
    (65, 20): ("diffusion", 0.12, 0.055, "diffusion"),
    (93, 44): ("n implant", 0.18, 0.025, "nimplant"),
    (94, 20): ("p implant", 0.18, 0.025, "pimplant"),
    (66, 20): ("polysilicon", 0.23, 0.085, "poly"),
    (66, 44): ("local contacts", 0.31, 0.19, "contact"),
    (67, 20): ("local interconnect", 0.50, 0.085, "li"),
    (67, 44): ("metal contacts", 0.58, 0.22, "contact"),
    (68, 20): ("metal 1", 0.80, 0.11, "metal1"),
}


def polygon_points(shape):
    import klayout.db as kdb

    if shape.is_box():
        polygon = kdb.Polygon(shape.box)
    elif shape.is_polygon():
        polygon = shape.polygon
    elif shape.is_path():
        polygon = shape.path.polygon()
    else:
        return None
    return [[point.x, point.y] for point in polygon.each_point_hull()]


def extract_geometry(gds_path: Path) -> dict:
    import klayout.db as kdb

    layout = kdb.Layout()
    layout.read(str(gds_path))
    cell = layout.top_cell()
    if cell is None:
        raise RuntimeError(f"No top cell in {gds_path}")

    bbox = cell.bbox()
    geometry = {
        "cell": cell.name,
        "dbu": layout.dbu,
        "bbox": [bbox.left, bbox.bottom, bbox.right, bbox.top],
        "layers": [],
    }

    for layer_index in layout.layer_indices():
        info = layout.get_info(layer_index)
        key = (info.layer, info.datatype)
        if key not in LAYER_STYLE:
            continue
        name, z, thickness, material = LAYER_STYLE[key]
        polygons = []
        for shape in cell.shapes(layer_index).each():
            points = polygon_points(shape)
            if points:
                polygons.append(points)
        if polygons:
            geometry["layers"].append(
                {
                    "name": name,
                    "z": z,
                    "thickness": thickness,
                    "material": material,
                    "polygons": polygons,
                }
            )
    return geometry


def look_at(obj, point):
    import mathutils

    direction = mathutils.Vector(point) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def make_material(name, color, metallic=0.0, roughness=0.35):
    import bpy

    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return material


def add_prism(name, points, z, thickness, material, scale, center):
    import bpy

    vertices_2d = [
        ((x - center[0]) * scale, (y - center[1]) * scale)
        for x, y in points
    ]
    count = len(vertices_2d)
    vertices = [(x, y, z) for x, y in vertices_2d]
    vertices += [(x, y, z + thickness) for x, y in vertices_2d]

    faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
    faces += [
        (index, (index + 1) % count, (index + 1) % count + count, index + count)
        for index in range(count)
    ]

    mesh = bpy.data.meshes.new(f"{name}-mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bevel = obj.modifiers.new("edge softness", "BEVEL")
    bevel.width = 0.012
    bevel.segments = 2
    return obj


def render_with_blender(geometry_path: Path, output_path: Path):
    import bpy

    geometry = json.loads(geometry_path.read_text())
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1125
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.filepath = str(output_path)
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100

    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world.color = (0.035, 0.045, 0.055)

    materials = {
        "substrate": make_material("silicon substrate", (0.075, 0.095, 0.105), 0.15, 0.26),
        "nwell": make_material("n-well", (0.12, 0.53, 0.43), 0.05, 0.36),
        "diffusion": make_material("diffusion", (0.18, 0.72, 0.48), 0.0, 0.42),
        "nimplant": make_material("n implant", (0.22, 0.52, 0.80), 0.0, 0.42),
        "pimplant": make_material("p implant", (0.72, 0.25, 0.47), 0.0, 0.42),
        "poly": make_material("polysilicon", (0.88, 0.30, 0.24), 0.05, 0.34),
        "contact": make_material("contacts", (0.72, 0.76, 0.78), 0.82, 0.19),
        "li": make_material("local interconnect", (0.91, 0.66, 0.19), 0.66, 0.23),
        "metal1": make_material("metal 1", (0.15, 0.52, 0.78), 0.78, 0.19),
    }

    left, bottom, right, top = geometry["bbox"]
    center = ((left + right) / 2, (bottom + top) / 2)
    dbu = geometry["dbu"]
    scale = dbu * 2.45

    width = (right - left) * scale
    depth = (top - bottom) * scale
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, -0.13))
    substrate = bpy.context.object
    substrate.name = "silicon base"
    substrate.scale = (width / 2 + 0.28, depth / 2 + 0.28, 0.13)
    substrate.data.materials.append(materials["substrate"])
    bevel = substrate.modifiers.new("rounded base", "BEVEL")
    bevel.width = 0.10
    bevel.segments = 5

    for layer in geometry["layers"]:
        for index, polygon in enumerate(layer["polygons"]):
            add_prism(
                f"{layer['name']} {index + 1}",
                polygon,
                layer["z"],
                layer["thickness"],
                materials[layer["material"]],
                scale,
                center,
            )

    bpy.ops.object.light_add(type="AREA", location=(5.5, -6.5, 9.5))
    key = bpy.context.object
    key.name = "key light"
    key.data.energy = 1050
    key.data.shape = "DISK"
    key.data.size = 6.0
    look_at(key, (0, 0, 0.2))

    bpy.ops.object.light_add(type="AREA", location=(-5.0, 2.5, 6.0))
    fill = bpy.context.object
    fill.name = "fill light"
    fill.data.energy = 750
    fill.data.size = 5.0
    look_at(fill, (0, 0, 0.4))

    bpy.ops.object.light_add(type="AREA", location=(1.0, 7.0, 4.0))
    rim = bpy.context.object
    rim.name = "rim light"
    rim.data.energy = 900
    rim.data.size = 4.0
    look_at(rim, (0, 0, 0.5))

    bpy.ops.object.camera_add(location=(8.8, -11.5, 9.0))
    camera = bpy.context.object
    camera.name = "isometric camera"
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(width, depth) * 1.23
    look_at(camera, (0, 0, 0.34))
    scene.camera = camera

    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)


def parse_blender_arguments():
    separator = sys.argv.index("--") if "--" in sys.argv else len(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument("geometry", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args(sys.argv[separator + 1 :])


def main():
    if "bpy" in sys.modules:
        args = parse_blender_arguments()
        render_with_blender(args.geometry, args.output)
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("--gds", type=Path, default=DEFAULT_GDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    geometry = extract_geometry(args.gds)
    with tempfile.TemporaryDirectory() as temporary_directory:
        geometry_path = Path(temporary_directory) / "inverter-geometry.json"
        geometry_path.write_text(json.dumps(geometry))
        subprocess.run(
            [
                "blender",
                "--background",
                "--python",
                str(Path(__file__).resolve()),
                "--",
                str(geometry_path),
                str(args.output.resolve()),
            ],
            check=True,
        )


if __name__ == "__main__":
    main()
