import sys
import pygame

import Skripte.constants as constants
from Skripte.Assets import background
from Skripte import player, level
from Skripte.camera import Camera
import Ui.options as options
import Ui.game_menu as game_menu


class Game:
    def __init__(self):
        pygame.display.set_caption("Abyssplatformer")

        settings_page = options.SettingsPage()
        settings = settings_page.get_settings()
        if settings and settings.get("fullscreen", False):
            self.screen = pygame.display.set_mode(
                (constants.WIDTH, constants.HEIGHT), pygame.FULLSCREEN
            )
        else:
            self.screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))

        self.clock = pygame.time.Clock()
        self.camera = Camera(constants.WIDTH, constants.HEIGHT)
        self.room = None

        self.active_rooms = []

        self.current_bg_name = "Gray.png"
        self.background, self.bg_image = background.load_background(
            self.current_bg_name, constants.WIDTH, constants.HEIGHT
        )

        self.objects = level.load_level("map.json")
        self.player = player.Player(100, 100, 40, 50)

    def update_active_content(self):
        if not self.room:
            return

        self.active_rooms = [self.room] + self.room.neighbors

        combined_blocks = []
        combined_objects = []

        for r in self.active_rooms:
            combined_blocks.extend(r.blocks)
            combined_objects.extend(r.objects)

        self.player.set_active_collision(combined_blocks, combined_objects)

    def draw(self):
        self.screen.fill(constants.BACKGROUND_COLOR)

        if self.room:
            self.camera.update(self.player, self.room)
            ox = int(self.camera.offset.x)
            oy = int(self.camera.offset.y)

            for tile in self.background:
                draw_x = tile[0] + self.room.rect.x - ox
                draw_y = tile[1] + self.room.rect.y - oy
                self.screen.blit(self.bg_image, (draw_x, draw_y))

            for r in self.active_rooms:
                for block in r.blocks:
                    block.draw(self.screen, ox, oy)
                for obj in r.objects:
                    obj.draw(self.screen, ox, oy)

        self.player.draw(self.screen, int(self.camera.offset.x), int(self.camera.offset.y))

        pygame.display.update()

    def open_game_menu(self):
        print("Game menu opened")
        game_menu.GameMenu().run()

    def run(self):
        while True:
            self.clock.tick(constants.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.open_game_menu()

            # Raum
            for room in self.objects:
                if room.check_player_in_room(self.player.rect):
                    if self.room != room:
                        self.room = room
                        self.player.spawn = room.spawn

                        self.update_active_content()

                        self.background, _ = background.load_background(
                            self.current_bg_name,
                            room.rect.width,
                            room.rect.height)

            self.player.loop()
            if not self.player.is_alive:
                self.camera.teleport_to_player(self.player, self.room)
                self.player.is_alive = True

            for r in self.active_rooms:
                for obj in r.objects:
                    if hasattr(obj, "loop"):
                        obj.loop()

            self.draw()
