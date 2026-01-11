import sys
import pygame

import constants
from Assets import background
import player
import level


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Abyssplatformer")

        self.screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))

        self.clock = pygame.time.Clock()

        self.background, self.bg_image = background.load_background("Gray.png")

        self.player = player.Player(100, 100, 50, 50)

        self.objects = level.load_level("../Data/Maps/map.json")

    def draw(self):
        #Background
        for tile in self.background:
            self.screen.blit(self.bg_image, tile)

        #Objekte
        for obj in self.objects:
            obj.draw(self.screen, 0, 0)

        #Player
        self.player.draw(self.screen)
        pygame.display.update()

    def run(self):
        while True:
            self.clock.tick(constants.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.player.loop(constants.FPS)
            for obj in self.objects:
                if hasattr(obj, "loop"):
                    obj.loop()
            self.draw()
