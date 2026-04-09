import os
from typing import AsyncIterator, Optional, Any

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
        formatted = []
        for msg in messages:
            msg_dict = {"role": msg.role, "content": msg.content}
            if msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id # type: ignore
            if msg.name:
                msg_dict["name"] = msg.name # type: ignore
            if msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls # type: ignore
            formatted.append(msg_dict)
        return formatted # type: ignore

    async def chat(self, messages: list[Message], tools: Optional[list[dict]] = None) -> str:
        kwargs = {
            "model": self.profile.model,
            "messages": self._format_messages(messages),
            "stream": False
        }
        if tools:
            kwargs["tools"] = tools
            
        response = await self.client.chat.completions.create(**kwargs)
        return str(response.choices[0].message.content)

    async def stream_chat(self, messages: list[Message], tools: Optional[list[dict]] = None) -> AsyncIterator[Any]:
        kwargs = {
            "model": self.profile.model,
            "messages": self._format_messages(messages),
            "stream": True
        }
        if tools:
            kwargs["tools"] = tools
            
        stream = await self.client.chat.completions.create(**kwargs)
        
        async for chunk in stream:
            delta = chunk.choices[0].delta
            tool_calls = getattr(delta, "tool_calls", None)
            if tool_calls:
                yield tool_calls
            elif delta.content is not None:
                yield delta.content
