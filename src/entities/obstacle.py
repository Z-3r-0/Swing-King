import pygame


class Obstacle:
    def __init__(self, position: pygame.Vector2, image_path: str, size: float = 100.0, is_colliding: bool = True,
                 nb_points: int = 10):
        self.points = []
        self.size = size  # in percentage
        self.position = position.copy()  # Use .copy() to avoid references
        self.shift = pygame.Vector2(0, 0)
        self.is_colliding = is_colliding  # Value to false for decorative elements
        self.moving = False  # Define if we are placing the obstacle

        self.image_path = image_path
        self.original_image = pygame.image.load(self.image_path)
        self.total_height = self.original_image.get_height()
        self.total_width = self.original_image.get_width()

        # Store the height/width ratio
        self.aspect_ratio = self.total_height / self.total_width

        # Resize the image
        self.image = pygame.transform.scale(self.original_image, (self.size, int(self.size * self.aspect_ratio)))
        self.mask = pygame.mask.from_surface(self.image.convert_alpha())
        self.points = self.mask.outline()

        self.reduce_nb_points(nb_points)

        self.transparent_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)

    def resize(self, size: int):
        """Resize the obstacle
        Set the new size, in pixels (width)
        """
        self.size = size
        # Recalculate the height based on the aspect ratio
        height = int(size * self.aspect_ratio)
        self.image = pygame.transform.scale(self.original_image, (size, height))
        self.mask = pygame.mask.from_surface(self.image.convert_alpha())
        self.points = self.mask.outline()
        self.reduce_nb_points()
        self.transparent_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)

    def change_size(self, mouse_pos: pygame.Vector2):
        """Change the size based on the mouse position"""
        # Limit to a minimum of 20px and calculate the width
        new_width = max(20, int(mouse_pos.x - self.position.x))
        self.resize(new_width)

    def reduce_nb_points(self, nb_points: int = 100):
        """Reduce the number of contour points to optimize performance"""
        if len(self.points) <= nb_points:
            return
        step = max(1, len(self.points) // nb_points)
        self.points = [self.points[i] for i in range(0, len(self.points), step)]

    def draw_points(self, screen: pygame.Surface):
        """Display the contour points (debug)"""
        for point in self.points:
            pygame.draw.circle(screen, (255, 0, 0), point + self.position, 2)

    def draw(self, screen: pygame.Surface, color: tuple[int, int, int, int] = (255, 255, 255, 0)):
        """Draw the obstacle on the screen"""
        screen.blit(self.image, self.position)  # Display the image at the position

        # Draw a transparent polygon on top for collision handling (if necessary)
        if len(self.points) > 2 and color[3] > 0:  # Only if alpha > 0
            self.transparent_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(self.transparent_surface, color, self.points)
            screen.blit(self.transparent_surface, self.position)

    def draw_bounding_box(self, screen: pygame.Surface, color=(255, 0, 0)):
        """Draw the bounding box of the obstacle"""
        pygame.draw.rect(screen, color, (
            self.position.x,
            self.position.y,
            self.image.get_width(),
            self.image.get_height()
        ), 2)

    def is_moved(self):
        """Put the obstacle in moving mode"""
        self.moving = True

    def place_obstacle(self, position: pygame.Vector2, camera_position: pygame.Vector2):
        """Place the obstacle at a specific position"""
        self.moving = False
        self.position = position - camera_position
        self.shift = camera_position

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

    def contains_point(self, point: pygame.Vector2) -> bool:
        """Check if a point is inside the obstacle"""
        local_point = point - self.position
        if 0 <= local_point.x < self.image.get_width() and 0 <= local_point.y < self.image.get_height():
            try:
                # Check if the pixel is not transparent
                pixel = self.image.get_at((int(local_point.x), int(local_point.y)))
                return pixel[3] > 0  # Alpha > 0
            except IndexError:
                return False
        return False