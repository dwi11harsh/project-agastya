import pytest
from textual.app import App, ComposeResult
from agastya.tui.sidebar import ManaSidebar
from agastya.mana.manager import ManaInfo
from unittest.mock import MagicMock

class MockSidebarApp(App):
    def compose(self) -> ComposeResult:
        yield ManaSidebar()

@pytest.mark.asyncio
async def test_sidebar_widget_mounting(monkeypatch):
    mock_manager = MagicMock()
    mock_manager.list_all.return_value = [
        ManaInfo(name="project_alpha", path="/dummy/alpha"),
        ManaInfo(name="project_beta", path="/dummy/beta")
    ]
    monkeypatch.setattr("agastya.tui.sidebar.ManaManager", MagicMock(return_value=mock_manager))

    app = MockSidebarApp()
    
    async with app.run_test() as pilot:
        sidebar = app.query_one(ManaSidebar)
        assert sidebar is not None
        
        # Checking native text renderings capturing correctly injected payloads properly avoiding physical links
        assert str(sidebar.root.label) == "Global Knowledge Manas"
