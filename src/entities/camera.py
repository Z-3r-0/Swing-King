import pygame

class Camera:
    def __init__(self, position: pygame.Vector2, width, height, level_max_length: int = -1, level_max_height: int = -1):
        self.position = position
        self.old_position = position
        self.width = width
        self.height = height
        self.camera = pygame.Rect(0, 0, width, height)
        self.level_max_length = level_max_length
        self.level_max_height = level_max_height
        self.current_shift = pygame.Vector2(0,0)

    def calculate_position(self, element_position: pygame.Vector2):
        """
        Calculate the position of the camera depending on the position of the element
        Used to move element to left or right depending on the element position (mostly the ball)

        Do not forget to update the position of the element with the camera position as:
            displayed_element_position = element_position - camera.position.x

        :param element_position: position of the element we want to center
        """
        self.old_position = self.position

        if self.level_max_length == -1:
            self.position.x = max(0, int(element_position.x) - self.width // 2)
        else:
            self.position.x = max(0, min(int(element_position.x) - self.width // 2, self.level_max_length - self.width))
        if self.level_max_height == -1:
            self.position.y = max(0, int(element_position.y) - self.height // 2)
        else:
            self.position.y = max(0, min(int(element_position.y) - self.height // 2, self.level_max_height - self.height))

        self.current_shift = self.position - self.old_position
