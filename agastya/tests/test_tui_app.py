import pytest
from agastya.tui.app import AgastyaApp

@pytest.mark.asyncio
async def test_tui_app_mounts():
    app = AgastyaApp()
    
    # Run a headless test capturing the UI mount loops natively validating text widgets properly without launching onto actual screens physically.
    async with app.run_test() as pilot:
        # Check standard definitions loaded securely
        assert app.title == "Agastya"
        assert app.sub_title == "Local Knowledge AI"
        
        # Optionally, verify the layout exists securely mapping widgets correctly
        assert app.query("Header")
        assert app.query("Footer")
