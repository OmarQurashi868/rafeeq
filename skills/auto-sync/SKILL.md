---
name: auto-sync
description: Run and maintain Rafeeq's repo-local auto-sync watcher that stages, commits, and pushes file changes. Use when the user asks for automatic commits/pushes, asks to move or update auto-sync behavior, or asks to adjust auto-generated commit messages.
---

# Auto Sync

## Workflow

Use `scripts/auto-sync.ps1` from this skill to watch the Rafeeq repo for file changes. The watcher debounces changes, stages all repo changes, commits them, and pushes to `origin master`.

Start it from the repo root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File skills/auto-sync/scripts/auto-sync.ps1
```

## Commit Messages

Auto-sync must use short summary commit messages based on changed paths:

- One top-level path: `Update <path>`
- Two or three top-level paths: `Update <path>, <path>`
- More than three top-level paths: `Update project files`

Do not use timestamp-only commit messages.

## Safety

- Stop any old watcher process before moving or changing the auto-sync script.
- Do not discard user changes when auto-sync fails.
- Keep this automation inside the repo-local `skills/auto-sync/` folder.
