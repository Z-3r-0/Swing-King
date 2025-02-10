import pygame


class Button:
    def __init__(self, screen, func, position: pygame.Vector2, size: pygame.Vector2, image_path: str,hovered_image_path: str,clicked_image_path):
        """
        Initializes a Button instance with the given parameters.
        :param screen: pygame screen
        :param func: function to be called
        :param position: position of the button
        :param size: size of the button
        :param image_path: path to image
        """
        self.screen = screen
        self.func = func
        self.position = position
        self.size = size

        self.imagePath = image_path



        self.rect = pygame.Rect(self.position, self.size)


        self.image = pygame.image.load(image_path).convert_alpha()
        self.hovered_image = pygame.image.load(hovered_image_path).convert_alpha()
        self.clicked_image = pygame.image.load(clicked_image_path).convert_alpha()


        self.image = pygame.transform.smoothscale(self.image, self.size)
        self.hovered_image = pygame.transform.smoothscale(self.hovered_image, self.size)
        self.clicked_image = pygame.transform.smoothscale(self.clicked_image, self.size)

        self.rendered_image = self.image.copy()

        self.rect = pygame.Rect(self.position, self.size)
        self.clicked = False
        self.enabled = True

    def hover(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.rendered_image = self.hovered_image.copy()
        else :
            self.rendered_image = self.image.copy()

    def listen(self):
        """
        Listens for mouse clicks on the button and triggers the button's function if clicked.
        """
        self.hover()
        self.click(self.func)

    def draw(self, surface):
        """
        Draws the button on the specified surface.
        :param surface: Surface to draw the button on.
        """

        surface.blit(self.rendered_image, self.position)

    def click(self, func):
        """
        Triggers the button's click effect and executes the provided function.
        :param func: function to be called
        """
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.rendered_image = self.clicked_image.copy()
            func()
        else :
            self.hover()
