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

        self.neighbors = []

    def check_player_in_room(self, player):
        self.contains_player = self.rect.colliderect(player)
        return self.contains_player

    def add_neighbors(self, other_room):
        if other_room not in self.neighbors:
            self.neighbors.append(other_room)
