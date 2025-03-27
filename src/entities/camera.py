import pygame

class Camera:
    def __init__(self, position: pygame.Vector2, width, height):
        self.position = position
        self.old_position = position
        self.width = width
        self.height = height
        self.camera = pygame.Rect(0, 0, width, height)

    def calculate_position(self, element_position: pygame.Vector2, level_max_length: int = -1, level_max_height: int = -1):
        """
        Calculate the position of the camera depending on the position of the element
        Used to move element to left or right depending on the element position (mostly the ball)

        Do not forget to update the position of the element with the camera position as:
            displayed_element_position = element_position - camera.position.x

        :param element_position: position of the element we want to center
        :param width: width of the display window
        :param height: height of the display window
        :param level_max_length: full length of the level (default: no limit) (used to limit the camera position)
        :param level_max_height: full height of the level (default: no limit) (used to limit the camera position)
        :return:
        """
        self.old_position = self.position

        if level_max_length == -1:
            self.position.x = max(0, int(element_position.x) - self.width // 2)
        else:
            self.position.x = max(0, min(int(element_position.x) - self.width // 2, level_max_length - self.width))
        if level_max_height == -1:
            self.position.y = max(0, int(element_position.y) - self.height // 2)
        else:
            self.position.y = max(0, min(int(element_position.y) - self.height // 2, level_max_height - self.height))

    def update(self, target_x, target_y):
        self.camera.x = target_x - self.width // 2
        self.camera.y = target_y - self.height // 2

    def apply(self, rect):
        return rect.move(-self.camera.x, -self.camera.y)