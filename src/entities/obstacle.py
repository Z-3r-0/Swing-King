import pygame
from pygame.transform import rotate
import math


class Obstacle:
    def __init__(self, position: pygame.Vector2, image_path: str, size: int = 100, is_colliding: bool = True,
                 angle:int=0,nb_points: int = 100, characteristic: str = None):

        self.position = position.copy()
        self.size = size
        # self.shift = pygame.Vector2(0, 0) # Seems related to editor mode
        self.is_colliding = is_colliding
        # self.moving = False # Seems related to editor mode
        self.nb_points = nb_points

        self.characteristic = characteristic

        # Define default physics properties, can be overridden by characteristic later
        self.friction = 0.3
        self.bounce_factor = 0.4
        # Example: if characteristic == "water": self.friction = 0.95; self.bounce_factor = 0.05

        self.image_path = image_path
        self.original_image = None
        self.image = None
        self.rotated_image = None
        self.mask = None
        self.rotated_mask = None
        self.points = []
        self.rotated_points = [] # Points relative to self.position

        self.aspect_ratio = 1.0
        self.angle = 0

        try:
            self.original_image = pygame.image.load(self.image_path).convert_alpha()
            if self.original_image.get_width() > 0:
                 self.aspect_ratio = self.original_image.get_height() / self.original_image.get_width()
            else:
                 self.aspect_ratio = 1.0 # Avoid division by zero
            self._resize_internal(self.size)
            self.rotate(angle)

        except pygame.error as e:
            print(f"Error loading obstacle image '{self.image_path}': {e}")
            self._create_fallback()
            self.rotate(angle) # Still apply rotation to fallback
        except Exception as e:
             print(f"Error initializing obstacle '{self.image_path}': {e}")
             self._create_fallback()
             self.rotate(angle)

    def _create_fallback(self):
         """Creates a fallback placeholder if image loading fails."""
         self.image = pygame.Surface((self.size, int(self.size * self.aspect_ratio)), pygame.SRCALPHA)
         self.image.fill((128, 128, 128, 180)) # Semi-transparent grey
         self.mask = pygame.mask.from_surface(self.image)
         # Create simple rectangular points for fallback
         h = int(self.size * self.aspect_ratio)
         self.points = [pygame.Vector2(0,0), pygame.Vector2(self.size,0), pygame.Vector2(self.size,h), pygame.Vector2(0,h)]
         self.rotated_image = self.image.copy()
         self.rotated_mask = self.mask.copy()
         self.rotated_points = self.points[:] # Copy


    def _resize_internal(self, width: int):
        self.size = max(10, width)
        height = int(self.size * self.aspect_ratio)
        if self.original_image:
            self.image = pygame.transform.scale(self.original_image, (self.size, height))
            self.mask = pygame.mask.from_surface(self.image)
            raw_points = self.mask.outline()
            # Convert mask outline points (relative to image top-left) to Vector2
            self.points = [pygame.Vector2(p) for p in self._reduce_nb_points(raw_points, self.nb_points)]
            self._update_rotation() # Re-apply rotation after resize

    def resize(self, size: int):
        """Resize the obstacle
        Set the new size, in pixels (width)
        """
        self._resize_internal(size)

    def change_size(self, mouse_pos: pygame.Vector2):
        """Change the size based on the mouse position"""
        # Limit to a minimum of 20px and calculate the width
        new_width = max(20, int(mouse_pos.x - self.position.x))
        self.resize(new_width)

    def _reduce_nb_points(self, points, max_points: int):
        if not points or len(points) <= max_points:
            return points
        step = max(1, len(points) // max_points)
        return [points[i] for i in range(0, len(points), step)]

    def _update_rotation(self):
         """Applies the stored angle to the current scaled image."""
         if self.image:
             self.rotated_image = pygame.transform.rotate(self.image, self.angle)
             self.rotated_mask = pygame.mask.from_surface(self.rotated_image)

             # Rotate the original relative points around the image center
             center = pygame.Vector2(self.image.get_width() / 2, self.image.get_height() / 2)
             angle_rad = math.radians(-self.angle) # Pygame rotate is CW, math is CCW
             cos_a = math.cos(angle_rad)
             sin_a = math.sin(angle_rad)

             self.rotated_points = []
             for p in self.points:
                 p_centered = p - center
                 x_new = p_centered.x * cos_a - p_centered.y * sin_a
                 y_new = p_centered.x * sin_a + p_centered.y * cos_a
                 rotated_p = pygame.Vector2(x_new, y_new) + center
                 self.rotated_points.append(rotated_p)

             # Alternative: Get outline from rotated mask (less reliable for exact points)
             # raw_rotated_points = self.rotated_mask.outline()
             # self.rotated_points = [pygame.Vector2(p) for p in self._reduce_nb_points(raw_rotated_points, self.nb_points)]


    def rotate(self, angle_degrees):
        """Rotate the obstacle by a given angle in degrees."""
        self.angle = angle_degrees % 360
        self._update_rotation()

    def get_rotated_rect(self) -> pygame.Rect:
         """Returns the bounding Rect of the *rotated* image in world coordinates."""
         if self.rotated_image:
             # get_rect() gives rect relative to 0,0, need to set its center/topleft
             rect = self.rotated_image.get_rect(topleft=self.position)
             return rect
         else:
             return pygame.Rect(self.position.x, self.position.y, self.size, int(self.size * self.aspect_ratio))


    def draw_points(self, screen: pygame.Surface, camera_offset: pygame.Vector2):
        """Display the contour points (debug)"""
        if not self.rotated_points: return
        world_points = [(p + self.position) for p in self.rotated_points]
        screen_points = [(wp - camera_offset) for wp in world_points]
        for sp in screen_points:
            pygame.draw.circle(screen, (255, 0, 0), sp, 2)

    def draw(self, screen: pygame.Surface, camera_offset: pygame.Vector2, color: tuple[int, int, int, int] = (255, 255, 255, 0)):
        """Draw the obstacle on the screen"""
        if self.rotated_image:
            screen_pos = self.position - camera_offset
            screen.blit(self.rotated_image, screen_pos)

        # Draw transparent polygon removed, collision handled by mask/physics

    def draw_bounding_box(self, screen: pygame.Surface, camera_offset: pygame.Vector2, color=(255, 0, 0)):
        """Draw the bounding box of the obstacle"""
        world_rect = self.get_rotated_rect()
        screen_rect = world_rect.move(-camera_offset.x, -camera_offset.y)
        pygame.draw.rect(screen, color, screen_rect, 1)

    # Editor-related methods removed/commented
    # def is_moved(self): ...
    # def place_obstacle(self, position: pygame.Vector2, camera_position: pygame.Vector2): ...
    # def shift_obstacle(self, shift: pygame.Vector2): ...
    # def update_obstacle(self, screen: pygame.Surface, camera_movement: pygame.Vector2): ...

    def shift_obstacle(self, shift: pygame.Vector2):
        """
        Move the obstacle according to a shift vector
        DO NOT GIVE COORDINATES OF CAMERA
        """
        self.position -= shift
        self.shift -= shift

    def update_obstacle(self, screen: pygame.Surface, camera_movement: pygame.Vector2):
        """Update the position of the obstacle based on camera movement and draw it"""
        self.shift_obstacle(camera_movement)
        self.draw(screen)

    def contains_point(self, world_point: pygame.Vector2) -> bool:
        """Check if a world point is inside the obstacle's rotated mask."""
        if not self.rotated_mask:
            return False
        rotated_rect = self.get_rotated_rect()
        if not rotated_rect.collidepoint(world_point):
            return False
        point_relative_to_mask = world_point - rotated_rect.topleft
        mask_width, mask_height = self.rotated_mask.get_size()
        if 0 <= point_relative_to_mask.x < mask_width and 0 <= point_relative_to_mask.y < mask_height:
            try:
                return self.rotated_mask.get_at((int(point_relative_to_mask.x), int(point_relative_to_mask.y))) != 0
            except IndexError:
                return False
        return False

    def rotate(self, angle_degrees):
        """Rotate the obstacle by a given angle in degrees."""
        self.angle = angle_degrees % 360  # Keep angle within 0-360 range
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)
        self.rotated_mask = pygame.mask.from_surface(self.rotated_image.convert_alpha())

        self.rotated_points = self.rotated_mask.outline()
        self.rotated_points = self.reduce_nb_points(self.rotated_points, self.nb_points)