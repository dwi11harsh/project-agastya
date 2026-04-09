import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import AsyncGenerator

from agastya.core.config import Profile
from agastya.llm.base import Message
from agastya.llm.openai_client import OpenAIClient

@pytest.fixture
def test_profile():
    return Profile(provider="openai", model="gpt-4", description="Test profile")

@pytest.fixture
def custom_base_url_profile():
    return Profile(provider="ollama", model="llama3", description="Local ollama", base_url="http://localhost:11434/v1")

@pytest.mark.asyncio
async def test_openai_client_chat(test_profile, monkeypatch):
    messages = [Message(role="user", content="Hello")]
    
    # Mocking the client
    mock_create = AsyncMock()
    mock_create.return_value.choices = [
        AsyncMock(message=AsyncMock(content="Hello back!"))
    ]
    
    monkeypatch.setattr("agastya.llm.openai_client.AsyncOpenAI", MagicMock())
    client = OpenAIClient(test_profile)
    
    # Overwrite the instantiated async openai class sub-objects
    client.client.chat.completions.create = mock_create
    
    response = await client.chat(messages)
    assert response == "Hello back!"
    
    mock_create.assert_called_once_with(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}],
        stream=False
    )

@pytest.mark.asyncio
async def test_openai_client_stream(test_profile, monkeypatch):
    messages = [Message(role="user", content="Tell me a story")]
    
    async def mock_stream(*args, **kwargs) -> AsyncGenerator:
        class Chunk:
            class Choice:
                class Delta:
                    def __init__(self, c):
                        self.content = c
                def __init__(self, c):
                    self.delta = self.Delta(c)
            def __init__(self, content):
                self.choices = [self.Choice(content)]
                
        yield Chunk("Once ")
        yield Chunk("upon ")
        yield Chunk("a time")
        # Empty chunk (simulating end response that some providers do)
        yield Chunk(None)

    mock_create = AsyncMock(side_effect=mock_stream)
    monkeypatch.setattr("agastya.llm.openai_client.AsyncOpenAI", MagicMock())
    
    client = OpenAIClient(test_profile)
    client.client.chat.completions.create = mock_create
    
    chunks = []
    async for chunk in client.stream_chat(messages):
        chunks.append(chunk)
        
    assert chunks == ["Once ", "upon ", "a time"]
    
    mock_create.assert_called_once_with(
        model="gpt-4",
        messages=[{"role": "user", "content": "Tell me a story"}],
        stream=True
    )

def test_openai_client_custom_base_url(custom_base_url_profile, monkeypatch):
    mock_async_openai = MagicMock()
    monkeypatch.setattr("agastya.llm.openai_client.AsyncOpenAI", mock_async_openai)
    
    client = OpenAIClient(custom_base_url_profile)
    
    # Verify the mocked AsyncOpenAI constructor got the base_url and dummy api_key
    mock_async_openai.assert_called_once_with(base_url="http://localhost:11434/v1", api_key="dummy")
