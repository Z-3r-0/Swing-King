from pygame import Vector2
from pygame import mixer
from src.hud.button import *

from src.scene import Scene, SceneType

from src.hud import Button


class Menu(Scene):

    def __init__(self, screen):  # Doesn't make sense to be able to go back to a scene from main menu
        super().__init__(screen, SceneType.MAIN_MENU, "Main menu", None)

        self.background = pygame.image.load("assets/images/backgrounds/swing_king_1.png").convert()
        self.play_bg = pygame.image.load("assets/images/backgrounds/swing_king_1.png").convert()
        self.options_bg = pygame.image.load("assets/images/backgrounds/swing_king_1.png").convert()

        button_size = Vector2(270, 80)

        pos_x = screen.get_width() / 2 - button_size.x / 2
        pos_y = screen.get_height() / 2 - button_size.y / 2

        self.PLAY = Button(screen, lambda: self.switch_scene(SceneType.LEVEL_SELECTOR), Vector2(pos_x, pos_y), Vector2(270, 80),
                           "assets/images/buttons/menus/main/play/play.png",
                           "assets/images/buttons/menus/main/play/play_hovered.png",
                           "assets/images/buttons/menus/main/play/play_clicked.png")
        self.OPTIONS = Button(screen, lambda: self.switch_scene(SceneType.OPTIONS_MENU), Vector2(pos_x, pos_y + 90),
                              Vector2(270, 80),
                              "assets/images/buttons/menus/main/options/options.png",
                              "assets/images/buttons/menus/main/options/options_hovered.png",
                              "assets/images/buttons/menus/main/options/options_clicked.png")
        self.LEVEL_CREATOR = Button(screen, lambda: self.switch_scene(SceneType.LEVEL_CREATOR),
                                    Vector2(pos_x, pos_y + 180),
                                    Vector2(270, 80),
                                    "assets/images/buttons/menus/main/level_creator/levelcreator.png",
                                    "assets/images/buttons/menus/main/level_creator/levelcreator_hovered.png",
                                    "assets/images/buttons/menus/main/level_creator/levelcreator_clicked.png"
                                    )
        self.CREDITS = Button(screen, lambda: self.switch_scene(SceneType.CREDITS), Vector2(pos_x, pos_y + 270), Vector2(270, 80),
                              "assets/images/buttons/menus/main/credits/credits.png",
                              "assets/images/buttons/menus/main/credits/credits_hovered.png",
                              "assets/images/buttons/menus/main/credits/credits_clicked.png")
        self.EXIT = Button(screen, lambda: pygame.quit(), Vector2(pos_x, pos_y + 360), Vector2(270, 80),
                           "assets/images/buttons/menus/main/exit/exit.png",
                           "assets/images/buttons/menus/main/exit/exit_hovered.png",
                           "assets/images/buttons/menus/main/exit/exit_clicked.png")

        self.buttons = [self.PLAY, self.OPTIONS, self.CREDITS, self.LEVEL_CREATOR, self.EXIT]

        pygame.mixer.music.load("assets/audio/music/SwingKing.mp3")
        pygame.mixer.music.set_volume(0.5)

        self.resize_elements()

    def run(self):
        super().run()
        
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
