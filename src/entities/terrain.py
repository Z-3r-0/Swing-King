import pygame


class Terrain:
    def __init__(self, terrain_type: str, position: pygame.Vector2, size: pygame.Vector2, rotation: float,
                 friction: float,
                 bounce_factor: float):
        """
        Initializes the terrain zone.

        :param terrain_type: Type of the terrain (e.g., 'green', 'fairway', 'bunker', 'lake').
        :param position: (x, y) position of the top-left corner of the terrain area.
        :param size: (width, height) of the terrain zone.
        :param friction: Friction coefficient affecting the ball's speed.
        :param bounce_factor: Determines how much the ball bounces (0 = no bounce, 1 = full bounce).
        """

        self.terrain_type = terrain_type
        self.position = position
        self.size = size
        self.rotation = rotation
        self.friction = friction
        self.bounce_factor = bounce_factor
        self.position_constant = position  # Constant of position at the start

    def apply_effects(self, ball):
        """
        Applies terrain-specific effects to the ball (e.g., friction, bounce).

        :param ball: (Ball): The ball object interacting with the terrain.
        """
        print("TODO - Implement apply_effects function")

    def check_collision(self, other):
        """
        Checks if the ball is currently colliding with the terrain zone.

        :param other: The other object to check for collision.

        :return: True if another object is in contact with the terrain, False otherwise.
        """
        # TODO: Check if we need to change this value with the position constant
        x, y = self.position
        width, height = self.size

        if (x <= other.position.x <= x + width) and (y <= other.position.y <= y + height):
            return True
        return False

    def draw(self, surface):
        """
        Draws the terrain zone on the specified surface with rotation.
        :param surface: The main display surface to draw the terrain on.
        """


        colors = {
            'green': (34, 139, 34),
            'fairway': (60, 179, 113),
            'bunker': (194, 178, 128),
            'lake': (30, 144, 255)
        }
        color = colors.get(self.terrain_type, (255, 255, 255))

        # Create a temporary surface with per-pixel alpha (transparency)
        temp_surface = pygame.Surface((int(self.size.x), int(self.size.y)), pygame.SRCALPHA)

        # Fill the temporary surface with the desired color.
        temp_surface.fill(color)

        rotated_surface = pygame.transform.rotate(temp_surface, self.rotation)

        # To ensure the terrain rotates around its center, get the rect of the rotated surface
        # and set its center to the center of the original terrain rectangle.
        original_center = (self.position.x + self.size.x / 2, self.position.y + self.size.y / 2)
        rotated_rect = rotated_surface.get_rect(center=original_center)

        # Final blit
        surface.blit(rotated_surface, rotated_rect.topleft)
