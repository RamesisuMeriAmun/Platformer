import pygame

CHAR_WIDTH = 16
CHAR_HEIGHT = 16
CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!?.,:"

pygame.init()
image = pygame.image.load("Data/Images/Menu/Text/font-white.png")
print(image.get_width(), image.get_height())
print("chars:", len(CHARS))
print(
    "cells:",
    (image.get_width() // CHAR_WIDTH) * (image.get_height() // CHAR_HEIGHT),
)
