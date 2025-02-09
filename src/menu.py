import sys
import pygame
pygame.init()



pygame.display.set_caption('SwingKing main menu')
screen = pygame.display.set_mode((1300, 755))
background = pygame.image.load("../assets/images/backgrounds/SwingKing1.png").convert()

clock = pygame.time.Clock()

greenbutton = pygame.image.load("../assets/images/buttons/green.png").convert_alpha()
greenbuttonhovered = pygame.image.load("../assets/images/buttons/green_hovered2.png").convert_alpha()

class Button():
    def __init__(self, x,y, image, scale):
        self.x = x
        self.y = y
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        #self.rect.topleft = (x,y)
        self.clicked = False


    def draw(self):

        #get mouse position
        pos = pygame.mouse.get_pos()

        action = False


        if self.rect.collidepoint(pos):

            if pygame.mouse.get_pressed()[0] == 1  and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0]==0:
            self.clicked = False
            return action
        screen.blit(self.image, self.rect)









#buttons instance
green1 = Button(517,265,greenbutton,0.8)
green2 = Button(517,365,greenbutton,0.8)
green3 = Button(517, 465, greenbutton, 0.8)

#buttons hovered instance
green1hovered = Button(517,265,greenbuttonhovered,0.8)
green2hovered = Button(517,365,greenbuttonhovered,0.8)
green3hovered = Button(517,465,greenbuttonhovered,0.8)


while True :
    screen.blit(background, (0, 0))

    green1.draw()
    green2.draw()
    #green3.draw()

    green1hovered.draw()
    #green2hovered.draw()
    #green3hovered.draw()


    #if green1.draw() == True:
    #    print('PLAY')
    #if green2.draw() == True:
    #    print('Credits')




    # let the user quit the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()



    pygame.display.update()
    clock.tick(60)

