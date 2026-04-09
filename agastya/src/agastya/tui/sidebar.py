from textual.widgets import Tree
from textual.app import ComposeResult
from agastya.mana.manager import ManaManager

class ManaSidebar(Tree):
    """
    Renders topological directory bindings tracking globally registered domains utilizing native Tree visualization cleanly.
    """
    def __init__(self, *args, **kwargs):
        # Override structural parameters safely rendering unified node formats
        super().__init__("Global Knowledge Manas", *args, **kwargs)
        self.manager = ManaManager()

    def on_mount(self) -> None:
        """Automates footprint bindings natively looping known directories."""
        # Setup aesthetic mapping 
        self.root.expand()

        try:
            # Poll config extracting native arrays seamlessly
            manas = self.manager.list_all()
            for mana in manas:
                # Add nodes rendering clean visual blocks avoiding physical nesting arrays
                node = self.root.add(str(mana.name))
                node.add_leaf(str(mana.path))
                node.expand()
        except Exception as e:
            # Add crash fallback mapping cleanly resolving unit faults safely
            self.root.add_leaf(f"Error loading manas: {e}")
