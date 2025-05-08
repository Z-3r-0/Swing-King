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

        # Calculate the rect (bounding box) of the polygon
        # Find min/max x and y coordinates
        min_x = min(point[0] for point in self.points)
        min_y = min(point[1] for point in self.points)
        max_x = max(point[0] for point in self.points)
        max_y = max(point[1] for point in self.points)

        # Calculate width and height
        width = max_x - min_x
        height = max_y - min_y

        # Create and return the Rect
        self.rect = pygame.Rect(min_x, min_y, width, height)

        # Surface de collision des polygones
        self.surface_collision = pygame.Surface((width, height), pygame.SRCALPHA)
        # Convert points relative to the surface
        shifted_points = [(p[0] - min_x, p[1] - min_y) for p in self.points]
        pygame.draw.polygon(self.surface_collision, (255, 255, 255), shifted_points)
        self.mask = pygame.mask.from_surface(self.surface_collision)

        # Dessiner le polygone sur la surface de collision
        shifted_points = [(point[0] - min_x, point[1] - min_y) for point in self.points]
        pygame.draw.polygon(self.surface_collision, (255, 255, 255), shifted_points)

        # Générer le masque à partir de la surface de collision
        self.mask = pygame.mask.from_surface(self.surface_collision)
        friction_factor = {
            'green': 0.5,
            'fairway': 0.2,
            'bunker': 0.1,
            'lake': 0.1,
            'rocks': 0.1,
            'dirt': 0.1,
            'darkgreen': 0.1,
            'darkrocks': 0.1,
            'darkdirt': 0.1
        }
        self.friction = friction_factor[self.terrain_type]
        bounce = {
            'green': 0.5,
            'fairway': 0.5,
            'bunker': 0.1,
            'lake': 0.1,
            'rocks': 0.1,
            'dirt': 0.1,
            'darkgreen': 0.1,
            'darkrocks': 0.1,
            'darkdirt': 0.1
        }
        self.bounce_factor = bounce[self.terrain_type]
    def apply_effects(self, ball):
        """
        Applies terrain-specific effects to the ball (e.g., friction, bounce).

        :param ball: The ball object interacting with the terrain.
        """
        print("TODO - Implement apply_effects function")

    def draw_polygon(self, screen: pygame.Surface, points: list = None):
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
        if points is None:
            points = self.points
        if len(points) > 2:
            pygame.draw.polygon(screen, color, points)

    def shift_poly(self, shift: pygame.Vector2):
        """
            Shifts the polygon by the shift_poly vector, such as (0, -10)
            DO NOT GIVE COORDINATES OF CAMERA
        """
        self.points = [(point[0] - shift.x, point[1] - shift.y) for point in self.points]

    def update(self, screen: pygame.Surface, camera_movement: pygame.Vector2):
        self.shift_poly(camera_movement)
        self.draw_polygon(screen)