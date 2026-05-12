# Project Plan: Rafeeq TUI Assistant

## Objective
Build a personal AI assistant TUI ("Rafeeq") for the LOS Hackathon that manages notes, tasks, and reminders through an immersive, full-screen terminal interface.

## Phase 1: Foundation & Setup
- **Project Structure:** Initialize a Python project with `pip` + `requirements.txt`.
- **TUI Framework:** Use `Textual` to build a full-screen, interactive terminal interface.
- **TUI Design:** Design a multi-pane layout (e.g., chat area, task sidebar, status bar).
- **Storage Layer:** Implement a simple JSON-based storage for notes and tasks to ensure portability.
- **AI Integration:** Setup Gemini API access using the OpenAI-compatible client for natural language processing.

## Phase 2: Core Features (Must-Haves)
- **Conversational Engine:** Create a loop where the user can type natural language, and the agent extracts intent (e.g., "Remind me to buy milk" -> Task creation).
- **Note Taking:** Implement commands/logic to save and categorize thoughts.
- **Task Management:** Implement CRUD operations for tasks (create, list, update, complete).

## Phase 3: Enhanced Features (Should-Haves)
- **Intelligent Retrieval:** Use natural language to query own notes and task history.
- **Daily Briefing:** A `brief` command that summarizes pending tasks and recent notes.
- **Reminders:** Basic time-based alerts.

## Phase 4: Refinement & Demo Prep
- **UX Polish:** Ensure clear output, help commands, and robust error handling.
- **Agentic Walkthrough:** Document the agentic paradigms used (planning, skills, sub-agents) for the hackathon presentation.
- **Final Testing:** End-to-end testing of conversational flows.

## Verification & Testing
- **Unit Tests:** Test intent extraction and storage logic.
- **Manual QA:** Verify natural language commands work as expected.
- **GitHub Sync:** Ensure all changes are committed and pushed regularly.
