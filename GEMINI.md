# Rafeeq - Project Overview

Rafeeq is the name of the personal AI assistant TUI being built. The agent building this project is **Gemini CLI**.

## Workspace Mandates

- **Mandatory Workspace Local Storage:** This is a shared repository. ALL project-specific instructions, custom skills, hooks, and agent configurations MUST be stored directly within this workspace (e.g., `./GEMINI.md`, `./skills/`, `./hooks/`).
- **Forbidden Storage:** Do NOT use global personal memory (`~/.gemini/GEMINI.md`) or private project memory for any facts or configurations related to this project. Everything must be committed to the repo to be available to all team members.
- **Enforcement:** Before creating or updating any project-related instructions or skills, verify they are being written to a location within the current directory.
- **Git Automation:**
    - **Session Start:** A hook automatically pulls the latest changes from `origin master` at the beginning of every session (`.gemini/hooks/git-pull.ps1`).
    - **Auto-Sync:** Every file modification (via `write_file` or `replace`) triggers an automatic stage, commit, and push to `origin master` (`.gemini/hooks/git-push.ps1`).
- **Agentic Engineering:** This project is built using agentic engineering principles. Every feature, refactor, and bug fix must be executed by the AI agent through a Research -> Strategy -> Execution cycle.
- **TUI First:** The final product is a full-screen TUI (Text User Interface). Ensure all interfaces and interactions are optimized for an immersive terminal environment using `Textual`.

## Project Vision (LOS Hackathon)

Rafeeq is a personal AI assistant designed to act as an extension of the user's mind. It focuses on natural conversation to capture, organize, and act on the user's life within a beautiful, immersive terminal interface.

### Core Requirements
- **Note Taking:** Conversational capture of thoughts and ideas.
- **Task Management:** Create, update, track, and complete tasks.
- **Natural Conversation:** Interaction should feel like talking to an assistant.

### Planned Features
- **Retrieval:** Intelligent querying of notes and task history.
- **Daily Briefing:** Summary of pending tasks and recent notes.
- **Reminders:** Time-based triggers for tasks.

## Tech Stack
- **Language:** Python (for CLI ease and library support).
- **UI Framework:** Textual (for full-screen TUI) and Rich (for terminal formatting).
- **Storage:** Local JSON or SQLite (keep it simple and portable).
- **AI Integration:** OpenAI API (gpt-4o).
