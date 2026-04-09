from dataclasses import dataclass
from typing import Protocol, AsyncIterator, Optional, Any
from agastya.core.config import Profile

@dataclass
class Message:
    role: str
    content: str
    tool_call_id: Optional[str] = None
    tool_calls: Optional[list[dict]] = None
    name: Optional[str] = None

class LLMClient(Protocol):
    """Protocol that all LLM implementations must satisfy"""
    
    async def chat(self, messages: list[Message], tools: Optional[list[dict]] = None) -> str:
        """Single turn, block till fully completed inference chat request."""
        ...
        
    async def stream_chat(self, messages: list[Message], tools: Optional[list[dict]] = None) -> AsyncIterator[Any]:
        """Single turn, streaming inference chat request yielding strings or native tool_calls mapping safely."""
        ...

class LLMClientFactory:
    """Factory to dispatch provider clients dependent on active profile configuration."""
    
    @classmethod
    def create(cls, profile: Profile) -> LLMClient:
        provider = profile.provider.lower()
        if provider in ["openai", "openrouter", "gemini", "ollama"]:
            from agastya.llm.openai_client import OpenAIClient
            return OpenAIClient(profile)
        elif provider == "anthropic":
            from agastya.llm.anthropic_client import AnthropicClient
            return AnthropicClient(profile)
        else:
            raise ValueError(f"Unknown LLM provider: {profile.provider}")
        
        # During the abstraction-only phase, unless mocked, we aren't instantiating real clients.
        # But this code will be caught by tests, and if unmocked and trying to use right now it fails safely.
        raise NotImplementedError("Concrete implementations will be added in Phase 5 and 6")
