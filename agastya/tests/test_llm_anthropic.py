import pytest
from unittest.mock import AsyncMock
from typing import AsyncGenerator

from agastya.core.config import Profile
from agastya.llm.base import Message
from agastya.llm.anthropic_client import AnthropicClient

@pytest.fixture
def test_profile():
    return Profile(provider="anthropic", model="claude-3-opus-20240229", description="Test profile")

@pytest.mark.asyncio
async def test_anthropic_client_chat(test_profile, monkeypatch):
    messages = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Hello")
    ]
    
    mock_create = AsyncMock()
    # Stubbing Anthropic's Message response
    mock_create.return_value.content = [
        AsyncMock(text="Hello back!")
    ]
    
    monkeypatch.setattr("agastya.llm.anthropic_client.AsyncAnthropic", AsyncMock)
    client = AnthropicClient(test_profile)
    
    client.client.messages.create = mock_create
    
    response = await client.chat(messages)
    assert response == "Hello back!"
    
    mock_create.assert_called_once_with(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        system="You are a helpful assistant.",
        messages=[{"role": "user", "content": "Hello"}],
    )

@pytest.mark.asyncio
async def test_anthropic_client_stream(test_profile, monkeypatch):
    messages = [Message(role="user", content="Tell me a story")]
    
    async def mock_stream(*args, **kwargs):
        class ContentBlockDeltaEvent:
            def __init__(self, t):
                class Delta:
                    def __init__(self, txt):
                        self.text = txt
                self.type = "content_block_delta"
                self.delta = Delta(t)
                
        class OtherEvent:
            def __init__(self):
                self.type = "message_start"

        # Anthropic streams different event types
        yield OtherEvent()
        yield ContentBlockDeltaEvent("Once ")
        yield ContentBlockDeltaEvent("upon ")
        yield ContentBlockDeltaEvent("a time")
        
    mock_create_stream = AsyncMock(side_effect=mock_stream)
    monkeypatch.setattr("agastya.llm.anthropic_client.AsyncAnthropic", AsyncMock)
    
    client = AnthropicClient(test_profile)
    client.client.messages.create = mock_create_stream
    
    chunks = []
    async for chunk in client.stream_chat(messages):
        chunks.append(chunk)
        
    assert chunks == ["Once ", "upon ", "a time"]
    
    mock_create_stream.assert_called_once_with(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        system="",
        messages=[{"role": "user", "content": "Tell me a story"}],
        stream=True
    )
