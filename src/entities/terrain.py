import pygame


class Terrain:
    def __init__(self, screen, size: tuple, color: pygame.Color, image_path: str = None):
        self._screen = screen
        self._size = size
        self._color = color
        self._image_path = image_path

        if self._image_path:
            self._image = pygame.image.load(self._image_path).convert()
            self._image = pygame.transform.scale(self._image, self._size)
        else:
            self._image = None

    def draw(self):
        if self._image:
            self._screen.blit(self._image, (0, 0))
        else:
            self._screen.fill(self._color)

        pygame.display.update()



