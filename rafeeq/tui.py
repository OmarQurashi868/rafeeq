import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Input, TextArea
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

    TextArea {
        height: 1fr;
        border: round #d8b4fe;
        background: #1b1b20;
        color: #f4f2f8;
        padding: 1 2;
        scrollbar-background: #1b1b20;
        scrollbar-color: #d8b4fe;
        scrollbar-color-hover: #e9d5ff;
    }

    TextArea:focus {
        border: round #e9d5ff;
    }
    
    Input {
        height: 3;
        margin-top: 1;
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
    """

    BINDINGS = [
        Binding("ctrl+c", "copy_selection", "Copy", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self, storage: StorageManager, ai: AIClient, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.ai = ai
        self.chat_transcript = ""

    def write_message(self, speaker: str, message: str, color: str) -> None:
        chat_area = self.query_one("#chat_area", TextArea)
        self.chat_transcript += f"{speaker}: {message}\n\n"
        chat_area.load_text(self.chat_transcript)
        chat_area.move_cursor(chat_area.document.end)
        chat_area.scroll_end(animate=False)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="app_shell"):
            yield TextArea(
                "",
                id="chat_area",
                read_only=True,
                show_cursor=False,
                show_line_numbers=False,
                soft_wrap=True,
            )
            yield Input(placeholder="Talk to Rafeeq...", id="user_input")
        yield Footer()

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
