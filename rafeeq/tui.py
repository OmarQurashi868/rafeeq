import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog
from textual.binding import Binding

from rafeeq.storage import StorageManager
from rafeeq.ai_client import AIClient

class RafeeqApp(App):
    CSS = """
    RichLog {
        height: 1fr;
        border: solid green;
        margin: 1;
        padding: 1;
    }
    
    Input {
        dock: bottom;
        margin: 1;
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
        yield RichLog(id="chat_area", highlight=True, markup=True)
        yield Input(placeholder="Talk to Rafeeq...", id="user_input")
        yield Footer()

    def on_mount(self) -> None:
        chat_area = self.query_one("#chat_area", RichLog)
        chat_area.write("[bold green]Rafeeq:[/bold green] Hello! I am your personal AI assistant. How can I help you today?")
        self.query_one("#user_input", Input).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_text = event.value.strip()
        if user_text:
            chat_area = self.query_one("#chat_area", RichLog)
            chat_area.write(f"[bold blue]You:[/bold blue] {user_text}")
            
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
        chat_area.write(f"[bold green]Rafeeq:[/bold green] {response}")

if __name__ == "__main__":
    storage = StorageManager()
    try:
        ai = AIClient()
    except ValueError:
        ai = None # Handle case where API key is missing for simple UI test
    
    app = RafeeqApp(storage=storage, ai=ai)
    app.run()
