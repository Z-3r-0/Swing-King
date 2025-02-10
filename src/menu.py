import sys
import pygame
pygame.init()

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

pygame.display.set_caption('SwingKing main menu')
screen = pygame.display.set_mode((1300, 755))
background = pygame.image.load("../assets/images/backgrounds/SwingKing1.png").convert()

clock = pygame.time.Clock()

PLAY = Button(screen, lambda: print("Button clicked"), (532,370), (270,80), "../assets/images/buttons/play/PLAY.png", "../assets/images/buttons/play/PLAY_HOVERED.png","../assets/images/buttons/play/PLAY_CLICKED.png")
OPTIONS = Button(screen, lambda: print("Button clicked"), (532,460), (270,80),
                 "../assets/images/buttons/options/OPTIONS.png", "../assets/images/buttons/options/OPTIONS_HOVERED.png",
                 "../assets/images/buttons/options/OPTIONS_CLICKED.png")
CREDITS = Button(screen, lambda: print("Button clicked"), (532,550), (270,80),
                 "../assets/images/buttons/credits/CREDITS.png", "../assets/images/buttons/credits/CREDITS_HOVERED.png",
                 "../assets/images/buttons/credits/CREDITS_CLICKED.png")
EXIT = Button(screen, lambda: print("Button clicked"), (532,640), (270,80), "../assets/images/buttons/exit/EXIT.png",
              "../assets/images/buttons/exit/EXIT_HOVERED.png",
              "../assets/images/buttons/exit/EXIT_CLICKED.png")

while True :
    screen.blit(background, (0, 0))

    PLAY.listen()
    OPTIONS.listen()
    CREDITS.listen()
    EXIT.listen()


    PLAY.draw(screen)
    OPTIONS.draw(screen)
    CREDITS.draw(screen)
    EXIT.draw(screen)


    # let the user quit the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()



    pygame.display.update()
    clock.tick(60)

