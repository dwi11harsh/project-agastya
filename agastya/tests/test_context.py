import pytest
from agastya.core.context import ContextManager
from agastya.llm.base import Message

def test_context_manager_system_prompt():
    manager = ContextManager()
    
    # Check default system prompt without explicit active mana details
    messages = manager.get_messages()
    assert len(messages) == 1
    assert messages[0].role == "system"
    assert "You are Agastya" in messages[0].content
    
    # Check injection of context dictionary parameters
    manager = ContextManager(mana_info={"name": "test_project", "description": "testing 123", "capabilities": "magic"})
    sys_msg = manager.get_messages()[0].content
    assert "test_project" in sys_msg
    assert "testing 123" in sys_msg
    assert "magic" in sys_msg

def test_context_manager_append_history():
    manager = ContextManager()
    manager.add_user_message("Query")
    manager.add_assistant_message("Response")
    
    messages = manager.get_messages()
    assert len(messages) == 3  # System + User + Assistant
    assert messages[1].role == "user"
    assert messages[1].content == "Query"
    assert messages[2].role == "assistant"
    assert messages[2].content == "Response"
