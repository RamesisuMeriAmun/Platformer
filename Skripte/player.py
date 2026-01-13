import pygame
import constants
import sprites
from Skripte.Assets.blocks import Block


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, all_objects):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.sprites = sprites.load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
        self.sprite = None
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.spawn = (x, y)

        self.x_vel = 0
        self.y_vel = 0
        self.falling_time = 0

        # Jump
        self.jump_count = 0
        self.jump_pressed = False
        self.jump_hold_time = 0

        self.JUMP_FORCE = 9
        self.DOUBLE_JUMP_FORCE = 7
        self.JUMP_HOLD_FORCE = 0.6
        self.MAX_JUMP_HOLD = 12

        #Kollision
        self.blocks = [obj for obj in all_objects if isinstance(obj, Block)]
        self.objects = [obj for obj in all_objects if not isinstance(obj, Block)]

        self.hit = False

    # Movement

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.x_vel = 0

        # Movement
        if keys[pygame.K_a]:
            self.move_left(constants.VEL)
        elif keys[pygame.K_d]:
            self.move_right(constants.VEL)

        # Jump
        if keys[pygame.K_SPACE]:
            if not self.jump_pressed:
                self.jump()
                self.jump_pressed = True
        else:
            self.jump_pressed = False

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

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

    def jump(self):
        if self.jump_count == 0:
            self.y_vel = -self.JUMP_FORCE
            self.jump_hold_time = 0

        if self.jump_count == 1:
            self.y_vel = -self.DOUBLE_JUMP_FORCE
            self.jump_hold_time = self.MAX_JUMP_HOLD

        self.jump_count += 1

    def update_jump(self):
        keys = pygame.key.get_pressed()

        if (
                keys[pygame.K_SPACE]
                and self.y_vel < 0
                and self.jump_hold_time < self.MAX_JUMP_HOLD
                and self.jump_count == 0
        ):
            self.y_vel -= self.JUMP_HOLD_FORCE
            self.jump_hold_time += 1

        if not keys[pygame.K_SPACE] and self.y_vel < 0:
            self.y_vel *= 0.35

    # Collision
    def handle_vertical_collision(self, blocks, dy):
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if dy > 0:
                    self.rect.bottom = block.rect.top
                    self.landed()
                elif dy < 0:
                    self.rect.top = block.rect.bottom
                    self.hit_head()

    def landed(self):
        self.falling_time = 0
        self.y_vel = 0
        self.jump_count = 0
        self.jump_hold_time = 0

    def hit_head(self):
        self.y_vel = 1

    def handle_horizontal_collision(self, blocks):
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.x_vel > 0:
                    self.rect.right = block.rect.left
                elif self.x_vel < 0:
                    self.rect.left = block.rect.right

    def handle_object_collision(self, objects):
        for obj in objects:
            if self.rect.colliderect(obj.rect):
                overlap_x = obj.rect.x - self.rect.x
                overlap_y = obj.rect.y - self.rect.y

                if self.mask.overlap(obj.mask, (overlap_x, overlap_y)):
                    self.react_to_object(obj)

    def react_to_object(self, obj):
        print("Collided with", obj)

    # Display
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            sprite_sheet = "jump" if self.jump_count == 1 else "double_jump"
        elif self.y_vel > constants.GRAVITY + 1 and self.jump_count > 0:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites_ = self.sprites.get(sprite_sheet_name, self.sprites.get("idle_right"))

        sprite_index = (self.animation_count // constants.ANIMATION_DELAY) % len(sprites_)
        self.sprite = sprites_[sprite_index]
        self.animation_count += 1
        self.update_mask()

    def update_mask(self):
        self.mask = pygame.mask.from_surface(self.sprite)

    def loop(self):
        self.handle_input()

        self.y_vel += constants.GRAVITY
        self.falling_time += 1

        self.move(self.x_vel, 0)
        self.handle_horizontal_collision(self.blocks)

        self.update_sprite()

        self.move(0, self.y_vel)
        self.handle_vertical_collision(self.blocks, self.y_vel)
        self.handle_object_collision(self.objects)
        self.update_jump()

    def draw(self, screen):
        screen.blit(self.sprite, self.sprite.get_rect(midbottom=self.rect.midbottom))
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)
