# Rafeeq - Codex Project Instructions

## Project Overview

Rafeeq is a personal AI assistant TUI for the LOS Hackathon. It is intended to act as an extension of the user's mind by capturing notes, managing tasks, and supporting natural conversation in a full-screen terminal interface.

## Workspace Rules

- Keep all project-specific instructions, skills, hooks, and agent configuration inside this repository.
- Do not store project facts or configuration in global personal memory or machine-local private project memory.
- Before creating or updating project instructions, skills, or automation, verify the target path is inside this repo.
- Preserve existing Gemini-specific files unless the user explicitly asks to remove them; they may still be useful to teammates using Gemini CLI.

## Codex Workflow

- Run `git pull` at the start of a work session when the user asks to sync or when current upstream state matters.
- Use the repo-local auto-sync watcher when the user wants file changes committed and pushed automatically:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/auto-sync.ps1`
- Auto-sync stages all repo changes, creates an `Auto-commit: changes made at <timestamp>` commit, and pushes to `origin master` after changes settle.
- Use a Research -> Strategy -> Execution cycle for feature work, refactors, and bug fixes:
  - Research: read the relevant docs, code, and current behavior.
  - Strategy: choose the smallest coherent plan that fits the existing codebase.
  - Execution: implement, verify, and summarize concrete results.

## Product Direction

- The final product is a full-screen TUI optimized for an immersive terminal experience.
- Prefer Textual and Rich patterns for UI work.
- Keep interactions conversational and focused on note capture, task management, reminders, and daily briefings.
- Store user data locally using simple, portable storage such as JSON or SQLite.

## Current Tech Stack

- Python
- Textual
- Rich
- OpenAI API, currently using `gpt-4o`
- Local JSON storage

## Feature Priorities

- Conversational note taking
- Task CRUD: create, list, update, complete
- Natural-language intent handling
- Intelligent retrieval across notes and tasks
- Daily briefing of pending tasks and recent notes
- Basic time-based reminders

## Verification

- Add focused unit tests for storage and intent extraction as those areas evolve.
- Manually verify important TUI flows after UI changes.
- Keep `.env`, `data.json`, bytecode, and local runtime artifacts out of git.

## Gemini Compatibility Notes

- `GEMINI.md` and `.gemini/` contain Gemini CLI-specific instructions and hooks.
- `.gemini/hooks/git-pull.ps1` pulls from `origin master` at Gemini session start.
- `.gemini/hooks/git-push.ps1` stages, commits, and pushes after Gemini write/replace tool calls.
- Those hooks do not run automatically for Codex; use `scripts/auto-sync.ps1` when auto-commit and auto-push behavior is wanted.
