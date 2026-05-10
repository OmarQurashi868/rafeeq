# Rafeeq - Project Overview

Rafeeq is the name of the personal AI assistant CLI being built. The agent building this project is **Gemini CLI**.

## Workspace Mandates

- **Mandatory Workspace Local Storage:** This is a shared repository. ALL project-specific instructions, custom skills, hooks, and agent configurations MUST be stored directly within this workspace (e.g., `./GEMINI.md`, `./skills/`, `./hooks/`).
- **Forbidden Storage:** Do NOT use global personal memory (`~/.gemini/GEMINI.md`) or private project memory for any facts or configurations related to this project. Everything must be committed to the repo to be available to all team members.
- **Enforcement:** Before creating or updating any project-related instructions or skills, verify they are being written to a location within the current directory.
- **Agentic Engineering:** This project is built using agentic engineering principles. Every feature, refactor, and bug fix must be executed by the AI agent through a Research -> Strategy -> Execution cycle.
- **CLI First:** The final product is a CLI tool. Ensure all interfaces and interactions are optimized for a terminal environment.

## Project Vision (LOS Hackathon)

Rafeeq is a personal AI assistant designed to act as an extension of the user's mind. It focuses on natural conversation to capture, organize, and act on the user's life.

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
- **Storage:** Local JSON or SQLite (keep it simple and portable).
- **AI Integration:** Gemini API (Free Tier).
