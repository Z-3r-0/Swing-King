import sys
import pygame
from pygame import mouse

pygame.init()

from hud import Button

pygame.display.set_caption('SwingKing main menu')
screen = pygame.display.set_mode((1300, 755))

background = pygame.image.load("../assets/images/backgrounds/SwingKing1.png").convert()
play_bg = pygame.image.load("../assets/images/backgrounds/SwingKing1.png").convert()
options_bg = pygame.image.load("../assets/images/backgrounds/SwingKing1.png").convert()
credits_bg = pygame.image.load("../assets/images/backgrounds/SwingKing1CREDITS.png").convert()

# Define game states
MAIN_MENU = "main_menu"
PLAY_SCREEN = "play_screen"
OPTIONS_SCREEN = "options_screen"
CREDITS_SCREEN = "credits_screen"
current_screen = MAIN_MENU  # Start with main menu

def go_to_play():
    global current_screen
    current_screen = PLAY_SCREEN

def go_to_options():
    global current_screen
    current_screen = OPTIONS_SCREEN

def go_to_credits():
    global current_screen
    current_screen = CREDITS_SCREEN

def go_to_menu():
    global current_screen
    current_screen = MAIN_MENU

running = True

def exit_function():
    pygame.quit()
    sys.exit()
credits = pygame.image.load("../assets/images/backgrounds/SwingKing1CREDITS.png").convert()

def credits_page() :
    while True :
        screen.fill((255,255,255))
        screen.blit(credits,(0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

clock = pygame.time.Clock()


PLAY = Button(screen, lambda: go_to_play(), (532,370), (270,80), "../assets/images/buttons/play/PLAY.png", "../assets/images/buttons/play/PLAY_HOVERED.png","../assets/images/buttons/play/PLAY_CLICKED.png")
OPTIONS = Button(screen, lambda: go_to_options(), (532,460), (270,80),
                 "../assets/images/buttons/options/OPTIONS.png", "../assets/images/buttons/options/OPTIONS_HOVERED.png",
                 "../assets/images/buttons/options/OPTIONS_CLICKED.png")
CREDITS = Button(screen, lambda : go_to_credits(), (532,550), (270,80),
                 "../assets/images/buttons/credits/CREDITS.png", "../assets/images/buttons/credits/CREDITS_HOVERED.png",
                 "../assets/images/buttons/credits/CREDITS_CLICKED.png")
EXIT = Button(screen, lambda: exit_function(), (532,640), (270,80), "../assets/images/buttons/exit/EXIT.png",
              "../assets/images/buttons/exit/EXIT_HOVERED.png",
              "../assets/images/buttons/exit/EXIT_CLICKED.png")
BACK = Button(screen, lambda: go_to_menu(), (532,640), (270,80), "../assets/images/buttons/back/BACK.png", "../assets/images/buttons/back/BACK_HOVERED.png","../assets/images/buttons/back/BACK_CLICKED.png")


'''''''''
#GAMELOOP1
while running :
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Check which screen is active and render it
    if current_screen == MAIN_MENU:
        screen.blit(background, (0, 0))

        # Draw and listen for buttons
        PLAY.listen(go_to_play)
        OPTIONS.listen(go_to_options)
        CREDITS.listen(go_to_credits)
        EXIT.listen(exit_function)

        PLAY.draw(screen)
        OPTIONS.draw(screen)
        CREDITS.draw(screen)
        EXIT.draw(screen)

    elif current_screen == PLAY_SCREEN:
        screen.blit(play_bg, (0, 0))
        BACK.listen(go_to_menu)
        BACK.draw(screen)

    elif current_screen == OPTIONS_SCREEN:
        screen.blit(options_bg, (0, 0))
        BACK.listen(go_to_menu)
        BACK.draw(screen)

    elif current_screen == CREDITS_SCREEN:
        screen.blit(credits_bg, (0, 0))
        BACK.listen(go_to_menu)
        BACK.draw(screen)

    pygame.display.update()
    clock.tick(60)
'''''''''


'''''''''
#Lu
def game():
    while running :
        screen.blit(background, (0, 0))


        PLAY.listen()
        OPTIONS.listen()
        CREDITS.listen()
        EXIT.listen()

        PLAY.draw(screen)
        OPTIONS.draw(screen)
        CREDITS.draw(screen)
        EXIT.draw(screen)


        #for event in pygame.event.get():
        #    if event.type == pygame.MOUSEBUTTONDOWN:
        #        CREDITS.click(credits_page())

        pygame.display.update()


        # let the user quit the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()



        pygame.display.update()
        clock.tick(60)


game()
'''''''''

running = True
while running:
    screen.fill((0, 0, 0))  # Efface l'écran avant de redessiner

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Passer l'événement aux boutons
        if current_screen == MAIN_MENU:
            PLAY.listen(event)
            OPTIONS.listen(event)
            CREDITS.listen(event)
            EXIT.listen(event)
        elif current_screen in {PLAY_SCREEN, OPTIONS_SCREEN, CREDITS_SCREEN}:
            BACK.listen(event)

    # Afficher les bons écrans
    if current_screen == MAIN_MENU:
        screen.blit(background, (0, 0))
        PLAY.hover()
        OPTIONS.hover()
        CREDITS.hover()
        EXIT.hover()
        PLAY.draw()
        OPTIONS.draw()
        CREDITS.draw()
        EXIT.draw()

    elif current_screen == PLAY_SCREEN:
        screen.blit(play_bg, (0, 0))
        BACK.hover()
        BACK.draw()

    elif current_screen == OPTIONS_SCREEN:
        screen.blit(options_bg, (0, 0))
        BACK.hover()
        BACK.draw()

    elif current_screen == CREDITS_SCREEN:
        screen.blit(credits_bg, (0, 0))
        BACK.hover()
        BACK.draw()

    pygame.display.update()
    clock.tick(60)