import pygame

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
