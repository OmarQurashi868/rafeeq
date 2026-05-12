---
name: pull-on-session-start
description: Pull latest changes before starting Gemini CLI work in the Rafeeq repository. Use when a Gemini CLI session begins in this repo, when resuming work here, or when the user asks for a repo-local session-start git pull hook or startup sync behavior.
---

# Pull On Session Start

## Workflow

When starting or resuming a Gemini CLI session in this repository:

1. Confirm the working directory is the Rafeeq repo root.
2. Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File skills/pull-on-session-start/scripts/session-start-git-pull.ps1`.
3. If the pull fails due to local changes, inspect `git status --short` and resolve conservatively without discarding user work.
4. Continue with the user's requested task only after the repo has been synced or the sync blocker has been reported.

## Hook Script

The repo-local hook entrypoint is `skills/pull-on-session-start/scripts/session-start-git-pull.ps1`. It changes to the repo root and runs:

```powershell
git pull origin master
```

Gemini CLI does not automatically execute arbitrary repo hooks by itself. `GEMINI.md` is the repo-local instruction source that tells future Gemini CLI sessions to run this hook at startup.
