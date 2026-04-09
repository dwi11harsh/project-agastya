import logging
from typing import AsyncIterator

from agastya.core.config import Profile
from agastya.llm.base import LLMClientFactory, Message

logger = logging.getLogger(__name__)

class Agent:
    """
    Core orchestrator handling the context window mapping LLM inputs/outputs against tool iterations accurately.
    """
    def __init__(self, profile: Profile, max_turns: int = 10):
        self.profile = profile
        self.max_turns = max_turns
        self.client = LLMClientFactory.create(self.profile)

    async def stream_infer(self, messages: list[Message]) -> AsyncIterator[str]:
        """
        Processes a multi-turn logic path evaluating tool requests securely without crashing the terminal stream boundaries.
        Currently natively forwards the generator straight from the client for UI streaming.
        Future extensions (post-phase 12) will trap tool-request XML/JSON payloads here to evaluate sub-loops dynamically.
        """
        # Right now we operate a single turn natively to bridge TUI rendering flows properly 
        # (Tools parsing logic will wedge here returning sub-turns)
        try:
            stream = self.client.stream_chat(messages)
            
            async for chunk in stream:
                yield chunk
                
        except Exception as e:
            logger.error(f"Agent stream error: {e}")
            yield f"\n[Error: {e}]"
