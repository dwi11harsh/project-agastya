from agastya.tools.registry import ToolRegistry
from agastya.tools.tavily import TavilySearcher
from agastya.builtins.executor import ShellExecutor
from agastya.builtins.file_ops import read_file, write_file, list_dir

def get_master_registry() -> ToolRegistry:
    """
    Initializes and maps all universal built-in parameters wrapping system capabilities into the LLM logic layer seamlessly.
    """
    registry = ToolRegistry()
    tavily = TavilySearcher()
    shell = ShellExecutor()
    
    # 1. Tavily Search binding
    registry.register(
        name="web_search",
        description="Searches the live Web via Tavily returning precise textual answers explicitly. Pass the query as 'payload'.",
        callback=lambda payload: tavily.search(payload)
    )
    
    # 2. Shell Execution binding
    registry.register(
        name="execute_shell_command",
        description="Executes a raw terminal bash command wrapping outcomes. Demands user approval visually! Pass command as 'payload'.",
        callback=lambda payload: shell.execute(payload)
    )
    
    # 3. File Operations bindings
    registry.register(
        name="read_file",
        description="Reads full content from an absolute or relative filepath. Pass filepath as 'payload'.",
        callback=lambda payload: read_file(payload)
    )
    
    registry.register(
        name="list_directory",
        description="Lists all files in a specific directory structure. Pass directory as 'payload'.",
        callback=lambda payload: list_dir(payload)
    )
    
    # Write file uses two arguments typically, but we map explicit dictionary json structs or parse basic logic.
    # To keep Phase 19 compliant with our basic single "payload" registry, we can expect "path|content" split by '|'.
    # In future registry refactors, this will use dynamic mapping schemas purely.
    def _split_write(payload: str) -> str:
        try:
            path, content = payload.split("|", 1)
            return write_file(path.strip(), content.strip())
        except ValueError:
            return "Error: write_file payload must be delimited with a pipe symbol: 'filepath|content'"
            
    registry.register(
        name="write_file",
        description="Writes mapped content directly to a filepath. payload format MUST be exactly: 'path|content'",
        callback=_split_write
    )
    
    # 4. Feature bindings
    def _feature_toggle(payload: str, feature: str) -> str:
        # Simplistic toggle simulation for Phase 19 context hooks without mapping heavy global states
        return f"[System: Context aware. {feature} logic footprint triggered for payload: {payload[:20]}...]"

    registry.register(
        name="generate_blog_post",
        description="Generates an extensive formatted blog post context block explicitly. Pass subject as 'payload'.",
        callback=lambda payload: _feature_toggle(payload, "Blog Generation")
    )
    
    registry.register(
        name="generate_tweet",
        description="Generates and structures a formatted Twitter post directly natively. Pass subject as 'payload'.",
        callback=lambda payload: _feature_toggle(payload, "Tweet Generation")
    )
    
    return registry
