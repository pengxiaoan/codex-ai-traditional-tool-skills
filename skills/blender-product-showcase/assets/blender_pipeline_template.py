"""Reusable Blender project core.

Copy this file to a generated project's scripts/project_pipeline.py, then
implement the four product-specific build functions.  Path handling,
configuration, saving, collection ownership, and still rendering are reusable.
"""

from __future__ import annotations

import json
from pathlib import Path

import bpy


PROJECT = Path(__file__).resolve().parents[1]
SPEC_PATH = PROJECT / "project_spec.json"


def log(message: str) -> None:
    print(f"[PRODUCT_SHOWCASE] {message}", flush=True)


def load_spec() -> dict:
    with SPEC_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_project_path(relative_path: str) -> Path:
    resolved = (PROJECT / relative_path).resolve()
    resolved.relative_to(PROJECT.resolve())
    return resolved


def ensure_output_dirs(spec: dict) -> None:
    outputs = spec["outputs"]
    for key in ("previews", "frames"):
        resolve_project_path(outputs[key]).mkdir(parents=True, exist_ok=True)
    for key in ("video", "hero_still"):
        resolve_project_path(outputs[key]).parent.mkdir(parents=True, exist_ok=True)


def owned_collection(name: str, clear: bool = False) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    if clear:
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    return collection


def configure_scene(spec: dict) -> None:
    scene = bpy.context.scene
    animation = spec["animation"]
    render = spec["render"]
    scene.unit_settings.system = "METRIC"
    scene.frame_start = int(animation["frame_start"])
    scene.frame_end = int(animation["frame_end"])
    scene.render.fps = int(animation["fps"])
    scene.render.fps_base = 1.0
    scene.render.resolution_x = int(render["resolution"][0])
    scene.render.resolution_y = int(render["resolution"][1])
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    engine = str(render.get("engine", "CYCLES")).upper()
    scene.render.engine = "CYCLES" if engine == "CYCLES" else "BLENDER_EEVEE"
    if scene.render.engine == "CYCLES":
        scene.cycles.samples = int(render.get("final_samples", 192))
        scene.cycles.preview_samples = int(render.get("preview_samples", 32))
        scene.cycles.use_denoising = True
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    ensure_output_dirs(spec)


def save_project(spec: dict) -> Path:
    target = resolve_project_path(spec["outputs"]["blend_file"])
    bpy.ops.wm.save_as_mainfile(filepath=str(target))
    log(f"Saved {target}")
    return target


def render_still(frame: int, relative_path: str) -> Path:
    scene = bpy.context.scene
    scene.frame_set(int(frame))
    target = resolve_project_path(relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(target)
    bpy.ops.render.render(write_still=True)
    return target


def check_project() -> None:
    spec = load_spec()
    configure_scene(spec)
    log(f"Blender {bpy.app.version_string}; project={PROJECT}")


def build_product() -> None:
    raise NotImplementedError("Implement product-specific geometry from project_spec.json")


def create_materials() -> None:
    raise NotImplementedError("Implement product-specific materials and texture bindings")


def setup_studio() -> None:
    raise NotImplementedError("Implement the studio, lighting rig, and cameras")


def create_animation() -> None:
    raise NotImplementedError("Implement product, camera, light, and material animation")


def render_previews() -> None:
    raise NotImplementedError("Render representative approval frames from the shot plan")


def render_final() -> None:
    raise NotImplementedError("Render the lossless sequence, hero still, and video delivery")
