# Recording and validation

## Recording boundary

A complete modeling recording begins before the first document/feature and includes:

1. part creation and major feature generation;
2. saving each required part;
3. assembly creation and component insertion/mating;
4. rebuild and error review;
5. standard-view or section-view inspection;
6. a stable final frame.

If automation is fast, add short deterministic pauses after meaningful visible steps. Do not pad with irrelevant idle time.

## Recorder lifecycle

Use a local recorder that can be stopped gracefully. With FFmpeg `gdigrab` on Windows:

```powershell
ffmpeg -y -loglevel error -f gdigrab -framerate 15 -draw_mouse 1 `
  -i desktop -c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p output.mp4
```

For programmatic recording:

- start FFmpeg with redirected standard input and no visible console;
- wait two seconds before starting SolidWorks work;
- run the builder without opening a foreground console;
- write `q` to FFmpeg standard input after the builder finishes;
- wait for clean encoder shutdown before validating the file.

Do not terminate FFmpeg forcibly unless graceful shutdown times out.

## Model validation

Check in SolidWorks:

- rebuild status and feature errors;
- expected solid/body count per part;
- no unintended suppressed components;
- expected component count;
- mate status or disclosed absolute positioning;
- axis, phase, and axial-stack correctness;
- internal visibility with section, transparency, exploded, or hidden-cover views;
- interference and clearance appropriate to model status;
- final saved state.

## Artifact validation

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/validate-delivery.ps1 `
  -OutputDirectory C:\path\to\output `
  -Assembly C:\path\to\output\main.SLDASM `
  -ExpectedPartCount 10 `
  -Video C:\path\to\output\process.mp4 `
  -ExpectedVideoDuration 240 `
  -DurationTolerance 30 `
  -RequireBuildComplete
```

The script checks files, counts, log completion, error markers, and FFprobe metadata. It does not prove geometric correctness.

## Visual validation

- Export a final isometric preview at 1600×900 or larger.
- Inspect the preview for missing parts, clipping, darkness, transparency, and incorrect camera fit.
- For recordings longer than one minute, extract a contact sheet at regular intervals.
- Inspect at least the first modeling stage, a profile/detail stage, assembly stage, and final view.

## Video acceptance

Verify with FFprobe:

- expected duration within tolerance;
- H.264 or requested codec;
- requested resolution and frame rate;
- `yuv420p` for broad MP4 compatibility unless another format was requested;
- nonzero file size and decodable frames.

No-audio video is acceptable only when narration/audio was not requested or will be added later.
