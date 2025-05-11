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

        width = max_x - min_x
        height = max_y - min_y

        self.rect = pygame.Rect(min_x, min_y, width, height)
        self.surface_collision = pygame.Surface((width, height), pygame.SRCALPHA)
        shifted_points = [(p[0] - min_x, p[1] - min_y) for p in self.points]
        pygame.draw.polygon(self.surface_collision, (255, 255, 255), shifted_points)
        self.mask = pygame.mask.from_surface(self.surface_collision)

        shifted_points = [(point[0] - min_x, point[1] - min_y) for point in self.points]
        pygame.draw.polygon(self.surface_collision, (255, 255, 255), shifted_points)

        self.mask = pygame.mask.from_surface(self.surface_collision)
        friction_factor = {
            'green': 0.2,
            'fairway': 0.3,
            'bunker': 0.7,
            'lake': -1,
            'rocks': 0.25,
            'dirt': 0.4,
            'darkgreen': 0.4,
            'darkrocks': 0.3,
            'darkdirt': 0.6}
        self.friction = friction_factor[self.terrain_type]
        bounce = {
            'green': 0.4,  # Moderate-low bounce, promotes roll.
            'fairway': 0.5,  # Standard moderate bounce.
            'bunker': 0.15,  # Very low bounce, absorbs energy.
            'lake': 0.1,  # Minimal bounce.
            'rocks': 0.7,  # High bounce.
            'dirt': 0.35,  # Moderate-low bounce.
            'darkgreen': 0.3,  # Low bounce (like rough).
            'darkrocks': 0.65,  # High bounce, slightly less than clean rocks.
            'darkdirt': 0.3  # Low bounce (softer/looser dirt).
        }
        self.bounce_factor = bounce[self.terrain_type]

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