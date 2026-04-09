import pytest
import re
from datetime import datetime
from pathlib import Path
from agastya.builtins.inbox import append_to_inbox

@pytest.fixture
def temp_mana(tmp_path):
    mana_dir = tmp_path / "test_mana"
    mana_dir.mkdir()
    (mana_dir / "NAV.md").touch()
    (mana_dir / "inbox.md").touch()
    return mana_dir

def test_append_to_inbox_success(temp_mana):
    content = "This is a new observation regarding testing."
    result = append_to_inbox(str(temp_mana), content)
    
    assert "Successfully appended to inbox" in result
    
    inbox_content = (temp_mana / "inbox.md").read_text()
    assert content in inbox_content
    
    # Verify the timestamp formatting roughly
    assert "\n\n---\n**" in inbox_content
    assert "**\n\nThis is a new observation regarding testing." in inbox_content

def test_append_to_inbox_missing_mana(tmp_path):
    invalid_dir = tmp_path / "ghost_mana"
    result = append_to_inbox(str(invalid_dir), "Content")
    
    assert result.startswith("Error appending to inbox")
    assert "not a valid initialized mana" in result

def test_append_to_inbox_missing_inbox_file(tmp_path):
    # A dir that is a mana (has NAV.md) but missing inbox.md
    broken_mana = tmp_path / "broken"
    broken_mana.mkdir()
    (broken_mana / "NAV.md").touch()
    
    result = append_to_inbox(str(broken_mana), "Content")
    assert "Successfully appended" in result
    
    # It should seamlessly auto-create the inbox.md
    assert (broken_mana / "inbox.md").exists()
    assert "Content" in (broken_mana / "inbox.md").read_text()
