import pygame
import math


class Terrain:
    def __init__(self, terrain_type: str, vertices: list):
        """
        Initializes the terrain zone.

        :param terrain_type: Type of the terrain (e.g., 'green', 'fairway', 'bunker', 'lake').
        :param vertices: List of world coordinate points (tuples or Vector2) that define the terrain zone polygon.
        """

        self.terrain_type = terrain_type
        self.points = [pygame.Vector2(p) for p in vertices]

        if len(self.points) < 3:
            raise ValueError("Terrain polygon must have at least three points.")

        # self.original_points = self.points.copy() # Not currently used

        min_x = min(point.x for point in self.points)
        min_y = min(point.y for point in self.points)
        max_x = max(point.x for point in self.points)
        max_y = max(point.y for point in self.points)

        width = max_x - min_x
        height = max_y - min_y
        self.rect = pygame.Rect(min_x, min_y, width, height)

        # Surface de collision des polygones
        # Ensure width/height are at least 1 for surface creation
        surf_w = math.ceil(width) if width > 0 else 1
        surf_h = math.ceil(height) if height > 0 else 1
        self.collision_surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        shifted_points = [(p.x - min_x, p.y - min_y) for p in self.points]
        pygame.draw.polygon(self.collision_surface, (255, 255, 255, 255), shifted_points)
        self.mask = pygame.mask.from_surface(self.collision_surface)

        friction_factor = {
            'green': 0.85,
            'fairway': 0.4,
            'bunker': 0.9,
            'lake': 0.95,
            'rocks': 0.5,
            'dirt': 0.6,
            'darkgreen': 0.5,
            'darkrocks': 0.4,
            'darkdirt': 0.7
        }
        self.friction = friction_factor.get(self.terrain_type, 0.5)

        bounce = {
            'green': 0.4,
            'fairway': 0.5,
            'bunker': 0.1,
            'lake': 0.05,
            'rocks': 0.7,
            'dirt': 0.3,
            'darkgreen': 0.4,
            'darkrocks': 0.6,
            'darkdirt': 0.2
        }
        self.bounce_factor = bounce.get(self.terrain_type, 0.4)

        self.colors = {
            'green': (62, 179, 62),
            'fairway': (85, 153, 74),
            'bunker': (218, 195, 154),
            'lake': (46, 118, 201),
            'rocks': (156, 151, 144),
            'dirt': (130, 99, 54),
            'darkgreen': (49, 110, 46),
            'darkrocks': (128, 128, 128),
            'darkdirt': (87, 59, 19)
        }
        self.draw_color = self.colors.get(self.terrain_type, (100, 100, 100))

    def apply_effects(self, ball):
        """
        Applies terrain-specific effects to the ball (e.g., friction, bounce).

        :param ball: The ball object interacting with the terrain.
        """
        print("TODO - Implement apply_effects function") # Original comment kept

    def draw_polygon(self, screen: pygame.Surface, camera_offset: pygame.Vector2):
        """
        Draws the terrain zone on the specified surface with rotation.
        :param screen: The main draw surface to draw the terrain on.
        :param camera_offset: The camera's top-left world coordinate.
        """
        screen_points = [(p.x - camera_offset.x, p.y - camera_offset.y) for p in self.points]
        screen_rect = self.rect.move(-camera_offset.x, -camera_offset.y)

        if screen_rect.colliderect(screen.get_rect()):
             pygame.draw.polygon(screen, self.draw_color, screen_points)

    # shift_poly removed
    # update removed