import sys
import pygame
from Skripte.constants import WIDTH, HEIGHT, WHITE, BLACK, BIG_FONT
from Ui.Components.slider import Slider
from Ui.Components.check_box import Checkbox
from Ui.Components.button import Button


class SettingsPage:
    def __init__(self):
        self.volume_slider = Slider("Volume", 250, 200, 300, value=67)
        self.fullscreen_checkbox = Checkbox("Fullscreen", 420, 250, checked=False)
        self.back_button = Button("Back", 300, 350, 200, 50)
        self.fullscreen_state = False

    def draw(self, screen):
        screen.fill(WHITE)
        title = BIG_FONT.render("Settings", True, BLACK)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))
        self.volume_slider.draw(screen, center=(WIDTH // 2, 200))
        self.fullscreen_checkbox.draw(screen, center=(WIDTH // 2, 250))
        self.back_button.draw(screen, center=(WIDTH // 2, 350))

    def handle_events(self, events):
        for event in events:
            self.volume_slider.update(event)
            toggled = self.fullscreen_checkbox.clicked(event)
            if toggled:
                if self.fullscreen_checkbox.checked:
                    pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    self.fullscreen_state = True
                else:
                    pygame.display.set_mode((WIDTH, HEIGHT))
                    self.fullscreen_state = False
            if self.back_button.clicked(event):
                return True  # tells menu to return
        return False

    def get_settings(self):
        return {
            "volume": self.volume_slider.value,
            "fullscreen": self.fullscreen_checkbox.checked,
        }

    def set_settings(self, settings):
        if "volume" in settings:
            self.volume_slider.value = settings["volume"]
            self.volume_slider.handle.centerx = (
                self.volume_slider.rect.x
                + (settings["volume"] / 100) * self.volume_slider.rect.w
            )
        if "fullscreen" in settings:
            self.fullscreen_checkbox.checked = settings["fullscreen"]
            self.fullscreen_state = settings["fullscreen"]

    def run(self):
        screen = pygame.display.get_surface()
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.handle_events(events):
                running = False

            self.draw(screen)
            pygame.display.flip()

        return self.get_settings()
