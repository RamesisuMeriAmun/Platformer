import pygame

from Skripte.Assets.objects_class import Object
from Skripte.sprites import load_sprite_sheets
from Skripte.constants import ANIMATION_DELAY


class Lava(Object):
    def __init__(self, x, y, width, height, hitbox_data=None):
        super().__init__(x, y, width, height, "lava", hitbox_data)
        self.lava = load_sprite_sheets("Traps", "Lava", width, height)
        self.image = self.lava.get("lava", [pygame.Surface((width, height))])[0]
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):

    def __init__(self, x, y, width, height, hitbox_data=None):
        super().__init__(x, y, width, height, "fire", hitbox_data)
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire.get("off", [pygame.Surface((width, height))])[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "on"

    def on(self):
        self.animation_name = "on"

    def loop(self):
        sprites = self.fire.get(self.animation_name, [self.image])
        idx = (self.animation_count // ANIMATION_DELAY) % len(sprites)
        self.image = sprites[idx]
        self.animation_count += 1
        self.mask = pygame.mask.from_surface(self.image)


class Trampoline(Object):
    def __init__(self, x, y, width, height, hitbox_data=None):
        super().__init__(x, y, width, height, "trampoline", hitbox_data)
        self.trampoline = load_sprite_sheets("Traps", "Trampoline", width, height)
        self.image = self.trampoline.get("Idle", [pygame.Surface((width, height))])[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "jump"
        self.is_jumping = False

    def trigger(self, player):
        player.rect.bottom = self.rect.top
        player.y_vel = -player.JUMP_FORCE * 1.4
        player.on_ground = False
        player.jump_count = 1
        player.can_dash = True

        if not self.is_jumping:
            self.animation_name = "Jump (28x28)"
            self.animation_count = 0
            self.is_jumping = True

    def loop(self):
        sprites = self.trampoline.get(self.animation_name, [])
        if not sprites:
            return

        idx = (self.animation_count // ANIMATION_DELAY) % len(sprites)
        self.image = sprites[idx]
        self.animation_count += 1

        if self.is_jumping and idx == len(sprites) - 1:
            self.is_jumping = False
            self.animation_name = "Idle"
            self.animation_count = 0

        self.mask = pygame.mask.from_surface(self.image)


class Checkpoint(Object):

    def __init__(self, x, y, width, height, hitbox_data=None):
        super().__init__(x, y, width, height, "checkpoint", hitbox_data)
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


class Spikes(Object):
    def __init__(self, x, y, width, height, hitbox_data=None):
        super().__init__(x, y, width, height, "spikes", hitbox_data)
        self.spike = load_sprite_sheets("Traps", "Spikes", width, height)
        self.image = self.spike.get("spikes", [pygame.Surface((width, height))])[0]
        self.mask = pygame.mask.from_surface(self.image)


OBJECTS_EDITOR_TILE_MAPPING = {
    "Fire": {"class": Fire, "width": 16, "height": 32, "auto_on": True},
    "Lava": {"class": Lava, "width": 96, "height": 20},
    "Trampoline": {"class": Trampoline, "width": 28, "height": 28, "hitbox_data": (0, 20, 28, 8)},
    "Checkpoint": {"class": Checkpoint, "width": 64, "height": 64},
    "Spikes": {"class": Spikes, "width": 16, "height": 16, "hitbox_data": (0, 8, 16, 8)},
}
