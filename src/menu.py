import sys
import pygame
from pygame import mouse
from pygame import mixer
from src.hud.button import *

pygame.init()


from hud import Button

pygame.display.set_caption('SwingKing main menu')
screen = pygame.display.set_mode((1300, 755))

background = pygame.image.load("../assets/images/backgrounds/SwingKing1.png").convert()
play_bg = pygame.image.load("../assets/images/backgrounds/SwingKing1.png").convert()
options_bg = pygame.image.load("../assets/images/backgrounds/SwingKing1.png").convert()
credits_bg = pygame.image.load("../assets/images/backgrounds/SwingKing1CREDITS.png").convert()

mixer.music.load("../assets/audio/music/SwingKing.mp3")
mixer.music.set_volume(0.5)

def play_music():
    mixer.music.play()
    


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
play_music()
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
        barres_button = {
            "Master": BarreVolume(200, 100, 400, 20),
            "Music": BarreVolume(200, 160, 400, 20),
            "SFX": BarreVolume(200, 220, 400, 20),
            "Voice": BarreVolume(200, 280, 400, 20),
        }

        bouton_fullscreen = Bouton(200, 340, 150, 50,
                                   "../assets/images/buttons/Option Menu/Fullscreen/Fullscreen.png",
                                   "../assets/images/buttons/Option Menu/Fullscreen/Fullscreen_Hovered.png",
                                   "../assets/images/buttons/Option Menu/Fullscreen/Fullscreen.png")
        menu_resolution = MenuDeroulant(200, 400, 150, 50, [
            "../assets/images/buttons/Option Menu/Resolution/800x600.png",
            "../assets/images/buttons/Option Menu/Resolution/1280x720.png",
            "../assets/images/buttons/Option Menu/Resolution/1920x1080.png"],
                                        "../assets/images/buttons/Option Menu/Resolution/800x600.png",
                                        "../assets/images/buttons/Option Menu/Resolution/800x600_Hovered.png")

        background = pygame.image.load("../assets/images/backgrounds/background.jpg")
        plein_ecran = False


        def redimensionner_elements():
            # Redimensionner le fond d'écran
            global background
            background = pygame.transform.scale(pygame.image.load("../assets/images/backgrounds/background.jpg"),
                                                (LARGEUR, HAUTEUR))

            # Redimensionner les autres éléments
            for barre in barres_button.values():
                barre.redimensionner()
            bouton_fullscreen.redimensionner()
            menu_resolution.redimensionner()


        redimensionner_elements()
        running = True
        while running:
            ECRAN.blit(background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for barre in barres_button.keys():
                        if barres_button[barre].rect.collidepoint(event.pos):
                            barres_button[barre].ajuster(event.pos[0], barre)

                    if bouton_fullscreen.est_clique(event.pos):
                        plein_ecran = not plein_ecran
                        ECRAN = pygame.display.set_mode((LARGEUR, HAUTEUR),
                                                        pygame.FULLSCREEN if plein_ecran else pygame.RESIZABLE)
                        redimensionner_elements()

                    menu_resolution.gerer_clic(event.pos)

                if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                    for barre in barres_button.keys():
                        if barres_button[barre].rect.collidepoint(event.pos):
                            barres_button[barre].ajuster(event.pos[0], barre)

            for nom, barre in barres_button.items():
                barre.afficher(ECRAN, nom)

            bouton_fullscreen.draw(ECRAN)
            menu_resolution.draw(ECRAN)

            pygame.display.flip()

        pygame.quit()
        screen.blit(options_bg, (0, 0))
        BACK.hover()
        BACK.draw()

    elif current_screen == CREDITS_SCREEN:
        screen.blit(credits_bg, (0, 0))
        BACK.hover()
        BACK.draw()

    pygame.display.update()
    clock.tick(60)