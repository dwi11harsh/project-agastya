import datetime
from pathlib import Path

def append_to_inbox(mana_path: str, content: str) -> str:
    """
    Appends a new entry to the inbox.md file of a given mana.
    This bypasses user-confirmation shell executors securely because it operates linearly on the local app state safely.
    """
    try:
        p = Path(mana_path)
        
        # Validation checks
        if not p.exists() or not p.is_dir():
            return f"Error appending to inbox: Path '{mana_path}' not a valid initialized mana directory."
            
        if not (p / "NAV.md").exists():
            return f"Error appending to inbox: Path '{mana_path}' not a valid initialized mana directory (missing NAV.md)."
            
        inbox_file = p / "inbox.md"
        
        # Prepare content string with ISO timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = f"\n\n---\n**{timestamp}**\n\n{content}\n"
        
        # Append logic (will create if it doesn't exist)
        with open(inbox_file, "a", encoding="utf-8") as f:
            f.write(payload)
            
        return f"Successfully appended to inbox at {inbox_file}"
        
    except Exception as e:
         return f"Error appending to inbox: {e}"
