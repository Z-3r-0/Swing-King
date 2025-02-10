import sys
import pygame
pygame.init()

from hud import Button

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

