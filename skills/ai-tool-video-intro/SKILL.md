---
name: ai-tool-video-intro
description: Generate a consistent 3-second branded intro for AI plus traditional-tool tutorial, guide, workflow, and screen-recording videos. Use when Codex needs to create, prepend, or standardize short opening clips for self-media videos about AI combined with AutoCAD, Office, CAD/CAM, coding, automation, or other traditional software tools.
---

# AI Tool Video Intro

## Purpose

Create a reusable 3-second opening clip for an "AI + traditional tools" tutorial channel. Keep the style fixed across videos: dark technical workstation, CAD-grid motion, cyan AI linework, amber highlights, concise Chinese title lockup, and a slow push-in camera feel.

## Quick Start

Use the bundled generator script:

```powershell
python <CODEX_HOME>\skills\ai-tool-video-intro\scripts\make_intro.py --input screen_recording.mp4 --output-intro outputs\intro.mp4 --output-combined outputs\with_intro.mp4
```

If the input video is not in the current directory, pass its absolute path. The script uses Python packages `PIL`, `numpy`, `imageio`, and `imageio_ffmpeg`; it does not require `ffmpeg` on PATH.

## Fixed Style

Use this default identity unless the user explicitly asks to change the brand:

- Main title: use the bundled Chinese default for "AI + traditional tools".
- Subtitle: use the bundled Chinese default for "auto drawing / guides / practical sharing".
- Caption: `WORKFLOW NOTES`
- Palette: near-black workstation background, cyan linework, amber active accent, off-white text.
- Visual motifs: blueprint grid, animated CAD polylines, circular gear-like construction marks, scan line, small tool tags.
- Motion: 3.2 seconds, simulated slow push-in, slight rightward parallax, linework reveal from 0.35s, title lock from 0.85s, amber transition bar near the end.

## Workflow

1. Locate the user's main recording, usually the newest `.mp4`, `.mov`, `.mkv`, `.avi`, or `.webm` in the workspace root or an `outputs/recordings` folder.
2. Generate an intro with `scripts/make_intro.py`, matching the source video resolution.
3. When the user wants the opener attached to the recording, pass `--output-combined`; otherwise provide only `--output-intro`.
4. Verify the generated intro duration is about 3 seconds and the combined video starts with the opener.
5. Return the absolute paths for the intro and combined output.

## Script Options

Common options:

- `--input`: source recording used for size and optional background context.
- `--output-intro`: intro-only MP4 path.
- `--output-combined`: optional MP4 path with intro prepended to the input.
- `--title`: override the fixed title.
- `--subtitle`: override the fixed subtitle.
- `--caption`: override the small top caption.
- `--highlight`: add an episode highlight line. Pass up to three times.
- `--duration`: default `3.2`.
- `--fps`: default `30`.

## Notes

- Keep the opener short, restrained, and technical; avoid generic colorful templates or marketing hero visuals.
- Do not alter the main recording content unless the user asks to prepend the intro.
- If Chinese text renders incorrectly, use a Windows Chinese font such as `C:\Windows\Fonts\simhei.ttf`, `msyh.ttc`, or `simsun.ttc`.
