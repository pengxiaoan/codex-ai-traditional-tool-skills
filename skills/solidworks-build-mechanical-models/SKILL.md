---
name: solidworks-build-mechanical-models
description: Plan, create, automate, assemble, record, and validate parameterized SolidWorks mechanical models on Windows. Use for SolidWorks parts or assemblies (`.SLDPRT`, `.SLDASM`), complex mechanisms, feature-based or API-assisted modeling, VBScript/COM generation, component placement and mates, modeling-process screen recordings, rebuild verification, previews, and delivery QA. Apply when a user asks to draw, reproduce, modify, document, or record a rigorous SolidWorks workflow from dimensions, sketches, drawings, images, or a mechanical concept.
---

# Build SolidWorks Mechanical Models

Produce an editable SolidWorks deliverable, not only a visually similar shape. Keep geometry, assembly structure, evidence, and recording reproducible.

## Route the task

Choose one execution lane and state it before editing:

- **GUI-first:** use for design intent that depends on interactive constraints, surfacing, loft tuning, or user review.
- **API-first:** use for deterministic primitives, patterned parts, repeated components, or a required full-process replay.
- **Hybrid:** generate stable features/components through the SolidWorks API, then use the GUI for inspection, appearance, mates, motion, and screenshots. Prefer this lane for complex recorded builds.

If controlling the Windows GUI, first use the available Windows computer-control skill and obey its observation and safety rules. Prefer SolidWorks-native APIs for structural edits when available.

## Read only the needed references

- Read [references/planning-and-acceptance.md](references/planning-and-acceptance.md) for every new model or major redesign.
- Read [references/api-automation.md](references/api-automation.md) before writing or changing SolidWorks COM/VBScript automation.
- Read [references/recording-and-validation.md](references/recording-and-validation.md) when the task requires a recording or formal delivery QA.
- Read [references/usage-tutorial.zh-CN.md](references/usage-tutorial.zh-CN.md) when the user asks how to install, invoke, or reuse this skill.

## Workflow

### 1. Define the acceptance contract

Record:

- authoritative dimensions and units;
- SolidWorks version and template paths;
- required parts, subassemblies, configurations, mates, motion, exports, preview images, and recording;
- manufacturing intent, tolerances, fit, material, and analysis requirements;
- which assumptions are conceptual versus production-authoritative.

Do not infer production readiness from a concept model. Mark unverified load, tolerance, material, and manufacturing assumptions explicitly.

### 2. Decompose the mechanism

Create a parameter table and an assembly tree before modeling. Classify each component as:

- rotational primitive;
- prismatic/extruded primitive;
- patterned component;
- profile-driven or freeform component;
- purchased/imported component.

Define a global origin, primary axis, axial stack, radial locations, angular phases, and component count. See the planning reference for the required table format.

### 3. Preflight SolidWorks

Verify, without changing unrelated documents:

- SolidWorks launches and exposes a targetable window or COM instance;
- the correct part and assembly templates exist;
- output paths are writable and isolated from user files;
- FFmpeg/FFprobe exist when recording is required;
- the model unit conversion is explicit. SolidWorks API length inputs are metres.

Never rely on a localized plane name. Traverse features and select the first `RefPlane`, or select a verified entity returned by the API.

### 4. Build parts deterministically

For each part:

1. Create a named document from a verified template.
2. Create the base feature first.
3. Add secondary material features before cuts and patterns.
4. Add holes, slots, fillets, chamfers, and cosmetic details after topology is stable.
5. Rebuild and check that the intended solid/body count is nonzero.
6. Save to a deterministic filename and verify the file exists.
7. Append a timestamped line to `build_log.txt`.

Prefer dimensions and named parameters over cursor coordinates. Avoid fragile selections based only on screen pixels.

### 5. Build the assembly

Insert components in hierarchy order:

1. ground/reference component;
2. housings and frames;
3. shafts, bearings, and constrained moving parts;
4. patterned fasteners, pins, rollers, or teeth;
5. covers and appearance-only components.

Use mates when kinematic correctness is required. Absolute transforms are acceptable for concept layouts only; label them as positioned rather than fully constrained. Validate expected component count, suppression state, interference intent, axial order, and phase relationships.

### 6. Record the process when requested

Start recording before the first new document or feature. End only after:

- the final assembly is saved;
- the rebuild succeeds;
- front/right/isometric or task-specific views are shown;
- the final view holds long enough to inspect.

Use the recording reference. Do not claim a complete recording when it begins after modeling or omits assembly and final validation.

### 7. Apply the validation gate

Do not report completion until all applicable checks pass:

- required `.SLDPRT` and `.SLDASM` files exist and are nonempty;
- the build log ends with `BUILD_COMPLETE` and contains no `ERROR:` line;
- part count and assembly component count match the plan;
- rebuild is clean and the final view shows the intended geometry;
- editable structure is present; imported/direct bodies are disclosed;
- recording duration, resolution, frame rate, and codec are verified with FFprobe;
- a final preview frame and, for long recordings, a timeline contact sheet have been inspected.

Run [scripts/validate-delivery.ps1](scripts/validate-delivery.ps1) for file/log/video checks. Visual and mechanical correctness still require SolidWorks inspection.

## Automation rules

- Keep retry-prone state out of localized UI labels.
- Treat COM return values conservatively. In VBScript, avoid bitwise `Not` on numeric/Boolean return values; verify the observable result.
- Verify saves with the filesystem rather than trusting a version-dependent return type.
- Keep the script idempotent: use deterministic filenames and an isolated output directory.
- Log every saved artifact and fatal error.
- Do not close documents that the workflow did not create.
- Do not hide failures with `On Error Resume Next`; scope it narrowly and restore normal handling.
- Use [assets/solidworks-builder-template.vbs](assets/solidworks-builder-template.vbs) as a starting point, then replace the sample feature and parameter block.

## Deliverables

Return links to:

- the main `.SLDASM` or `.SLDPRT`;
- its sibling part files or a packaged directory;
- the complete process recording when requested;
- the final preview image;
- the build log;
- the reusable automation source when API-assisted.

State SolidWorks version, model status (concept or production-authoritative), component/part counts, recording specifications, and any unverified assumptions.
