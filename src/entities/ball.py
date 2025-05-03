from math import floor
import pygame


class Ball:

    def __init__(self, position: pygame.Vector2, diameter: float, mass: float, color: pygame.Color, image_path: str = None):
        self.position = position
        self.old_position = position
        self.start_position = position

        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)

        self.scale_value = 7
        self.diameter = floor(diameter) # * self.scale_value
        self.radius = self.diameter / 2 # * self.scale_value / 2
        self.rect = pygame.Rect((self.position.x - self.radius * self.scale_value), (self.position.y - self.radius * self.scale_value), (self.radius * self.scale_value)*2, (self.radius * self.scale_value)*2)



        self.color = color
        self.mass = mass

        self.is_moving = False
        self.is_colliding = False
        self.image_path = image_path

        self.force = 0
        self.angle = 0
        self.velocity = pygame.Vector2(0, 0)

        if self.image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.smoothscale(self.image, (
                self.diameter * self.scale_value, self.diameter * self.scale_value))  # Arbitrary self.scale_value * 7 scale value
        self.surface = pygame.Surface((self.diameter * self.scale_value, self.diameter * self.scale_value), pygame.SRCALPHA)
        self.mask = pygame.mask.from_surface(self.surface)

    def draw(self, surface):
        """
        Draws the ball on the specified surface.

        :param surface: The surface to draw the ball on.
        :return:
        """

        surface.blit(self.image, (self.position.x - self.radius * self.scale_value, self.position.y - self.radius * self.scale_value))
    def get_speed(self,pos_camera_x: float = 0, fps: float = (1/60)):
        """
        Returns the speed of the ball.
        :return: The speed of the ball
        """
        old_position = self.old_position
        new_position = self.position + pygame.Vector2(pos_camera_x, 0)
        distance = new_position.distance_to(old_position)
        return distance / fps

    def update_position(self, new_position: pygame.Vector2):
        """
        Updates the position of the ball.
        :param new_position: The new position of the ball.
        :return:
        """
        self.surface.fill((0, 0, 0, 0))  # Clear surface
        pygame.draw.circle(self.surface, (255, 255, 255),
                           (self.radius * self.scale_value, self.radius * self.scale_value),
                           self.radius * self.scale_value)
        self.mask = pygame.mask.from_surface(self.surface)

        self.old_position = self.position
        self.position = new_position
        self.rect = pygame.Rect((self.position.x - self.radius * self.scale_value), (self.position.y - self.radius * self.scale_value), (self.radius * self.scale_value)*2, (self.radius * self.scale_value)*2)

    def shift_out_of_collision(self, poly_mask: pygame.Mask, poly_rect: pygame.Rect,
                               normal: pygame.Vector2, max_push: int = 10) -> bool:
        """
        Tente de repousser la balle hors de la collision le long de la normale.
        :param poly_mask: mask du polygone
        :param poly_rect: rect du polygone
        :param normal: normale unitaire au point d'impact
        :param max_push: distance max (en pixels) à tester
        :return: True si la balle a pu sortir, False sinon
        """
        for i in range(1, max_push + 1):
            shift = normal * i
            # On déplace temporairement
            self.shift_position(shift)
            offset = (self.rect.left - poly_rect.left,
                      self.rect.top - poly_rect.top)
            # Si plus de collision, on garde ce déplacement
            if not poly_mask.overlap(self.mask, offset):
                return True
            # Sinon on annule et on teste un push plus grand
            self.shift_position(-shift)
        return False

    def shift_position(self, shift:pygame.Vector2):
        """
        Shifts the position of the ball.
        :param shift: The shift vector.
        :return:
        """
        self.surface.fill((0, 0, 0, 0))  # Clear surface
        pygame.draw.circle(self.surface, (255, 255, 255),
                           (self.radius * self.scale_value, self.radius * self.scale_value),
                           self.radius * self.scale_value)
        self.mask = pygame.mask.from_surface(self.surface)

        self.position += shift
        self.rect = pygame.Rect((self.position.x - self.radius * self.scale_value), (self.position.y - self.radius * self.scale_value), (self.radius * self.scale_value)*2, (self.radius * self.scale_value)*2)
    def check_collision(self, element: pygame.Rect):
        """
        Checks if the ball is currently colliding with the element.
        :param element: The element to check for collision.
        :return: True if the ball is in contact with the element, False otherwise.
        """
        if element.colliderect(pygame.Rect(self.position.x - self.radius * self.scale_value, self.position.y - self.radius * self.scale_value, self.radius * self.scale_value, self.radius * self.scale_value)):
            return True
        return False