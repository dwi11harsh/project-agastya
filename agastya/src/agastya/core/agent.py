import logging
import json
from typing import AsyncIterator, Optional
from agastya.tools.registry import ToolRegistry

from agastya.core.config import Profile
from agastya.llm.base import LLMClientFactory, Message

logger = logging.getLogger(__name__)

class Agent:
    """
    Core orchestrator handling the context window mapping LLM inputs/outputs against tool iterations accurately.
    """
    def __init__(self, profile: Profile, max_turns: int = 10, registry: Optional[ToolRegistry] = None):
        self.profile = profile
        self.max_turns = max_turns
        self.client = LLMClientFactory.create(self.profile)
        self.registry = registry

    async def stream_infer(self, messages: list[Message]) -> AsyncIterator[str]:
        """
        Processes a multi-turn logic path evaluating tool requests securely without crashing the terminal stream boundaries.
        Iteratively executes `ToolRegistry` bindings mid-stream returning output recursively.
        """
        tools_schema = self.registry.get_tool_descriptions() if self.registry else None
        
        try:
            for turn in range(self.max_turns):
                stream = self.client.stream_chat(messages, tools=tools_schema)
                
                tool_calls = {}
                content_buffer = ""
                
                async for chunk in stream:
                    if isinstance(chunk, str):
                        content_buffer += chunk
                        yield chunk
                    else:
                        # Chunk maps to native delta tool calls safely mapping indexes dynamically
                        for tc in chunk:
                            idx = tc.index
                            if idx not in tool_calls:
                                tool_calls[idx] = {"id": tc.id, "type": "function", "function": {"name": "", "arguments": ""}}
                            if tc.id:
                                tool_calls[idx]["id"] = tc.id
                            if tc.function.name:
                                tool_calls[idx]["function"]["name"] += tc.function.name
                            if tc.function.arguments:
                                tool_calls[idx]["function"]["arguments"] += tc.function.arguments
                                
                if not tool_calls:
                    return # Final inference completed natively
                    
                # Store the loop iterations mapping parameters explicitly matching upstream bindings safely
                messages.append(Message(role="assistant", content=content_buffer, tool_calls=list(tool_calls.values())))
                
                # Recursively mapping executions sequentially bouncing results back immediately
                for idx, tc in tool_calls.items():
                    name = tc["function"]["name"]
                    args_str = tc["function"]["arguments"]
                    
                    try:
                        args = json.loads(args_str)
                    except Exception:
                        args = {"payload": args_str}
                        
                    yield f"\n[dim magenta]>> agastya executing: {name}[/dim magenta]\n"
                    
                    if self.registry:
                        result = self.registry.execute(name, args)
                    else:
                        result = "Error: Tool Registry uninitialized."
                        
                    messages.append(Message(role="tool", content=str(result), tool_call_id=tc["id"], name=name))
                    
        except Exception as e:
            logger.error(f"Agent stream error: {e}")
            yield f"\n[red]Error: {e}[/red]"
