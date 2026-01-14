import pygame

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

FONT = pygame.font.SysFont(None, 36)
BIG_FONT = pygame.font.SysFont(None, 56)

class Button:
    def __init__(self, text, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen):
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


def settings_page(screen, events):
    back_button = Button("Back", 300, 350, 200, 50)

    screen.fill(WHITE)

    title = BIG_FONT.render("Settings", True, BLACK)
    screen.blit(title, title.get_rect(center=(400, 120)))

    back_button.draw(screen)

    for event in events:
        if back_button.clicked(event):
            return True  # tells menu to return

    return False