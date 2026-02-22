import pygame


class BackgroundManager:
    def __init__(self):
        self.factors = {
            4: 0.01,
            3: 0.05,
            2: 0.4,
            1: 0.7,
            0: 1.0,
            -1: 1.3
        }

    def draw_layer(self, screen, decorations, cam_offset, layer_index):
        factor = self.factors.get(layer_index, 1.0)

        for deco in decorations:
            if layer_index == 4:

                off_x = int(cam_offset.x * factor)
                off_y = int(cam_offset.y * factor)
                screen.blit(deco.image, (deco.rect.x - off_x, deco.rect.y - off_y))
            else:
                off_x = int(cam_offset.x * factor)
                off_y = int(cam_offset.y * factor)
                deco.draw(screen, off_x, off_y)
