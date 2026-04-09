import os
from pathlib import Path

def read_file(path: str) -> str:
    """Read a file's contents safely."""
    try:
        p = Path(path)
        return p.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(path: str, content: str) -> str:
    """Write content to a file, creating parent directories if they don't exist."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"

def list_dir(path: str) -> list[str]:
    """List directory contents, adding a trailing slash to directories."""
    try:
        p = Path(path)
        if not p.exists() or not p.is_dir():
            raise FileNotFoundError(f"Directory not found: {path}")
            
        entries = []
        for entry in p.iterdir():
            name = entry.name
            if entry.is_dir():
                name += "/"
            entries.append(name)
        return sorted(entries)
    except Exception as e:
        return [f"Error listing directory: {e}"]
