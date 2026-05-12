import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Input, RichLog, Static
from textual.containers import Container
from textual.binding import Binding

from rafeeq.storage import StorageManager
from rafeeq.ai_client import AIClient

class RafeeqApp(App):
    CSS = """
    Screen {
        background: #111113;
        color: #f4f2f8;
    }

    #app_shell {
        height: 1fr;
        padding: 1 3;
        background: #111113;
    }

    #top_bar {
        height: 3;
        margin-bottom: 1;
        padding: 0 2;
        border: round #3a3344;
        background: #18181d;
        color: #d8b4fe;
        text-style: bold;
        content-align: left middle;
    }

    RichLog {
        height: 1fr;
        border: round #5b4b70;
        background: #1b1b20;
        color: #f4f2f8;
        margin-bottom: 1;
        padding: 1 2;
        scrollbar-background: #1b1b20;
        scrollbar-color: #d8b4fe;
        scrollbar-color-hover: #e9d5ff;
    }
    
    Input {
        height: 3;
        border: round #4b4258;
        background: #202027;
        color: #f4f2f8;
        padding: 0 1;
    }

    Input:focus {
        border: round #d8b4fe;
    }

    Input > .input--placeholder {
        color: #8b8495;
    }

    #bottom_bar {
        height: 3;
        margin-top: 1;
        padding: 0 2;
        border: round #2d2934;
        background: #18181d;
        color: #bdb7c8;
        content-align: left middle;
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

    def write_message(self, speaker: str, message: str, color: str) -> None:
        chat_area = self.query_one("#chat_area", RichLog)
        chat_area.write(f"[bold {color}]{speaker}:[/bold {color}] {message}")
        chat_area.write("")

    def compose(self) -> ComposeResult:
        with Container(id="app_shell"):
            yield Static("Rafeeq  |  Personal assistant", id="top_bar")
            yield RichLog(id="chat_area", highlight=True, markup=True, wrap=True)
            yield Input(placeholder="Talk to Rafeeq...", id="user_input")
            yield Static("Ctrl+C copy selected text  |  Q quit", id="bottom_bar")

    def on_mount(self) -> None:
        self.write_message("Rafeeq", "Hello! I am your personal AI assistant. How can I help you today?", "#d8b4fe")
        self.query_one("#user_input", Input).focus()

    def action_copy_selection(self) -> None:
        selected_text = self.screen.get_selected_text()
        if selected_text:
            self.copy_to_clipboard(selected_text)
            self.notify("Copied selected text")
        else:
            self.notify("Select chat text first", severity="warning")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_text = event.value.strip()
        if user_text:
            self.write_message("You", user_text, "#c4b5fd")
            
            if self.ai:
                # Use a task to avoid blocking the UI thread if possible, 
                # although Textual's worker is better for this.
                # For now, a simple awaitable approach or worker.
                self.run_worker(self.get_ai_response(user_text))
            else:
                self.write_message("System", "AI Client not initialized. Please check your API key.", "red")
            
            event.input.value = ""

    async def get_ai_response(self, user_text: str) -> None:
        response = await asyncio.to_thread(self.ai.get_response, user_text)
        self.write_message("Rafeeq", response, "#d8b4fe")

if __name__ == "__main__":
    storage = StorageManager()
    try:
        ai = AIClient()
    except ValueError:
        ai = None # Handle case where API key is missing for simple UI test
    
    app = RafeeqApp(storage=storage, ai=ai)
    app.run()
