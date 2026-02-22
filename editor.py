import os
import json
import pygame
from Skripte.Assets.blocks import Block
from Skripte.Assets import objects as o
from Skripte.Assets.decoration import Decoration
from Skripte.constants import BLOCK_SIZE, WIDTH, HEIGHT
from Skripte import rooms

FPS = 60

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_DIR = os.path.join(BASE_DIR, "Data", "Maps")


class LevelEditor:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH // 1.5, HEIGHT // 1.5))
        pygame.display.set_caption(
            "Level Editor - Scrollen zum Wechseln | [0-5] Layer | [STRG+0-5] Sichtbarkeit"
        )
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

        self.scroll = [0, 0]
        self.zoom = 1.0
        self.movement = [False, False, False, False]

        self.ongrid = True
        self.room_mode = False
        self.debug = False

        self.show_ui = False
        self.ui_page = 0
        self.ui_category = "Blocks"

        self.tilemap = {}
        self.offgrid_tiles = []
        self.rooms_list = []

        self.room_start_pos = None
        self.room_types = list(rooms.ROOM_MAPPING.keys())
        self.current_room_idx = 0

        self.sky_mode = False
        self.current_layer = 0

        self.layer_visibility = {4: True, 3: True, 2: True, 1: True, 0: True, -1: True}
        self.layer_display_data = {
            4: {"name": "L4: Global Background", "color": (255, 215, 0)},
            3: {"name": "L3: Far Back", "color": (100, 100, 255)},
            2: {"name": "L2: Background", "color": (150, 150, 255)},
            1: {"name": "L1: Midground", "color": (200, 200, 255)},
            0: {"name": "L0: Gameplay", "color": (255, 255, 255)},
            -1: {"name": "L-1: Foreground", "color": (255, 100, 100)}
        }

        self.assets = {}
        for name in Block.BLOCKS_EDITOR_TILE_MAPPING:
            self.assets[name] = Block(0, 0, name).image
        for name, params in o.OBJECTS_EDITOR_TILE_MAPPING.items():
            cls = params["class"]
            width = params.get("width", 32)
            height = params.get("height", 32)
            hitbox = params.get("hitbox_data")
            extra_args = params.get("extra_args", {})
            surf = cls(0, 0, width, height, hitbox_data=hitbox, **extra_args).image
            self.assets[name] = surf
        for name in Decoration.DECORATION_TILE_MAPPING:
            self.assets[name] = Decoration(0, 0, name).image

        self.tile_list = list(self.assets.keys())
        self.current_type_idx = 0

        self.block_types = [n for n in self.tile_list if n in Block.BLOCKS_EDITOR_TILE_MAPPING]
        self.object_types = [n for n in self.tile_list if n in o.OBJECTS_EDITOR_TILE_MAPPING]
        self.decoration_types = [n for n in self.tile_list if n in Decoration.DECORATION_TILE_MAPPING]

    @staticmethod
    def create_object(typ, x, y):
        if typ in Block.BLOCKS_EDITOR_TILE_MAPPING:
            return Block(x, y, typ)
        elif typ in o.OBJECTS_EDITOR_TILE_MAPPING:
            params = o.OBJECTS_EDITOR_TILE_MAPPING[typ]
            cls = params["class"]
            width = params.get("width", 32)
            height = params.get("height", 32)
            hitbox = params.get("hitbox_data")
            extra_args = params.get("extra_args", {})
            obj = cls(x, y, width, height, hitbox_data=hitbox, **extra_args)
            if params.get("auto_on"):
                obj.on()
            return obj
        return None

    def save_map(self):
        new_rooms_data = []
        global_assets = []

        for loc, data in self.tilemap.items():
            if data.get("layer") == 4:
                coords = list(map(int, loc.split(";")))
                global_assets.append({
                    "type": data["type"],
                    "pos": [coords[0] * BLOCK_SIZE, coords[1] * BLOCK_SIZE],
                    "layer": 4,
                    "is_grid": True,
                    "loc": loc
                })

        for tile in self.offgrid_tiles:
            if tile.get("layer") == 4:
                global_assets.append(tile)

        for room in self.rooms_list:
            r_rect = pygame.Rect(room["rect"])
            room_content = {
                "rect": room["rect"],
                "type": room["type"],
                "spawn": room["spawn"],
                "grid": {},
                "offgrid": [],
                "decorations": []
            }

            for loc, t_data in self.tilemap.items():
                if t_data.get("layer") == 4:
                    continue
                coords = list(map(int, loc.split(";")))
                if r_rect.collidepoint(coords[0] * BLOCK_SIZE, coords[1] * BLOCK_SIZE):
                    room_content["grid"][loc] = t_data

            for tile in self.offgrid_tiles:
                if tile.get("layer") == 4:
                    continue
                if r_rect.collidepoint(tile["pos"]):
                    if tile["type"] in Decoration.DECORATION_TILE_MAPPING:
                        room_content["decorations"].append(tile)
                    else:
                        room_content["offgrid"].append(tile)

            new_rooms_data.append(room_content)

        data = {"global_background": global_assets,
                "rooms": new_rooms_data}

        os.makedirs(MAP_DIR, exist_ok=True)
        path = os.path.join(MAP_DIR, "map.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Level gespeichert: {path}")

    def load_map(self):
        path = os.path.join(MAP_DIR, "map.json")
        if not os.path.exists(path):
            print("Keine Map-Datei gefunden.")
            return

        with open(path, "r") as f:
            data = json.load(f)

        self.tilemap = {}
        self.offgrid_tiles = []
        self.rooms_list = []

        for g_item in data.get("global_background", []):
            if g_item.get("is_grid"):
                self.tilemap[g_item["loc"]] = {"type": g_item["type"], "layer": 4}
            else:
                self.offgrid_tiles.append(g_item)

        for r_data in data.get("rooms", []):
            self.rooms_list.append({
                "rect": r_data["rect"],
                "type": r_data["type"],
                "spawn": r_data["spawn"]
            })

            for loc, t_info in r_data.get("grid", {}).items():
                if isinstance(t_info, dict):
                    self.tilemap[loc] = t_info
                else:
                    self.tilemap[loc] = {"type": t_info, "layer": 0}

            for item in r_data.get("offgrid", []):
                self.offgrid_tiles.append(item)

            for item in r_data.get("decorations", []):
                self.offgrid_tiles.append(item)

    def draw_ui(self):
        if not self.show_ui: return
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.window.blit(overlay, (0, 0))

        if self.ui_category == "Blocks":
            items = self.block_types
        elif self.ui_category == "Objects":
            items = self.object_types
        else:
            items = self.decoration_types

        page_size = 20
        start = self.ui_page * page_size
        for i, name in enumerate(items[start:start + page_size]):
            x, y = 100 + (i % 5) * 120, 100 + (i // 5) * 120
            if self.tile_list[self.current_type_idx] == name:
                pygame.draw.rect(self.window, (255, 255, 0), (x - 5, y - 5, 74, 74), 2)
            self.window.blit(pygame.transform.scale(self.assets[name], (64, 64)), (x, y))
            self.window.blit(self.font.render(name[:10], True, (255, 255, 255)), (x, y + 70))

        max_pages = max(1, (len(items) + page_size - 1) // page_size)
        header = f"UI: {self.ui_category} | Seite {self.ui_page + 1}/{max_pages} | [TAB] Wechseln"
        self.window.blit(self.font.render(header, True, (255, 255, 0)), (100, 50))

    def run(self):
        run = True
        while run:
            self.window.fill((40, 40, 40))

            keys = pygame.key.get_pressed()
            speed = 15 / self.zoom
            if not self.show_ui and not self.sky_mode:
                if keys[pygame.K_a]: self.scroll[0] -= speed
                if keys[pygame.K_d]: self.scroll[0] += speed
                if keys[pygame.K_w]: self.scroll[1] -= speed
                if keys[pygame.K_s]: self.scroll[1] += speed

            mpos = pygame.mouse.get_pos()

            if self.sky_mode:
                world_x = mpos[0] / self.zoom
                world_y = mpos[1] / self.zoom
            else:
                world_x = (mpos[0] / self.zoom) + self.scroll[0]
                world_y = (mpos[1] / self.zoom) + self.scroll[1]

            grid_x, grid_y = int(world_x // BLOCK_SIZE), int(world_y // BLOCK_SIZE)
            tile_loc = f"{grid_x};{grid_y}"

            if self.room_mode:
                current_selection = self.room_types[self.current_room_idx]
            else:
                current_selection = self.tile_list[self.current_type_idx]

            if self.sky_mode:
                for x in range(0, int(WIDTH / self.zoom), BLOCK_SIZE):
                    dx = x * self.zoom
                    pygame.draw.line(self.window, (0, 100, 200), (dx, 0), (dx, HEIGHT))
                for y in range(0, int(HEIGHT / self.zoom), BLOCK_SIZE):
                    dy = y * self.zoom
                    pygame.draw.line(self.window, (0, 100, 200), (0, dy), (WIDTH, dy))
            elif self.ongrid or self.debug:
                for x in range(0, int(WIDTH / self.zoom) + BLOCK_SIZE, BLOCK_SIZE):
                    dx = (x - (self.scroll[0] % BLOCK_SIZE)) * self.zoom
                    pygame.draw.line(self.window, (60, 60, 60), (dx, 0), (dx, HEIGHT))
                for y in range(0, int(HEIGHT / self.zoom) + BLOCK_SIZE, BLOCK_SIZE):
                    dy = (y - (self.scroll[1] % BLOCK_SIZE)) * self.zoom
                    pygame.draw.line(self.window, (60, 60, 60), (0, dy), (WIDTH, dy))

            for loc, t_data in self.tilemap.items():
                t_layer = t_data.get("layer", 0)
                if self.layer_visibility.get(t_layer, True):
                    coords = list(map(int, loc.split(";")))
                    img = self.assets[t_data["type"]]

                    if t_layer == 4:
                        if self.sky_mode:
                            draw_x = coords[0] * BLOCK_SIZE * self.zoom
                            draw_y = coords[1] * BLOCK_SIZE * self.zoom
                        else:
                            draw_x = (coords[0] * BLOCK_SIZE - self.scroll[0] * 0.02) * self.zoom
                            draw_y = (coords[1] * BLOCK_SIZE - self.scroll[1] * 0.02) * self.zoom
                    else:
                        draw_x = (coords[0] * BLOCK_SIZE - self.scroll[0]) * self.zoom
                        draw_y = (coords[1] * BLOCK_SIZE - self.scroll[1]) * self.zoom

                    s_w = int(img.get_width() * self.zoom)
                    s_h = int(img.get_height() * self.zoom)
                    scaled = pygame.transform.scale(img, (max(1, s_w), max(1, s_h)))
                    self.window.blit(scaled, (draw_x, draw_y))
                    if self.debug:
                        pygame.draw.rect(self.window, (255, 0, 0), (draw_x, draw_y, s_w, s_h), 1)

            for tile in self.offgrid_tiles:
                layer = tile.get("layer", 0)
                if self.layer_visibility.get(layer, True):
                    img = self.assets[tile["type"]]

                    if layer == 4:
                        if self.sky_mode:
                            draw_x = tile["pos"][0] * self.zoom
                            draw_y = tile["pos"][1] * self.zoom
                        else:
                            draw_x = (tile["pos"][0] - self.scroll[0] * 0.02) * self.zoom
                            draw_y = (tile["pos"][1] - self.scroll[1] * 0.02) * self.zoom
                    else:
                        draw_x = (tile["pos"][0] - self.scroll[0]) * self.zoom
                        draw_y = (tile["pos"][1] - self.scroll[1]) * self.zoom

                    s_w = int(img.get_width() * self.zoom)
                    s_h = int(img.get_height() * self.zoom)
                    scaled = pygame.transform.scale(img, (max(1, s_w), max(1, s_h)))
                    self.window.blit(scaled, (draw_x, draw_y))
                    if self.debug:
                        pygame.draw.rect(self.window, (255, 255, 0), (draw_x, draw_y, s_w, s_h), 1)

            for room in self.rooms_list:
                r = room["rect"]
                r_type = room["type"]
                color = rooms.ROOM_MAPPING.get(r_type, {"color": (0, 255, 0)})["color"]
                rect_screen = pygame.Rect(
                    (r[0] - self.scroll[0]) * self.zoom,
                    (r[1] - self.scroll[1]) * self.zoom,
                    r[2] * self.zoom,
                    r[3] * self.zoom,
                )
                thickness = 3 if self.debug else 1
                pygame.draw.rect(self.window, color, rect_screen, thickness)
                if self.debug:
                    label = self.font.render(f"ROOM: {r_type}", True, color)
                    self.window.blit(label, (rect_screen.x + 5, rect_screen.y + 5))
                if "spawn" in room:
                    sp = room["spawn"]
                    s_size = max(4, int(10 * self.zoom))
                    spawn_rect = pygame.Rect(
                        (sp[0] - self.scroll[0]) * self.zoom - s_size // 2,
                        (sp[1] - self.scroll[1]) * self.zoom - s_size // 2,
                        s_size,
                        s_size,
                    )
                    pygame.draw.rect(self.window, (255, 0, 255), spawn_rect)

            if self.room_mode and self.room_start_pos:
                curr_rect = [
                    min(self.room_start_pos[0], world_x),
                    min(self.room_start_pos[1], world_y),
                    abs(self.room_start_pos[0] - world_x),
                    abs(self.room_start_pos[1] - world_y),
                ]
                pygame.draw.rect(
                    self.window, (255, 255, 255),
                    ((curr_rect[0] - self.scroll[0]) * self.zoom,
                     (curr_rect[1] - self.scroll[1]) * self.zoom,
                     curr_rect[2] * self.zoom,
                     curr_rect[3] * self.zoom), 1
                )

            if not self.room_mode and not self.show_ui:
                p_img = self.assets[current_selection]
                preview = pygame.transform.scale(p_img, (
                    int(p_img.get_width() * self.zoom), int(p_img.get_height() * self.zoom)))
                preview.set_alpha(150)
                if self.ongrid:
                    if self.sky_mode:
                        self.window.blit(preview, (grid_x * BLOCK_SIZE * self.zoom,
                                                   grid_y * BLOCK_SIZE * self.zoom))
                    else:
                        self.window.blit(preview, ((grid_x * BLOCK_SIZE - self.scroll[0]) * self.zoom,
                                                   (grid_y * BLOCK_SIZE - self.scroll[1]) * self.zoom))
                else:
                    self.window.blit(preview, mpos)

            self.draw_ui()

            mode_str = "ROOM-MODE" if self.room_mode else "TILE-MODE"
            if self.sky_mode: mode_str = "SKY-EDIT-MODE"
            info = self.font.render(f"{mode_str} | Zoom: {int(self.zoom * 100)}% | [U] UI", True,
                                    (255, 255, 255))
            self.window.blit(info, (10, 10))

            for i, l_id in enumerate([4, 3, 2, 1, 0, -1]):
                data = self.layer_display_data[l_id]
                is_active = (self.current_layer == l_id)
                is_visible = self.layer_visibility[l_id]

                color = data["color"] if is_active else (100, 100, 100)
                status = "" if is_visible else " [HIDDEN]"
                txt = self.font.render(f"{'> ' if is_active else '  '}{data['name']}{status}", True, color)
                self.window.blit(txt, (self.window.get_width() - txt.get_width() - 10, 10 + i * 20))

            if self.debug:
                editor_help = ["DEBUG MODE ACTIVE", "W,A,S,D: Move", "R: Switch Mode", "P: Set Spawn", "G: Toggle Grid",
                               "O: Save | L: Load", "F3: Toggle Debug"]
                for i, text in enumerate(editor_help):
                    h_img = self.font.render(text, True, (255, 215, 0) if i == 0 else (200, 200, 200))
                    self.window.blit(h_img, (10, 40 + i * 20))
            else:
                hint = self.font.render("Press F3 for Debug Info", True, (100, 100, 100))
                self.window.blit(hint, (self.window.get_width() - hint.get_width() - 20, self.window.get_height() - 30))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEWHEEL:
                    if self.room_mode:
                        self.current_room_idx = (self.current_room_idx - event.y) % len(self.room_types)
                    else:
                        self.current_type_idx = (self.current_type_idx - event.y) % len(self.tile_list)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.show_ui and event.button == 1:
                        items = self.block_types if self.ui_category == "Blocks" else self.object_types if self.ui_category == "Objects" else self.decoration_types
                        start = self.ui_page * 20
                        for i, name in enumerate(items[start:start + 20]):
                            ix, iy = 100 + (i % 5) * 120, 100 + (i // 5) * 120
                            if pygame.Rect(ix, iy, 64, 64).collidepoint(mpos):
                                self.current_type_idx = self.tile_list.index(name)
                                self.show_ui = False
                    elif not self.show_ui:
                        if event.button == 1:
                            if self.room_mode and pygame.key.get_mods() & pygame.KMOD_CTRL:
                                snap_x = (world_x // BLOCK_SIZE) * BLOCK_SIZE
                                snap_y = (world_y // BLOCK_SIZE) * BLOCK_SIZE
                                self.room_start_pos = (snap_x, snap_y)
                            elif not self.room_mode:
                                if self.ongrid:
                                    self.tilemap[tile_loc] = {"type": current_selection, "layer": self.current_layer}
                                else:
                                    self.offgrid_tiles.append({"type": current_selection, "pos": [world_x, world_y],
                                                               "layer": self.current_layer})
                        if event.button == 3:
                            if self.room_mode:
                                for room in self.rooms_list[::-1]:
                                    if pygame.Rect(room["rect"]).collidepoint(world_x, world_y):
                                        self.rooms_list.remove(room)
                                        break
                            else:
                                if self.ongrid and tile_loc in self.tilemap:
                                    del self.tilemap[tile_loc]
                                else:
                                    for tile in self.offgrid_tiles[::-1]:
                                        rect = pygame.Rect(tile["pos"][0], tile["pos"][1],
                                                           self.assets[tile["type"]].get_width(),
                                                           self.assets[tile["type"]].get_height())
                                        if rect.collidepoint(world_x, world_y): self.offgrid_tiles.remove(tile); break

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.room_start_pos:
                        snap_end_x = (world_x // BLOCK_SIZE) * BLOCK_SIZE + BLOCK_SIZE
                        snap_end_y = (world_y // BLOCK_SIZE) * BLOCK_SIZE + BLOCK_SIZE
                        new_x, new_y = min(self.room_start_pos[0], snap_end_x), min(self.room_start_pos[1], snap_end_y)
                        final_w, final_h = max(BLOCK_SIZE, abs(self.room_start_pos[0] - snap_end_x)), max(BLOCK_SIZE,
                                                                                                          abs(
                                                                                                              self.room_start_pos[
                                                                                                                  1] - snap_end_y))
                        overlap = any(
                            pygame.Rect(r["rect"]).colliderect(pygame.Rect(new_x, new_y, final_w, final_h)) for r in
                            self.rooms_list)
                        if not overlap:
                            self.rooms_list.append({"rect": [new_x, new_y, final_w, final_h],
                                                    "type": self.room_types[self.current_room_idx],
                                                    "spawn": [new_x + 50, new_y + 50]})
                        self.room_start_pos = None

                if event.type == pygame.KEYDOWN:
                    mods = pygame.key.get_mods()
                    if event.key == pygame.K_u:
                        self.show_ui = not self.show_ui
                        self.ui_page = 0

                    if self.show_ui:
                        categories = ["Blocks", "Objects", "Decorations"]
                        if event.key == pygame.K_TAB:
                            idx = categories.index(self.ui_category)
                            self.ui_category = categories[(idx + 1) % len(categories)]
                            self.ui_page = 0
                        current_items = self.block_types if self.ui_category == "Blocks" else self.object_types if self.ui_category == "Objects" else self.decoration_types
                        max_pages = max(1, (len(current_items) + 19) // 20)
                        if event.key == pygame.K_RIGHT:
                            self.ui_page = (self.ui_page + 1) % max_pages
                        if event.key == pygame.K_LEFT:
                            self.ui_page = (self.ui_page - 1) % max_pages

                    if event.key == pygame.K_F3: self.debug = not self.debug
                    if event.key == pygame.K_p and self.room_mode:
                        for room in self.rooms_list:
                            if pygame.Rect(room["rect"]).collidepoint(world_x, world_y): room["spawn"] = [world_x,
                                                                                                          world_y]
                    if event.key == pygame.K_r: self.room_mode = not self.room_mode
                    if event.key == pygame.K_o: self.save_map()
                    if event.key == pygame.K_l: self.load_map()
                    if event.key == pygame.K_g: self.ongrid = not self.ongrid
                    if event.key in [pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS]: self.zoom = min(2.0,
                                                                                                        self.zoom + 0.1)
                    if event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]: self.zoom = max(0.2, self.zoom - 0.1)

                    layer_keys = {pygame.K_0: 0, pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: -1,
                                  pygame.K_5: 4}
                    if event.key in layer_keys:
                        target_l = layer_keys[event.key]
                        if mods & pygame.KMOD_CTRL:
                            self.layer_visibility[target_l] = not self.layer_visibility[target_l]
                        else:
                            self.current_layer = target_l
                            self.sky_mode = (target_l == 4)

            pygame.display.update()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    LevelEditor().run()