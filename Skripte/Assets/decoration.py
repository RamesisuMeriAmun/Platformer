import pygame
import os
from Skripte.Assets.objects_class import Object

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMAGE_DIR = os.path.join(BASE_DIR, "Data", "Images")


class Decoration(Object):
    # Name : (Dateipfad, (x, y, w, h), Ziel_Breite, Ziel_Höhe)
    DECORATION_TILE_MAPPING = {
        "Deko_Busch": ("Terrain/Terrain.png", (0, 128, 48, 48), 64, 64),
        "Deko_Mondstein": ("Terrain/Moon.png", (192, 96, 48, 48), 48, 48),
        "Deko_Wolke": ("Items/Decorations/Clouds.png", (0, 0, 64, 64), 128, 70),
    }

    def __init__(self, x, y, deco_type):
        path, rect, target_w, target_h = self.DECORATION_TILE_MAPPING.get(
            deco_type, (None, (0, 0, 32, 32), 32, 32)
        )
        super().__init__(x, y, target_w, target_h, name=deco_type)

        self.image = self.load_deco(path, rect, target_w, target_h)
        self.mask = None

    def load_deco(self, image_path, rect_coords, target_w, target_h):
        if not image_path:
            return pygame.Surface((target_w, target_h), pygame.SRCALPHA)

        path = os.path.join(IMAGE_DIR, *image_path.split("/"))
        if not os.path.exists(path):
            return pygame.Surface((target_w, target_h), pygame.SRCALPHA)

        full_sheet = pygame.image.load(path).convert_alpha()
        surface = pygame.Surface((rect_coords[2], rect_coords[3]), pygame.SRCALPHA)
        surface.blit(full_sheet, (0, 0), rect_coords)
        return pygame.transform.scale(surface, (target_w, target_h))
