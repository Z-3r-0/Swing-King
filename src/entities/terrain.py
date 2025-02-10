import pygame
import math


class Terrain:
    def __init__(self, terrain_type: str, position: pygame.Vector2, size: pygame.Vector2, rotation: float):
        """
        Initializes the terrain zone.

        :param terrain_type: Type of the terrain (e.g., 'green', 'fairway', 'bunker', 'lake').
        :param position: (x, y) position of the top-left corner of the terrain area.
        :param size: (width, height) of the terrain zone.
        :param rotation: Rotation angle of the terrain zone (in degrees).
        """
        self.terrain_type = terrain_type
        self.position = position
        self.size = size
        self.rotation = -rotation
        self.start_position = position  # Constant of position at the start
        self.rect = pygame.Rect(self.position, self.size)

        self.friction = {  # Purely random values for implementing purposes
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

        # Calculate and store the rotated polygon once
        self.polygon = self._calculate_polygon()

    def _calculate_polygon(self):
        """
        Computes the vertices of the terrain's rectangle after applying the rotation.

        :return: A list of (x, y) tuples representing the rotated rectangle's corners.
        """
        # Get the center of the rectangle
        center = self.rect.center

        # Define the four corners of the original rectangle
        corners = [
            self.rect.topleft,
            self.rect.topright,
            self.rect.bottomright,
            self.rect.bottomleft
        ]

        # Calculate the rotated positions for each corner
        rotated_corners = []
        cos_theta = math.cos(math.radians(self.rotation))
        sin_theta = math.sin(math.radians(self.rotation))
        for corner in corners:
            # Translate the corner so that the center becomes the origin
            translated_x = corner[0] - center[0]
            translated_y = corner[1] - center[1]

            # Rotate the point using the 2D rotation matrix
            rotated_x = translated_x * cos_theta - translated_y * sin_theta
            rotated_y = translated_x * sin_theta + translated_y * cos_theta

            # Translate back to the original center position
            final_x = rotated_x + center[0]
            final_y = rotated_y + center[1]
            rotated_corners.append((final_x, final_y))

        return rotated_corners

    def update_polygon(self, position: pygame.Vector2 = None, rotation: float = None):
        """
        Updates the polygon attribute. Call this method when changing the terrain's
        position or rotation to recalculate the polygon.

        :param position: Optional new position (top-left corner) as pygame.Vector2.
        :param rotation: Optional new rotation angle (in degrees).
        """
        self.position = position
        self.rect.topleft = self.position
        self.rotation = rotation

        # Recalculate and update the stored polygon
        self.polygon = self._calculate_polygon()

    def apply_effects(self, ball):
        """
        Applies terrain-specific effects to the ball (e.g., friction, bounce).

        :param ball: The ball object interacting with the terrain.
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
        pygame.draw.polygon(surface, color, self.polygon)

    def position_update(self, position: pygame.Vector2, camera: pygame.Vector2):
        """
        Updates the position of the terrain zone (and its polygon) based on the camera position.

        :param position: The new position of the terrain zone.
        :param camera: The camera position.
        """
        self.position = position - camera
        self.rect.topleft = self.position
        # Update the polygon since the terrain's position has changed.
        self.polygon = self._calculate_polygon()
