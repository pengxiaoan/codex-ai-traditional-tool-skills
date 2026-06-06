---
name: ai-tutorial-video-packager
description: Package AI tool tutorial screen recordings into upload-ready self-media videos with narration scripts, Chinese voiceover, styled subtitles, fixed AI/traditional-tool intros, and final MP4 audio-video merging. Use for Codex plus AutoCAD, AI plus Office, CAD/CAM, coding, automation, workflow guide, tutorial, and strategy videos that need explanation, voice, captions, and publishing polish.
---

# AI Tutorial Video Packager

## Purpose

Turn a raw screen recording into a publishable tutorial video: create guide-style narration, synthesize Chinese voiceover, generate subtitles, prepend the fixed opener when available, and merge everything into one final MP4.

## Quick Start

```powershell
python <CODEX_HOME>\skills\ai-tutorial-video-packager\scripts\package_tutorial_video.py --input screen_recording.mp4 --title "Codex + AutoCAD" --output-dir outputs\published_codex_autocad
```

The script defaults to the local Windows WinRT Chinese male voice when available, keeps Edge neural TTS and SAPI as fallbacks, and uses `imageio_ffmpeg` for muxing/subtitle burn-in. It does not require `ffmpeg` on PATH.

## Workflow

1. Inspect the recording filename, duration, visible content, logs, and user prompt.
2. Write a short guide-style narration focused on what the viewer learns, not only what happens on screen.
3. Pass `--title`, `--topic`, and up to three `--highlight` values. Use `--script-file` when Codex has written a custom narration.
4. Let the script generate:
   - `narration.txt`
   - `voiceover.wav`
   - `subtitles.ass`
   - optional `intro.mp4` and `video_with_intro.mp4`
   - `final_upload_ready.mp4`
5. Verify the final MP4 has video, voiceover audio, and burned-in subtitles.

## Narration Style

Use Chinese, practical, and guide-oriented wording:

- Start with the exact tool combination, such as `Codex + AutoCAD`.
- Highlight the result early: Codex planning and AutoCAD automatic drawing.
- Explain the process as steps: prompt, planning, scripting, tool control, drawing, validation, output.
- Keep sentences short enough for subtitles.
- Avoid vague hype; use specific benefits and workflow tips.

## Common Options

- `--input`: source recording.
- `--title`: opener title and narration topic.
- `--topic`: more detailed subject; defaults to title.
- `--highlight`: opener highlight line. Pass up to three times.
- `--script-file`: custom narration text.
- `--output-dir`: folder for all generated assets.
- `--tts-engine`: `winrt` by default for local Chinese male voice; `edge` and `sapi` are fallbacks.
- `--winrt-voice`: local Windows voice hint, default `Kangkang`.
- `--edge-voice`: Edge neural voice, default `zh-CN-YunxiNeural`.
- `--voice-rate`: Windows SAPI fallback rate, default `0`.
- `--no-intro`: skip fixed opener.

## Coordination With Intro Skill

When `ai-tool-video-intro` is installed, use its `scripts/make_intro.py` to keep the fixed visual identity. Pass the actual episode title and highlights instead of generic text.
