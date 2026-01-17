import pygame


class Attackhandler:
    def __init__(self, player):
        self.player = player
        self.active = False
        self.direction = None  # "up", "down", "left", "right"
        self.timer = 0
        self.duration = 10
        self.cooldown = 0
        self.cooldown_max = 25

        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.attack_range = 40
        self.attack_thickness = 30

        self.pogo_targets = ["spikes"]

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
        if self.active:
            pygame.draw.rect(screen, (255, 0, 0),
                             (self.hitbox.x - offset_x, self.hitbox.y - offset_y,
                              self.hitbox.width, self.hitbox.height), 2)
