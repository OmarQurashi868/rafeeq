# Project Plan: Rafeeq TUI Assistant

## Objective
Build a personal AI assistant TUI ("Rafeeq") for the LOS Hackathon that manages notes, tasks, and reminders through an immersive, full-screen terminal interface.

## Phase 1: Foundation & Setup [COMPLETE]
- **Project Structure:** Initialize a Python project with `pip` + `requirements.txt`.
- **TUI Framework:** Use `Textual` to build a full-screen, interactive terminal interface.
- **TUI Design:** Design a multi-pane layout (e.g., chat area, task sidebar, status bar).
- **AI Integration:** Setup Gemini API access using the OpenAI-compatible client for natural language processing.

## Phase 2: Core Features (Must-Haves) [COMPLETE]
- **Storage Layer:** Implement a simple JSON-based storage for notes and tasks.
- **Conversational Engine:** Create a loop for natural language intent extraction.
- **Note Taking:** Implement logic to save and categorize thoughts.
- **Task Management:** Implement CRUD operations for tasks.
- **Testing:** Unit tests for storage and intent logic.

## Phase 3: Enhanced Features (Should-Haves) [IN PROGRESS]
- **Intelligent Retrieval:** [COMPLETE] Keyword search for notes and tasks.
- **Daily Briefing:** [COMPLETE] Summary of pending tasks and recent notes.
- **TUI Immersive Upgrade:** [COMPLETE] Dedicated task sidebar and split layout.
- **Reminders:** Basic time-based alerts.
- **Advanced Retrieval:** Semantic search or vector-based retrieval (future).

## Phase 4: Refinement & Demo Prep
- **UX Polish:** Ensure clear output, help commands, and robust error handling.
- **Agentic Walkthrough:** Document the agentic paradigms used (planning, skills, sub-agents) for the hackathon presentation.
- **Final Testing:** End-to-end testing of conversational flows.

## Verification & Testing
- **Unit Tests:** Test intent extraction and storage logic.
- **Manual QA:** Verify natural language commands work as expected.
- **GitHub Sync:** Ensure all changes are committed and pushed regularly.
