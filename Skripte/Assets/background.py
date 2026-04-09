import pygame


class BackgroundManager:
    def __init__(self):
        self.factors = {4: 0.01, 3: 0.05, 2: 0.2, 1: 0.5, 0: 1.0, -1: 1.2}

    def draw_layer(self, screen, decorations, cam_offset, layer_index, scale=1.0):
        factor = self.factors.get(layer_index, 1.0)

        for deco in decorations:
            if layer_index == 4:

                off_x = cam_offset.x * factor
                off_y = cam_offset.y * factor
                deco.draw(screen, off_x, off_y, scale)
            else:
                off_x = cam_offset.x * factor
                off_y = cam_offset.y * factor
                deco.draw(screen, off_x, off_y, scale)
