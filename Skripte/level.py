import os
import json
from Skripte.Assets.blocks import Block
from Skripte.Assets import objects as o
from Skripte.rooms import Room
from Skripte.constants import BLOCK_SIZE
from Skripte.Assets.decoration import Decoration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "Data", "Maps")


def load_level(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []

    with open(path, "r") as f:
        data = json.load(f)

    global_decorations = []
    for item in data.get("global_background", []):
        obj = Decoration(item["pos"][0], item["pos"][1], item["type"])
        global_decorations.append(obj)
    rooms = []

    for r_data in data.get("rooms", []):
        rect = r_data["rect"]
        new_room = Room(rect[0], rect[1], rect[2], rect[3], r_data["type"],
                        r_data["spawn"][0], r_data["spawn"][1])

        def process_tile(t_type, pos, layer):
            # 1. Ist es ein BLOCK?
            if t_type in Block.BLOCKS_EDITOR_TILE_MAPPING:
                obj = Block(pos[0], pos[1], t_type)
                # Nur Layer 0 behält die physische Kollision
                if layer == 0:
                    new_room.blocks.append(obj)
                else:
                    # Blöcke auf anderen Layern werden visuell einsortiert
                    assign_to_visual_layer(obj, layer)

            # 2. Ist es ein OBJEKT?
            elif t_type in o.OBJECTS_EDITOR_TILE_MAPPING:
                params = o.OBJECTS_EDITOR_TILE_MAPPING[t_type]
                obj = params["class"](pos[0], pos[1], params.get("width"), params.get("height"),
                                      hitbox_data=params.get("hitbox_data"), **params.get("extra_args", {}))
                if params.get("auto_on") and hasattr(obj, "on"): obj.on()
                new_room.objects.append(obj)

            # 3. Ist es reine DEKO?
            elif t_type in Decoration.DECORATION_TILE_MAPPING:
                obj = Decoration(pos[0], pos[1], t_type)
                assign_to_visual_layer(obj, layer)

        def assign_to_visual_layer(obj, layer):
            if layer == 3:
                new_room.layer_3.append(obj)
            elif layer == 2:
                new_room.layer_2.append(obj)
            elif layer == 1:
                new_room.layer_1.append(obj)
            elif layer == -1:
                new_room.layer_foreground.append(obj)
            else:
                new_room.decorations.append(obj)

        # GRID verarbeiten (Unterstützt jetzt das neue Layer-Dictionary)
        for loc, t_info in r_data.get("grid", {}).items():
            coords = list(map(int, loc.split(";")))
            pos = [coords[0] * BLOCK_SIZE, coords[1] * BLOCK_SIZE]

            # Check, ob t_info ein Dictionary (neu) oder String (alt) ist
            if isinstance(t_info, dict):
                process_tile(t_info["type"], pos, t_info.get("layer", 0))
            else:
                process_tile(t_info, pos, 0)

        # OFFGRID verarbeiten
        for item in r_data.get("offgrid", []):
            process_tile(item["type"], item["pos"], item.get("layer", 0))

        # DECORATIONS verarbeiten
        for item in r_data.get("decorations", []):
            process_tile(item["type"], item["pos"], item.get("layer", 0))

        rooms.append(new_room)

    # Nachbarn berechnen
    for r1 in rooms:
        check_rect = r1.rect.inflate(BLOCK_SIZE * 2, BLOCK_SIZE * 2)
        for r2 in rooms:
            if r1 != r2 and check_rect.colliderect(r2.rect):
                r1.add_neighbors(r2)

    return rooms, global_decorations