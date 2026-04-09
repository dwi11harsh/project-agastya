import pytest
from textual.app import App, ComposeResult
from agastya.tui.chat import ChatWidget

class MockChatApp(App):
    def compose(self) -> ComposeResult:
        yield ChatWidget()

@pytest.mark.asyncio
async def test_chat_widget_mounting():
    app = MockChatApp()
    
    async with app.run_test() as pilot:
        # Check components load safely avoiding hard UI lockups
        chat_widget = app.query_one(ChatWidget)
        assert chat_widget is not None
        
        # Verify nested structures instantiate cleanly mapping valid properties securely
        input_widget = chat_widget.query_one("Input")
        assert input_widget.placeholder == "Ask Agastya anything..."
        
        log_widget = chat_widget.query_one("RichLog")
        assert log_widget is not None
