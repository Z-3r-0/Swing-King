import pygame
import math


class Terrain:
    def __init__(self, terrain_type: str, vertices: list):
        """
        Initializes the terrain zone.

        :param terrain_type: Type of the terrain (e.g., 'green', 'fairway', 'bunker', 'lake').
        :param vertices: List of vertices that define the terrain zone.
        """

        self.terrain_type = terrain_type
        self.vertices = []

        screen_height = 600  # Adjust this based on your actual screen height

        # We need at least 2 points to form a closed shape
        if len(vertices) < 2:
            raise ValueError("Terrain must have at least two vertices.")

        # Create the extended polygon in the correct order
        lower_vertices = [(x, screen_height + 100) for x, y in vertices]  # New vertices below the screen

        for i in range(len(vertices) - 1):
            # Order is: A → A' → B' → B
            self.vertices.append(vertices[i])       # A
            self.vertices.append(lower_vertices[i]) # A'
            self.vertices.append(lower_vertices[i+1]) # B'
            self.vertices.append(vertices[i+1])     # B

        self.original_vertices = self.vertices.copy()
        self.start_position = self.vertices[0]
        self.rect = pygame.Rect(self.start_position[0], self.start_position[1], 0, 0)

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
        pygame.draw.polygon(surface, color, self.vertices)

    def position_update(self, camera_pos: pygame.Vector2):
        """
        Updates the terrain's position based on the camera's movement.
        """

        # Compute the offset due to camera movement
        offset_x = -camera_pos.x
        offset_y = -camera_pos.y

        # Apply the offset to all vertices
        self.vertices = [(x + offset_x, y + offset_y) for (x, y) in self.original_vertices]

        # Update the rect's position based on the first vertex
        self.rect.topleft = self.vertices[0]

