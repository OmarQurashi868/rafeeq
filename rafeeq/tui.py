import asyncio
import re

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Markdown, TextArea
from textual.containers import Container, VerticalScroll
from textual.binding import Binding
from textual.message import Message

from rafeeq.storage import StorageManager, Note, Task
from rafeeq.ai_client import AIClient

SYSTEM_PROMPT = """You are Rafeeq, a focused personal assistant dedicated to note-taking and life organization.
Your goal is to be concise, helpful, and proactive in capturing information.
Avoid general-purpose chatter; stay focused on being the user's external brain.

When the user wants to save a note or remember something:
- Include `[SAVE_NOTE: <content>]` in your response.
When the user wants to add a task or to-do item:
- Include `[ADD_TASK: <title>]` in your response.
When the user wants to see their notes:
- Include `[LIST_NOTES]` in your response.
When the user wants to see their tasks:
- Include `[LIST_TASKS]` in your response.
"""

class MessageInput(TextArea):
# ... (rest of the class)
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
    CSS = """
    Screen {
        background: #111113;
        color: #f4f2f8;
    }

    Header {
        background: #18181c;
        color: #d8b4fe;
        text-style: bold;
    }

    Footer {
        background: #18181c;
        color: #bdb7c8;
    }

    #app_shell {
        height: 1fr;
        padding: 1 2;
        background: #111113;
    }

    #chat_area {
        height: 1fr;
        border: round #d8b4fe;
        background: #1b1b20;
        color: #f4f2f8;
        padding: 1 2;
        scrollbar-background: #1b1b20;
        scrollbar-color: #d8b4fe;
        scrollbar-color-hover: #e9d5ff;
    }

    #chat_area:focus {
        border: round #e9d5ff;
    }

    .message {
        width: 100%;
        margin-bottom: 1;
        padding: 0 1;
        background: #1b1b20;
    }

    .assistant-message {
        color: #f4f2f8;
    }

    .user-message {
        color: #9b94a8;
    }

    #message_input {
        height: 3;
        margin-top: 1;
        border: round #4b4258;
        background: #202027;
        color: #f4f2f8;
        padding: 0 1;
    }

    #message_input:focus {
        border: round #d8b4fe;
    }

    """

    BINDINGS = [
        Binding("ctrl+c", "copy_selection", "Copy", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self, storage: StorageManager, ai: AIClient, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.ai = ai

    def write_message(self, message: str, message_class: str) -> None:
        chat_area = self.query_one("#chat_area", VerticalScroll)
        chat_area.mount(Markdown(message, classes=f"message {message_class}", open_links=False))
        chat_area.scroll_end(animate=False)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="app_shell"):
            yield VerticalScroll(id="chat_area")
            yield MessageInput(
                "",
                id="message_input",
                show_line_numbers=False,
                soft_wrap=True,
                placeholder="Talk to Rafeeq...",
            )
        yield Footer()

    def on_mount(self) -> None:
        self.write_message("Hello! I am your personal AI assistant. How can I help you today?", "assistant-message")
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
                self.run_worker(self.get_ai_response(user_text))
            else:
                self.write_message("AI Client not initialized. Please check your API key.", "assistant-message")
            
            message_input.clear()
            message_input.fit_content_height()

    async def get_ai_response(self, user_text: str) -> None:
        response = await asyncio.to_thread(self.ai.get_response, user_text, system_message=SYSTEM_PROMPT)
        
        # Process intents and clean response
        clean_response = self.process_ai_intent(response)
        
        if clean_response:
            self.write_message(clean_response, "assistant-message")

    def process_ai_intent(self, text: str) -> str:
        # Regex patterns for markers
        note_pattern = r"\[SAVE_NOTE:\s*(.*?)\]"
        task_pattern = r"\[ADD_TASK:\s*(.*?)\]"
        list_notes_pattern = r"\[LIST_NOTES\]"
        list_tasks_pattern = r"\[LIST_TASKS\]"

        # Handle SAVE_NOTE
        notes = re.findall(note_pattern, text)
        for content in notes:
            self.storage.add_note(Note(content=content))
            self.notify(f"Note saved", severity="information")

        # Handle ADD_TASK
        tasks = re.findall(task_pattern, text)
        for title in tasks:
            self.storage.add_task(Task(title=title))
            self.notify(f"Task added", severity="information")

        # Handle LIST_NOTES
        if re.search(list_notes_pattern, text):
            all_notes = self.storage.get_notes()
            if not all_notes:
                text += "\n\n*No notes found.*"
            else:
                notes_list = "\n".join([f"- {n['content']} *({n['timestamp'][:10]})*" for n in all_notes])
                text += f"\n\n### Your Notes\n{notes_list}"

        # Handle LIST_TASKS
        if re.search(list_tasks_pattern, text):
            all_tasks = self.storage.get_tasks()
            if not all_tasks:
                text += "\n\n*No tasks found.*"
            else:
                tasks_list = "\n".join([f"- [{'x' if t['completed'] else ' '}] {t['title']}" for t in all_tasks])
                text += f"\n\n### Your Tasks\n{tasks_list}"

        # Clean up markers from the final text
        text = re.sub(note_pattern, "", text)
        text = re.sub(task_pattern, "", text)
        text = re.sub(list_notes_pattern, "", text)
        text = re.sub(list_tasks_pattern, "", text)

        return text.strip()

if __name__ == "__main__":
    storage = StorageManager()
    try:
        ai = AIClient()
    except ValueError:
        ai = None # Handle case where API key is missing for simple UI test
    
    app = RafeeqApp(storage=storage, ai=ai)
    app.run()
