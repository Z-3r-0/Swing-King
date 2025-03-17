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


PLAY = Button(screen, lambda: go_to_play(), (532,370), (270,80), "../assets/images/buttons/Main Menu/play/PLAY.png",
              "../assets/images/buttons/Main Menu/play/PLAY_HOVERED.png",
              "../assets/images/buttons/Main Menu/play/PLAY_CLICKED.png")
OPTIONS = Button(screen, lambda: go_to_options(), (532,460), (270,80),
                 "../assets/images/buttons/Main Menu/options/OPTIONS.png",
                 "../assets/images/buttons/Main Menu/options/OPTIONS_HOVERED.png",
                 "../assets/images/buttons/Main Menu/options/OPTIONS_CLICKED.png")
CREDITS = Button(screen, lambda : go_to_credits(), (532,550), (270,80),
                 "../assets/images/buttons/Main Menu/credits/CREDITS.png",
                 "../assets/images/buttons/Main Menu/credits/CREDITS_HOVERED.png",
                 "../assets/images/buttons/Main Menu/credits/CREDITS_CLICKED.png")
EXIT = Button(screen, lambda: exit_function(), (532,640), (270,80), "../assets/images/buttons/Main Menu/exit/EXIT.png",
              "../assets/images/buttons/Main Menu/exit/EXIT_HOVERED.png",
              "../assets/images/buttons/Main Menu/exit/EXIT_CLICKED.png")
BACK = Button(screen, lambda: go_to_menu(), (532,640), (270,80), "../assets/images/buttons/Main Menu/back/BACK.png",
              "../assets/images/buttons/Main Menu/back/BACK_HOVERED.png",
              "../assets/images/buttons/Main Menu/back/BACK_CLICKED.png")

running = True

while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


        if current_screen == MAIN_MENU:
            PLAY.listen(event)
            OPTIONS.listen(event)
            CREDITS.listen(event)
            EXIT.listen(event)
        elif current_screen in {PLAY_SCREEN, OPTIONS_SCREEN, CREDITS_SCREEN}:
            BACK.listen(event)

    # affichage des différetnes scènes
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