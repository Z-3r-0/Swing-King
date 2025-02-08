from math import floor
import pygame


class Ball:

    def __init__(self, position: pygame.Vector2, diameter: float, mass: float, color: pygame.Color, image_path: str = None):
        self.position = position
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.diameter = floor(diameter)
        self.rayon = self.diameter * 7 / 2
        self.color = color
        self.mass = mass
        self.is_moving = False

        self.image_path = image_path

        if self.image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.smoothscale(self.image, (
                self.diameter * 7, self.diameter * 7))  # Arbitrary 7 scale value

    def draw_ball(self, surface):
        """
        Draws the ball on the specified surface.

        Named draw_ball instead of draw because draw is a basic function of pygame, so to not intefere we needed to change it
        :param surface: The surface to draw the ball on.
        :return:
        """

        surface.blit(self.image, (self.position.x - self.rayon, self.position.y - self.rayon))
