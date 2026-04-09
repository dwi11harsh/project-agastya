from typing import Optional
from agastya.llm.base import Message

class ContextManager:
    """
    Maintains conversation history and generates the system context prompt boundary securely encapsulating LLM awareness.
    """
    def __init__(self, mana_info: Optional[dict[str, str]] = None):
        self.mana_info = mana_info or {}
        self.history: list[Message] = []

    def _generate_system_prompt(self) -> str:
        base_prompt = "You are Agastya, an AI agent handling federated personal knowledge spaces called 'Manas'."
        
        if self.mana_info:
            base_prompt += "\n\nACTIVE MANA CONTEXT:\n"
            base_prompt += f"Name: {self.mana_info.get('name', 'Unknown')}\n"
            if desc := self.mana_info.get("description"):
                base_prompt += f"Description: {desc}\n"
            if caps := self.mana_info.get("capabilities"):
                base_prompt += f"Capabilities: {caps}\n"
                
        base_prompt += "\n\nUse your tools wisely to parse the environment. Follow terminal CLI safety rules strictly."
        return base_prompt

    def add_user_message(self, content: str) -> None:
        self.history.append(Message(role="user", content=content))

    def add_assistant_message(self, content: str) -> None:
        self.history.append(Message(role="assistant", content=content))

    def get_messages(self) -> list[Message]:
        return [Message(role="system", content=self._generate_system_prompt())] + self.history

    def clear(self) -> None:
        self.history = []
