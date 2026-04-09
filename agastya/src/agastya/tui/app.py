from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from agastya.tui.chat import ChatWidget

class AgastyaApp(App):
    """
    Main Textual Application for the Agastya Federate Knowledge Agent.
    Serves as the root visual UI connecting terminal inputs towards the executor mapping layers natively.
    """
    
    TITLE = "Agastya"
    SUB_TITLE = "Local Knowledge AI"
    
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets defining the overarching graphical format natively mapping headers and footers."""
        yield Header(show_clock=True)
        yield ChatWidget()
        yield Footer()
