import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog
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

    RichLog {
        height: 1fr;
        border: round #d8b4fe;
        background: #1b1b20;
        color: #f4f2f8;
        padding: 1 2;
        scrollbar-background: #1b1b20;
        scrollbar-color: #d8b4fe;
        scrollbar-color-hover: #e9d5ff;
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
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self, storage: StorageManager, ai: AIClient, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.ai = ai

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="app_shell"):
            yield RichLog(id="chat_area", highlight=True, markup=True)
            yield Input(placeholder="Talk to Rafeeq...", id="user_input")
        yield Footer()

    def on_mount(self) -> None:
        chat_area = self.query_one("#chat_area", RichLog)
        chat_area.write("[bold #d8b4fe]Rafeeq:[/bold #d8b4fe] Hello! I am your personal AI assistant. How can I help you today?")
        self.query_one("#user_input", Input).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_text = event.value.strip()
        if user_text:
            chat_area = self.query_one("#chat_area", RichLog)
            chat_area.write(f"[bold #c4b5fd]You:[/bold #c4b5fd] {user_text}")
            
            if self.ai:
                # Use a task to avoid blocking the UI thread if possible, 
                # although Textual's worker is better for this.
                # For now, a simple awaitable approach or worker.
                self.run_worker(self.get_ai_response(user_text))
            else:
                chat_area.write("[bold red]System:[/bold red] AI Client not initialized. Please check your API key.")
            
            event.input.value = ""

    async def get_ai_response(self, user_text: str) -> None:
        chat_area = self.query_one("#chat_area", RichLog)
        response = await asyncio.to_thread(self.ai.get_response, user_text)
        chat_area.write(f"[bold #d8b4fe]Rafeeq:[/bold #d8b4fe] {response}")

if __name__ == "__main__":
    storage = StorageManager()
    try:
        ai = AIClient()
    except ValueError:
        ai = None # Handle case where API key is missing for simple UI test
    
    app = RafeeqApp(storage=storage, ai=ai)
    app.run()
