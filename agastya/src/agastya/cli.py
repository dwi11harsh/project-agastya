import argparse
import sys
import os
from pathlib import Path
from agastya.mana.manager import ManaManager

def launch_tui():
    """Shell placeholder mapping future textal components loading loop execution natively."""
    print("Launching Agastya Terminal UI Layer (Phase 15+ implementation mapping pending).")

def main():
    parser = argparse.ArgumentParser(
        description="Agastya - Federated Personal Knowledge Context AI Agent"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available sub-commands")
    
    # 'init' command
    init_parser = subparsers.add_parser("init", help="Initialize the current directory as a new Mana")
    
    args = parser.parse_args()
    
    if args.command == "init":
        manager = ManaManager()
        try:
            cwd = os.getcwd()
            # The manager natively reads the given root internally dynamically utilizing OS layers
            manager.init(Path(cwd))
            print(f"Successfully initialized mana environment in: {cwd}")
        except Exception as e:
            print(f"Error initializing mana: {e}")
            sys.exit(1)
    else:
        # Default application boot sequence loading Textual interface
        launch_tui()

if __name__ == "__main__":
    main()
