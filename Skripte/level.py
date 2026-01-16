import os
import json
from Skripte.Assets.blocks import Block
from Skripte.Assets import objects as o
from Skripte.rooms import Room
from Skripte.constants import BLOCK_SIZE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "Data", "Maps")


def load_level(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []

    with open(path, "r") as f:
        data = json.load(f)

    rooms = []

    for r_data in data.get("rooms", []):
        rect = r_data["rect"]
        new_room = Room(rect[0], rect[1], rect[2], rect[3], r_data["type"],
                        r_data["spawn"][0], r_data["spawn"][1])

        # Blöcke laden
        for loc, t_type in r_data.get("grid", {}).items():
            coords = list(map(int, loc.split(";")))
            new_room.blocks.append(Block(coords[0] * BLOCK_SIZE, coords[1] * BLOCK_SIZE, t_type))

        # Objekte laden
        for item in r_data.get("offgrid", []):
            params = o.OBJECTS_EDITOR_TILE_MAPPING[item["type"]]
            obj = params["class"](item["pos"][0], item["pos"][1],
                                  params.get("width", 32), params.get("height", 32))
            new_room.objects.append(obj)

        rooms.append(new_room)

    for r1 in rooms:
        check_rect = r1.rect.inflate(BLOCK_SIZE * 2, BLOCK_SIZE * 2)

        for r2 in rooms:
            if r1 != r2 and check_rect.colliderect(r2.rect):
                r1.add_neighbors(r2)

    return rooms
