import asyncio
import re
from datetime import datetime

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Markdown, TextArea
from textual.containers import Container, VerticalScroll, Horizontal
from textual.binding import Binding
from textual.message import Message
from textual.theme import Theme

from rafeeq.storage import StorageManager, Note, Task
from rafeeq.ai_client import AIClient
from rafeeq.logic import execute_intents

# Theme definitions
AMETHYST = Theme(
    name="amethyst",
    primary="#d8b4fe",
    secondary="#18181c",
    accent="#e9d5ff",
    foreground="#f4f2f8",
    background="#111113",
    success="#4ade80",
    warning="#fbbf24",
    error="#f87171",
    surface="#1b1b20",
    panel="#4b4258",
    dark=True,
)

EMERALD = Theme(
    name="emerald",
    primary="#6ee7b7",
    secondary="#064e3b",
    accent="#a7f3d0",
    foreground="#ecfdf5",
    background="#06100d",
    success="#10b981",
    warning="#f59e0b",
    error="#ef4444",
    surface="#065f46",
    panel="#059669",
    dark=True,
)

AMBER = Theme(
    name="amber",
    primary="#fbbf24",
    secondary="#451a03",
    accent="#fcd34d",
    foreground="#fffbeb",
    background="#110903",
    success="#f59e0b",
    warning="#d97706",
    error="#dc2626",
    surface="#78350f",
    panel="#b45309",
    dark=True,
)

SYSTEM_PROMPT = """You are Rafeeq, a focused personal assistant dedicated to note-taking and life organization.
Your goal is to be concise, helpful, and proactive in capturing information.
Avoid general-purpose chatter; stay focused on being the user's external brain.

When listing notes or tasks, ALWAYS include their 6-character unique ID in square brackets, e.g., `[abc123]`.

You have access to several commands via markers. When you use a marker, the system will execute it and provide you with an `OBSERVATION`. You should then use that observation to provide a final natural language response to the user.

Markers:
- `[SAVE_NOTE: <content>]`: Save a new note.
- `[UPDATE_NOTE: <id> | <new_content>]`: Update an existing note.
- `[DELETE_NOTE: <id>]`: Delete a note.
- `[ADD_TASK: <title> | DUE: <YYYY-MM-DD HH:MM>]`: Add a task (DUE is optional).
- `[UPDATE_TASK: <id> | TITLE: <new_title> | DUE: <new_due> | COMPLETED: <true/false>]`: Update a task.
- `[DELETE_TASK: <id>]`: Delete a task.
- `[LIST_NOTES]`: List all notes.
- `[LIST_TASKS]`: List all tasks.
- `[COMPLETE_TASK: <id_or_title>]`: Mark a task as completed.
- `[SEARCH: <query>]`: Search notes and tasks.
- `[DAILY_BRIEF]`: Get a summary of pending tasks and recent notes.
- `[TASK_BRIEF]`: Get a natural language summary of only pending tasks.

If you need more information to fulfill a request
 (e.g., you don't know the ID of a note to delete), PROACTIVELY use the appropriate marker (like `[LIST_NOTES]` or `[SEARCH: <query>]`) to get that information. Do not ask the user for the ID if you can find it yourself using a marker first. Once you receive the observation with the information you need, proceed to fulfill the original request.

DO NOT just output the marker. Always follow up with a natural language response after you receive the observation.
"""

class TaskSidebar(VerticalScroll):
    def __init__(self, storage: StorageManager, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage

    def on_mount(self) -> None:
        self.update_tasks()

    def update_tasks(self) -> None:
        self.query("Markdown").remove()
        tasks = self.storage.get_tasks()
        pending = [t for t in tasks if not t["completed"]]

        if not pending:
            self.mount(Markdown("*No pending tasks*"))
        else:
            task_list = "\n".join([f"- `[{t['id']}]` {t['title']}" for t in pending])
            self.mount(Markdown(f"### Pending Tasks\n{task_list}"))

class MessageInput(TextArea):
    BINDINGS = [
        Binding("enter", "submit", show=False, priority=True),
        Binding("shift+enter", "newline", show=False, priority=True),
    ]

    class Submitted(Message):
        pass

    def action_submit(self) -> None:
        self.post_message(self.Submitted())

    def action_newline(self) -> None:
        self.insert("\n")

    def on_text_area_changed(self) -> None:
        self.fit_content_height()

    def fit_content_height(self) -> None:
        line_count = max(1, self.text.count("\n") + 1)
        self.styles.height = min(6, line_count + 2)

class RafeeqApp(App):
    TITLE = "Rafeeq"
    
    CSS = """
    Screen {
        background: $background;
        color: $foreground;
    }

    Header {
        background: $secondary;
        color: $primary;
        text-style: bold;
    }

    Footer {
        background: $secondary;
        color: $foreground;
        opacity: 0.8;
    }

    #app_shell {
        height: 1fr;
        padding: 1 2;
        background: $background;
    }

    #main_layout {
        height: 1fr;
    }

    #chat_container {
        width: 7fr;
        height: 1fr;
    }

    #chat_area {
        height: 1fr;
        border: round $primary;
        background: $surface;
        color: $foreground;
        padding: 1 2;
        scrollbar-background: $surface;
        scrollbar-color: $primary;
        scrollbar-color-hover: $foreground;
    }

    #chat_area:focus {
        border: round $foreground;
    }

    #sidebar {
        width: 3fr;
        height: 1fr;
        border: round $panel;
        background: $secondary;
        padding: 1;
        margin-left: 1;
    }

    .message {
        width: 100%;
        margin-bottom: 1;
        padding: 0 1;
        background: $surface;
    }

    .assistant-message {
        color: $foreground;
    }

    .user-message {
        color: #9b94a8;
    }

    .thinking-message {
        color: $primary;
        text-style: italic;
        opacity: 0.7;
    }

    #message_input {
        height: 3;
        margin-top: 1;
        border: round $panel;
        background: #202027;
        color: $foreground;
        padding: 0 1;
    }

    #message_input:focus {
        border: round $primary;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "copy_selection", "Copy", show=True),
        Binding("f1", "show_commands", "Commands", show=True),
        Binding("ctrl+t", "toggle_theme", "Themes", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self, storage: StorageManager, ai: AIClient, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.ai = ai
        self.theme_list = ["amethyst", "emerald", "amber"]
        self.current_theme_index = 0

    def action_toggle_theme(self) -> None:
        self.current_theme_index = (self.current_theme_index + 1) % len(self.theme_list)
        new_theme = self.theme_list[self.current_theme_index]
        self.theme = new_theme
        self.notify(f"Theme switched to: {new_theme.capitalize()}")

    def action_show_commands(self) -> None:
        commands_msg = """
# Rafeeq Commands & Capabilities
You can interact with Rafeeq using natural language or these specific triggers:

### 🛠️ Navigation & UI
- **F1**: Show this command menu.
- **Ctrl+T**: Toggle between UI themes (Amethyst, Emerald, Amber).
- **Ctrl+C**: Copy selected text.
- **Q**: Quit the application.

### 🤖 Chat Commands
- **/brief**: Get a natural language summary of your pending tasks.
- **"daily brief"**: Get a summary of both tasks and recent notes.

### 💡 Natural Language Examples
- "Remind me to [title] on [date] at [time]" -> *Automatically schedules a Windows notification!*
- "Save a note about [content]"
- "Find [query]" -> *Search through all your notes and tasks.*
- "I've finished [task_id_or_title]" -> *Marks task as completed.*
- "List my tasks" or "Show my notes"
- "Delete note [id]" or "Delete task [id]"

### 🔔 Windows Notifications
Tasks with a due date will trigger a system notification even if Rafeeq is closed!
"""
        self.write_message(commands_msg.strip(), "assistant-message")

    def write_message(self, message: str, message_class: str) -> None:
        chat_area = self.query_one("#chat_area", VerticalScroll)
        chat_area.mount(Markdown(message, classes=f"message {message_class}", open_links=False))
        chat_area.scroll_end(animate=False)

    def show_thinking(self) -> None:
        chat_area = self.query_one("#chat_area", VerticalScroll)
        chat_area.mount(Markdown("Rafeeq is thinking...", id="thinking_msg", classes="message thinking-message"))
        chat_area.scroll_end(animate=False)

    def hide_thinking(self) -> None:
        try:
            self.query_one("#thinking_msg").remove()
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="app_shell"):
            with Horizontal(id="main_layout"):
                with Container(id="chat_container"):
                    yield VerticalScroll(id="chat_area")
                    yield MessageInput(
                        "",
                        id="message_input",
                        show_line_numbers=False,
                        soft_wrap=True,
                        placeholder="Talk to Rafeeq...",
                    )
                yield TaskSidebar(self.storage, id="sidebar")
        yield Footer()

    def on_mount(self) -> None:
        # Register custom themes
        self.register_theme(AMETHYST)
        self.register_theme(EMERALD)
        self.register_theme(AMBER)
        self.theme = "amethyst"

        welcome_msg = """
# Welcome to Rafeeq! 
I am your personal AI assistant, designed to be an extension of your mind. Here is how I can assist you:

### 📝 Note Taking
Simply tell me something you want to remember, and I'll save it as a note. You can search through them later or ask for a summary.

### ✅ Task Management
I can help you stay on top of your to-dos:
- **Create**: "Add a task to buy groceries"
- **Schedule**: "Remind me to call the bank tomorrow at 10am"
- **Update/Complete**: "I've finished the report" or "Change my 5pm meeting to 6pm"
- **List**: "What are my pending tasks?"

### 🔔 Smart Reminders
When you add a task with a due date, I'll automatically schedule a **Windows Notification** to remind you at the exact time.

### 🔍 Intelligent Retrieval
Ask me to search for anything in your history:
- "Find my notes about the project launch"
- "Search for tasks related to travel"

### 📊 Daily Briefings
Start your day by asking for a **"daily brief"** to get a snapshot of your pending tasks and recent notes.

---
**How can I help you get started today?**
"""
        self.write_message(welcome_msg.strip(), "assistant-message")
        self.query_one("#message_input", TextArea).focus()

    def action_copy_selection(self) -> None:
        selected_text = self.screen.get_selected_text()
        if selected_text:
            self.copy_to_clipboard(selected_text)
            self.notify("Copied selected text")

    async def on_message_input_submitted(self) -> None:
        await self.submit_user_message()

    async def submit_user_message(self) -> None:
        message_input = self.query_one("#message_input", MessageInput)
        user_text = message_input.text.strip()
        if user_text:
            self.write_message(user_text, "user-message")

            if self.ai:
                # Handle slash commands
                if user_text.lower() == "/brief":
                    prompt = "Provide a natural language summary of my current pending tasks using the [TASK_BRIEF] command."
                else:
                    prompt = user_text
                
                self.run_worker(self.get_ai_response(prompt))
            else:
                self.write_message("AI Client not initialized. Please check your API key.", "assistant-message")

            message_input.clear()
            message_input.fit_content_height()

    async def get_ai_response(self, user_text: str) -> None:
        current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        dynamic_system_prompt = f"{SYSTEM_PROMPT}\n\nCurrent context: The date and time is {current_time}."

        max_turns = 3
        turn = 0
        prompt = user_text

        self.show_thinking()
        try:
            while turn < max_turns:
                response = await asyncio.to_thread(self.ai.get_response, prompt, system_message=dynamic_system_prompt)

                # Process intents and get observations
                clean_text, observations = execute_intents(response, self.storage)

                if not observations:
                    # Final response from AI
                    self.hide_thinking()
                    if clean_text:
                        self.write_message(clean_text, "assistant-message")
                    break

                # Add observations to history and loop for a natural language follow-up
                for obs in observations:
                    self.ai.add_observation(obs)

                # Update sidebar in case tasks changed
                self.query_one(TaskSidebar).update_tasks()

                # Next call to AI will be to react to observations
                prompt = None
                turn += 1
            else:
                # Hit max turns
                self.hide_thinking()
        except Exception as e:
            self.hide_thinking()
            self.write_message(f"Error getting response: {str(e)}", "assistant-message")

    def process_ai_intent(self, text: str) -> str:
        # This is now handled inside get_ai_response loop,
        # but kept for backward compatibility if needed elsewhere
        clean_text, _ = execute_intents(text, self.storage)
        return clean_text

if __name__ == "__main__":
    storage = StorageManager()
    try:
        ai = AIClient()
    except ValueError:
        ai = None # Handle case where API key is missing for simple UI test

    app = RafeeqApp(storage=storage, ai=ai)
    app.run()
