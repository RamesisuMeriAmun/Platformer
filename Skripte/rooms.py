import pygame


class Room:
    COLOR = (100, 150, 255, 50)  # halbtransparent blau

    def __init__(self, x, y, width, height, name=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name or f"Room_{x}_{y}"
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface, zoom=1.0, scroll=(0, 0)):
        s = pygame.Surface((self.width*zoom, self.height*zoom), pygame.SRCALPHA)
        s.fill(self.COLOR)
        surface.blit(s, ((self.x - scroll[0])*zoom, (self.y - scroll[1])*zoom))
        font = pygame.font.SysFont("Arial", int(14*zoom))
        text = font.render(self.name, True, (255, 255, 255))
        surface.blit(text, ((self.x - scroll[0])*zoom + 5, (self.y - scroll[1])*zoom + 5))

    @staticmethod
    def generate_rooms(map_width, map_height, room_width=2000, room_height=1500):
        rooms = []
        cols = (map_width + room_width - 1) // room_width
        rows = (map_height + room_height - 1) // room_height

        for col in range(cols):
            for row in range(rows):
                x = col * room_width
                y = row * room_height
                rooms.append(Room(x, y, room_width, room_height, f"Room_{col}_{row}"))
        return rooms
