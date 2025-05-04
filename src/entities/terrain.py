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

        bounce = {
            'green': 0.40,      # Lower bounce than fairway, promotes roll
            'fairway': 0.50,    # Standard moderate bounce
            'bunker': 0.15,     # Very low bounce, absorbs energy
            'lake': 0.10,       # Minimal bounce
            'rocks': 0.70,      # High bounce
            'dirt': 0.35,       # Moderate-low bounce
            'darkgreen': 0.35,  # Low bounce (like rough)
            'darkrocks': 0.65,  # High bounce, slightly less than clean rocks
            'darkdirt': 0.30    # Low bounce (softer/looser dirt)
        }
        self.bounce_factor = bounce.get(self.terrain_type, 0.4) # Default to 0.4 if type unknown

        # --- IMPORTANT ---
        # Don't forget friction! Realistic behavior needs both.
        friction_factor = {
            'green': 0.85,      # Low friction (high value means less speed reduction) -> promotes roll
            'fairway': 0.70,    # Moderate friction
            'bunker': 0.40,     # High friction (low value means more speed reduction) -> slows ball quickly
            'lake': 0.30,       # Very high friction/drag
            'rocks': 0.80,      # Low friction (less rolling resistance)
            'dirt': 0.60,       # Moderate-high friction
            'darkgreen': 0.55,  # Higher friction than fairway (rough)
            'darkrocks': 0.75,  # Low friction
            'darkdirt': 0.50    # High friction
        }
        # NOTE: Your previous friction values seemed inverted if 1.0 meant no friction.
        # I've adjusted them assuming a factor applied to tangential velocity like:
        # new_vt = vt * friction_factor (where friction_factor is closer to 1 for less friction)
        # OR if your physics uses it like: new_vt = vt * (1.0 - friction_coefficient)
        # then the values should be low for low friction (green) and high for high friction (bunker).
        # Double-check how friction is applied in src/physics.py!
        # Let's assume your physics uses: new_vt = vt * (1 - fric_coeff)
        # Then the coefficients should be:
        friction_coeffs = {
             'green': 0.15,      # Low friction coeff -> less speed loss
             'fairway': 0.30,
             'bunker': 0.70,     # High friction coeff -> more speed loss
             'lake': 0.85,
             'rocks': 0.20,
             'dirt': 0.40,
             'darkgreen': 0.50,  # Rough has higher friction
             'darkrocks': 0.25,
             'darkdirt': 0.60
        }
        # Choose the correct dictionary based on your physics implementation!
        # Assuming the second model (1.0 - coeff):
        self.friction = friction_coeffs.get(self.terrain_type, 0.3) # Default friction coeff

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