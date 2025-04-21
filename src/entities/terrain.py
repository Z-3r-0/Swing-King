import pygame
import math


class Terrain:
    def __init__(self, terrain_type: str, vertices: list):
        """
        Initializes the terrain zone.

        :param terrain_type: Type of the terrain (e.g., 'green', 'fairway', 'bunker', 'lake').
        :param vertices: List of points that define the terrain zone.
        """

        self.terrain_type = terrain_type
        self.points = vertices

        # We need at least 2 points to form a closed shape
        if len(vertices) < 2:
            raise ValueError("Terrain must have at least two points.")

        self.original_points = self.points.copy()
        self.rect = pygame.Rect(self.points[0][0], self.points[0][1], 0, 0)

        self.friction = {
            'green': 0.1,
            'fairway': 0.1,
            'bunker': 0.1,
            'lake': 0.1
        }

        self.bounce_factor = {
            'green': 0.1,
            'fairway': 0.1,
            'bunker': 0.1,
            'lake': 0.1
        }

    def apply_effects(self, ball):
        """
        Applies terrain-specific effects to the ball (e.g., friction, bounce).

        :param ball: The ball object interacting with the terrain.
        """
        print("TODO - Implement apply_effects function")

    def draw_polygon(self, screen: pygame.Surface):
        """
        Draws the terrain zone on the specified surface with rotation.
        :param surface: The main draw surface to draw the terrain on.
        """

        colors = {
        'green': (62, 179, 62),  # @Lucas ici pour la couleur des terrains
        'fairway': (62, 133, 54),
        'bunker': (255, 197, 106),
        'lake': (46, 118, 201),
        'rocks': (156, 151, 144),
        'dirt': (130, 99, 54),
        'darkgreen': (49, 110, 46),
        'darkrocks': (128, 128, 128),
        'darkdirt': (87, 59, 19)
        }
        color = colors.get(self.terrain_type, (255, 255, 255))
        if len(self.points) > 2:
            pygame.draw.polygon(screen, color, self.points)

    def shift_poly(self, shift: pygame.Vector2):
        """
            Shifts the polygon by the shift_poly vector, such as (0, -10)
            DO NOT GIVE COORDINATES OF CAMERA
        """
        self.points = [(point[0] - shift.x, point[1] - shift.y) for point in self.points]

    def update(self, screen: pygame.Surface, camera_movement: pygame.Vector2):
        self.shift_poly(camera_movement)
        self.draw_polygon(screen)
