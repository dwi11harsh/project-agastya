import os
from typing import AsyncIterator, Optional, Any

from anthropic import AsyncAnthropic
from anthropic.types import MessageParam

from agastya.core.config import Profile
from agastya.llm.base import LLMClient, Message

class AnthropicClient(LLMClient):
    def __init__(self, profile: Profile):
        self.profile = profile
        
        client_kwargs = {}
        if self.profile.base_url:
            client_kwargs["base_url"] = self.profile.base_url
            
        if not os.getenv("ANTHROPIC_API_KEY") and self.profile.base_url:
            client_kwargs["api_key"] = "dummy"

        self.client = AsyncAnthropic(**client_kwargs)

    def _extract_system_and_messages(self, messages: list[Message]) -> tuple[str, list[MessageParam]]:
        system_prompt = ""
        chat_messages: list[MessageParam] = []
        
        for msg in messages:
            if msg.role == "system":
                system_prompt += msg.content + "\n"
            else:
                chat_messages.append({"role": msg.role, "content": msg.content}) # type: ignore
                
        return system_prompt.strip(), chat_messages

    async def chat(self, messages: list[Message], tools: Optional[list[dict]] = None) -> str:
        system_prompt, chat_messages = self._extract_system_and_messages(messages)
        
        response = await self.client.messages.create(
            model=self.profile.model,
            max_tokens=4096,
            system=system_prompt,
            messages=chat_messages,
        )
        return response.content[0].text

    async def stream_chat(self, messages: list[Message], tools: Optional[list[dict]] = None) -> AsyncIterator[Any]:
        system_prompt, chat_messages = self._extract_system_and_messages(messages)
        
        stream = await self.client.messages.create(
            model=self.profile.model,
            max_tokens=4096,
            system=system_prompt,
            messages=chat_messages,
            stream=True
        )
        
        async for event in stream:
            if event.type == "content_block_delta":
                yield event.delta.text # type: ignore
