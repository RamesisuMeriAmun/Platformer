import pygame


class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.offset = pygame.math.Vector2(0, 0)
        self.smooth_speed = 0.3

        self.camera_box_width = 400
        self.camera_box_height = 100
        self.horizontal_bias = 100
        self.vertical_bias = 50
        self.camera_box = pygame.Rect(
            (self.width - self.camera_box_width) // 2 - self.horizontal_bias,
            (self.height - self.camera_box_height) // 2 + self.vertical_bias,
            self.camera_box_width,
            self.camera_box_height
        )

    def update(self, player, room):
        if hasattr(player, "direction"):
            target_bias = -150 if player.direction == "right" else 150
            self.horizontal_bias += (target_bias - self.horizontal_bias) * 0.01

            self.camera_box.x = (self.width - self.camera_box_width) // 2 + self.horizontal_bias

        player_screen_x = player.rect.centerx - self.offset.x
        player_screen_y = player.rect.centery - self.offset.y

        target_x = self.offset.x
        target_y = self.offset.y

        if player_screen_x < self.camera_box.left:
            target_x = player.rect.centerx - self.camera_box.left
        elif player_screen_x > self.camera_box.right:
            target_x = player.rect.centerx - self.camera_box.right

        if player_screen_y < self.camera_box.top:
            target_y = player.rect.centery - self.camera_box.top
        elif player_screen_y > self.camera_box.bottom:
            target_y = player.rect.centery - self.camera_box.bottom

        target_x = max(room.rect.left, min(target_x, room.rect.right - self.width))
        target_y = max(room.rect.top, min(target_y, room.rect.bottom - self.height))

        self.offset.x += (target_x - self.offset.x) * self.smooth_speed
        self.offset.y += (target_y - self.offset.y) * self.smooth_speed

    def apply_to_rect(self, rect):
        return rect.move(-int(self.offset.x), -int(self.offset.y))

    def teleport_to_player(self, player, room):
        target_x = player.rect.centerx - self.width // 2
        target_y = player.rect.centery - self.height // 2

        self.offset.x = max(room.rect.left, min(target_x, room.rect.right - self.width))
        self.offset.y = max(room.rect.top, min(target_y, room.rect.bottom - self.height))

    def resize(self, new_width, new_height):
        self.width = new_width
        self.height = new_height
        self.camera_box.x = (self.width - self.camera_box_width) // 2 + self.horizontal_bias
        self.camera_box.y = (self.height - self.camera_box_height) // 2 + self.vertical_bias

    def draw_debug(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), self.camera_box, 2)
