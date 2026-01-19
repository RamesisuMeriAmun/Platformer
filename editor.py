import os
import json
import pygame
from Skripte.Assets.blocks import Block
from Skripte.Assets import objects as o
from Skripte.constants import BLOCK_SIZE, WIDTH, HEIGHT
from Skripte import rooms

FPS = 60

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_DIR = os.path.join(BASE_DIR, "Data", "Maps")


class LevelEditor:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(
            "Level Editor - Blöcke & Objekte | Zoom [+/-] | Save [O]"
        )
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

        # Kamera & Zoom
        self.scroll = [0, 0]
        self.zoom = 1.0
        self.movement = [False, False, False, False]

        # Ongrid/Offgrid/Room
        self.ongrid = True
        self.room_mode = False
        # Debugging wie im Game
        self.debug = False  # Startet im normalen Modus

        # Tiles
        self.tilemap = {}  # grid tiles
        self.offgrid_tiles = []  # frei platzierte tiles
        self.rooms_list = []

        # Raum_Logik
        self.room_start_pos = None
        self.room_types = list(rooms.ROOM_MAPPING.keys())
        self.current_room_idx = 0

        # Assets: Blocks + Objekte
        self.assets = {}
        for name in Block.BLOCKS_EDITOR_TILE_MAPPING:
            self.assets[name] = Block(0, 0, name).image
        for name, params in o.OBJECTS_EDITOR_TILE_MAPPING.items():
            cls = params["class"]
            width = params.get("width", 32)
            height = params.get("height", 32)
            surf = cls(0, 0, width, height).image
            self.assets[name] = surf

        self.tile_list = list(self.assets.keys())
        self.current_type_idx = 0

    @staticmethod
    def create_object(typ, x, y):
        # Blöcke
        if typ in Block.BLOCKS_EDITOR_TILE_MAPPING:
            return Block(x, y, typ)
        # Andere Objekte
        elif typ in o.OBJECTS_EDITOR_TILE_MAPPING:
            params = o.OBJECTS_EDITOR_TILE_MAPPING[typ]
            cls = params["class"]
            width = params.get("width", 32)
            height = params.get("height", 32)
            obj = cls(x, y, width, height)
            if params.get("auto_on"):
                obj.on()
            return obj
        return None

    def save_map(self):
        new_rooms_data = []

        for room in self.rooms_list:
            r_rect = pygame.Rect(room["rect"])
            room_content = {
                "rect": room["rect"],
                "type": room["type"],
                "spawn": room["spawn"],
                "grid": {},
                "offgrid": []
            }

            for loc, t_type in self.tilemap.items():
                coords = list(map(int, loc.split(";")))
                if r_rect.collidepoint(coords[0] * BLOCK_SIZE, coords[1] * BLOCK_SIZE):
                    room_content["grid"][loc] = t_type

            for tile in self.offgrid_tiles:
                if r_rect.collidepoint(tile["pos"]):
                    room_content["offgrid"].append(tile)

            new_rooms_data.append(room_content)

        data = {"rooms": new_rooms_data}

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

        for r_data in data.get("rooms", []):
            self.rooms_list.append({
                "rect": r_data["rect"],
                "type": r_data["type"],
                "spawn": r_data["spawn"]
            })

            for loc, t_type in r_data.get("grid", {}).items():
                self.tilemap[loc] = t_type

            for item in r_data.get("offgrid", []):
                self.offgrid_tiles.append(item)

    def run(self):
        run = True
        while run:
            self.window.fill((40, 40, 40))

            # Kontinuierliche Abfrage fuer flüssige Kamera-Bewegung
            keys = pygame.key.get_pressed()
            speed = 15 / self.zoom
            if keys[pygame.K_a]: self.scroll[0] -= speed
            if keys[pygame.K_d]: self.scroll[0] += speed
            if keys[pygame.K_w]: self.scroll[1] -= speed
            if keys[pygame.K_s]: self.scroll[1] += speed

            # Mausposition
            mpos = pygame.mouse.get_pos()
            world_x = (mpos[0] / self.zoom) + self.scroll[0]
            world_y = (mpos[1] / self.zoom) + self.scroll[1]
            grid_x, grid_y = int(world_x // BLOCK_SIZE), int(world_y // BLOCK_SIZE)
            tile_loc = f"{grid_x};{grid_y}"
            current_type = self.tile_list[self.current_type_idx]

            # Aktueller Modus
            if self.room_mode:
                current_selection = self.room_types[self.current_room_idx]
            else:
                current_selection = self.tile_list[self.current_type_idx]

            # Gitter zeichnen (Nur sichtbar wenn ongrid aktiv oder im Debug Modus)
            if self.ongrid or self.debug:
                for x in range(0, int(WIDTH / self.zoom) + BLOCK_SIZE, BLOCK_SIZE):
                    dx = (x - (self.scroll[0] % BLOCK_SIZE)) * self.zoom
                    pygame.draw.line(self.window, (60, 60, 60), (dx, 0), (dx, HEIGHT))
                for y in range(0, int(HEIGHT / self.zoom) + BLOCK_SIZE, BLOCK_SIZE):
                    dy = (y - (self.scroll[1] % BLOCK_SIZE)) * self.zoom
                    pygame.draw.line(self.window, (60, 60, 60), (0, dy), (WIDTH, dy))

            # Tiles zeichnen
            for loc, t_type in self.tilemap.items():
                coords = list(map(int, loc.split(";")))
                img = self.assets[t_type]

                draw_x = (coords[0] * BLOCK_SIZE - self.scroll[0]) * self.zoom
                draw_y = (coords[1] * BLOCK_SIZE - self.scroll[1]) * self.zoom
                s_w = int(img.get_width() * self.zoom)
                s_h = int(img.get_height() * self.zoom)

                scaled = pygame.transform.scale(img, (max(1, s_w), max(1, s_h)))
                self.window.blit(scaled, (draw_x, draw_y))

                # Debug Hitboxen fuer Grid-Blöcke (Nur bei F3)
                if self.debug:
                    pygame.draw.rect(self.window, (255, 0, 0), (draw_x, draw_y, s_w, s_h), 1)

            for tile in self.offgrid_tiles:
                img = self.assets[tile["type"]]

                draw_x = (tile["pos"][0] - self.scroll[0]) * self.zoom
                draw_y = (tile["pos"][1] - self.scroll[1]) * self.zoom
                s_w = int(img.get_width() * self.zoom)
                s_h = int(img.get_height() * self.zoom)

                scaled = pygame.transform.scale(img, (max(1, s_w), max(1, s_h)))
                self.window.blit(scaled, (draw_x, draw_y))

                # Debug Hitboxen fuer Offgrid-Objekte (Nur bei F3)
                if self.debug:
                    pygame.draw.rect(self.window, (255, 255, 0), (draw_x, draw_y, s_w, s_h), 1)

            # Räume zeichnen
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

                # Räume sind immer sichtbar, aber im Debug Modus dicker
                thickness = 3 if self.debug else 1
                pygame.draw.rect(self.window, color, rect_screen, thickness)

                # Raum-Label und Spawn (Nur im Debug)
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

            # Raum-Ziehen Vorschau
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

            # Assets Vorschau
            if not self.room_mode:
                p_img = self.assets[current_selection]
                preview = pygame.transform.scale(p_img, (
                int(p_img.get_width() * self.zoom), int(p_img.get_height() * self.zoom)))
                preview.set_alpha(150)
                if self.ongrid:
                    self.window.blit(preview, ((grid_x * BLOCK_SIZE - self.scroll[0]) * self.zoom,
                                               (grid_y * BLOCK_SIZE - self.scroll[1]) * self.zoom))
                else:
                    self.window.blit(preview, mpos)

            # --- UI: Status & Debug Help ---
            mode_str = "ROOM-MODE" if self.room_mode else "TILE-MODE"

            # Linke Seite (Basis Info)
            info = self.font.render(f"{mode_str} | {current_selection} | Zoom: {int(self.zoom * 100)}%", True,
                                    (255, 255, 255))
            self.window.blit(info, (10, 10))

            # Rechte Seite (Debug Hilfe - wird bei F3 umgeschaltet)
            if self.debug:
                editor_help = [
                    "DEBUG MODE ACTIVE",
                    "W,A,S,D: Move",
                    "R: Switch Mode",
                    "P: Set Spawn",
                    "G: Toggle Grid",
                    "O: Save | L: Load",
                    "F3: Toggle Debug"
                ]
                for i, text in enumerate(editor_help):
                    h_img = self.font.render(text, True, (255, 215, 0) if i == 0 else (200, 200, 200))
                    x_pos = WIDTH - h_img.get_width() - 20
                    self.window.blit(h_img, (x_pos, 10 + i * 20))
            else:
                # Kleiner Hinweis wenn Debug aus ist-
                hint = self.font.render("Press F3 for Debug Info", True, (100, 100, 100))
                self.window.blit(hint, (WIDTH - hint.get_width() - 20, 10))

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.room_mode and pygame.key.get_mods() & pygame.KMOD_CTRL:
                            snap_x = (world_x // BLOCK_SIZE) * BLOCK_SIZE
                            snap_y = (world_y // BLOCK_SIZE) * BLOCK_SIZE
                            self.room_start_pos = (snap_x, snap_y)
                        elif not self.room_mode:
                            if self.ongrid:
                                self.tilemap[tile_loc] = current_selection
                            else:
                                self.offgrid_tiles.append({"type": current_selection, "pos": [world_x, world_y]})

                    if event.button == 3:
                        if self.room_mode:
                            for room in self.rooms_list[::-1]:
                                if pygame.Rect(room["rect"]).collidepoint(world_x, world_y):
                                    self.rooms_list.remove(room);
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
                        final_w, final_h = max(WIDTH, abs(self.room_start_pos[0] - snap_end_x)), max(HEIGHT, abs(
                            self.room_start_pos[1] - snap_end_y))

                        overlap = any(
                            pygame.Rect(r["rect"]).colliderect(pygame.Rect(new_x, new_y, final_w, final_h)) for r in
                            self.rooms_list)
                        if not overlap:
                            self.rooms_list.append({"rect": [new_x, new_y, final_w, final_h],
                                                    "type": self.room_types[self.current_room_idx],
                                                    "spawn": [new_x + 50, new_y + 50]})
                        self.room_start_pos = None

                if event.type == pygame.MOUSEWHEEL:
                    if self.room_mode:
                        self.current_room_idx = (self.current_room_idx - event.y) % len(self.room_types)
                    else:
                        self.current_type_idx = (self.current_type_idx - event.y) % len(self.tile_list)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F3:  # Debug einschalten
                        self.debug = not self.debug
                    if event.key == pygame.K_p and self.room_mode:
                        for room in self.rooms_list:
                            if pygame.Rect(room["rect"]).collidepoint(world_x, world_y):
                                room["spawn"] = [world_x, world_y]
                    if event.key == pygame.K_r: self.room_mode = not self.room_mode
                    if event.key == pygame.K_o: self.save_map()
                    if event.key == pygame.K_l: self.load_map()
                    if event.key == pygame.K_g: self.ongrid = not self.ongrid
                    if event.key in [pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS]: self.zoom = min(2.0,
                                                                                                        self.zoom + 0.1)
                    if event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]: self.zoom = max(0.2, self.zoom - 0.1)

            pygame.display.update()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    LevelEditor().run()