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
        surface = pygame.display.get_surface()
        if surface:
            self.width, self.height = surface.get_size()
        else:
            self.width, self.height = WIDTH // 2, HEIGHT // 2

        self.volume_slider = None
        self.fullscreen_checkbox = None
        self.back_button = None
        self.fullscreen_state = False
        self.keybinds = DEFAULT_KEYBINDS.copy()
        self.keybind_buttons = {}
        self.rebuild_layout()
        self.waiting_for_key = None
        if settings:
            self.set_settings(settings)

    def rebuild_layout(self):
        center_x = self.width // 2
        top_y = max(80, int(self.height * 0.14))
        slider_y = top_y + int(self.height * 0.12)
        checkbox_y = slider_y + 55
        keys_start_y = checkbox_y + 70
        button_width = max(180, min(320, int(self.width * 0.24)))
        button_height = 50

        self.volume_slider = Slider("Volume", 0, 0, button_width, value=67)
        self.fullscreen_checkbox = Checkbox("Fullscreen", 0, 0, checked=False)
        self.back_button = Button("Back", 0, 0, button_width, button_height)

        self.layout_title_y = top_y
        self.layout_slider_y = slider_y
        self.layout_checkbox_y = checkbox_y
        self.layout_keys_start_y = keys_start_y
        self.layout_button_width = button_width
        self.layout_button_height = button_height

        self.keybind_buttons = {}
        y = keys_start_y
        for action, key in self.keybinds.items():
            self.keybind_buttons[action] = Button(
                f"{KEYBIND_LABELS[action]}: {pygame.key.name(key).upper()}",
                0,
                0,
                button_width,
                40,
            )
            y += 50

    def draw(self, screen):
        self.width, self.height = screen.get_size()
        screen.fill(WHITE)
        center_x = self.width // 2
        title = BIG_FONT.render("Settings", True, BLACK)
        screen.blit(title, title.get_rect(center=(center_x, self.layout_title_y)))
        self.volume_slider.draw(screen, center=(center_x, self.layout_slider_y))
        self.fullscreen_checkbox.draw(screen, center=(center_x, self.layout_checkbox_y))
        y = self.layout_keys_start_y
        for action, button in self.keybind_buttons.items():
            button.draw(screen, center=(center_x, y))
            y += 50
        if self.waiting_for_key:
            info = SMALL_FONT.render(
                f"Press a key for {KEYBIND_LABELS[self.waiting_for_key]}",
                True,
                (200, 0, 0),
            )
            screen.blit(
                info, info.get_rect(center=(center_x, self.layout_title_y + 70))
            )
        self.back_button.draw(screen, center=(center_x, self.height - 70))

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
            if event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.size
                pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                self.rebuild_layout()
            toggled = self.fullscreen_checkbox.clicked(event)
            if toggled:
                if self.fullscreen_checkbox.checked:
                    pygame.display.set_mode(
                        (self.width, self.height), pygame.FULLSCREEN
                    )
                    self.fullscreen_state = True
                else:
                    pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
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
            "window_size": [self.width, self.height],
            "keybinds": self.keybinds.copy(),
        }

    def set_settings(self, settings):
        volume_value = settings.get("volume", self.volume_slider.value)
        fullscreen_value = settings.get("fullscreen", self.fullscreen_checkbox.checked)
        window_size = settings.get("window_size")
        keybinds = settings.get("keybinds", {})

        if window_size and isinstance(window_size, list) and len(window_size) == 2:
            self.width, self.height = window_size

        self.rebuild_layout()

        self.volume_slider.value = volume_value
        self.volume_slider.handle.centerx = (
            self.volume_slider.rect.x + (volume_value / 100) * self.volume_slider.rect.w
        )
        self.fullscreen_checkbox.checked = fullscreen_value
        self.fullscreen_state = fullscreen_value

        for action, key in keybinds.items():
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
        running = True
        while running:
            screen = pygame.display.get_surface()
            if screen:
                self.width, self.height = screen.get_size()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.handle_events(events):
                self.save_settings()
                running = False

            screen = pygame.display.get_surface()
            self.draw(screen)
            pygame.display.flip()

        return self.get_settings()
