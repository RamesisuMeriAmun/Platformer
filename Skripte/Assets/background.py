import pygame
from os.path import join
import Skripte.constants as constants


def load_background(name):
    image = pygame.image.load(join("Data", "Images", "Background", name)).convert()
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(constants.WIDTH // width + 1):
        for j in range(constants.HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image
