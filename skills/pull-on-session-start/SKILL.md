---
name: pull-on-session-start
description: Pull latest changes before starting Codex work in the Rafeeq repository. Use when a Codex session begins in this repo, when resuming work here, or when the user asks for a repo-local session-start git pull hook or startup sync behavior.
---

# Pull On Session Start

## Workflow

When starting or resuming a Codex session in this repository:

1. Confirm the working directory is the Rafeeq repo root.
2. Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File hooks/session-start-git-pull.ps1`.
3. If the pull fails due to local changes, inspect `git status --short` and resolve conservatively without discarding user work.
4. Continue with the user's requested task only after the repo has been synced or the sync blocker has been reported.

## Hook Script

The repo-local hook entrypoint is `hooks/session-start-git-pull.ps1`. It changes to the repo root and runs:

```powershell
git pull origin master
```

Codex does not automatically execute arbitrary repo hooks by itself. `AGENTS.md` is the repo-local instruction source that tells future Codex sessions to run this hook at startup.
