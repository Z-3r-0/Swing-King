import pygame


class Obstacle:


    def __init__(self, screen, position: pygame.Vector2, size: pygame.Vector2, color: pygame.Color, image_path: str = None):
        self._screen = screen
        self._position = position
        self._size = size
        self._color = color
        self._image_path = image_path
        self._rect = pygame.Rect(self._position, self._size)

        if image_path:
            self._image = pygame.image.load(image_path).convert_alpha()
            self._image = pygame.transform.smoothscale(self._image, size)

    def draw(self):
        if self._image:
            self._screen.blit(self._image, self._position)
        else:
            pygame.draw.rect(self._screen, self._color, self._rect)