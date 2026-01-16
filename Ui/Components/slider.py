import pygame
from Skripte.constants import BLACK, GRAY

FONT = pygame.font.SysFont(None, 36)


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
