import os
import json
import pygame
from os import listdir
from os.path import isfile, join

# --- KONFIGURATION ---
WIDTH, HEIGHT = 1000, 750
BLOCK_SIZE = 96
FPS = 60


def get_block_asset(path_parts, size, rect_coords):
    path = join("assets", *path_parts)
    if not os.path.exists(path):
        # Pinker Platzhalter, falls Datei fehlt
        surf = pygame.Surface((size, size))
        surf.fill((255, 0, 255))
        return pygame.transform.scale2x(surf)
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(*rect_coords)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class LevelEditor:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Level Editor - Blöcke 1-5 | Zoom [+/-] | Save [O]")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

        # Kamera & Zoom
        self.scroll = [0, 0]
        self.zoom = 1.0
        self.movement = [False, False, False, False]
        self.ongrid = True

        self.tilemap = {}
        self.offgrid_tiles = []

        # --- ASSETS (Hier sind jetzt alle 5 Blöcke drin) ---
        self.assets = {
            "Block1": get_block_asset(["Terrain", "Terrain.png"], 48, (96, 64, 48, 48)),  # Braune Erde
            "Block2": get_block_asset(["Terrain", "Terrain.png"], 48, (0, 64, 48, 48)),  # Holz
            "Block3": get_block_asset(["Terrain", "Terrain.png"], 48, (0, 64 * 2, 48, 48)),  # Gras
            "Block4": get_block_asset(["Terrain", "Sand Mud Ice.png"], 48, (64, 0, 48, 48)),  # Erde
            "Fire": self.load_simple_asset("Traps", "Fire", "Off.png", 16, 32),
            "Trampoline": self.load_simple_asset("Traps", "Trampoline", "Idle.png", 28, 28),
            "Checkpoint": self.load_simple_asset("Items", "Checkpoints", "Checkpoint/Checkpoint (No Flag).png", 64, 64),
            "Lava": self.load_simple_asset("Traps", "Lava", "lava.png", 96, 20)
        }

        self.tile_list = list(self.assets.keys())
        self.current_type_idx = 0

    def load_simple_asset(self, d1, d2, d3, w, h):
        path = join("assets", d1, d2, d3)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            surf.blit(img, (0, 0), (0, 0, w, h))
            return pygame.transform.scale2x(surf)
        return pygame.Surface((w * 2, h * 2))

    def apply_autotile(self):
        """Wandelt Block 1-5 basierend auf Nachbarn um (Beispiel für Block 1 & 2)"""
        new_map = {}
        for loc, t_type in self.tilemap.items():
            if t_type in ["Block1", "Block2"]:
                x, y = map(int, loc.split(";"))
                above = f"{x};{y - 1}"
                new_map[loc] = "Block1" if above not in self.tilemap else "Block2"
            else:
                new_map[loc] = t_type
        self.tilemap = new_map

    def save_map(self):
        data = {"grid": self.tilemap, "offgrid": self.offgrid_tiles}
        with open("map.json", "w") as f:
            json.dump(data, f)
        print("Level gespeichert!")

    def load_map(self):
        if os.path.exists("map.json"):
            with open("map.json", "r") as f:
                data = json.load(f)
                self.tilemap = data.get("grid", {})
                self.offgrid_tiles = data.get("offgrid", [])
            print("Level geladen!")

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

            # Maus & Zoom Logik
            mpos = pygame.mouse.get_pos()
            world_x = (mpos[0] / self.zoom) + self.scroll[0]
            world_y = (mpos[1] / self.zoom) + self.scroll[1]
            grid_x, grid_y = int(world_x // BLOCK_SIZE), int(world_y // BLOCK_SIZE)
            tile_loc = f"{grid_x};{grid_y}"

            # Gitter zeichnen
            if self.ongrid:
                for x in range(0, int(WIDTH / self.zoom) + BLOCK_SIZE, BLOCK_SIZE):
                    dx = (x - (self.scroll[0] % BLOCK_SIZE)) * self.zoom
                    pygame.draw.line(self.window, (60, 60, 60), (dx, 0), (dx, HEIGHT))
                for y in range(0, int(HEIGHT / self.zoom) + BLOCK_SIZE, BLOCK_SIZE):
                    dy = (y - (self.scroll[1] % BLOCK_SIZE)) * self.zoom
                    pygame.draw.line(self.window, (60, 60, 60), (0, dy), (WIDTH, dy))

            # Tiles zeichnen (Skaliert nach Zoom)
            for loc, t_type in self.tilemap.items():
                coords = list(map(int, loc.split(";")))
                img = self.assets[t_type]
                scaled = pygame.transform.scale(img,
                                                (int(img.get_width() * self.zoom), int(img.get_height() * self.zoom)))
                self.window.blit(scaled, ((coords[0] * BLOCK_SIZE - self.scroll[0]) * self.zoom,
                                          (coords[1] * BLOCK_SIZE - self.scroll[1]) * self.zoom))

            for tile in self.offgrid_tiles:
                img = self.assets[tile['type']]
                scaled = pygame.transform.scale(img,
                                                (int(img.get_width() * self.zoom), int(img.get_height() * self.zoom)))
                self.window.blit(scaled, (
                (tile['pos'][0] - self.scroll[0]) * self.zoom, (tile['pos'][1] - self.scroll[1]) * self.zoom))

            # Vorschau
            curr_type = self.tile_list[self.current_type_idx]
            p_img = self.assets[curr_type]
            preview = pygame.transform.scale(p_img,
                                             (int(p_img.get_width() * self.zoom), int(p_img.get_height() * self.zoom)))
            preview.set_alpha(150)
            if self.ongrid:
                self.window.blit(preview, (
                (grid_x * BLOCK_SIZE - self.scroll[0]) * self.zoom, (grid_y * BLOCK_SIZE - self.scroll[1]) * self.zoom))
            else:
                self.window.blit(preview, mpos)

            # UI Info
            info = self.font.render(f"Zoom: {int(self.zoom * 100)}% | Objekt: {curr_type} | [O] Save", True,
                                    (255, 255, 255))
            self.window.blit(info, (10, 10))

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT: run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.ongrid:
                            self.tilemap[tile_loc] = curr_type
                        else:
                            self.offgrid_tiles.append({'type': curr_type, 'pos': [world_x, world_y]})
                    if event.button == 3:
                        if self.ongrid and tile_loc in self.tilemap:
                            del self.tilemap[tile_loc]
                        else:
                            for tile in self.offgrid_tiles[::-1]:
                                rect = pygame.Rect(tile['pos'][0], tile['pos'][1],
                                                   self.assets[tile['type']].get_width(),
                                                   self.assets[tile['type']].get_height())
                                if rect.collidepoint(world_x, world_y):
                                    self.offgrid_tiles.remove(tile)
                                    break
                    if event.button == 4: self.current_type_idx = (self.current_type_idx - 1) % len(self.tile_list)
                    if event.button == 5: self.current_type_idx = (self.current_type_idx + 1) % len(self.tile_list)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a: self.movement[0] = True
                    if event.key == pygame.K_d: self.movement[1] = True
                    if event.key == pygame.K_w: self.movement[2] = True
                    if event.key == pygame.K_s: self.movement[3] = True
                    if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS: self.zoom = min(2.0,
                                                                                                    self.zoom + 0.1)
                    if event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS: self.zoom = max(0.2,
                                                                                                      self.zoom - 0.1)
                    if event.key == pygame.K_g: self.ongrid = not self.ongrid
                    if event.key == pygame.K_t: self.apply_autotile()
                    if event.key == pygame.K_o: self.save_map()
                    if event.key == pygame.K_l: self.load_map()

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