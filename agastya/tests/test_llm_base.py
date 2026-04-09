import pytest
from typing import AsyncIterator
from agastya.core.config import Profile
from agastya.llm.base import LLMClient, Message, LLMClientFactory

# Dummy implementations for testing the factory logic
class DummyOpenAIClient(LLMClient):
    def __init__(self, profile: Profile):
        self.profile = profile

    async def chat(self, messages: list[Message]) -> str:
        return "openai test"

    async def stream_chat(self, messages: list[Message]) -> AsyncIterator[str]:
        yield "openai test"

class DummyAnthropicClient(LLMClient):
    def __init__(self, profile: Profile):
        self.profile = profile

    async def chat(self, messages: list[Message]) -> str:
        return "anthropic test"

    async def stream_chat(self, messages: list[Message]) -> AsyncIterator[str]:
        yield "anthropic test"


class DummyOllamaClient(LLMClient):
    def __init__(self, profile: Profile):
        self.profile = profile

    async def chat(self, messages: list[Message]) -> str:
        return "ollama test"

    async def stream_chat(self, messages: list[Message]) -> AsyncIterator[str]:
        yield "ollama test"


@pytest.fixture
def mock_factory(monkeypatch):
    """
    Mock the module-level registry or creation mechanism to use Dummy clients
    so we don't depend on un-implemented providers in base.py tests.
    """
    def mock_create(cls, profile: Profile) -> LLMClient:
        provider = profile.provider.lower()
        if provider in ["openai", "openrouter", "gemini"]:
            return DummyOpenAIClient(profile)
        elif provider == "anthropic":
            return DummyAnthropicClient(profile)
        elif provider == "ollama":
            return DummyOllamaClient(profile)
        else:
            raise ValueError(f"Unknown LLM provider: {profile.provider}")
    
    monkeypatch.setattr(LLMClientFactory, "create", classmethod(mock_create))

def test_llm_client_protocol():
    """Verify that Message and dummy clients implement the right structure"""
    msg = Message(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"

def test_create_client_openai_provider(mock_factory):
    profile = Profile(provider="openai", model="gpt-4o-mini", description="")
    client = LLMClientFactory.create(profile)
    assert isinstance(client, DummyOpenAIClient)
    assert client.profile == profile

def test_create_client_anthropic_provider(mock_factory):
    profile = Profile(provider="anthropic", model="claude-3-opus", description="")
    client = LLMClientFactory.create(profile)
    assert isinstance(client, DummyAnthropicClient)

def test_create_client_unknown_provider():
    profile = Profile(provider="unknown_provider", model="none", description="")
    # Original factory should throw Error
    with pytest.raises(ValueError, match="Unknown LLM provider: unknown_provider"):
        LLMClientFactory.create(profile)

def test_profile_to_client_mapping(mock_factory):
    """Test that openrouter and gemini also map to openai compat"""
    profile1 = Profile(provider="openrouter", model="meta-llama/llama-3.3-70b", description="")
    client1 = LLMClientFactory.create(profile1)
    assert isinstance(client1, DummyOpenAIClient)

    profile2 = Profile(provider="gemini", model="gemini-1.5-pro", description="")
    client2 = LLMClientFactory.create(profile2)
    assert isinstance(client2, DummyOpenAIClient)
