# Planning and acceptance

Use this reference to turn an underspecified mechanical idea into a reproducible SolidWorks plan.

## 1. Authority order

When sources disagree, use this default order unless the user overrides it:

1. explicit numeric dimensions and tolerances;
2. authoritative CAD/drawing annotations;
3. manufacturer specifications;
4. scaled measurements from a calibrated image;
5. visual proportion;
6. aesthetic inference.

Record conflicts instead of silently blending them.

## 2. Parameter table

Create a table with at least these fields:

| Parameter | Symbol | Value | Unit | Authority | Used by | Validation |
|---|---|---:|---|---|---|---|
| Outer diameter | `housing_od` | 172 | mm | user dimension | housing, covers | bounding box |
| Pin count | `pin_count` | 18 | count | mechanism requirement | pin pattern | component count |
| Axial clearance | `disc_gap` | 1.0 | mm | conceptual assumption | assembly stack | section view |

Convert API length values once at the boundary: `metres = millimetres / 1000`.

## 3. Assembly coordinate contract

Define before part creation:

- global origin and positive directions;
- main rotation/translation axis;
- reference face for axial stack values;
- angular zero and rotation direction;
- component insertion origin;
- phase conventions for repeated or paired parts.

For an axial mechanism, maintain a stack table:

| Item | Start Z | Thickness | End Z | Interface/clearance |
|---|---:|---:|---:|---|
| Rear cover | -7 | 6 | -1 | housing face |
| Mechanism | 0 | 26 | 26 | internal envelope |
| Front cover | 27 | 6 | 33 | 1 mm gap |

## 4. Component classification

Choose the simplest stable feature strategy:

- **Axisymmetric:** revolve when design intent matters; stacked extrudes are acceptable for a concept.
- **Prismatic:** sketch/extrude, then cuts and edge treatments.
- **Patterned:** model one seed component, then use a circular/linear pattern or repeated assembly insertion.
- **Profile-driven:** use a closed polyline/spline with enough resolution; validate closure and self-intersection.
- **Purchased:** preserve supplier part identity and source; do not redraw unless necessary.

## 5. Feature ordering

Use this default order to reduce topology breakage:

1. master/base feature;
2. functional bosses and webs;
3. functional cuts and bores;
4. repeated patterns;
5. fillets and chamfers;
6. cosmetic features and appearance.

Avoid referencing faces likely to disappear after later cuts. Prefer planes, axes, origin geometry, and named sketches.

## 6. Model-status levels

Declare one level in the handoff:

- **Concept:** geometry communicates arrangement; absolute transforms and assumed clearances are allowed.
- **Engineering layout:** principal dimensions, mates, and interfaces are authoritative; manufacturing details may be incomplete.
- **Production-authoritative:** tolerances, materials, fits, fasteners, manufacturability, and analysis have been reviewed.

Do not call a model production-ready without evidence for the last level.

## 7. Acceptance matrix

Write checks before building:

| Requirement | Evidence | Pass condition |
|---|---|---|
| Ten unique part types | output directory | 10 nonempty `.SLDPRT` files |
| Complete assembly | SolidWorks tree/log | expected component count and clean rebuild |
| Process recording | FFprobe/contact sheet | full duration, target resolution, start-to-finish coverage |
| Editable design | feature tree | intended features or disclosed direct/imported bodies |

If a requirement has no observable evidence, it is not yet an acceptance criterion.
