import pytest
import os
from unittest.mock import MagicMock
from agastya.tools.registry import ToolRegistry
from agastya.tools.tavily import TavilySearcher

def test_tool_registry_formatting():
    registry = ToolRegistry()
    
    def dummy_tool(payload: str) -> str:
        return f"Hello {payload}"
        
    registry.register("test_tool", "A dummy tool", dummy_tool)
    
    # Verify metadata formatting correctly wraps variables natively avoiding null limits
    schemas = registry.get_tool_descriptions()
    assert len(schemas) == 1
    assert schemas[0]["function"]["name"] == "test_tool"
    assert "payload" in schemas[0]["function"]["parameters"]["properties"]
    
    # Check execution boundaries safely mapping inputs correctly
    res = registry.execute("test_tool", {"payload": "World"})
    assert res == "Hello World"

def test_tavily_search_mocking(monkeypatch):
    mock_client = MagicMock()
    mock_client.search.return_value = {
        "results": [
            {"title": "Test Content", "content": "This is a dummy result"}
        ]
    }
    
    monkeypatch.setattr("os.environ.get", lambda k, default=None: "dummy_key" if k == "TAVILY_API_KEY" else default)
    monkeypatch.setattr("os.getenv", lambda k, default=None: "dummy_key" if k == "TAVILY_API_KEY" else default)
    
    # Bypass actual SDK initialization explicitly setting internal dependency references properly
    searcher = TavilySearcher()
    monkeypatch.setattr(searcher, "_client", mock_client)
    
    result = searcher.search("hello")
    assert "Test Content" in result
    assert "dummy result" in result
