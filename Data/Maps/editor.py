import os
import json
import pygame
from Skripte.Assets.blocks import Block
from Skripte.Assets import objects as o
from Skripte.constants import BLOCK_SIZE
from Skripte import rooms

WIDTH, HEIGHT = 1000, 750
FPS = 60

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_DIR = os.path.dirname(os.path.abspath(__file__))


class LevelEditor:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Level Editor - Blöcke & Objekte | Zoom [+/-] | Save [O]")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

        # Kamera & Zoom
        self.scroll = [0, 0]
        self.zoom = 1.0
        self.movement = [False, False, False, False]

        # Ongrid/Offgrid
        self.ongrid = True

        # Tiles
        self.tilemap = {}          # grid tiles
        self.offgrid_tiles = []    # frei platzierte tiles

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
        data = {"grid": self.tilemap, "offgrid": self.offgrid_tiles}
        os.makedirs(MAP_DIR, exist_ok=True)
        path = os.path.join(MAP_DIR, "map.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Level gespeichert: {path}")

    def load_map(self):
        path = os.path.join(MAP_DIR, "map.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                self.tilemap = data.get("grid", {})
                self.offgrid_tiles = data.get("offgrid", [])
            print(f"Level geladen: {path}")
        else:
            print("Keine Map gefunden!")

    def run(self):
        run = True
        while run:
            self.window.fill((40, 40, 40))

            # Kamera-Bewegung
            speed = 15 / self.zoom
            if self.movement[0]: self.scroll[0] -= speed
            if self.movement[1]: self.scroll[0] += speed
            if self.movement[2]: self.scroll[1] -= speed
            if self.movement[3]: self.scroll[1] += speed

            # Mausposition
            mpos = pygame.mouse.get_pos()
            world_x = (mpos[0] / self.zoom) + self.scroll[0]
            world_y = (mpos[1] / self.zoom) + self.scroll[1]
            grid_x, grid_y = int(world_x // BLOCK_SIZE), int(world_y // BLOCK_SIZE)
            tile_loc = f"{grid_x};{grid_y}"
            current_type = self.tile_list[self.current_type_idx]

            # Gitter zeichnen
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
                scaled = pygame.transform.scale(img, (int(img.get_width() * self.zoom), int(img.get_height() * self.zoom)))
                self.window.blit(scaled, ((coords[0]*BLOCK_SIZE - self.scroll[0])*self.zoom,
                                          (coords[1]*BLOCK_SIZE - self.scroll[1])*self.zoom))
            for tile in self.offgrid_tiles:
                img = self.assets[tile["type"]]
                scaled = pygame.transform.scale(img, (int(img.get_width()*self.zoom), int(img.get_height()*self.zoom)))
                self.window.blit(scaled, ((tile["pos"][0] - self.scroll[0])*self.zoom,
                                          (tile["pos"][1] - self.scroll[1])*self.zoom))

            # Vorschau
            p_img = self.assets[current_type]
            preview = pygame.transform.scale(p_img, (int(p_img.get_width()*self.zoom), int(p_img.get_height()*self.zoom)))
            preview.set_alpha(150)
            if self.ongrid:
                self.window.blit(preview, ((grid_x*BLOCK_SIZE - self.scroll[0])*self.zoom,
                                           (grid_y*BLOCK_SIZE - self.scroll[1])*self.zoom))
            else:
                self.window.blit(preview, mpos)

            # UI Info
            info = self.font.render(f"Zoom: {int(self.zoom*100)}% | Objekt: {current_type} | [O] Save | [L] Load |"
                                    f" [G] Grid", True, (255, 255, 255))
            self.window.blit(info, (10, 10))

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT: run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.ongrid:
                            self.tilemap[tile_loc] = current_type
                        else:
                            self.offgrid_tiles.append({"type": current_type, "pos": [world_x, world_y]})
                    if event.button == 3:
                        # Entfernen
                        if self.ongrid and tile_loc in self.tilemap:
                            del self.tilemap[tile_loc]
                        else:
                            for tile in self.offgrid_tiles[::-1]:
                                rect = pygame.Rect(tile["pos"][0], tile["pos"][1],
                                                   self.assets[tile["type"]].get_width(),
                                                   self.assets[tile["type"]].get_height())
                                if rect.collidepoint(world_x, world_y):
                                    self.offgrid_tiles.remove(tile)
                                    break
                    if event.button == 4:
                        self.current_type_idx = (self.current_type_idx - 1) % len(self.tile_list)
                    if event.button == 5:
                        self.current_type_idx = (self.current_type_idx + 1) % len(self.tile_list)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a: self.movement[0] = True
                    if event.key == pygame.K_d: self.movement[1] = True
                    if event.key == pygame.K_w: self.movement[2] = True
                    if event.key == pygame.K_s: self.movement[3] = True
                    if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS: self.zoom = min(2.0, self.zoom + 0.1)
                    if event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS: self.zoom = max(0.2, self.zoom - 0.1)
                    if event.key == pygame.K_g: self.ongrid = not self.ongrid
                    if event.key == pygame.K_o: self.save_map()
                    if event.key == pygame.K_l: self.load_map()
                    if event.key == pygame.K_RIGHT: self.current_type_idx = (self.current_type_idx + 1) % len(self.tile_list)
                    if event.key == pygame.K_LEFT: self.current_type_idx = (self.current_type_idx - 1) % len(self.tile_list)

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a: self.movement[0] = False
                    if event.key == pygame.K_d: self.movement[1] = False
                    if event.key == pygame.K_w: self.movement[2] = False
                    if event.key == pygame.K_s: self.movement[3] = False

            pygame.display.update()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    LevelEditor().run()
