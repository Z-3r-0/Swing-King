import pygame

class Camera:
    def __init__(self, position: pygame.Vector2, width, height, level_max_width: int = -1, level_max_height: int = -1): # Renamed length to width
        self.position = position.copy()
        # self.old_position = position # Not used
        self.width = width
        self.height = height
        # self.camera = pygame.Rect(0, 0, width, height) # Can be generated on the fly
        self.level_max_width = level_max_width
        self.level_max_height = level_max_height
        # self.current_shift = pygame.Vector2(0,0) # Not needed

    def calculate_position(self, target_world_pos: pygame.Vector2):
        """
        Calculate the position of the camera depending on the position of the element
        Used to move element to left or right depending on the element position (mostly the ball)

        Do not forget to update the position of the element with the camera position as:
            displayed_element_position = element_position - camera.position

        :param target_world_pos: position of the element we want to center
        """
        # self.old_position = self.position.copy() # Not needed unless calculating shift

        desired_x = target_world_pos.x - self.width // 2
        desired_y = target_world_pos.y - self.height // 2

        if self.level_max_width != -1:
            clamped_x = max(0, min(desired_x, self.level_max_width - self.width))
        else:
            clamped_x = max(0, desired_x)

        if self.level_max_height != -1:
            clamped_y = max(0, min(desired_y, self.level_max_height - self.height))
        else:
            clamped_y = max(0, desired_y)

        self.position.x = clamped_x
        self.position.y = clamped_y

        # self.current_shift = self.position - self.old_position # Not needed

    def get_rect(self) -> pygame.Rect:
        """Returns the camera's view rectangle in world coordinates."""
        return pygame.Rect(self.position.x, self.position.y, self.width, self.height)