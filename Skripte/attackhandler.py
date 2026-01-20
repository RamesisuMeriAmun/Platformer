import pygame


class Attackhandler:
    def __init__(self, player):
        self.player = player
        self.active = False
        self.direction = None
        self.timer = 0
        self.duration = 10
        self.cooldown = 0
        self.cooldown_max = 25

        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.attack_range = 40
        self.attack_thickness = 30

        self.pogo_targets = ["spikes"]

        self.dash_attack_beam_rect = None
        self.dash_attack_beam_timer = 0

    def trigger_dash_attack(self, blocks, direction_key):
        if self.cooldown > 0:
            return

        dx, dy = 0, 0
        if direction_key == "up":
            dy = -1
        elif direction_key == "left":
            dx = -1
        elif direction_key == "right":
            dx = 1
        else:
            dx = 1 if self.player.direction == "right" else -1

        max_range = 300
        line_thickness = 20

        if dy == -1:
            beam = pygame.Rect(self.player.rect.centerx - (line_thickness // 2),
                               self.player.rect.top - max_range,
                               line_thickness, max_range)
        elif dx != 0:
            if dx > 0:
                beam = pygame.Rect(self.player.rect.right,
                                   self.player.rect.centery - (line_thickness // 2),
                                   max_range, line_thickness)
            else:
                beam = pygame.Rect(self.player.rect.left - max_range,
                                   self.player.rect.centery - (line_thickness // 2),
                                   max_range, line_thickness)

        self.dash_attack_beam_rect = beam
        self.dash_attack_beam_timer = 10

        closest_dist = max_range
        hit_target = False

        for block in blocks:
            if beam.colliderect(block.rect):
                if dy == -1:
                    dist = self.player.rect.top - block.rect.bottom
                else:
                    dist = (block.rect.left - self.player.rect.right) if dx > 0 else (
                            self.player.rect.left - block.rect.right)

                if 0 <= dist < closest_dist:
                    closest_dist = dist
                    hit_target = True

        if hit_target:
            target_x = self.player.rect.x + (closest_dist * dx)
            target_y = self.player.rect.y + (closest_dist * dy)
            self.player.start_auto_dash(target_x, target_y)
            self.cooldown = 40

    def update(self, objects):
        if self.cooldown > 0:
            self.cooldown -= 1

        if self.active:
            self.timer -= 1
            self._update_hitbox_pos()
            self._check_collisions(objects)
            if self.timer <= 0:
                self.active = False

    def trigger(self, direction):
        if self.cooldown <= 0 and not self.active:
            self.active = True
            self.direction = direction
            self.timer = self.duration
            self.cooldown = self.cooldown_max

    def _update_hitbox_pos(self):
        p_rect = self.player.rect
        if self.direction == "down":
            self.hitbox.size = (p_rect.width * 1.5, self.attack_thickness)
            self.hitbox.midtop = (p_rect.centerx, p_rect.bottom + 5)
        elif self.direction == "up":
            self.hitbox.size = (p_rect.width * 1.5, self.attack_thickness)
            self.hitbox.midbottom = (p_rect.centerx, p_rect.top - 5)
        elif self.direction == "left":
            self.hitbox.size = (self.attack_thickness, p_rect.height)
            self.hitbox.midright = (p_rect.left - 5, p_rect.centery)
        elif self.direction == "right":
            self.hitbox.size = (self.attack_thickness, p_rect.height)
            self.hitbox.midleft = (p_rect.right + 5, p_rect.centery)

    def _check_collisions(self, objects):
        for obj in objects:
            if self.hitbox.colliderect(obj.rect):
                if self.direction == "down" and self.player.y_vel > 0:
                    if obj.name in self.pogo_targets:
                        self.player.execute_pogo_bounce()
                        self.active = False
                        break

    def draw(self, screen, offset_x, offset_y):
        # 1. Normaler Angriff
        if self.active:
            pygame.draw.rect(screen, (255, 0, 0),
                             (self.hitbox.x - offset_x, self.hitbox.y - offset_y,
                              self.hitbox.width, self.hitbox.height), 2)

        # 2. Dash-Attack Strahl
        if self.dash_attack_beam_rect and self.dash_attack_beam_timer > 0:
            draw_rect = self.dash_attack_beam_rect.move(-offset_x, -offset_y)
            pygame.draw.rect(screen, (0, 255, 255), draw_rect, 2)
            self.dash_attack_beam_timer -= 1
        else:
            self.dash_attack_beam_rect = None