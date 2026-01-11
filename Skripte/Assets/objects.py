import pygame

from .objects_class import Object
from sprites import load_sprite_sheets
from constants import ANIMATION_DELAY


class Lava(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "lava")
        self.lava = load_sprite_sheets("Traps", "Lava", width, height)
        self.image = self.lava.get("lava", [pygame.Surface((width, height))])[0]
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire.get("off", [pygame.Surface((width, height))])[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def loop(self):
        sprites = self.fire.get(self.animation_name, [self.image])
        idx = (self.animation_count // ANIMATION_DELAY) % len(sprites)
        self.image = sprites[idx]
        self.animation_count += 1
        self.mask = pygame.mask.from_surface(self.image)


class Trampoline(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "trampoline")
        self.trampoline = load_sprite_sheets("Traps", "Trampoline", width, height)
        self.image = self.trampoline.get("Idle", [pygame.Surface((width, height))])[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "jump"

    def stand_player(self, player):
        player.rect.bottom = self.rect.top + 36
        player.landed()
        player.jump_count = 0


class Checkpoint(Object):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "checkpoint")
        self.checkpoint = load_sprite_sheets("Items", "Checkpoints", width, height, False, "Checkpoint")
        self.image = self.checkpoint.get("Checkpoint (No Flag)", [pygame.Surface((width, height))])[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Checkpoint (No Flag)"

    def gets_reached(self):
        self.animation_name = "Checkpoint (Flag Out)(64x64)"
        self.reached()

    def reached(self):
        self.animation_name = "Checkpoint (Flag Idle)(64x64)"

    def loop(self):
        sprites = self.checkpoint.get(self.animation_name, [self.image])
        idx = (self.animation_count // ANIMATION_DELAY) % len(sprites)
        self.image = sprites[idx]
        self.animation_count += 1
        self.mask = pygame.mask.from_surface(self.image)