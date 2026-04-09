import os
from typing import AsyncIterator

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from agastya.core.config import Profile
from agastya.llm.base import LLMClient, Message

class OpenAIClient(LLMClient):
    def __init__(self, profile: Profile):
        self.profile = profile
        
        client_kwargs = {}
        if self.profile.base_url:
            client_kwargs["base_url"] = self.profile.base_url
            
        # Ensure a dummy key is set for local endpoints that don't need one to bypass validation
        if not os.getenv("OPENAI_API_KEY") and self.profile.base_url:
            client_kwargs["api_key"] = "dummy"

        self.client = AsyncOpenAI(**client_kwargs)

    def _format_messages(self, messages: list[Message]) -> list[ChatCompletionMessageParam]:
        return [{"role": msg.role, "content": msg.content} for msg in messages] # type: ignore

    async def chat(self, messages: list[Message]) -> str:
        response = await self.client.chat.completions.create(
            model=self.profile.model,
            messages=self._format_messages(messages),
            stream=False
        )
        # mypy type check for str
        return str(response.choices[0].message.content)

    async def stream_chat(self, messages: list[Message]) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.profile.model,
            messages=self._format_messages(messages),
            stream=True
        )
        
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content
