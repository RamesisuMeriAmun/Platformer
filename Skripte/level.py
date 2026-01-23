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

        for loc, t_type in r_data.get("grid", {}).items():
            coords = list(map(int, loc.split(";")))
            pos_x = coords[0] * BLOCK_SIZE
            pos_y = coords[1] * BLOCK_SIZE

            if t_type in Block.BLOCKS_EDITOR_TILE_MAPPING:
                new_room.blocks.append(Block(pos_x, pos_y, t_type))

            elif t_type in o.OBJECTS_EDITOR_TILE_MAPPING:
                params = o.OBJECTS_EDITOR_TILE_MAPPING[t_type]
                cls = params["class"]
                width = params.get("width")
                height = params.get("height")
                obj = cls(pos_x, pos_y, width, height)

                if params.get("auto_on") and hasattr(obj, "on"):
                    obj.on()

                new_room.objects.append(obj)

        for item in r_data.get("offgrid", []):
            t_type = item["type"]
            pos = item["pos"]

            if t_type in Block.BLOCKS_EDITOR_TILE_MAPPING:
                new_room.blocks.append(Block(pos[0], pos[1], t_type))

            elif t_type in o.OBJECTS_EDITOR_TILE_MAPPING:
                params = o.OBJECTS_EDITOR_TILE_MAPPING[t_type]
                cls = params["class"]
                width = params.get("width")
                height = params.get("height")
                obj = cls(pos[0], pos[1], width, height)

                if params.get("auto_on") and hasattr(obj, "on"):
                    obj.on()

                new_room.objects.append(obj)

        rooms.append(new_room)

    for r1 in rooms:
        check_rect = r1.rect.inflate(BLOCK_SIZE * 2, BLOCK_SIZE * 2)
        for r2 in rooms:
            if r1 != r2 and check_rect.colliderect(r2.rect):
                r1.add_neighbors(r2)

    return rooms
