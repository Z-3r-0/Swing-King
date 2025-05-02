from pygame import Vector2
from pygame import mixer
from src.hud.button import *

from src.scene import Scene
from src.scenetype import SceneType

from src.hud import Button


class Menu(Scene):

    def __init__(self, screen):  # Doesn't make sense to be able to go back to a scene from main menu
        super().__init__(screen, SceneType.MAIN_MENU, "Main menu", None)

        self.background = pygame.image.load("assets/images/backgrounds/swing_king_1.png").convert()
        self.play_bg = pygame.image.load("assets/images/backgrounds/swing_king_1.png").convert()
        self.options_bg = pygame.image.load("assets/images/backgrounds/swing_king_1.png").convert()
        self.credits_bg = pygame.image.load("assets/images/backgrounds/swing_king_credits.png").convert()

        self.credits = pygame.image.load("assets/images/backgrounds/swing_king_credits.png").convert()

        self.PLAY = Button(screen, lambda: self.switch_scene(SceneType.LEVEL_SELECTOR), Vector2(825, 520), Vector2(270, 80),
                           "assets/images/buttons/menus/main/play/play.png",
                           "assets/images/buttons/menus/main/play/play_hovered.png",
                           "assets/images/buttons/menus/main/play/play_clicked.png")
        self.OPTIONS = Button(screen, lambda: self.switch_scene(SceneType.OPTIONS_MENU), Vector2(825, 610),
                              Vector2(270, 80),
                              "assets/images/buttons/menus/main/options/options.png",
                              "assets/images/buttons/menus/main/options/options_hovered.png",
                              "assets/images/buttons/menus/main/options/options_clicked.png")
        self.CREDITS = Button(screen, lambda: self.switch_scene(SceneType.CREDITS), Vector2(825, 700), Vector2(270, 80),
                              "assets/images/buttons/menus/main/credits/credits.png",
                              "assets/images/buttons/menus/main/credits/credits_hovered.png",
                              "assets/images/buttons/menus/main/credits/credits_clicked.png")
        self.LEVEL_CREATOR = Button(screen, lambda: self.switch_scene(SceneType.LEVEL_CREATOR), Vector2(825, 790),
                                    Vector2(270, 80),
                                    "assets/images/buttons/menus/main/credits/credits.png",
                                    "assets/images/buttons/menus/main/credits/credits_hovered.png",
                                    "assets/images/buttons/menus/main/credits/credits_clicked.png"
                                    )
        self.EXIT = Button(screen, lambda: pygame.quit(), Vector2(825, 880), Vector2(270, 80),
                           "assets/images/buttons/menus/main/exit/exit.png",
                           "assets/images/buttons/menus/main/exit/exit_hovered.png",
                           "assets/images/buttons/menus/main/exit/exit_clicked.png")
        # self.BACK = Button(screen, lambda: self.switch_scene(), (825, 640), (270, 80),
        #               "assets/images/buttons/menus/main/back/back.png",
        #               "assets/images/buttons/menus/main/back/back_hovered.png",
        #               "assets/images/buttons/menus/main/back/back_clicked.png")

        self.buttons = [self.PLAY, self.OPTIONS, self.CREDITS, self.LEVEL_CREATOR, self.EXIT]

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
            self.clock.tick(self.fps)

    def resize_elements(self):

        self.background = pygame.transform.scale(self.background, self.screen.get_size())
