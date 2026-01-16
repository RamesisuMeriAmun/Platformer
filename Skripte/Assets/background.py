import pygame
from os.path import join


def load_background(name, target_width, target_height):
    # Bild laden
    image = pygame.image.load(join("Data", "Images", "Background", name)).convert()
    tile_w, tile_h = image.get_size()
    tiles = []
    buffer = 25
    for i in range(-buffer, target_width // tile_w + 1 + buffer):
        for j in range(-buffer, target_height // tile_h + 1 + buffer):
            pos = (i * tile_w, j * tile_h)
            tiles.append(pos)

    return tiles, image
