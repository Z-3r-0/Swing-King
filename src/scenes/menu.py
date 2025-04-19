from pygame import Vector2
from pygame import mixer
from src.hud.button import *

from src.scene import Scene
from src.scenetype import SceneType

from src.hud import Button

class Menu(Scene):

    def __init__(self, screen):  # Doesn't make sense to be able to go back to a scene from main menu
        super().__init__(screen, SceneType.MAIN_MENU, "Main menu", None)

        self.background = pygame.image.load("assets/images/backgrounds/SwingKing1.png").convert()
        self.play_bg = pygame.image.load("assets/images/backgrounds/SwingKing1.png").convert()
        self.options_bg = pygame.image.load("assets/images/backgrounds/SwingKing1.png").convert()
        self.credits_bg = pygame.image.load("assets/images/backgrounds/SwingKing1CREDITS.png").convert()

        self.credits = pygame.image.load("assets/images/backgrounds/SwingKing1CREDITS.png").convert()

        self.PLAY = Button(screen, lambda: self.switch_scene(SceneType.GAME), Vector2(825, 520), Vector2(270, 80),
                      "assets/images/buttons/Main Menu/play/PLAY.png",
                      "assets/images/buttons/Main Menu/play/PLAY_HOVERED.png",
                      "assets/images/buttons/Main Menu/play/PLAY_CLICKED.png")
        self.OPTIONS = Button(screen, lambda: self.switch_scene(SceneType.OPTIONS_MENU), Vector2(825, 610), Vector2(270, 80),
                         "assets/images/buttons/Main Menu/options/OPTIONS.png",
                         "assets/images/buttons/Main Menu/options/OPTIONS_HOVERED.png",
                         "assets/images/buttons/Main Menu/options/OPTIONS_CLICKED.png")
        self.CREDITS = Button(screen, lambda: self.switch_scene(SceneType.CREDITS), Vector2(825, 700), Vector2(270, 80),
                         "assets/images/buttons/Main Menu/credits/CREDITS.png",
                         "assets/images/buttons/Main Menu/credits/CREDITS_HOVERED.png",
                         "assets/images/buttons/Main Menu/credits/CREDITS_CLICKED.png")
        self.EXIT = Button(screen, lambda: pygame.quit(), Vector2(825, 790), Vector2(270, 80),
                      "assets/images/buttons/Main Menu/exit/EXIT.png",
                      "assets/images/buttons/Main Menu/exit/EXIT_HOVERED.png",
                      "assets/images/buttons/Main Menu/exit/EXIT_CLICKED.png")
        # self.BACK = Button(screen, lambda: self.switch_scene(), (825, 640), (270, 80),
        #               "assets/images/buttons/Main Menu/back/BACK.png",
        #               "assets/images/buttons/Main Menu/back/BACK_HOVERED.png",
        #               "assets/images/buttons/Main Menu/back/BACK_CLICKED.png")

        self.buttons = [self.PLAY, self.OPTIONS, self.CREDITS, self.EXIT]

        pygame.mixer.music.load("assets/audio/music/SwingKing.mp3")
        pygame.mixer.music.set_volume(0.5)
        
        self.resize_elements()

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
            pygame.time.Clock().tick(self.fps)
            
    def resize_elements(self):
        
        self.background = pygame.transform.scale(self.background, self.screen.get_size())