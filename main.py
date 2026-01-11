import sys
import os

sys.path.insert(0, os.path.abspath("Skripte"))
from Skripte.game import Game

if __name__ == "__main__":
    Game().run()
