import pygame
import os
from Skripte.Assets.objects_class import Object

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMAGE_DIR = os.path.join(BASE_DIR, "Data", "Images")


class Decoration(Object):
    # Name : (Dateipfad, (x, y, w, h), Ziel_Breite, Ziel_Höhe)
    DECORATION_TILE_MAPPING = {
        "Busch": ("Terrain/Terrain.png", (0, 128, 48, 48), 64, 64),
        "Mond": ("Background/Moons.png", (0, 0, 128, 128), 128, 128),
        "Sonne": ("Background/Moons.png", (128, 0, 128, 128), 128, 128),

        #Stars
        "Stern1": ("Background/Stars.png", (0, 0, 16, 16), 16, 16),
        "Stern2": ("Background/Stars.png", (16, 0, 16, 16), 16, 16),
        "Stern3": ("Background/Stars.png", (32, 0, 16, 16), 16, 16),
        "Stern4": ("Background/Stars.png", (48, 0, 16, 16), 16, 16),
        "Stern5": ("Background/Stars.png", (64, 0, 16, 16), 16, 16),
        "Stern6": ("Background/Stars.png", (80, 0, 16, 16), 16, 16),
        "Stern7": ("Background/Stars.png", (96, 0, 16, 16), 16, 16),
        "Stern8": ("Background/Stars.png", (112, 0, 16, 16), 16, 16),
        "Stern9": ("Background/Stars.png", (0, 16, 16, 16), 16, 16),
        "Stern10": ("Background/Stars.png", (16, 16, 16, 16), 16, 16),
        "Stern11": ("Background/Stars.png", (32, 16, 16, 16), 16, 16),
        "Stern12": ("Background/Stars.png", (48, 16, 16, 16), 16, 16),
        "Stern13": ("Background/Stars.png", (64, 16, 16, 16), 16, 16),
        "Stern14": ("Background/Stars.png", (80, 16, 16, 16), 16, 16),
        "Stern15": ("Background/Stars.png", (96, 16, 16, 16), 16, 16),
        "Stern16": ("Background/Stars.png", (112, 16, 16, 16), 16, 16),
        "Stern17": ("Background/Stars.png", (0, 32, 16, 16), 16, 16),
        "Stern18": ("Background/Stars.png", (16, 32, 16, 16), 16, 16),
        "Stern19": ("Background/Stars.png", (32, 32, 16, 16), 16, 16),
        "Stern20": ("Background/Stars.png", (48, 32, 16, 16), 16, 16),
        "Stern21": ("Background/Stars.png", (64, 32, 16, 16), 16, 16),
        "Stern22": ("Background/Stars.png", (80, 32, 16, 16), 16, 16),
        "Stern23": ("Background/Stars.png", (96, 32, 16, 16), 16, 16),
        "Stern24": ("Background/Stars.png", (112, 32, 16, 16), 16, 16),


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
