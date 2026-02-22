import pygame

ROOM_MAPPING = {
    "NORMAL": {"color": (0, 255, 0), "id": 0},
    "BOSS":   {"color": (255, 0, 0), "id": 2},
    "START": {"color": (255, 255, 0), "id": 3}
}


class Room:
    def __init__(self, x, y, width, height, room_id, spawn_x, spawn_y):
        self.room_id = room_id
        self.rect = pygame.Rect(x, y, width, height)
        self.contains_player = False
        self.spawn = (spawn_x, spawn_y)

        self.blocks = []
        self.objects = []
        self.decorations = []

        self.layer_3 = []
        self.layer_2 = []
        self.layer_1 = []
        self.layer_foreground = []

        self.neighbors = []

    def check_player_in_room(self, player):
        self.contains_player = self.rect.colliderect(player)
        return self.contains_player

    def add_neighbors(self, other_room):
        if other_room not in self.neighbors:
            self.neighbors.append(other_room)

    def draw_debug(self, screen, offset_x, offset_y):

        rel_rect = self.rect.move(-int(offset_x), -int(offset_y))

        color = (255, 255, 0) if self.contains_player else (200, 200, 200)

        pygame.draw.rect(screen, color, rel_rect, 3)

        if hasattr(self, 'font'):
            info_str = f"Room: {self.room_id} | Neighbors: {len(self.neighbors)}"
            label = self.font.render(info_str, True, color)
            screen.blit(label, (rel_rect.x + 10, rel_rect.y + 10))

        spawn_pos = (self.spawn[0] - offset_x, self.spawn[1] - offset_y)
        pygame.draw.circle(screen, (0, 255, 255), spawn_pos, 5)