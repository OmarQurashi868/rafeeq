# Rafeeq - Codex Project Instructions

## Project Overview

Rafeeq is a personal AI assistant TUI for the LOS Hackathon. It is intended to act as an extension of the user's mind by capturing notes, managing tasks, and supporting natural conversation in a full-screen terminal interface.

## Workspace Rules

- Keep all project-specific instructions, skills, hooks, and agent configuration inside this repository.
- Do not store project facts or configuration in global personal memory or machine-local private project memory.
- Before creating or updating project instructions, skills, or automation, verify the target path is inside this repo.
- Keep repo-local skills under `skills/`.

## Codex Workflow

- Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File hooks/session-start-git-pull.ps1` at the start of every Codex session in this directory.
- Use the local `pull-on-session-start` skill for this startup sync workflow.
- Use the repo-local auto-sync watcher when the user wants file changes committed and pushed automatically:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File skills/auto-sync/scripts/auto-sync.ps1`
- Use the local `auto-sync` skill when changing auto-sync behavior.
- Auto-sync stages all repo changes, creates a short summary commit message based on changed paths, and pushes to `origin master` after changes settle.
- Commit messages should be short summaries of the change. Do not use timestamp-only commit messages.
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
- Gemini API via the OpenAI-compatible Python client, currently using `gemini-2.5-flash`
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
