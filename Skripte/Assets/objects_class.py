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
        self._scaled_cache = {}

    def draw(self, win, offset_x, offset_y, scale=1.0):
        if self.hitbox_data:
            off_x, off_y, _, _ = self.hitbox_data
            world_x = self.rect.x - off_x - float(offset_x)
            world_y = self.rect.y - off_y - float(offset_y)
        else:
            world_x = self.rect.x - float(offset_x)
            world_y = self.rect.y - float(offset_y)

        draw_x = round(world_x * scale)
        draw_y = round(world_y * scale)

        if abs(scale - 1.0) < 1e-6:
            win.blit(self.image, (draw_x, draw_y))
            return

        src_w, src_h = self.image.get_size()
        target_size = (max(1, round(src_w * scale)), max(1, round(src_h * scale)))
        cache_key = (id(self.image), target_size)
        scaled_image = self._scaled_cache.get(cache_key)
        if scaled_image is None:
            scaled_image = pygame.transform.scale(self.image, target_size)
            self._scaled_cache = {cache_key: scaled_image}

        win.blit(scaled_image, (draw_x, draw_y))

    def draw_debug(self, screen, offset_x, offset_y):
        rel_rect = self.rect.move(-offset_x, -offset_y)
        pygame.draw.rect(screen, (0, 255, 255), rel_rect, 1)
