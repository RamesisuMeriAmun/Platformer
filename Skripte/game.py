import sys
import pygame

import Skripte.constants as constants
from Skripte.Assets import background
from Skripte import player, level


class Game:
    def __init__(self):

        pygame.display.set_caption("Abyssplatformer")

        self.screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))

        self.clock = pygame.time.Clock()

        self.background, self.bg_image = background.load_background("Gray.png")

        self.objects = level.load_level("map.json")

        self.player = player.Player(100, 100, 40, 50, self.objects)

    def draw(self):
        # Background
        for tile in self.background:
            self.screen.blit(self.bg_image, tile)

        # Objekte
        for obj in self.objects:
            obj.draw(self.screen, 0, 0)

        # Player
        self.player.draw(self.screen)
        pygame.display.update()

    def run(self):
        while True:
            self.clock.tick(constants.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.player.loop()
            for obj in self.objects:
                if hasattr(obj, "loop"):
                    obj.loop()
            self.draw()
