import sys
import pygame
pygame.init()

#
#
#
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

    def set_enabled(self, enabled: bool):
        """
        Enables or disables the button.
        :param enabled: enables or disables the button
        """
        self.enabled = enabled
#
#
#

pygame.display.set_caption('SwingKing main menu')
screen = pygame.display.set_mode((1300, 755))
background = pygame.image.load("../assets/images/backgrounds/SwingKing1.png").convert()

clock = pygame.time.Clock()
"""""""""
greenbutton = pygame.image.load("../assets/images/buttons/green.png").convert_alpha()
greenbuttonhovered = pygame.image.load("../assets/images/buttons/green_hovered2.png").convert_alpha()

main_font = pygame.font.SysFont('cambria',50)
print(pygame.font.get_fonts())
"""""""""
"""""""""
class Button():
    def __init__(self, x,y,text_input, image,hovered, scale):
        self.x = x
        self.y = y
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
        self.hovered = pygame.transform.scale(hovered,(int(width*scale), int(height*scale)) )
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.text_input = text_input
        self.text = main_font.render(self.text_input,True,'white')
        self.text_rect =
        self.clicked = False


    def draw(self):
        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()




        if self.rect.collidepoint(pos):

            if pygame.mouse.get_pressed()[0] == 1  and self.clicked == False:
                self.clicked = True
                action = True
                print("Clicked")

        if pygame.mouse.get_pressed()[0]==0:
            self.clicked = False

        screen.blit(self.image, self.rect)
        screen.blit(self.text,self.rect)
        return action








#buttons instance
green1 = Button(517,265,'test1',greenbutton,greenbuttonhovered,0.8)
green2 = Button(517,365,'test2',greenbutton,greenbuttonhovered,0.8)
green3 = Button(517,465,'test3',greenbutton,greenbuttonhovered,0.8)

#buttons hovered instance
#green1hovered = Button(517,265,greenbuttonhovered,0.8)
#green2hovered = Button(517,365,greenbuttonhovered,0.8)
#green3hovered = Button(517,465,greenbuttonhovered,0.8)

"""""""""

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

    PLAY.hover()
    OPTIONS.hover()
    CREDITS.hover()
    EXIT.hover()
    PLAY.draw(screen)
    OPTIONS.draw(screen)
    CREDITS.draw(screen)
    EXIT.draw(screen)

    #if pygame.mouse.get_pos() ==

    if PLAY.draw(screen) == True:
        print('PLAY')
    #if green2.draw() == True:
    #    print('Credits')




    # let the user quit the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()



    pygame.display.update()
    clock.tick(60)

