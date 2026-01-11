import pygame
from os.path import join

from .objects_class import Object


def load_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 64, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


def load_block_2(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 64 * 1, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


def load_block_3(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 64 * 2, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


def load_block_4(size):
    path = join("assets", "Terrain", "Sand Mud Ice.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(64, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        self.image.blit(load_block(size), (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Block2(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        self.image.blit(load_block_2(size), (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Block3(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        self.image.blit(load_block_3(size), (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Block4(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        self.image.blit(load_block_4(size), (0, 0))
        self.mask = pygame.mask.from_surface(self.image)