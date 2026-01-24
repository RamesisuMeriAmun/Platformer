import sys
import pygame
from Skripte.constants import WIDTH, HEIGHT, WHITE, BLACK
from Ui.Components.slider import Slider
from Ui.Components.check_box import Checkbox
from Ui.Components.button import Button

BIG_FONT = pygame.font.SysFont(None, 56)
SMALL_FONT = pygame.font.SysFont(None, 36)

DEFAULT_KEYBINDS = {
    "jump": pygame.K_SPACE,
    "left": pygame.K_a,
    "right": pygame.K_d,
    "down": pygame.K_s,
}

KEYBIND_LABELS = {
    "jump": "Jump",
    "left": "Left",
    "right": "Right",
    "down": "Down",
}


class SettingsPage:
    def __init__(self):
        import os, json

        settings_path = "Data/Settings/settings.json"
        settings = None
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as f:
                    settings = json.load(f)
            except Exception:
                settings = None
        self.volume_slider = Slider("Volume", 250, 200, 300, value=67)
        self.fullscreen_checkbox = Checkbox("Fullscreen", 420, 250, checked=False)
        self.back_button = Button("Back", 300, 500, 200, 50)
        self.fullscreen_state = False
        self.keybinds = DEFAULT_KEYBINDS.copy()
        self.keybind_buttons = {}
        y = 320
        for action, key in self.keybinds.items():
            self.keybind_buttons[action] = Button(
                f"{KEYBIND_LABELS[action]}: {pygame.key.name(key).upper()}",
                300,
                y,
                200,
                40,
            )
            y += 50
        self.waiting_for_key = None
        if settings:
            self.set_settings(settings)

    def draw(self, screen):
        screen.fill(WHITE)
        title = BIG_FONT.render("Settings", True, BLACK)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))
        self.volume_slider.draw(screen, center=(WIDTH // 2, 200))
        self.fullscreen_checkbox.draw(screen, center=(WIDTH // 2, 250))
        y = 320
        for action, button in self.keybind_buttons.items():
            button.draw(screen, center=(WIDTH // 2, y))
            y += 50
        if self.waiting_for_key:
            info = SMALL_FONT.render(
                f"Press a key for {KEYBIND_LABELS[self.waiting_for_key]}",
                True,
                (200, 0, 0),
            )
            screen.blit(info, info.get_rect(center=(WIDTH // 2, 170)))
        self.back_button.draw(screen, center=(WIDTH // 2, 500))

    def handle_events(self, events):
        for event in events:
            if self.waiting_for_key:
                if event.type == pygame.KEYDOWN:
                    self.keybinds[self.waiting_for_key] = event.key
                    self.keybind_buttons[self.waiting_for_key].text = (
                        f"{KEYBIND_LABELS[self.waiting_for_key]}: {pygame.key.name(event.key).upper()}"
                    )
                    self.waiting_for_key = None
                continue
            self.volume_slider.update(event)
            toggled = self.fullscreen_checkbox.clicked(event)
            if toggled:
                if self.fullscreen_checkbox.checked:
                    pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    self.fullscreen_state = True
                else:
                    pygame.display.set_mode((WIDTH // 2, HEIGHT // 2), pygame.RESIZABLE)
                    self.fullscreen_state = False
            for action, button in self.keybind_buttons.items():
                if button.clicked(event):
                    self.waiting_for_key = action
            if self.back_button.clicked(event):
                return True  # tells menu to return
        return False

    def get_settings(self):
        return {
            "volume": self.volume_slider.value,
            "fullscreen": self.fullscreen_checkbox.checked,
            "keybinds": self.keybinds.copy(),
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
        if "keybinds" in settings:
            for action, key in settings["keybinds"].items():
                if action in self.keybinds:
                    self.keybinds[action] = key
                    self.keybind_buttons[action].text = (
                        f"{KEYBIND_LABELS[action]}: {pygame.key.name(key).upper()}"
                    )

    def save_settings(self, filepath="Data/Settings/settings.json"):
        import json, os

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.get_settings(), f, indent=4)

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
                self.save_settings()  # Save settings on exit
                running = False

            self.draw(screen)
            pygame.display.flip()

        return self.get_settings()
