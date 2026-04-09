import os
from typing import Optional

class TavilySearcher:
    """
    Maps dynamic queries into the external Tavily index securely handling connection configurations properly isolating failures.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY")
        if not self.api_key:
            self._client = None
        else:
            try:
                from tavily import TavilyClient
                self._client = TavilyClient(api_key=self.api_key)
            except ImportError:
                self._client = None
                
    def is_available(self) -> bool:
        return self._client is not None

    def search(self, query: str) -> str:
        """Provides native textual summaries safely returning results without freezing scopes asynchronously."""
        if not self._client:
            return "Error: Tavily client unavailable (missing API Key or dependencies)."
        
        try:
            response = self._client.search(query=query, search_depth="basic")
            results = response.get("results", [])
            output = ""
            for item in results:
                title = item.get("title", "No Title")
                content = item.get("content", "No content provided.")
                output += f"--- {title} ---\n{content}\n\n"
            return output if output else "No results found."
        except Exception as e:
            return f"Search execution failed: {e}"
