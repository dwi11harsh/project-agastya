import re
from pathlib import Path

class NavManager:
    """
    Manages generation and semantic parsing of NAV.md files for a mana directory.
    """
    def generate_default(self, name: str) -> str:
        """Returns standard boiler-plate content for a new NAV.md document"""
        return f"""# NAV: {name}

## Description
Describe the purpose of this mana here.

## Capabilities
List tools, domains, or abilities associated with this mana.

## Connections
List internal mana links or external URLs relevant to this context.
"""
        
    def parse(self, path: str) -> dict[str, str]:
        """
        Extracts semantic properties from NAV.md using resilient string matching.
        Returns a dictionary containing 'name', 'description', and 'capabilities'.
        """
        p = Path(path)
        if not p.exists() or not p.is_file():
            return {"name": "Unknown", "description": "", "capabilities": ""}
            
        try:
            content = p.read_text(encoding="utf-8")
        except Exception:
            return {"name": "Unknown", "description": "", "capabilities": ""}
            
        data = {
            "name": "Unknown",
            "description": "",
            "capabilities": ""
        }
        
        # Match "# NAV: Name"
        name_match = re.search(r'^#\s*NAV:\s*(.*?)$', content, re.MULTILINE)
        if name_match:
            data["name"] = name_match.group(1).strip()
            
        # Match description block (stops at next H2 or EOF)
        desc_match = re.search(r'##\s*Description\s*\n(.*?)(?=\n##|$)', content, re.DOTALL | re.IGNORECASE)
        if desc_match:
            data["description"] = desc_match.group(1).strip()
            
        # Match capabilities block
        cap_match = re.search(r'##\s*Capabilities\s*\n(.*?)(?=\n##|$)', content, re.DOTALL | re.IGNORECASE)
        if cap_match:
            data["capabilities"] = cap_match.group(1).strip()
            
        return data
