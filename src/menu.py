import pygame
from pygame import mouse
from pygame import mixer
from src.hud.button import *

pygame.init()


from hud import Button

pygame.display.set_caption('SwingKing main menu')
screen = pygame.display.set_mode((1300, 755))

from src.hud import Button
from src.scene import Scene
from src.scenetype import SceneType
from src.events import events

class Menu(Scene):

    def __init__(self, screen):
        super().__init__(SceneType.MAIN_MENU, "Main menu", screen)

        self.background = pygame.image.load("assets/images/backgrounds/SwingKing1.png").convert()
        self.play_bg = pygame.image.load("assets/images/backgrounds/SwingKing1.png").convert()
        self.options_bg = pygame.image.load("assets/images/backgrounds/SwingKing1.png").convert()
        self.credits_bg = pygame.image.load("assets/images/backgrounds/SwingKing1CREDITS.png").convert()

        self.credits = pygame.image.load("assets/images/backgrounds/SwingKing1CREDITS.png").convert()

        self.PLAY = Button(screen, lambda: self.switch_scene(SceneType.GAME), (532, 370), (270, 80),
                      "assets/images/buttons/Main Menu/play/PLAY.png",
                      "assets/images/buttons/Main Menu/play/PLAY_HOVERED.png",
                      "assets/images/buttons/Main Menu/play/PLAY_CLICKED.png")
        self.OPTIONS = Button(screen, lambda: self.switch_scene(SceneType.OPTIONS_MENU), (532, 460), (270, 80),
                         "assets/images/buttons/Main Menu/options/OPTIONS.png",
                         "assets/images/buttons/Main Menu/options/OPTIONS_HOVERED.png",
                         "assets/images/buttons/Main Menu/options/OPTIONS_CLICKED.png")
        self.CREDITS = Button(screen, lambda: self.switch_scene(SceneType.CREDITS), (532, 550), (270, 80),
                         "assets/images/buttons/Main Menu/credits/CREDITS.png",
                         "assets/images/buttons/Main Menu/credits/CREDITS_HOVERED.png",
                         "assets/images/buttons/Main Menu/credits/CREDITS_CLICKED.png")
        self.EXIT = Button(screen, lambda: pygame.quit(), (532, 640), (270, 80),
                      "assets/images/buttons/Main Menu/exit/EXIT.png",
                      "assets/images/buttons/Main Menu/exit/EXIT_HOVERED.png",
                      "assets/images/buttons/Main Menu/exit/EXIT_CLICKED.png")
        # self.BACK = Button(screen, lambda: self.switch_scene(), (532, 640), (270, 80),
        #               "assets/images/buttons/Main Menu/back/BACK.png",
        #               "assets/images/buttons/Main Menu/back/BACK_HOVERED.png",
        #               "assets/images/buttons/Main Menu/back/BACK_CLICKED.png")

        self.buttons = [self.PLAY, self.OPTIONS, self.CREDITS, self.EXIT]

        pygame.mixer.music.load("assets/audio/music/SwingKing.mp3")
        pygame.mixer.music.set_volume(0.5)

    def switch_scene(self, scene: SceneType):
        self.running = False
        pygame.event.post(pygame.event.Event(events[scene]))

    def run(self):
        self.running = True

        while self.running:
            self.screen.blit(self.background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                for button in self.buttons:
                    button.listen(event)

            for button in self.buttons:
                button.hover()
                button.draw()

            pygame.display.flip()
            pygame.time.Clock().tick(60)
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
