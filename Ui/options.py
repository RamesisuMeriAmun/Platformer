import pygame
from Skripte.constants import WIDTH, HEIGHT

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

FONT = pygame.font.SysFont(None, 36)
BIG_FONT = pygame.font.SysFont(None, 56)


class Button:
    def __init__(self, text, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen, center=None):
        if center:
            self.rect.center = center
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        text = FONT.render(self.text, True, BLACK)
        screen.blit(text, text.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


class Slider:
    def __init__(self, label, x, y, w, value=50):
        self.label = label
        self.rect = pygame.Rect(x, y, w, 10)
        self.handle = pygame.Rect(x + (value / 100) * w - 5, y - 5, 10, 20)
        self.value = value
        self.dragging = False

    def draw(self, screen, center=None):
        if center:
            self.rect.center = center
            self.handle.centery = self.rect.centery
        label_text = FONT.render(self.label, True, BLACK)
        screen.blit(label_text, (self.rect.x, self.rect.y - 30))

        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        pygame.draw.rect(screen, BLACK, self.handle)

        value_text = FONT.render(f"{self.value}%", True, BLACK)
        screen.blit(value_text, (self.rect.x + self.rect.w + 10, self.rect.y - 10))

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.handle.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.handle.centerx = max(
                self.rect.x, min(event.pos[0], self.rect.x + self.rect.w)
            )
            self.value = int(((self.handle.centerx - self.rect.x) / self.rect.w) * 100)


class Checkbox:
    def __init__(self, label, x, y, checked=False):
        self.label = label
        self.rect = pygame.Rect(x, y, 20, 20)
        self.checked = checked

    def draw(self, screen, center=None):
        # if center:
        #     self.rect.center = center
        label_text = FONT.render(self.label, True, BLACK)
        screen.blit(label_text, (self.rect.x + 30, self.rect.y - 2))

        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        if self.checked:
            pygame.draw.line(
                screen,
                BLACK,
                (self.rect.x + 4, self.rect.y + 10),
                (self.rect.x + 8, self.rect.y + 16),
                2,
            )
            pygame.draw.line(
                screen,
                BLACK,
                (self.rect.x + 8, self.rect.y + 16),
                (self.rect.x + 16, self.rect.y + 4),
                2,
            )

    def clicked(self, event):
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        ):
            self.checked = not self.checked
            return True
        return False


def settings_page(screen, events):
    # Use static variables to persist state across calls
    if not hasattr(settings_page, "volume_slider"):
        settings_page.volume_slider = Slider("Volume", 250, 200, 300, value=70)
    if not hasattr(settings_page, "fullscreen_checkbox"):
        settings_page.fullscreen_checkbox = Checkbox(
            "Fullscreen", 420, 250, checked=False
        )
    if not hasattr(settings_page, "back_button"):
        settings_page.back_button = Button("Back", 300, 350, 200, 50)
    if not hasattr(settings_page, "fullscreen_state"):
        settings_page.fullscreen_state = False

    volume_slider = settings_page.volume_slider
    fullscreen_checkbox = settings_page.fullscreen_checkbox
    back_button = settings_page.back_button

    screen.fill(WHITE)

    title = BIG_FONT.render("Settings", True, BLACK)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))
    volume_slider.draw(screen, center=(WIDTH // 2, 200))
    fullscreen_checkbox.draw(screen, center=(WIDTH // 2, 250))
    back_button.draw(screen, center=(WIDTH // 2, 350))

    for event in events:
        volume_slider.update(event)
        toggled = fullscreen_checkbox.clicked(event)
        if toggled:
            if fullscreen_checkbox.checked:
                pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                settings_page.fullscreen_state = True
            else:
                pygame.display.set_mode((WIDTH, HEIGHT))
                settings_page.fullscreen_state = False
        if back_button.clicked(event):
            return True  # tells menu to return

    return False
