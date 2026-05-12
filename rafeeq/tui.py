import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Markdown, TextArea
from textual.containers import Container, VerticalScroll
from textual.binding import Binding
from textual.message import Message

from rafeeq.storage import StorageManager
from rafeeq.ai_client import AIClient

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
        response = await asyncio.to_thread(self.ai.get_response, user_text)
        self.write_message(response, "assistant-message")

if __name__ == "__main__":
    storage = StorageManager()
    try:
        ai = AIClient()
    except ValueError:
        ai = None # Handle case where API key is missing for simple UI test
    
    app = RafeeqApp(storage=storage, ai=ai)
    app.run()
