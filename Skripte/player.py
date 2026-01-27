import pygame
import json
from Skripte import constants, sprites
from Skripte.attackhandler import Attackhandler


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.sprites = sprites.load_sprite_sheets(
            "MainCharacters", "MaskDude", 32, 32, True
        )
        with open("Data/Settings/settings.json", "r") as f:
            settings = json.load(f)
        self.load_settings(settings)
        self.sprite = None
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.spawn = (x, y)
        self.is_alive = True
        self.on_ground = False

        self.x_vel = 0
        self.y_vel = 0
        self.falling_time = 0

        # Jump
        self.jump_count = 0
        self.jump_pressed = False
        self.jump_hold_time = 0

        self.JUMP_FORCE = 7
        self.DOUBLE_JUMP_FORCE = 6
        self.JUMP_HOLD_FORCE = 0.6
        self.MAX_JUMP_HOLD = 12

        # Walljump
        self.wall_jump_force_x = 3
        self.wall_jump_force_y = 7
        self.is_on_wall = False
        self.wall_direction = 0  # -1 = left, 1 = right
        self.wall_jump_timer = 0

        # Dash
        self.dashing = False
        self.dash_velocity = 12
        self.dash_duration = 12
        self.dash_timer = 0
        self.can_dash = True
        self.dash_cooldown = 700
        self.last_dash_time = 0

        # Auto-Dash
        self.auto_dashing = False
        self.auto_dash_target_x = 0
        self.auto_dash_target_y = 0
        self.auto_dash_speed = 18
        self.attack_pressed = False

        # Pogo / Combat
        self.combat = Attackhandler(self)
        self.is_pogoing = False
        self.is_attacking = False

        # Kollision
        self.blocks = []
        self.objects = []

        self.hit = False

    # Movement
    def handle_input(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        # Movement
        if not self.dashing:
            if self.wall_jump_timer <= 0:
                self.x_vel = 0
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

        # Dash
        if keys[pygame.K_LSHIFT]:
            self.dash()

        if mouse[0]:
            if not self.attack_pressed:

                if self.dashing:
                    direction = None
                    if keys[pygame.K_w]:
                        direction = "up"
                    elif keys[pygame.K_a]:
                        direction = "left"
                    elif keys[pygame.K_d]:
                        direction = "right"

                    self.combat.trigger_dash_attack(self.blocks, direction)

                else:
                    if keys[pygame.K_s]:
                        self.combat.trigger("down")
                    elif keys[pygame.K_w]:
                        self.combat.trigger("up")
                    elif self.direction == "left":
                        self.combat.trigger("left")
                    else:
                        self.combat.trigger("right")
                    self.is_attacking = True

                self.attack_pressed = True
            else:
                self.attack_pressed = False
                self.is_attacking = False

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
        if self.on_ground and not self.is_on_wall:
            self.y_vel = -self.JUMP_FORCE
            self.jump_count = 1
            self.jump_hold_time = 0
            self.on_ground = False

        elif self.is_on_wall:
            self.y_vel = -self.wall_jump_force_y
            self.x_vel = -self.wall_direction * self.wall_jump_force_x
            self.jump_count = 1
            self.wall_jump_timer = 15

        elif self.jump_count == 1:
            self.y_vel = -self.DOUBLE_JUMP_FORCE
            self.jump_count = 2

    def load_settings(self, settings):
        keybinds = settings.get("keybinds", {})
        self.key_jump = keybinds.get("jump", pygame.K_SPACE)
        self.key_left = keybinds.get("left", pygame.K_a)
        self.key_right = keybinds.get("right", pygame.K_d)
        self.key_down = keybinds.get("down", pygame.K_s)

    def update_jump(self):
        keys = pygame.key.get_pressed()

        if not self.is_pogoing:
            if (
                    keys[self.key_jump]
                    and self.y_vel < 0
                    and self.jump_hold_time < self.MAX_JUMP_HOLD
                    and self.jump_count
                    == 0
            ):
                self.y_vel -= self.JUMP_HOLD_FORCE
                self.jump_hold_time += 1

            if not keys[self.key_jump] and self.y_vel < 0:
                if self.jump_hold_time < self.MAX_JUMP_HOLD:
                    self.y_vel *= 0.35

    def check_grounded(self):
        floor_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, 2)
        found_floor = False
        for block in self.blocks:
            if floor_rect.colliderect(block.rect):
                found_floor = True
                break

        if found_floor:
            self.on_ground = True
            self.jump_count = 0
            self.can_dash = True
        else:
            self.on_ground = False
            if self.jump_count == 0:
                self.jump_count = 1

    # Dash
    def dash(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_dash_time >= self.dash_cooldown and self.can_dash:
            if self.is_on_wall:
                self.direction = "left" if self.wall_direction == 1 else "right"
                self.animation_count = 0
                self.is_on_wall = False
                self.can_dash = False
            self.dashing = True
            self.dash_timer = self.dash_duration
            self.last_dash_time = current_time
            self.can_dash = False

    # Auto-Dash
    def start_auto_dash(self, target_x, target_y):
        self.auto_dashing = True
        self.auto_dash_target_x = target_x
        self.auto_dash_target_y = target_y
        self.x_vel = 0
        self.y_vel = 0
        self.jump_count = 1

    # Pogo
    def execute_pogo_bounce(self):
        self.y_vel = -self.JUMP_FORCE * 0.8
        self.is_pogoing = True
        self.falling_time = 0
        self.on_ground = False
        self.jump_count = 1
        self.can_dash = True

    # Kollision
    def set_active_collision(self, blocks, objects):
        self.blocks = blocks
        self.objects = objects

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
        self.y_vel = 0
        self.falling_time = 0
        self.can_dash = True

    def hit_head(self):
        self.y_vel = 1
        self.is_pogoing = False

    def handle_horizontal_collision(self, blocks):
        self.is_on_wall = False
        self.wall_direction = 0

        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.x_vel > 0:
                    self.rect.right = block.rect.left
                    self.is_on_wall = True
                    self.wall_direction = 1
                    self.can_dash = True
                    self.auto_dashing = False
                elif self.x_vel < 0:
                    self.rect.left = block.rect.right
                    self.is_on_wall = True
                    self.wall_direction = -1
                    self.can_dash = True
                    self.auto_dashing = False

    def handle_object_collision(self, objects):
        for obj in objects:
            if self.rect.colliderect(obj.rect):
                overlap_x = obj.rect.x - self.rect.x
                overlap_y = obj.rect.y - self.rect.y

                if self.mask.overlap(obj.mask, (overlap_x, overlap_y)):
                    self.react_to_object(obj)

    def react_to_object(self, obj):
        if obj.name == "spikes":
            self.is_alive = False
            self.death()

        if obj.name == "lava":
            self.is_alive = False
            self.death()

        if obj.name == "trampoline":
            obj.trigger(self)
            self.jump_count = 1
            self.jump_hold_time = self.MAX_JUMP_HOLD

        if obj.name == "wall_trampoline":
            obj.trigger(self)
            self.jump_count = 1
            self.jump_hold_time = self.MAX_JUMP_HOLD

    def death(self):
        if not self.is_alive:
            self.rect.topleft = self.spawn
            self.x_vel = 0
            self.y_vel = 0
            self.direction = "right"
            self.dashing = False
            self.dash_timer = 0
            self.auto_dashing = False
            self.wall_jump_timer = 0
            self.animation_count = 0
            self.on_ground = True
            self.is_alive = True

    # Display
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.dashing:
            sprite_sheet = "run"  # hat keinen eigenen Dash-Sprite
        elif self.is_on_wall:
            sprite_sheet = "wall_jump"
        elif self.y_vel < 0:
            sprite_sheet = "jump" if self.jump_count == 1 else "double_jump"
        elif self.y_vel > constants.GRAVITY + 1:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        if self.combat.active:  # hat noch keine eigenen sprites
            pass

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites_ = self.sprites.get(sprite_sheet_name, self.sprites.get("idle_right"))

        sprite_index = (self.animation_count // constants.ANIMATION_DELAY) % len(
            sprites_
        )
        self.sprite = sprites_[sprite_index]
        self.animation_count += 1
        self.update_mask()

    def update_mask(self):
        self.mask = pygame.mask.from_surface(self.sprite)

    def loop(self):
        if not self.is_alive:
            self.death()
            return

        if self.auto_dashing:
            pull_speed = self.auto_dash_speed + 5

            dx = self.auto_dash_target_x - self.rect.x
            if abs(dx) > pull_speed:
                self.rect.x += pull_speed if dx > 0 else -pull_speed
            else:
                self.rect.x = self.auto_dash_target_x

            dy = self.auto_dash_target_y - self.rect.y
            if abs(dy) > pull_speed:
                self.rect.y += pull_speed if dy > 0 else -pull_speed
            else:
                self.rect.y = self.auto_dash_target_y

            if (
                    self.rect.x == self.auto_dash_target_x
                    and self.rect.y == self.auto_dash_target_y
            ):
                self.auto_dashing = False
                self.dashing = False  # Setzt auch den normalen Dash zurück
                self.y_vel = 0

        if self.wall_jump_timer > 0:
            self.wall_jump_timer -= 1

        self.combat.update(self.objects)

        if self.dashing:
            self.x_vel = (
                self.dash_velocity if self.direction == "right" else -self.dash_velocity
            )
            self.y_vel = 0
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dashing = False
        else:
            self.y_vel += constants.GRAVITY
            if self.is_on_wall and self.y_vel > 0:
                self.y_vel = min(self.y_vel, 2)

        self.move(self.x_vel, 0)
        self.handle_horizontal_collision(self.blocks)
        self.move(0, self.y_vel)

        self.handle_vertical_collision(self.blocks, self.y_vel)
        self.handle_object_collision(self.objects)

        if self.y_vel >= 0:
            self.is_pogoing = False

        if not self.is_alive:
            self.x_vel = 0
            self.y_vel = 0
            self.update_sprite()
            return

        self.check_grounded()
        self.handle_input()
        self.update_jump()
        self.update_sprite()

    def draw(self, screen, offset_x=0, offset_y=0):
        draw_pos = self.sprite.get_rect(
            midbottom=(
                self.rect.midbottom[0] - int(offset_x),
                self.rect.midbottom[1] - int(offset_y),
            )
        )
        screen.blit(self.sprite, draw_pos)

        self.combat.draw(screen, offset_x, offset_y)

    def draw_debug(self, screen, offset_x, offset_y):

        rel_rect = self.rect.move(-offset_x, -offset_y)
        pygame.draw.rect(screen, (255, 0, 0), rel_rect, 2)

        floor_rect = pygame.Rect(rel_rect.x, rel_rect.bottom, rel_rect.width, 2)
        pygame.draw.rect(screen, (255, 255, 0), floor_rect, 2)

        if self.mask:
            mask_surf = self.mask.to_surface(
                setcolor=(0, 100, 255, 150), unsetcolor=(0, 0, 0, 0)
            )
            draw_pos = self.sprite.get_rect(midbottom=rel_rect.midbottom)
            screen.blit(mask_surf, draw_pos)

        if self.combat:
            self.combat.draw(screen, offset_x, offset_y)
