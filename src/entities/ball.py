from math import floor
import pygame


class Ball:

    def __init__(self, position: tuple, diameter: float, mass: float, color: pygame.Color, image_path: str = None):
        self.position = pygame.math.Vector2(position)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.diameter = floor(diameter)
        self.rayon = self.diameter * 7 / 2
        self.color = color
        self.mass = mass
        self.is_moving = False

        self._image_path = image_path

        if self._image_path:
            self._image = pygame.image.load(image_path).convert_alpha()
            self._image = pygame.transform.smoothscale(self._image, (
                self.diameter * 7, self.diameter * 7))  # Arbitrary 7 scale value

    def draw(self, surface):

        """
        Draws the ball on the specified surface.
        :param surface: The surface to draw the ball on.
        :return:
        """

        surface.blit(self._image, (self.position.x - self.rayon, self.position.y - self.rayon))
