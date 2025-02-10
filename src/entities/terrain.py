import pygame


class Terrain:
    def __init__(self, terrain_type: str, position: pygame.Vector2, size: pygame.Vector2, rotation: float):
        """
        Initializes the terrain zone.

        :param terrain_type: Type of the terrain (e.g., 'green', 'fairway', 'bunker', 'lake').
        :param position: (x, y) position of the top-left corner of the terrain area.
        :param size: (width, height) of the terrain zone.
        :param rotation: Rotation angle of the terrain zone.
        """

        self.terrain_type = terrain_type
        self.position = position
        self.size = size
        self.rotation = rotation
        self.start_position = position  # Constant of position at the start
        self.rect = pygame.Rect(self.position, self.size)

        self.friction = {  # Purely random value, put here temporarily just for implementing purposes
            'green': 0.1,
            'fairway': 0.1,
            'bunker': 0.1,
            'lake': 0.1
        }

        self.bounce_factor = {  # Same
            'green': 0.1,
            'fairway': 0.1,
            'bunker': 0.1,
            'lake': 0.1
        }

    def apply_effects(self, ball):
        """
        Applies terrain-specific effects to the ball (e.g., friction, bounce).

        :param ball: (Ball): The ball object interacting with the terrain.
        """
        print("TODO - Implement apply_effects function")


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
