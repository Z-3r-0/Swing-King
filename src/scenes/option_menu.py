import pygame
from pygame import Vector2

from src.utils.settings_loader import *
from src.hud import Button
from src.hud.slider import Slider
from src.scene import Scene, SceneType

class OptionMenu(Scene):
    
    def __init__(self, screen, scene_from: SceneType = None):
        
        super().__init__(screen, SceneType.OPTIONS_MENU, "Options menu", scene_from)

        self.volumes_sliders = {
            "Master": Slider(screen, Vector2(((screen.get_width()/2)-screen.get_width()/8), screen.get_height()/4), Vector2(400, 20),load_json_settings('data/settings/settings.json')["audio"]["Master"]),
            "Music": Slider(screen, Vector2(((screen.get_width()/2)-screen.get_width()/8), screen.get_height()/4+screen.get_height()/16), Vector2(400, 20),load_json_settings('data/settings/settings.json')["audio"]["Music"]),
            "SFX": Slider(screen, Vector2(((screen.get_width()/2)-screen.get_width()/8), screen.get_height()/4+screen.get_height()/8), Vector2(400, 20),load_json_settings('data/settings/settings.json')["audio"]["SFX"]),
        }

        self.fullscreen_btn = Button(screen, lambda: self.lambda_fullscreen(), Vector2(((screen.get_width()/2)-screen.get_width()/16), screen.get_height()/2), Vector2(270, 80),
                                "assets/images/buttons/menus/option/fullscreen/fullscreen.png",
                                "assets/images/buttons/menus/option/fullscreen/Fullscreen_Hovered.png",
                                "assets/images/buttons/menus/option/fullscreen/fullscreen.png")

        self.back_btn = Button(screen, lambda: self.switch_scene(self.scene_from), Vector2(((screen.get_width()/2)-screen.get_width()/16), screen.get_height()/2+screen.get_height()/4), Vector2(270, 80),
                      "assets/images/buttons/menus/main/back/back.png",
                      "assets/images/buttons/menus/main/back/back_hovered.png",
                      "assets/images/buttons/menus/main/back/back_clicked.png")
        
        self.buttons = [self.fullscreen_btn, self.back_btn]
        
        self.background = pygame.image.load("assets/images/backgrounds/swing_king_1.png")
        
        self.resize_elements()

    def resize_elements(self):
        self.background = pygame.transform.scale(self.background, self.screen.get_size())

        for bar in self.volumes_sliders.values():
            bar.resize()
            
        self.fullscreen_btn.resize()

    def lambda_fullscreen(self):
        self.screen = pygame.display.set_mode(self.screen.get_size(), pygame.FULLSCREEN)
        self.resize_elements()
        
    def run(self):
        
        super().run()
        
        while self.running:
            self.screen.blit(self.background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for barre in self.volumes_sliders.keys():
                        if self.volumes_sliders[barre].rect.collidepoint(event.pos):
                            self.volumes_sliders[barre].save(event.pos[0], barre)

                    
                    for button in self.buttons:
                        button.listen(event)

                if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                    for barre in self.volumes_sliders.keys():
                        if self.volumes_sliders[barre].rect.collidepoint(event.pos):
                            self.volumes_sliders[barre].save(event.pos[0], barre)

            for nom, barre in self.volumes_sliders.items():
                barre.draw(nom)
            
            for button in self.buttons:
                button.hover()
                button.draw()

        
            pygame.display.flip()