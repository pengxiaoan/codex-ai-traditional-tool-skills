---
name: blender-product-showcase
description: Create, rebuild, animate, validate, and render editable Blender product models from a design brief, reference images, textures, drawings, or an existing 3D model. Use for Blender product visualization, hard-surface modeling, logo-free concept products, studio lighting, camera animation, keyframe previews, PNG sequences, hero stills, MP4 delivery, reusable Blender Python stage scripts, or a complete .blend project.
---

# Blender Product Showcase

Build a source-backed, editable Blender product scene and a cinematic showcase animation. Execute the work in Blender; do not stop at advice or sample code.

## Inputs

Collect or infer:

- Workspace root and project slug.
- Product category, dimensions, required parts, and assembly relationships.
- Reference images, drawings, textures, optional models, and their intended uses.
- Brand policy: default to logo-free when permission is unclear.
- Video duration, aspect ratio, resolution, frame rate, shots, and render budget.

If the workspace lacks structure, run:

```bash
python scripts/init_project.py --root <workspace> --slug <project-slug> --name "<product name>"
```

Use `assets/project-spec.example.json` as the machine-readable input example. Read `references/prompt-template.md` when writing or expanding the production prompt.

## Workflow

### 1. Inspect and normalize

1. Enumerate only the user-scoped workspace.
2. Read the brief and classify each asset as geometry, material, lighting, camera, or composition reference.
3. Validate the project with `scripts/validate_project.py <project-dir>`.
4. Record missing required inputs. Continue with procedural modeling when an external model is optional.
5. Preserve unrelated files and existing Blender work.

### 2. Choose the modeling path

- Reuse an existing model when licensing, topology, scale, and editability are acceptable.
- Programmatically rebuild when no model exists, dimensions are explicit, or repeatability matters.
- Use a hybrid approach when a clean base model needs procedural details, hierarchy, materials, or animation.

Keep visible parts separate. Name objects, materials, lights, cameras, and collections semantically. Establish real pivots before animation. Apply transforms deliberately, correct normals, bevel visible edges, and avoid non-manifold or intersecting geometry.

### 3. Implement repeatable stages

Maintain these scripts in the generated project:

1. `01_check_project.py`
2. `02_build_product.py`
3. `03_create_materials.py`
4. `04_setup_studio.py`
5. `05_create_animation.py`
6. `06_render_previews.py`
7. `07_render_final.py`

Make every stage idempotent, scoped to the project, and explicit about errors. Save the `.blend` after each material stage.

### 4. Build the scene

Create:

- A root object and meaningful assembly hierarchy.
- Physically plausible materials with restrained micro-surface detail.
- A wide, seamless studio with floor contact and controlled reflections.
- Soft key light, cool rim light, optional warm edge light, and restrained fill.
- Named cameras with a shared or intentionally animated focus target.
- Product, component, screen/display, light, and camera animations as required.

Use the supplied textures for their declared purpose. Do not use reference images as final backgrounds unless explicitly requested.

### 5. Preview and correct

Render representative frames before the full sequence. Read `references/quality-checklist.md` and correct:

- Cropping, empty composition, wrong scale, or unintended wide-angle distortion.
- Intersections, floating parts, broken pivots, incorrect normals, or inconsistent hierarchy.
- Plastic-looking metal, dead-black details, clipped highlights, or unreadable screen content.
- Mechanical camera motion, discontinuous cuts, focus drift, or excessive depth of field.
- Logos, text, or identifiers that violate the brief.

Re-render failed preview frames after correction.

### 6. Render and deliver

Prefer a lossless image sequence before encoding video. Match the requested engine and quality; use a documented fast-preview profile only when the user prioritizes speed.

Deliver, when requested:

- Editable `.blend` project.
- Seven stage scripts and any shared helpers.
- Preview frames.
- Full PNG or EXR sequence.
- H.264 MP4 at the requested frame rate.
- High-resolution hero still.
- Project-specific usage notes covering assets, hierarchy, materials, lights, cameras, animation, and rerendering.

Leave Blender on a rendered result or rendered viewport when the user is recording the visible process. Distinguish solid/wireframe playback from a true render.

## Resource routing

- Read `references/prompt-template.md` to generate a complete reusable production prompt.
- Read `references/project-spec.md` to interpret or author `project_spec.json`.
- Read `references/quality-checklist.md` before approving preview or final renders.
- Run `scripts/build_prompt_docx.py` when a user needs the generalized prompt as DOCX.
- Copy from `assets/project-spec.example.json` when starting a custom project spec.

## Constraints

- Keep all generated assets and scripts inside the scoped project unless the user chooses another destination.
- Do not download unknown models, add-ons, HDRIs, or scripts.
- Do not introduce third-party branding or copyrighted marks without permission.
- Do not claim a full animation is rendered when only viewport playback or still frames exist.
- Do not overwrite an unrelated `.blend`; save to the project path or an explicitly approved target.
