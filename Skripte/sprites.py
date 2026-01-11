import pygame
import os
from os import listdir
from os.path import isfile, join


def flip_sprites(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False, dir3=""):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    path = join(BASE_DIR, "..", "Data", "Images", dir1, dir2, dir3)
    if not os.path.exists(path):
        return {}

    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip_sprites(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites
