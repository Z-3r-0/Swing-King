from math import floor
import pygame


class Ball:

    def __init__(self, screen, position: tuple, diameter: float, mass: float, color: pygame.Color, image_path: str = None):
        self._screen = screen
        self._position = pygame.math.Vector2(position)
        self._velocity = pygame.math.Vector2(0, 0)
        self._acceleration = pygame.math.Vector2(0, 0)
        self._diameter = floor(diameter)
        self._rayon = self._diameter*7/2
        self._color = color
        self._mass = mass
        self._is_moving = False

        self._image_path = image_path

        if self._image_path:
            self._image = pygame.image.load(image_path).convert_alpha()
            self._image = pygame.transform.smoothscale(self._image, (
                self._diameter * 7, self._diameter * 7))  # Arbitrary 7 scale value

    def draw(self, surface):

        """
        Draws the ball on the specified surface.
        :param surface: The surface to draw the ball on.
        :return:
        """

        surface.blit(self._image, (self._position.x-self._rayon, self._position.y-self._rayon))
        pygame.display.update()
