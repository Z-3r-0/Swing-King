from math import floor
import pygame


class Ball:

    def __init__(self, position: pygame.Vector2, diameter: float, mass: float, color: pygame.Color, image_path: str = None):
        self.position = position.copy()
        # self.old_position = position # Not used in current logic
        self.start_position = position.copy()

        self.velocity = pygame.Vector2(0, 0)
        # self.acceleration = pygame.Vector2(0, 0) # Not used

        self.scale_value = 7
        self.diameter = floor(diameter)
        self.radius = self.diameter / 2

        self.scaled_radius = self.radius * self.scale_value
        self.scaled_diameter = self.diameter * self.scale_value

        self.rect = pygame.Rect(
            self.position.x - self.scaled_radius,
            self.position.y - self.scaled_radius,
            self.scaled_diameter,
            self.scaled_diameter
        )

        self.color = color
        self.mass = mass

        # self.is_moving = False # Handled by Game class
        # self.is_colliding = False # Handled by Game class
        self.image_path = image_path
        self.image = None
        self.mask = None
        # self.surface = None # Not needed if mask is from image

        if self.image_path:
            try:
                self.original_image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.smoothscale(self.original_image, (self.scaled_diameter, self.scaled_diameter))
                self.mask = pygame.mask.from_surface(self.image)
            except pygame.error as e:
                print(f"Error loading ball image '{image_path}': {e}")
                self._create_fallback_surface()
        else:
             self._create_fallback_surface()

    def _create_fallback_surface(self):
        self.image = pygame.Surface((self.scaled_diameter, self.scaled_diameter), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.scaled_radius, self.scaled_radius), self.scaled_radius)
        self.mask = pygame.mask.from_surface(self.image)


    def draw(self, surface: pygame.Surface, camera_offset: pygame.Vector2):
        """
        Draws the ball on the specified surface, adjusted by camera offset.

        :param surface: The surface to draw the ball on.
        :param camera_offset: The camera's top-left world coordinate.
        """
        if self.image:
            screen_pos_x = self.position.x - self.scaled_radius - camera_offset.x
            screen_pos_y = self.position.y - self.scaled_radius - camera_offset.y
            surface.blit(self.image, (screen_pos_x, screen_pos_y))
        # No fallback drawing needed if _create_fallback_surface works

    def get_speed(self,pos_camera_x: float = 0, fps: float = (1/60)):
        """
        Returns the speed of the ball.
        :return: The speed of the ball
        """
        # This function seems problematic:
        # 1. Uses old_position which isn't reliably updated.
        # 2. Adds camera_x but not camera_y.
        # 3. Relies on fixed fps argument.
        # Better approach: return self.velocity.length()
        # old_position = self.old_position
        # new_position = self.position + pygame.Vector2(pos_camera_x, 0)
        # distance = new_position.distance_to(old_position)
        # return distance / fps
        return self.velocity.length() # Return current speed magnitude

    def update_position(self, new_position: pygame.Vector2):
        """
        Updates the position of the ball and its rect.
        :param new_position: The new world position of the ball's center.
        """
        self.position = new_position.copy()
        self.rect.center = self.position
        # No need to recreate mask/surface on position update

    def shift_position(self, shift:pygame.Vector2):
        """
        Shifts the position of the ball by a given vector and updates its rect.
        :param shift: The vector to add to the current position.
        """
        self.position += shift
        self.rect.center = self.position
        # No need to recreate mask/surface on position update

    # shift_out_of_collision removed as penetration is handled directly

    def check_collision(self, element_rect: pygame.Rect):
        """
        Checks if the ball's bounding box is currently colliding with the element's rect.
        :param element_rect: The pygame.Rect of the element to check against.
        :return: True if the bounding boxes overlap, False otherwise.
        """
        # The original check was incorrect (used ball pos/radius instead of rect)
        return self.rect.colliderect(element_rect)