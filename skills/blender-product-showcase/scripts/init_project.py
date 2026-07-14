#!/usr/bin/env python3
"""Create a reusable Blender product-showcase project scaffold."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_SPEC = SKILL_ROOT / "assets" / "project-spec.example.json"
PIPELINE_TEMPLATE = SKILL_ROOT / "assets" / "blender_pipeline_template.py"

STAGES = [
    ("01_check_project.py", "check_project"),
    ("02_build_product.py", "build_product"),
    ("03_create_materials.py", "create_materials"),
    ("04_setup_studio.py", "setup_studio"),
    ("05_create_animation.py", "create_animation"),
    ("06_render_previews.py", "render_previews"),
    ("07_render_final.py", "render_final"),
]


def valid_slug(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,62}", value):
        raise argparse.ArgumentTypeError("slug must use lowercase letters, digits, '_' or '-'")
    return value


def write_text(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def stage_source(function_name: str) -> str:
    return f'''"""Generated stage wrapper. Customize project_pipeline.py, not this file."""\nimport sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).resolve().parent))\nfrom project_pipeline import load_spec, configure_scene, save_project, {function_name}\n\n\ndef main():\n    spec = load_spec()\n    configure_scene(spec)\n    {function_name}()\n    save_project(spec)\n\n\nif __name__ == "__main__":\n    main()\n'''


def create_project(root: Path, slug: str, name: str, force: bool) -> Path:
    root = root.resolve()
    project = (root / slug).resolve()
    project.relative_to(root)
    project.mkdir(parents=True, exist_ok=True)
    for relative in (
        "assets/references",
        "assets/textures",
        "assets/models",
        "assets/hdri",
        "scripts",
        "previews",
        "renders/frames",
        "renders/stills",
        "renders/video",
    ):
        (project / relative).mkdir(parents=True, exist_ok=True)

    spec = json.loads(EXAMPLE_SPEC.read_text(encoding="utf-8"))
    spec["project"]["slug"] = slug
    spec["project"]["title"] = name
    spec["product"]["name"] = name
    spec["outputs"]["blend_file"] = f"{slug}.blend"
    spec["outputs"]["video"] = f"renders/video/{slug}.mp4"
    spec["outputs"]["hero_still"] = f"renders/stills/{slug}_hero_4k.png"
    write_text(project / "project_spec.json", json.dumps(spec, ensure_ascii=False, indent=2) + "\n", force)

    pipeline_target = project / "scripts" / "project_pipeline.py"
    if force or not pipeline_target.exists():
        shutil.copyfile(PIPELINE_TEMPLATE, pipeline_target)
    for filename, function_name in STAGES:
        write_text(project / "scripts" / filename, stage_source(function_name), force)

    notes = f"""# {name}\n\nGenerated with the `blender-product-showcase` skill.\n\n1. Edit `project_spec.json`.\n2. Add references, textures, or licensed models under `assets/`.\n3. Implement product-specific functions in `scripts/project_pipeline.py`.\n4. Run the seven stages in Blender in numerical order.\n5. Approve preview frames before rendering the final sequence.\n"""
    write_text(project / "PROJECT_NOTES.md", notes, force)
    return project


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Parent workspace directory")
    parser.add_argument("--slug", type=valid_slug, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--force", action="store_true", help="Overwrite generated text templates")
    args = parser.parse_args()
    project = create_project(args.root, args.slug, args.name, args.force)
    print(project)


if __name__ == "__main__":
    main()
