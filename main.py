import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
import json

pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 750
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False, dir3=""):
    path = join("assets", dir1, dir2, dir3)
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
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


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


def load_level(path):
    if not os.path.exists(path):
        print(f"Fehler: {path} nicht gefunden!")
        return []

    with open(path, "r") as f:
        data = json.load(f)

    objects = []

    for loc, t_type in data["grid"].items():
        coords = list(map(int, loc.split(";")))
        x = coords[0] * 96
        y = coords[1] * 96

        if t_type == "Block1":
            objects.append(Block(x, y, 96))
        elif t_type == "Block2":
            objects.append(Block2(x, y, 96))
        elif t_type == "Block3":
            objects.append(Block3(x, y, 96))
        elif t_type == "Block4":
            objects.append(Block4(x, y, 96))

    for item in data.get("offgrid", []):
        ox, oy = item["pos"]
        if item["type"] == "Checkpoint":
            objects.append(Checkpoint(ox, oy, 64, 64))
        elif item["type"] == "Trampoline":
            objects.append(Trampoline(ox, oy, 28, 28))
        elif item["type"] == "Fire":
            fire_obj = Fire(ox, oy, 16, 32)
            fire_obj.on()
            objects.append(fire_obj)
        elif item["type"] == "Lava":
            objects.append(Lava(ox, oy, 96, 20))

    return objects


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 4

    def __init__(self, x, y, width, height):
        super().__init__()
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(self.start_x, self.start_y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.dead = False
        self.lives = 3
        self.full = load_sprite_sheets("Items", "Fruits", 28, 32)
        self.full_image = self.full["Bananas"][0]

        # Dash Mechanik Variablen
        self.dashing = False
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.dash_vel = 20  # Geschwindigkeit des Dash
        self.dash_duration = 10  # Frames, die der Dash anhält
        self.dash_cooldown_time = 40  # Frames bis zum nächsten Dash möglich

    def hearts(self):
        if self.lives >= 1:
            window.blit(self.full_image, (350, 15))
        if self.lives >= 2:
            window.blit(self.full_image, (468, 15))
        if self.lives == 3:
            window.blit(self.full_image, (586, 15))

    def dash(self):
        if self.dash_cooldown == 0:
            self.dashing = True
            self.dash_timer = self.dash_duration
            self.dash_cooldown = self.dash_cooldown_time
            self.y_vel = 0  # Dash ist horizontal stabil

    def jump(self):
        if not self.hit:
            if self.jump_count < 2:
                if self.jump_count == 0:
                    self.y_vel = -self.GRAVITY * 8
                else:
                    self.y_vel = -self.GRAVITY * 12

                self.animation_count = 0
                self.jump_count += 1

                if self.jump_count == 1:
                    self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        # Dash Logik abarbeiten
        if self.dashing:
            multiplier = 1 if self.direction == "right" else -1
            self.x_vel = self.dash_vel * multiplier
            self.y_vel = 0  # Keine Schwerkraft beim Dashen
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dashing = False
                self.x_vel = 0
        else:
            # Normale Schwerkraft
            self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0
            self.lives -= 1

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def is_dead(self):
        if self.rect.y >= HEIGHT * 4 or self.lives <= 0:
            self.dead = True
        else:
            self.dead = False

    def reached_checkpoint(self, x, y):
        self.start_x = x
        self.start_y = y

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        # Dash könnte man hier visuell mit "run" oder "jump" anzeigen
        elif self.dashing:
            sprite_sheet = "run"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x, offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))


# --- Objekt-Klassen bleiben weitgehend gleich ---

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = load_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Block2(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = load_block_2(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Block3(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = load_block_3(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Block4(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = load_block_4(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Lava(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "lava")
        self.lava = load_sprite_sheets("Traps", "Lava", width, height)
        self.image = self.lava["lava"][0]
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self): self.animation_name = "on"

    def off(self): self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)


class Trampoline(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "trampoline")
        self.trampoline = load_sprite_sheets("Traps", "Trampoline", width, height)
        self.image = self.trampoline["Idle"][0]
        self.mask = pygame.mask.from_surface(self.image)

    def stand_player(self, player):
        player.rect.bottom = self.rect.top + 36
        player.landed()


class Checkpoint(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "checkpoint")
        self.checkpoint = load_sprite_sheets("Items", "Checkpoints", width, height, False, "Checkpoint")
        self.image = self.checkpoint["Checkpoint (No Flag)"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Checkpoint (No Flag)"

    def gets_reached(self):
        self.animation_name = "Checkpoint (Flag Out)(64x64)"

    def loop(self):
        sprites = self.checkpoint[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.mask = pygame.mask.from_surface(self.image)


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            tiles.append((i * width, j * height))
    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x, offset_y):
    for tile in background:
        window.blit(bg_image, tile)
    for obj in objects:
        obj.draw(window, offset_x, offset_y)
    player.draw(window, offset_x, offset_y)
    player.hearts()
    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj) and obj.name != "checkpoint":
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
            collided_objects.append(obj)
        elif pygame.sprite.collide_mask(player, obj) and obj.name == "checkpoint":
            collided_objects.append(obj)
    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if (pygame.sprite.collide_mask(player, obj) and
                obj.name not in ["checkpoint", "trampoline"]):
            collided_object = obj
            break
    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    # Bewegung nur verarbeiten, wenn NICHT gedasht wird
    if not player.dashing:
        player.x_vel = 0
        collide_left = collide(player, objects, -PLAYER_VEL * 2)
        collide_right = collide(player, objects, PLAYER_VEL * 2)

        if keys[pygame.K_a] and not collide_left:
            player.move_left(PLAYER_VEL)
        if keys[pygame.K_d] and not collide_right:
            player.move_right(PLAYER_VEL)
    else:
        # Während des Dashs prüfen wir trotzdem auf Wände
        dash_dir = 1 if player.direction == "right" else -1
        if collide(player, objects, player.dash_vel * dash_dir):
            player.dashing = False
            player.x_vel = 0

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [*vertical_collide]

    # Seitliche Kollisionschecks hinzufügen
    side_collide = collide(player, objects, player.x_vel)
    if side_collide: to_check.append(side_collide)

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()
        if obj and obj.name == "checkpoint":
            player.reached_checkpoint(obj.rect.x, obj.rect.y)
            obj.gets_reached()
        if obj and obj.name == "lava":
            player.lives = 0

    for obj in vertical_collide:
        if obj and obj.name == "trampoline":
            player.y_vel = -18  # Trampolin Sprung
            obj.stand_player(player)

    player.is_dead()
    if player.dead:
        player.rect.x, player.rect.y = player.start_x, player.start_y
        player.lives = 3
        player.dead = False


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Yellow.png")
    player = Player(450, 300, 50, 50)
    objects = load_level("map.json")

    offset_x = 0
    offset_y = 0
    scroll_area_width = 400

    go = True
    while go:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                go = False
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_w or event.key == pygame.K_SPACE) and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    player.dash()

        player.loop(FPS)
        for obj in objects:
            if hasattr(obj, "loop"):
                obj.loop()

        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x, offset_y)

        # Kamera Scroll Logik (Horizontal)
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or \
                ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

        # Vertikaler Kamera-Folge-Effekt (Einfach)
        if player.rect.top - offset_y < 200:
            offset_y -= 5
        if player.rect.bottom - offset_y > HEIGHT - 200:
            offset_y += 5

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)