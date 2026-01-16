import sys
import pygame

import Skripte.constants as constants
from Skripte.Assets import background
from Skripte import player, level
from Skripte.rooms import Room
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

        self.current_bg_name = "Gray.png"

        self.background, self.bg_image = background.load_background(self.current_bg_name, constants.WIDTH, constants.HEIGHT)

        self.objects = level.load_level("map.json")

        self.player = player.Player(100, 100, 40, 50, self.objects)

    def draw(self):

        self.screen.fill(constants.BACKGROUND_COLOR)
        # Kamera-Position basierend auf Spieler und aktuellem Raum aktualisieren
        self.camera.update(self.player, self.room)

        # Offsets für die draw-Aufrufe zwischenspeichern
        ox = int(self.camera.offset.x)
        oy = int(self.camera.offset.y)

        # 1. Hintergrund zeichnen
        for tile in self.background:
            draw_x = tile[0] + self.room.rect.x - ox
            draw_y = tile[1] + self.room.rect.y - oy
            self.screen.blit(self.bg_image, (draw_x, draw_y))

        # 2. Objekte zeichnen
        for obj in self.objects:
            if not isinstance(obj, Room):
                obj.draw(self.screen, ox, oy)

        # 3. Spieler zeichnen
        self.player.draw(self.screen, ox, oy)

        pygame.display.update()

    def open_game_menu(self):
        # Placeholder for game menu logic
        print("Game menu opened")
        game_menu.GameMenu().run()
        # You can replace this with actual menu logic

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

            self.player.loop()

            for room in self.objects:
                if isinstance(room, Room):
                    if room.check_player_in_room(self.player.rect):
                        if self.room != room:
                            self.room = room
                            self.player.spawn = room.spawn
                            # HIER: Hintergrund für die Größe des neuen Raums neu generieren
                            self.background, _ = background.load_background(
                                self.current_bg_name,
                                room.rect.width,
                                room.rect.height
                            )

            for obj in self.objects:
                if hasattr(obj, "loop"):
                    obj.loop()

            self.draw()
