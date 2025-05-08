import pygame

class Camera:
    def __init__(self, position: pygame.Vector2, width, height, level_max_width: int = -1, level_max_height: int = -1, level_min_x:int = -1, level_min_y:int = -1): # Renamed length to width
        self.position = position.copy()
        self.old_position = position.copy()
        self.width = width
        self.height = height
        self.level_max_width = level_max_width
        self.level_max_height = level_max_height
        self.level_min_x = level_min_x
        self.level_min_y = level_min_y
        self.current_shift = pygame.Vector2(0,0)

    def calculate_position(self, target_world_pos: pygame.Vector2):
        """
        Calculate the position of the camera to center the target_world_pos,
        respecting level boundaries.
        """
        self.old_position = self.position.copy()
        desired_x = target_world_pos.x - self.width // 2
        desired_y = target_world_pos.y - self.height // 2
        final_x = desired_x
        if self.level_min_x != -1:
            final_x = max(self.level_min_x, final_x)
        if self.level_max_width != -1:
            max_camera_x = self.level_max_width - self.width
            if self.level_min_x != -1:
                max_camera_x = max(self.level_min_x, max_camera_x)
            final_x = min(final_x, max_camera_x)
        final_y = desired_y
        if self.level_min_y != -1:
            final_y = max(self.level_min_y, final_y)
        if self.level_max_height != -1:
            max_camera_y = self.level_max_height - self.height
            if self.level_min_y != -1:
                max_camera_y = max(self.level_min_y, max_camera_y)
            final_y = min(final_y, max_camera_y)

        self.position.x = final_x
        self.position.y = final_y

        self.current_shift = self.position - self.old_position


    def get_rect(self) -> pygame.Rect:
        """Returns the camera's view rectangle in world coordinates."""
        return pygame.Rect(self.position.x, self.position.y, self.width, self.height)