import os
import json
from Skripte.Assets.blocks import Block
from Skripte.Assets import objects as o
from Skripte.constants import BLOCK_SIZE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "Data", "Maps")


def load_level(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"Fehler: {path} nicht gefunden!")
        return []

    with open(path, "r") as f:
        data = json.load(f)

    objects = []

    # Grid-Objekte (Blöcke)
    for loc, t_type in data.get("grid", {}).items():
        coords = list(map(int, loc.split(";")))
        x = coords[0] * BLOCK_SIZE
        y = coords[1] * BLOCK_SIZE

        if t_type in Block.BLOCKS_EDITOR_TILE_MAPPING:
            objects.append(Block(x, y, t_type))
        else:
            print(f"Warnung: unbekannter Block-Typ {t_type}")

    # Offgrid-Objekte (alle anderen)
    for item in data.get("offgrid", []):
        ox, oy = item["pos"]
        typ = item["type"]

        if typ in o.OBJECTS_EDITOR_TILE_MAPPING:
            params = o.OBJECTS_EDITOR_TILE_MAPPING[typ]
            cls = params["class"]
            width = params.get("width", 32)
            height = params.get("height", 32)
            obj = cls(ox, oy, width, height)
            if params.get("auto_on"):
                obj.on()
            objects.append(obj)
        else:
            print(f"Warnung: unbekannter Offgrid-Typ {typ}")

    return objects
