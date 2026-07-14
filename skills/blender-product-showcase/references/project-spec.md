# Project specification

Use `project_spec.json` as the stable contract between the brief, Blender scripts, and validation.

## Required fields

- `project.slug`: lowercase filesystem-safe identifier.
- `product.name`: user-facing product name.
- `product.category`: broad class such as laptop, appliance, tool, gearbox, or vehicle component.
- `product.brand_policy`: `logo-free`, `provided-brand-assets-only`, or `user-approved`.
- `geometry.dimensions_m`: width, depth, and height in meters.
- `geometry.parts`: required visible parts and optional parent names.
- `animation.duration_seconds`, `fps`, `frame_start`, and `frame_end`.
- `render.aspect_ratio`, `resolution`, `preview_samples`, `final_samples`, and `engine`.
- `outputs`: blend file, preview directory, frame directory, video path, and hero still path.

## Optional fields

- `assets.references`, `assets.textures`, and `assets.models`.
- `geometry.pivots`, `geometry.clearances_m`, and `geometry.modeling_notes`.
- `materials` with physically based targets.
- `studio`, `lights`, `shots`, and `validation` rules.
- `delivery.fast_preview_profile` for a lower-cost approval render.

## Rules

- Resolve relative paths from the project directory.
- Treat missing optional assets as a procedural-build signal, not an automatic failure.
- Fail validation when required dimensions are non-positive, the frame range disagrees with duration and fps, or output paths escape the project directory.
- Keep units in meters in JSON; convert to display units only in documentation or the Blender UI.
