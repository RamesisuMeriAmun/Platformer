import pygame


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None, hitbox_data=None):
        super().__init__()
        self.name = name
        self.width = width
        self.height = height
        self.hitbox_data = hitbox_data
        self.rect = pygame.Rect(x, y, width, height)

        if self.hitbox_data:
            off_x, off_y, w, h = self.hitbox_data
            self.rect = pygame.Rect(x + off_x, y + off_y, w, h)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)

    def draw(self, win, offset_x, offset_y):
        if self.hitbox_data:
            off_x, off_y, _, _ = self.hitbox_data
            win.blit(self.image, (self.rect.x - off_x - int(offset_x),
                                  self.rect.y - off_y - int(offset_y)))
        else:
            win.blit(self.image, (self.rect.x - int(offset_x),
                                  self.rect.y - int(offset_y)))

    def draw_debug(self, screen, offset_x, offset_y):
        rel_rect = self.rect.move(-offset_x, -offset_y)
        pygame.draw.rect(screen, (0, 255, 255), rel_rect, 1)
