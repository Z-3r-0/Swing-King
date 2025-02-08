import pygame


class Button:
    def __init__(self, screen, func, position: pygame.Vector2, size: pygame.Vector2, image_path: str):
        """
        Initializes a Button instance with the given parameters.
        :param screen: pygame screen
        :param func: function to be called
        :param position: position of the button
        :param size: size of the button
        :param image_path: path to image
        """

        self.screen = screen
        self._func = func
        self.position = position
        self.size = size
        self.imagePath = image_path

        self.rect = pygame.Rect(self.position, self.size)

        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, self.size)

        self.rect = pygame.Rect(self.position, self.size)

        self.clicked = False
        self.enabled = True

    def get_position(self):
        """
        Returns the current position of the button.
        """
        return self.position

    def get_size(self):
        """
        Returns the current size of the button.
        """
        return self.size

    def get_image(self):
        """
        Returns the button's image surface.
        """
        return self.image

    def get_image_path(self):
        """
        Returns the file path to the button's image.
        """
        return self.imagePath

    def set_position(self, position: tuple):
        """
        Sets the position of the button.
        :param position: The new position of the button.
        """
        self.position = position

    def set_size(self, size: tuple):
        """
        Sets the size of the button.
        :param size: The size of the button.
        """
        self.size = size

    def set_image(self, image_path):
        """
        Sets the button's image using the provided image path.
        :param image_path: The image path.
        """
        self.imagePath = image_path
        self.image = pygame.image.load(image_path).convert_alpha()

    def listen(self):
        """
        Listens for mouse clicks on the button and triggers the button's function if clicked.
        """
        if self.enabled and pygame.mouse.get_pressed()[0] and self.is_clicked():
            self.click(self._func)

    def is_clicked(self):
        """
        Checks if the button is currently clicked.
        """
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.clicked = True
            return True
        return False

    def draw(self, surface):
        """
        Draws the button on the specified surface.
        :param surface: Surface to draw the button on.
        """

        surface.blit(self.image, self.position)

    def click_effect(self):
        """
        Applies a visual effect when the button is clicked.
        """

        # Clear the area around the button with the scene background color
        s = pygame.Surface(self.size)
        s.set_alpha(128)
        s.fill((255, 255, 255))
        self.screen.blit(s, self.position)

        # Draw the offset image if clicked
        offset = 4 if self.clicked else 0

        self.screen.blit(self.image, (self.position[0], self.position[1] + offset))
        pygame.display.update()

    def click(self, func):
        """
        Triggers the button's click effect and executes the provided function.
        :param func: function to be called
        """
        if self.clicked:
            self.click_effect()
            func()
            self.clicked = False

    def set_enabled(self, enabled: bool):
        """
        Enables or disables the button.
        :param enabled: enables or disables the button
        """
        self.enabled = enabled