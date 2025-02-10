import pygame

class Camera:
    def __init__(self, position: pygame.Vector2):
        self.position = position
        self.old_position = position

    def calculate_position(self, element_position: pygame.Vector2, window_width: int, window_height: int, level_max_length: int = -1, level_max_height: int = -1):
        """
        Calculate the position of the camera depending on the position of the element
        Used to move element to left or right depending on the element position (mostly the ball)

        Do not forget to update the position of the element with the camera position as:
            displayed_element_position = element_position - camera.position.x

        :param element_position: position of the element we want to center
        :param window_width: width of the display window
        :param window_height: height of the display window
        :param level_max_length: full length of the level (default: no limit) (used to limit the camera position)
        :param level_max_height: full height of the level (default: no limit) (used to limit the camera position)
        :return:
        """
        self.old_position = self.position

        if level_max_length == -1:
            self.position.x = max(0, int(element_position.x) - window_width // 2)
        else:
            self.position.x = max(0, min(int(element_position.x) - window_width // 2, level_max_length - window_width))
        if level_max_height == -1:
            self.position.y = max(0, int(element_position.y) - window_height // 2)
        else:
            self.position.y = max(0, min(int(element_position.y) - window_height // 2, level_max_height - window_height))
