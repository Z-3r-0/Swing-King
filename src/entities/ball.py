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
        self.visual_radius = self.radius * self.scale_value
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
    def _update_mask_surface(self):
        """Helper to redraw circle on surface and update mask."""
        self.surface.fill((0, 0, 0, 0))  # Clear surface
        pygame.draw.circle(self.surface, (255, 255, 255),
                           (int(self.visual_radius), int(self.visual_radius)),
                           int(self.visual_radius))
        self.mask = pygame.mask.from_surface(self.surface)
    def draw(self, surface, position_cam: pygame.Vector2 = pygame.Vector2(0, 0)):
        """
        Draws the ball on the specified surface.

        :param surface: The surface to draw the ball on.
        :return:
        """
        draw_pos_x = self.position.x - position_cam.x - self.radius * self.scale_value
        draw_pos_y = self.position.y - position_cam.y - self.radius * self.scale_value
        surface.blit(self.image, (draw_pos_x, draw_pos_y))
        self._update_mask_surface()
