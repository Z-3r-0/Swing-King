import math
import pygame

class Ball:

    MAX_COLLISION_TOGGLES = 6 # Number of rapid back-and-forth collisions before stopping

    def __init__(self, position: pygame.Vector2, diameter: float, mass: float, color: pygame.Color, image_path: str = None):
        self.start_position = position.copy()
        self.position = position.copy()
        self.velocity = pygame.Vector2(0, 0)

        # Physical properties
        self.diameter = math.floor(diameter)
        self.radius = self.diameter / 2
        self.mass = mass # Currently unused in simple physics, but good to have

        # Scaling for display
        self.scale_value = 7 # Pixels per meter (adjust as needed for visual scale)
        self.scaled_radius = self.radius * self.scale_value
        self.scaled_diameter = self.diameter * self.scale_value

        # Pygame Rect for broad-phase collision and drawing position
        self.rect = pygame.Rect(
            self.position.x - self.scaled_radius,
            self.position.y - self.scaled_radius,
            self.scaled_diameter,
            self.scaled_diameter
        )

        # Visuals
        self.color = color
        self.image_path = image_path
        self.original_image = None
        self.image = None # Scaled image for drawing
        self.mask = None  # Mask for pixel-perfect collision (if needed, currently using geometric)

        self._load_and_scale_image()

        # State variables
        self.is_moving = False

        # Collision state tracking (for anti-stuck logic)
        self.last_collided_object_id = None
        self.collision_toggle_count = 0


    def _load_and_scale_image(self):
        """Loads the ball image, scales it, and creates a mask."""
        try:
            if self.image_path:
                self.original_image = pygame.image.load(self.image_path).convert_alpha()
                self.image = pygame.transform.smoothscale(
                    self.original_image,
                    (int(self.scaled_diameter), int(self.scaled_diameter))
                )
                self.mask = pygame.mask.from_surface(self.image)
            else:
                raise ValueError("No image path provided")
        except (pygame.error, FileNotFoundError, ValueError) as e:
            print(f"Warning: Could not load ball image '{self.image_path}'. Creating fallback circle. Error: {e}")
            self._create_fallback_surface()

    def _create_fallback_surface(self):
        """Creates a simple circle surface if image loading fails."""
        self.image = pygame.Surface((self.scaled_diameter, self.scaled_diameter), pygame.SRCALPHA)
        pygame.draw.circle(
            self.image,
            self.color,
            (self.scaled_radius, self.scaled_radius), # Center of the surface
            self.scaled_radius
        )
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface: pygame.Surface, camera_offset: pygame.Vector2):
        """
        Draws the ball on the specified surface, adjusted by camera offset.

        :param surface: The surface to draw the ball on.
        :param camera_offset: The camera's top-left world coordinate (Vector2).
        """
        if self.image:
            # Calculate top-left corner for blitting based on center position
            screen_pos_x = self.position.x - self.scaled_radius - camera_offset.x
            screen_pos_y = self.position.y - self.scaled_radius - camera_offset.y
            surface.blit(self.image, (screen_pos_x, screen_pos_y))
        else:
            # Fallback drawing if image is somehow None (shouldn't happen after init)
            screen_center = self.position - camera_offset
            pygame.draw.circle(surface, self.color, screen_center, self.scaled_radius)

    def apply_force(self, force_vector: pygame.Vector2, dt: float):
        """Applies a force vector over a time delta dt (unused in current impulse model)."""
        # For continuous force: acceleration = force_vector / self.mass
        # self.velocity += acceleration * dt
        pass # Currently using direct velocity change for shots

    def shoot(self, force_magnitude: float, angle_degrees: float):
        """Applies an initial velocity impulse to the ball."""
        if force_magnitude > 0:
            angle_radians = math.radians(angle_degrees)
            # Calculate velocity components based on angle
            # Remember: angle is typically counter-clockwise from positive x-axis
            self.velocity = pygame.Vector2(
                force_magnitude * math.cos(angle_radians),
                force_magnitude * math.sin(angle_radians)
            )
            self.is_moving = True
            self.reset_collision_state() # Reset anti-stuck state on new shot
            print(f"Shot: Force={force_magnitude:.1f}, Angle={angle_degrees:.1f}, Initial Vel={self.velocity}")
        else:
            self.velocity = pygame.Vector2(0, 0)
            self.is_moving = False

    def update_collision_state(self, collided_object):
        """Updates the anti-stuck mechanism state."""
        current_id = id(collided_object)
        if self.last_collided_object_id is not None and current_id != self.last_collided_object_id:
            self.collision_toggle_count += 1
            # print(f"Collision toggle: {self.collision_toggle_count}")
        else:
            # Reset counter if colliding with the same object again or first collision
            self.collision_toggle_count = 0
        self.last_collided_object_id = current_id

    def reset_collision_state(self):
        """Resets the anti-stuck mechanism state."""
        self.last_collided_object_id = None
        self.collision_toggle_count = 0

    def is_stuck(self):
        """Checks if the ball is considered stuck due to rapid toggling."""
        return self.collision_toggle_count >= self.MAX_COLLISION_TOGGLES

    # Removed unused/redundant methods like get_speed, update_position, shift_position, check_collision
    # Position/rect are updated directly or within physics logic.