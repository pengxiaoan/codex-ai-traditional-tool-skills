# Codex AI Traditional Tool Skills

This repository contains reusable Codex skills for AI plus traditional-software workflows.

## Included Skills

- `ai-tool-video-intro`: creates a consistent 3-second branded intro for AI + traditional-tool videos.
- `ai-tutorial-video-packager`: packages screen recordings into upload-ready tutorial videos with narration, subtitles, intro, and final MP4 merging.
- `solidworks-build-mechanical-models`: plans, creates, assembles, records, and validates rigorous SolidWorks mechanical models through GUI, API, or hybrid workflows.

## Install In Codex

Ask Codex to install a skill from its GitHub path:

```text
Install https://github.com/pengxiaoan/codex-ai-traditional-tool-skills/tree/main/skills/ai-tool-video-intro
Install https://github.com/pengxiaoan/codex-ai-traditional-tool-skills/tree/main/skills/ai-tutorial-video-packager
Install https://github.com/pengxiaoan/codex-ai-traditional-tool-skills/tree/main/skills/solidworks-build-mechanical-models
```

Restart Codex after installation.

## Manual Install

Copy the desired folder under `skills/` into the local Codex skills directory:

```text
Windows: C:\Users\<username>\.codex\skills\
macOS/Linux: ~/.codex/skills/
```

Example final structure:

```text
~/.codex/skills/solidworks-build-mechanical-models/SKILL.md
```

The SolidWorks skill includes a Chinese usage tutorial at `references/usage-tutorial.zh-CN.md`.