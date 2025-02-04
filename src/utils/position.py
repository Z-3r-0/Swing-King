import pygame


def invert_y(screen: pygame.surface, y: int):
    return -y + screen.get_height()