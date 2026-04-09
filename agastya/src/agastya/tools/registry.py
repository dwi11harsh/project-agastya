import inspect
import json
from typing import Callable, Any

class ToolRegistry:
    """
    Standardizes native Python callbacks binding JSON-Schema metadata limits securely avoiding malformed arguments externally.
    """
    def __init__(self):
        self.tools: dict[str, dict] = {}
        self.callbacks: dict[str, Callable] = {}

    def register(self, name: str, description: str, callback: Callable) -> None:
        """Dynamically builds metadata extraction natively formatting internal variables to JSON structures."""
        # For simplicity, Phase 18 builds primitive definitions (future iterations pull explicitly mapped kwargs robustly)
        schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payload": {"type": "string", "description": "Raw string argument representation mapped explicitly"}
                    },
                    "required": ["payload"]
                }
            }
        }
        self.tools[name] = schema
        self.callbacks[name] = callback

    def get_tool_descriptions(self) -> list[dict]:
        return list(self.tools.values())

    def execute(self, name: str, args: dict[str, Any]) -> str:
        if name not in self.callbacks:
            return f"Error: Tool '{name}' not found."
            
        try:
            # We map explicit single parameters per initial Phase 18 boundary constraint simplifies execution dynamically
            payload = args.get("payload", "")
            result = self.callbacks[name](payload)
            return str(result)
        except Exception as e:
            return f"Tool Execution Error ({name}): {e}"
