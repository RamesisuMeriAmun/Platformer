import pygame
import os
from Skripte.Assets.objects_class import Object
from Skripte.constants import BLOCK_SIZE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMAGE_DIR = os.path.join(BASE_DIR, "Data", "Images")


class Block(Object):
    BLOCKS_EDITOR_TILE_MAPPING = {
        "Braune Erde": ("Terrain/Terrain.png", (96, 64, 48, 48)),
        "Holz": ("Terrain/Terrain.png", (0, 64, 48, 48)),
        "Busch": ("Terrain/Terrain.png", (0, 64*2, 48, 48)),
        "Stein": ("Terrain/Terrain.png", (0, 0, 48, 48)),

        "Graß": ("Terrain/Sand Mud Ice.png", (64, 0, 48, 48)),
        "Ice": ("Terrain/Sand Mud Ice.png", (64*2, 0, 48, 48)),
        "Sand": ("Terrain/Sand Mud Ice.png", (0, 0, 48, 48)),
    }

    def __init__(self, x, y, block_type="Block1"):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE)

        if block_type in self.BLOCKS_EDITOR_TILE_MAPPING:
            image_name, rect_coords = self.BLOCKS_EDITOR_TILE_MAPPING[block_type]
        else:
            image_name, rect_coords = None, (0, 0, BLOCK_SIZE, BLOCK_SIZE)

        self.image = self.load_tile(image_name, rect_coords)
        self.mask = pygame.mask.from_surface(self.image)

    @staticmethod
    def load_tile(image_name, rect_coords):
        if image_name is None:
            surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
            surf.fill((255, 0, 255))
            return surf

        path = os.path.join(IMAGE_DIR, *image_name.split("/"))
        if not os.path.exists(path):
            surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
            surf.fill((255, 0, 255))
            return surf

        image = pygame.image.load(path).convert_alpha()
        surface = pygame.Surface((rect_coords[2], rect_coords[3]), pygame.SRCALPHA)
        surface.blit(image, (0, 0), rect_coords)
        return pygame.transform.scale(surface, (BLOCK_SIZE, BLOCK_SIZE))
