import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / "Skripte"))

from Skripte import game

if __name__ == "__main__":
    game.Game().run()
