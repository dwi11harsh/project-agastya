import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class ManaInfo:
    name: str
    path: str
    page_count: int = 0
    source_count: int = 0

class ManaManager:
    def __init__(self, config_dir: Path | None = None):
        if config_dir is None:
            config_dir = Path.home() / ".agastya"
        self.config_dir = config_dir
        self.registry_file = self.config_dir / "manas.yaml"
        
    def is_mana(self, path: Path) -> bool:
        return (path / "NAV.md").exists()

    def register(self, path: Path) -> None:
        if not self.is_mana(path):
            raise ValueError("Directory does not contain a NAV.md file. It is not a valid mana.")
            
        registry = self._load_registry()
        name = path.name
        
        if name in registry:
            raise ValueError(f"Mana with name '{name}' is already registered")
            
        registry[name] = {
            "path": str(path.absolute())
        }
        
        self._save_registry(registry)

    def unregister(self, name: str) -> None:
        registry = self._load_registry()
        if name not in registry:
            raise ValueError(f"Mana '{name}' is not registered")
            
        del registry[name]
        self._save_registry(registry)

    def list_all(self) -> List[ManaInfo]:
        registry = self._load_registry()
        manas = []
        for name, data in registry.items():
            manas.append(ManaInfo(
                name=name,
                path=data.get("path", "")
            ))
        return manas

    def init(self, path: Path) -> None:
        if path.exists() and self.is_mana(path):
            raise ValueError("Directory is already a mana.")

        path.mkdir(parents=True, exist_ok=True)
        
        (path / "NAV.md").touch()
        (path / "schema.md").touch()
        (path / "log.md").touch()
        (path / "inbox.md").touch()
        
        (path / "raw").mkdir(exist_ok=True)
        (path / "pages").mkdir(exist_ok=True)
        (path / ".agastya").mkdir(exist_ok=True)

    def _load_registry(self) -> dict:
        if not self.registry_file.exists():
            return {}
        try:
            with open(self.registry_file, "r") as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        except yaml.YAMLError:
            return {}

    def _save_registry(self, data: dict) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, "w") as f:
            yaml.dump(data, f)
