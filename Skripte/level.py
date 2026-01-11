import os
import json
from Assets import blocks
from Assets import objects as o


def load_level(path):
    if not os.path.exists(path):
        print(f"Fehler: {path} nicht gefunden!")
        return []

    with open(path, "r") as f:
        data = json.load(f)

    objects = []

    for loc, t_type in data["grid"].items():
        coords = list(map(int, loc.split(";")))
        x = coords[0] * 96
        y = coords[1] * 96

        if t_type == "Block1":
            objects.append(blocks.Block(x, y, 96))
        elif t_type == "Block2":
            objects.append(blocks.Block2(x, y, 96))
        elif t_type == "Block3":
            objects.append(blocks.Block3(x, y, 96))
        elif t_type == "Block4":
            objects.append(blocks.Block4(x, y, 96))

    for item in data.get("offgrid", []):
        ox, oy = item["pos"]
        if item["type"] == "Checkpoint":
            objects.append(o.Checkpoint(ox, oy, 64, 64))
        elif item["type"] == "Trampoline":
            objects.append(o.Trampoline(ox, oy, 28, 28))
        elif item["type"] == "Fire":
            fire_obj = o.Fire(ox, oy, 16, 32)
            fire_obj.on()
            objects.append(fire_obj)
        elif item["type"] == "Lava":
            objects.append(o.Lava(ox, oy, 96, 20))

    return objects
