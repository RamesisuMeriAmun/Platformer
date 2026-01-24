import os
import pygame
import sys
from Ui import options
from Skripte import game
from Skripte.constants import WIDTH, HEIGHT


class MainMenu:
    def __init__(self):
        os.environ["SDL_VIDEO_WINDOW_POS"] = "center"
        settings_page = options.SettingsPage()
        settings = settings_page.get_settings()
        if settings and settings.get("fullscreen", False):
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
            self.width = WIDTH
            self.height = HEIGHT
        else:
            self.screen = pygame.display.set_mode(
                (WIDTH // 2, HEIGHT // 2), pygame.RESIZABLE
            )
            self.width = WIDTH // 2
            self.height = HEIGHT // 2
        pygame.display.set_caption("Main Menu")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.running = True
        self.showing_settings = False

        # Button properties
        self.buttons = [
            {"label": "Start", "rect": pygame.Rect(300, 200, 200, 60)},
            {"label": "Settings", "rect": pygame.Rect(300, 300, 200, 60)},
            {"label": "Quit", "rect": pygame.Rect(300, 400, 200, 60)},
        ]
        self.button_color = (100, 100, 100)
        self.button_hover_color = (150, 150, 150)
        self.button_text_color = (255, 255, 255)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(event.pos)
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.size
                self.screen = pygame.display.set_mode(
                    (self.width, self.height), pygame.RESIZABLE
                )

    def handle_click(self, pos):
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                action = button["label"].lower()
                if action == "start":
                    game.Game().run()
                elif action == "settings":
                    settings_page = options.SettingsPage()
                    settings = settings_page.run()
                    if settings:
                        print("Einstellungen gespeichert:", settings)
                elif action == "quit":
                    self.running = False

    def draw(self):
        self.screen.fill((30, 30, 30))

        # Draw title
        title = self.font_large.render("PLATFORMER", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title, title_rect)

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        button_width = 200
        button_height = 60
        button_spacing = 40
        total_height = (
            len(self.buttons) * button_height + (len(self.buttons) - 1) * button_spacing
        )
        start_y = (self.height - total_height) // 2
        for i, button in enumerate(self.buttons):
            x = (self.width - button_width) // 2
            y = start_y + i * (button_height + button_spacing)
            button["rect"].x = x
            button["rect"].y = y
            color = (
                self.button_hover_color
                if button["rect"].collidepoint(mouse_pos)
                else self.button_color
            )
            pygame.draw.rect(self.screen, color, button["rect"])
            pygame.draw.rect(self.screen, (255, 255, 255), button["rect"], 3)

            text = self.font_medium.render(
                button["label"], True, self.button_text_color
            )
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


def main_menu():
    menu = MainMenu()
    menu.run()
