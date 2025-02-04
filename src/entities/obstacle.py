import pygame


class Obstacle:

    def __init__(self, position: pygame.Vector2, size: pygame.Vector2, color: pygame.Color, image_path: str = None):

        """
        :param position: The position where the obstacle will be drawn
        :param size: The size of the obstacle
        :param color: The color overlay of the obstacle
        :param image_path: The path to the image of the obstacle
        """

        self.position = position
        self.size = size
        self.color = color
        self.image_path = image_path
        self.rect = pygame.Rect(self.position, self.size)

        if image_path:
            self._image = pygame.image.load(image_path).convert_alpha()
            self._image = pygame.transform.smoothscale(self._image, size)

    def draw(self, surface: pygame.Surface):

        """
        Draws the obstacle on the specified surface.
        :param surface: The surface to draw the obstacle on.
        """

        if self._image:
            surface.blit(self._image, self.position)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
