import pygame
from Skripte.constants import BLACK, GRAY, FONT


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
