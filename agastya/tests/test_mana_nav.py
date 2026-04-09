import pytest
from agastya.mana.nav import NavManager

def test_generate_default_nav():
    manager = NavManager()
    content = manager.generate_default("quantum_physics")
    
    assert "# NAV: quantum_physics" in content
    assert "## Description" in content
    assert "## Capabilities" in content

def test_parse_nav_valid(tmp_path):
    nav_file = tmp_path / "NAV.md"
    nav_file.write_text("""
# NAV: my_project

## Description
This is an awesome project for testing the parser.

## Capabilities
- testing
- validation
""")
    
    manager = NavManager()
    info = manager.parse(str(nav_file))
    
    assert info.get("name") == "my_project"
    assert "This is an awesome project" in info.get("description", "")
    assert "testing" in info.get("capabilities", "")

def test_parse_nav_missing(tmp_path):
    missing_file = tmp_path / "missing_NAV.md"
    manager = NavManager()
    info = manager.parse(str(missing_file))
    
    assert info.get("name") == "Unknown"
    assert info.get("description") == ""
    assert info.get("capabilities") == ""
