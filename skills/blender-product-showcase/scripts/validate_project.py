#!/usr/bin/env python3
"""Validate a blender-product-showcase project without launching Blender."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_DIRS = (
    "assets/references",
    "assets/textures",
    "assets/models",
    "scripts",
    "previews",
    "renders/frames",
    "renders/stills",
    "renders/video",
)

REQUIRED_SCRIPTS = (
    "01_check_project.py",
    "02_build_product.py",
    "03_create_materials.py",
    "04_setup_studio.py",
    "05_create_animation.py",
    "06_render_previews.py",
    "07_render_final.py",
)


def inside(project: Path, relative: str) -> bool:
    try:
        (project / relative).resolve().relative_to(project.resolve())
        return True
    except ValueError:
        return False


def validate(project: Path) -> list[str]:
    errors: list[str] = []
    project = project.resolve()
    spec_path = project / "project_spec.json"
    if not spec_path.is_file():
        return ["missing project_spec.json"]
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid project_spec.json: {exc}"]

    for relative in REQUIRED_DIRS:
        if not (project / relative).is_dir():
            errors.append(f"missing directory: {relative}")
    for filename in REQUIRED_SCRIPTS:
        if not (project / "scripts" / filename).is_file():
            errors.append(f"missing script: scripts/{filename}")

    try:
        slug = spec["project"]["slug"]
        name = spec["product"]["name"]
        dims = spec["geometry"]["dimensions_m"]
        animation = spec["animation"]
        render = spec["render"]
        outputs = spec["outputs"]
    except (KeyError, TypeError) as exc:
        errors.append(f"missing required field: {exc}")
        return errors

    if not isinstance(slug, str) or not slug:
        errors.append("project.slug must be a non-empty string")
    if not isinstance(name, str) or not name:
        errors.append("product.name must be a non-empty string")
    for axis in ("width", "depth", "height"):
        if not isinstance(dims.get(axis), (int, float)) or dims[axis] <= 0:
            errors.append(f"geometry.dimensions_m.{axis} must be positive")

    duration = animation.get("duration_seconds")
    fps = animation.get("fps")
    start = animation.get("frame_start")
    end = animation.get("frame_end")
    if not all(isinstance(v, (int, float)) for v in (duration, fps, start, end)):
        errors.append("animation timing fields must be numeric")
    elif int(round(duration * fps)) != int(end - start + 1):
        errors.append("animation duration, fps, and frame range disagree")

    resolution = render.get("resolution")
    if not isinstance(resolution, list) or len(resolution) != 2 or any(not isinstance(v, int) or v <= 0 for v in resolution):
        errors.append("render.resolution must contain two positive integers")

    for key in ("blend_file", "previews", "frames", "video", "hero_still"):
        value = outputs.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"outputs.{key} must be a non-empty relative path")
        elif not inside(project, value):
            errors.append(f"outputs.{key} escapes the project directory")

    for group in ("references", "textures", "models"):
        for item in spec.get("assets", {}).get(group, []):
            if isinstance(item, dict) and item.get("required"):
                path = item.get("path", "")
                if not path or not (project / path).is_file():
                    errors.append(f"missing required asset: {path or group}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    errors = validate(args.project)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"OK: {args.project.resolve()}")


if __name__ == "__main__":
    main()
