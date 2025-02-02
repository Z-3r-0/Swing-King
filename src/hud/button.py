import pygame


class Button:
    def __init__(self, screen, func, position: tuple, size: tuple = None, image_path: str = None,
                 foreground_color: pygame.Color = None, background_color: pygame.Color = None, text: str = None,
                 font_path: str = None, font_color: pygame.Color = None, scene_bg_color: pygame.Color = None):
        """
        Initializes a Button instance with the given parameters.
        :param screen: pygame screen
        :param func: function to be called
        :param position: position of the button
        :param size: size of the button
        :param image_path: path to image
        :param foreground_color: color of the button
        :param background_color: color of the button
        :param text: text of the button
        :param font_path: path to font file
        :param font_color: color of the button
        :param scene_bg_color: color of the button
        """
        self._screen = screen
        self._func = func
        self._position = position
        self._size = size
        self._imagePath = image_path
        self._foreground_color = foreground_color
        self._background_color = background_color
        self._text = text
        self._font_path = font_path
        self._font_color = font_color
        self._scene_bg_color = scene_bg_color

        self._rect = pygame.Rect(self._position, self._size)

        if text:
            self._font_size = 20  # arbitrary value TODO - Change this value using a function depending on the size of the button
            self._font = pygame.font.Font(self._font_path, self._font_size)
            self._text_surface = self._font.render(self._text, True, self._font_color)

        if self._imagePath:
            self._image = pygame.image.load(image_path).convert_alpha()

            if self._size:
                self._image = pygame.transform.smoothscale(self._image, self._size)
            else:
                self._size = (self._image.get_width(), self._image.get_height())

            self._rect = pygame.Rect(self._position, self._size)
        else:
            self._image = None

            # Create two rects filled with foreground and background color to draw them later
            self._back = self._rect
            self._top = self._back.move(-4, -4)

        self._clicked = False
        self._enabled = True

    def get_position(self):
        """
        Returns the current position of the button.
        """
        return self._position

    def get_size(self):
        """
        Returns the current size of the button.
        """
        return self._size

    def get_image(self):
        """
        Returns the button's image surface.
        """
        return self._image

    def get_image_path(self):
        """
        Returns the file path to the button's image.
        """
        return self._imagePath

    def set_position(self, position: tuple):
        """
        Sets the position of the button.
        :param position: The new position of the button.
        """
        self._position = position

    def set_size(self, size: tuple):
        """
        Sets the size of the button.
        :param size: The size of the button.
        """
        self._size = size

    def set_image(self, image_path):
        """
        Sets the button's image using the provided image path.
        :param image_path: The image path.
        """
        self._imagePath = image_path
        self._image = pygame.image.load(image_path).convert_alpha()

    def listen(self):
        """
        Listens for mouse clicks on the button and triggers the button's function if clicked.
        """
        if self._enabled and pygame.mouse.get_pressed()[0] and self.is_clicked():
            self.click(self._func)

    def is_clicked(self):
        """
        Checks if the button is currently clicked.
        """
        mouse_pos = pygame.mouse.get_pos()
        if self._rect.collidepoint(mouse_pos):
            self._clicked = True
            return True
        return False

    def draw(self, surface):
        """
        Draws the button on the specified surface.
        :param surface: Surface to draw the button on.
        """

        if self._imagePath:
            surface.blit(self._image, self._position)
            pygame.display.update()
        else:
            # Draw the button based on its state (enabled or disabled)
            bg_color = self._background_color if self._enabled else (200, 200, 200)  # Grey out if disabled
            fg_color = self._foreground_color if self._enabled else (150, 150, 150)  # Dim the color

            pygame.draw.rect(self._screen, bg_color, self._back)
            pygame.draw.rect(self._screen, fg_color, self._top)

            self._screen.blit(self._text_surface, (
                self._position[0] + (self._size[0] - self._text_surface.get_width()) / 2,
                self._position[1] + (self._size[1] - self._text_surface.get_height()) / 2
            ))

    def click_effect(self):
        """
        Applies a visual effect when the button is clicked.
        """

        # Clear the area around the button with the scene background color
        area_to_clear = self._rect.inflate(8, 8)  # 8, 8 are test-obtained arbitrary values
        self._screen.fill(self._scene_bg_color, area_to_clear)

        # Draw the offset image if clicked
        offset = 4 if self._clicked else 0

        if self._image:
            self._screen.blit(self._image, (self._position[0], self._position[1] + offset))
        else:

            if self._clicked:
                self._back = pygame.draw.rect(self._screen, self._foreground_color, self._rect)
                self._top = self._back.move(-4, -4)
            else:
                self._back = pygame.draw.rect(self._screen, self._background_color, self._rect)
                self._top = self._back.move(-4, -4)

            self._screen.blit(
                self._text_surface,
                (
                    self._position[0] + offset + (self._size[0] - self._text_surface.get_width()) / 2,
                    self._position[1] + offset + (self._size[1] - self._text_surface.get_height()) / 2,
                )
            )
        pygame.display.update()

    def click(self, func):
        """
        Triggers the button's click effect and executes the provided function.
        :param func: function to be called
        """
        if self._clicked:
            self.click_effect()
            func()
            self._clicked = False

    def set_enabled(self, enabled: bool):
        """
        Enables or disables the button.
        :param enabled: enables or disables the button
        """
        self._enabled = enabled
