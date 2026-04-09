import pytest
import sys
from unittest.mock import MagicMock
from agastya.cli import main

def test_cli_init_command(monkeypatch):
    mock_initialize = MagicMock()
    monkeypatch.setattr("agastya.mana.manager.ManaManager.init", mock_initialize)
    monkeypatch.setattr("agastya.cli.os.getcwd", MagicMock(return_value="/mock/path"))
    
    # Mock sys.argv safely to mimic invoking "mana init"
    monkeypatch.setattr(sys, "argv", ["mana", "init"])
    
    # Run the entrypoint
    main()
    
    # Verify manager successfully invoked its init parameters properly securely
    mock_initialize.assert_called_once()

def test_cli_default_run(monkeypatch, capsys):
    # Mock TUI application block so we don't drop into terminal takeover
    mock_tui = MagicMock()
    monkeypatch.setattr("agastya.cli.launch_tui", mock_tui)
    
    # Mock sys.argv to run just "mana"
    monkeypatch.setattr(sys, "argv", ["mana"])
    
    main()
    
    # Verify the fallback launch path successfully executed preventing raw exceptions 
    mock_tui.assert_called_once_with()
