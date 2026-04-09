from dataclasses import dataclass
from typing import Protocol, AsyncIterator
from agastya.core.config import Profile

@dataclass
class Message:
    role: str
    content: str

class LLMClient(Protocol):
    """Protocol that all LLM implementations must satisfy"""
    
    async def chat(self, messages: list[Message]) -> str:
        """Single turn, block till fully completed inference chat request."""
        ...
        
    async def stream_chat(self, messages: list[Message]) -> AsyncIterator[str]:
        """Single turn, streaming inference chat request yielding strings."""
        ...

class LLMClientFactory:
    """Factory to dispatch provider clients dependent on active profile configuration."""
    
    @classmethod
    def create(cls, profile: Profile) -> LLMClient:
        provider = profile.provider.lower()
        if provider in ["openai", "openrouter", "gemini", "ollama"]:
            # Note: actual implementations for OpenAI compatible clients and Anthropic client 
            # will be provided in subsequent phases. 
            # For now, it serves as abstract factory structure.
            # In Phase 5/6 we will replace these dummy raises with real instantiations.
            pass
        elif provider == "anthropic":
            pass
        else:
            raise ValueError(f"Unknown LLM provider: {profile.provider}")
        
        # During the abstraction-only phase, unless mocked, we aren't instantiating real clients.
        # But this code will be caught by tests, and if unmocked and trying to use right now it fails safely.
        raise NotImplementedError("Concrete implementations will be added in Phase 5 and 6")
