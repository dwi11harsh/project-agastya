from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, RichLog
import asyncio

from agastya.core.agent import Agent
from agastya.core.config import ConfigLoader
from agastya.core.context import ContextManager

class ChatWidget(Vertical):
    """
    Core visual widget abstracting complex asynchronous LLM loops against interactive terminal prompts.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Load default setup natively bypassing UI locks securely
        try:
            config = ConfigLoader().load()
            profile = config.get_active_profile()
            self.agent = Agent(profile)
        except Exception:
            # Fallback initialization resolving barebones mock profile gracefully in testing
            from agastya.core.config import Profile
            self.agent = Agent(Profile(provider="openai", model="gpt-4", description="Fallback base profile", base_url="http://dummy"))
            
        self.context = ContextManager()
        self.log_widget = RichLog(wrap=True, highlight=True, markup=True)
        self.input_widget = Input(placeholder="Ask Agastya anything...")
        self._current_response_buffer = []

    def compose(self) -> ComposeResult:
        yield self.log_widget
        yield self.input_widget

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        user_text = message.value.strip()
        if not user_text:
            return

        # Prepare parameters clearing input safely
        self.input_widget.value = ""
        self.input_widget.disabled = True
        
        # UI Print logic establishing clear tracking separation logically
        self.log_widget.write(f"\n[bold blue]You:[/bold blue] {user_text}")
        
        self.context.add_user_message(user_text)
        self.log_widget.write("[bold green]Agastya:[/bold green] ", expand=True)

        self._current_response_buffer = []
        self.stream_response()

    @work(exclusive=True, thread=True)
    async def stream_response(self) -> None:
        """Background asynchronous thread isolating intensive AI queries preventing UI block loops safely."""
        try:
            messages = self.context.get_messages()
            
            async for chunk in self.agent.stream_infer(messages):
                self._current_response_buffer.append(chunk)
                # Appending safely across thread scopes notifying textual correctly
                self.app.call_from_thread(self.log_widget.write, chunk, expand=True)
                
            final_content = "".join(self._current_response_buffer)
            self.context.add_assistant_message(final_content)
            
        except Exception as e:
            self.app.call_from_thread(self.log_widget.write, f"\n[red]Stream Error: {e}[/red]")
            
        finally:
            self.app.call_from_thread(self._finish_stream)

    def _finish_stream(self) -> None:
        """Safely re-activates standard processing streams explicitly via standard app thread layouts."""
        self.log_widget.write("\n")
        self.input_widget.disabled = False
        self.input_widget.focus()
