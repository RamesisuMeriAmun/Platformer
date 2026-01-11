import pygame
import constants
import sprites


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.player = pygame.Rect(x, y, width, height)
        self.sprites = sprites.load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
        self.sprite = None
        self.mask = None
        self.direction = "right"
        self.animation_count = 0

        self.x_vel = 0
        self.y_vel = 0
        self.falling_time = 0
        self.jump_count = 0

        self.hit = False

    # Movement
    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.x_vel = 0

        if keys[pygame.K_a]:
            self.move_left(constants.VEL)
        elif keys[pygame.K_d]:
            self.move_right(constants.VEL)

    def move(self, dx, dy):
        self.player.x += dx
        self.player.y += dy

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

    # Display
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            sprite_sheet = "jump" if self.jump_count == 1 else "double_jump"
        elif self.y_vel > constants.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.sprites.get(sprite_sheet_name, self.sprites.get("idle_right"))

        sprite_index = (self.animation_count // constants.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update_mask()

    def update_mask(self):
        self.player = self.sprite.get_rect(topleft=(self.player.x, self.player.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def loop(self, fps):
        self.handle_input()
        self.move(self.x_vel, self.y_vel)

        self.y_vel += min(1, (self.falling_time / fps) * constants.GRAVITY)
        self.falling_time += 1

        self.update_sprite()

    def draw(self, screen):
        screen.blit(self.sprite, (self.player.x, self.player.y))
