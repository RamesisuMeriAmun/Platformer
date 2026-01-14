import sys
from pathlib import Path

import pygame

pygame.init()
from Ui.main_menu import main_menu

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / "Skripte"))

if __name__ == "__main__":
    main_menu()
