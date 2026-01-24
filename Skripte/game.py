import os
import sys
import pygame
import json


import Skripte.constants as constants
from Skripte.Assets import background
from Skripte import player, level
from Skripte.camera import Camera
import Ui.options as options
import Ui.game_menu as game_menu


class Game:
    def __init__(self):
        os.environ["SDL_VIDEO_WINDOW_POS"] = "center"
        pygame.display.set_caption("Abyssplatformer")

        settings_page = options.SettingsPage()
        settings = settings_page.get_settings()
        if settings and settings.get("fullscreen", False):
            self.screen = pygame.display.set_mode(
                (constants.WIDTH, constants.HEIGHT), pygame.FULLSCREEN
            )
        else:
            self.screen = pygame.display.set_mode(
                (constants.WIDTH // 2, constants.HEIGHT // 2), pygame.RESIZABLE
            )

        self.clock = pygame.time.Clock()
        self.camera = Camera(constants.WIDTH, constants.HEIGHT)
        self.room = None

        self.active_rooms = []

        self.current_bg_name = "Gray.png"
        self.background, self.bg_image = background.load_background(
            self.current_bg_name, constants.WIDTH, constants.HEIGHT
        )

        self.objects = level.load_level("map.json")
        self.player = player.Player(100, 100, 20, 25)

        #  Debugging
        self.debug = False
        self.font = pygame.font.SysFont("Arial", 18)
        self.zoom_level = 1.0
        self.debug_scroll_off_x = 0
        self.debug_scroll_off_y = 0
        self.load_save("Data/GameSave/savefile.json")

    def load_save(self, filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                player_data = data.get("player", {})
                self.player.rect.x = player_data.get("position", [100, 100])[0]
                self.player.rect.y = player_data.get("position", [100, 100])[1]
                room_id = data.get("room_id", None)
                camera_pos = data.get("camera_position", None)
                if camera_pos:
                    self.camera.offset.x = camera_pos[0]
                    self.camera.offset.y = camera_pos[1]

                if room_id is not None:
                    for room in self.objects:
                        if room.room_id == room_id:
                            self.room = room
                            self.player.spawn = room.spawn
                            self.update_active_content()
                            break

        except FileNotFoundError:
            print("Save file not found.")
        except json.JSONDecodeError:
            print("Error decoding save file.")

    def save_game(self, filepath):
        data = {
            "player": {
                "position": [self.player.rect.x, self.player.rect.y],
            },
            "room_id": self.room.room_id if self.room else None,
            "camera_position": [self.camera.offset.x, self.camera.offset.y],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

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

        self.player.draw(
            self.screen, int(self.camera.offset.x), int(self.camera.offset.y)
        )

        if self.debug:
            debug_surf = pygame.Surface((constants.WIDTH, constants.HEIGHT))
            debug_surf.fill((30, 30, 30))
            scroll_x = (
                self.player.rect.centerx - (constants.WIDTH / 2) / self.zoom_level
            ) + self.debug_scroll_off_x
            scroll_y = (
                self.player.rect.centery - (constants.HEIGHT / 2) / self.zoom_level
            ) + self.debug_scroll_off_y

            for r in self.active_rooms:
                # 1.
                r_rect = pygame.Rect(
                    (r.rect.x - scroll_x) * self.zoom_level,
                    (r.rect.y - scroll_y) * self.zoom_level,
                    r.rect.width * self.zoom_level,
                    r.rect.height * self.zoom_level,
                )
                pygame.draw.rect(debug_surf, (0, 255, 0), r_rect, 2)

                # 2.
                for item in r.blocks + r.objects:
                    img = item.sprite if hasattr(item, "sprite") else item.image
                    if img:
                        s_w = int(img.get_width() * self.zoom_level)
                        s_h = int(img.get_height() * self.zoom_level)
                        scaled = pygame.transform.scale(img, (max(1, s_w), max(1, s_h)))

                        draw_x = (item.rect.x - scroll_x) * self.zoom_level
                        draw_y = (item.rect.y - scroll_y) * self.zoom_level
                        debug_surf.blit(scaled, (draw_x, draw_y))

                    item_hitbox = pygame.Rect(
                        (item.rect.x - scroll_x) * self.zoom_level,
                        (item.rect.y - scroll_y) * self.zoom_level,
                        item.rect.width * self.zoom_level,
                        item.rect.height * self.zoom_level,
                    )
                    pygame.draw.rect(debug_surf, (255, 0, 0), item_hitbox, 1)

            # 3.
            p_img = self.player.sprite
            if p_img:
                ps_w = int(p_img.get_width() * self.zoom_level)
                ps_h = int(p_img.get_height() * self.zoom_level)
                p_scaled = pygame.transform.scale(p_img, (max(1, ps_w), max(1, ps_h)))

                p_midbottom_x = (
                    self.player.rect.midbottom[0] - scroll_x
                ) * self.zoom_level
                p_midbottom_y = (
                    self.player.rect.midbottom[1] - scroll_y
                ) * self.zoom_level

                p_draw_rect = p_scaled.get_rect(
                    midbottom=(int(p_midbottom_x), int(p_midbottom_y))
                )
                debug_surf.blit(p_scaled, p_draw_rect)

            p_rect_scaled = pygame.Rect(
                (self.player.rect.x - scroll_x) * self.zoom_level,
                (self.player.rect.y - scroll_y) * self.zoom_level,
                self.player.rect.width * self.zoom_level,
                self.player.rect.height * self.zoom_level,
            )
            pygame.draw.rect(debug_surf, (255, 255, 255), p_rect_scaled, 1)

            # 4.
            if self.player.combat and self.player.combat.active:
                atk_rect = self.player.combat.hitbox
                atk_debug_rect = pygame.Rect(
                    (atk_rect.x - scroll_x) * self.zoom_level,
                    (atk_rect.y - scroll_y) * self.zoom_level,
                    atk_rect.width * self.zoom_level,
                    atk_rect.height * self.zoom_level,
                )
                pygame.draw.rect(debug_surf, (255, 0, 255), atk_debug_rect, 2)
            # 4b.
            if (
                self.player.combat
                and self.player.combat.dash_attack_beam_rect
                and self.player.combat.dash_attack_beam_timer > 0
            ):
                beam_rect = self.player.combat.dash_attack_beam_rect
                beam_debug_rect = pygame.Rect(
                    (beam_rect.x - scroll_x) * self.zoom_level,
                    (beam_rect.y - scroll_y) * self.zoom_level,
                    beam_rect.width * self.zoom_level,
                    beam_rect.height * self.zoom_level,
                )

                pygame.draw.rect(debug_surf, (0, 255, 255), beam_debug_rect, 2)

            # 5.
            c_box = self.camera.camera_box
            c_rect = pygame.Rect(
                (c_box.x + self.camera.offset.x - scroll_x) * self.zoom_level,
                (c_box.y + self.camera.offset.y - scroll_y) * self.zoom_level,
                c_box.width * self.zoom_level,
                c_box.height * self.zoom_level,
            )
            pygame.draw.rect(debug_surf, (255, 255, 0), c_rect, 2)

            self.screen.blit(debug_surf, (0, 0))
            self.draw_debug()

        pygame.display.update()

    def draw_debug(self):
        #  Linke Seite: Status Infos
        fps = str(int(self.clock.get_fps()))
        pos = f"Pos: {self.player.rect.x}, {self.player.rect.y}"
        zoom = f"Zoom: {int(self.zoom_level * 100)}%"
        room_info = f"Room ID: {self.room.room_id if self.room else 'None'}"

        status_text = [f"FPS: {fps}", pos, zoom, room_info]

        for i, text in enumerate(status_text):
            img = self.font.render(text, True, (255, 255, 255))
            shadow = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(shadow, (11, 11 + i * 20))
            self.screen.blit(img, (10, 10 + i * 20))

        #  Rechte Seite: Steuerungshilfe
        controls_help = [
            "CONTROLS:",
            "F3: Close Debug",
            "+ / -: Zoom In/Out",
            "Arrows: Move Cam",
            "R: Reset Cam",
        ]

        for i, text in enumerate(controls_help):
            color = (255, 200, 0) if i == 0 else (200, 200, 200)

            img = self.font.render(text, True, color)
            shadow = self.font.render(text, True, (0, 0, 0))

            text_width = img.get_width()
            x_pos = constants.WIDTH - text_width - 20
            y_pos = 10 + i * 20

            self.screen.blit(shadow, (x_pos + 1, y_pos + 1))
            self.screen.blit(img, (x_pos, y_pos))

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
                        self.save_game("Data/GameSave/savefile.json")
                        self.open_game_menu()
                    elif event.type == pygame.VIDEORESIZE:
                        self.width, self.height = event.size
                        self.screen = pygame.display.set_mode(
                            (self.width, self.height), pygame.RESIZABLE
                        )
                    # Debug
                    if event.key == pygame.K_F3:
                        self.debug = not self.debug
                        self.debug_scroll_off_x = 0
                        self.debug_scroll_off_y = 0
                    if event.key == pygame.K_r:
                        self.debug_scroll_off_x = 0
                        self.debug_scroll_off_y = 0
                    if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                        self.zoom_level += 0.1
                    if event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                        self.zoom_level = max(0.1, self.zoom_level - 0.1)

            if self.debug:
                keys = pygame.key.get_pressed()
                debug_cam_speed = 10 / self.zoom_level

                if keys[pygame.K_LEFT]:
                    self.debug_scroll_off_x -= debug_cam_speed
                if keys[pygame.K_RIGHT]:
                    self.debug_scroll_off_x += debug_cam_speed
                if keys[pygame.K_UP]:
                    self.debug_scroll_off_y -= debug_cam_speed
                if keys[pygame.K_DOWN]:
                    self.debug_scroll_off_y += debug_cam_speed

            # Raum
            for room in self.objects:
                if room.check_player_in_room(self.player.rect):
                    if self.room != room:
                        self.room = room
                        self.player.spawn = room.spawn

                        self.update_active_content()

                        self.background, _ = background.load_background(
                            self.current_bg_name, room.rect.width, room.rect.height
                        )

            self.player.loop()
            if not self.player.is_alive:
                self.camera.teleport_to_player(self.player, self.room)
                self.player.is_alive = True

            for r in self.active_rooms:
                for obj in r.objects:
                    if hasattr(obj, "loop"):
                        obj.loop()

            self.draw()
