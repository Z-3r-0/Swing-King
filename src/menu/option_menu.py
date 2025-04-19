import pygame
from pygame import Vector2

from src.hud import Button
from src.hud.dropdown import Dropdown
from src.hud.slider import Slider
from src.scene import Scene
from src.scenetype import SceneType


class OptionMenu(Scene):
    
    def __init__(self, screen, scene_from: SceneType = None):
        
        super().__init__(screen, SceneType.OPTIONS_MENU, "Options Menu", scene_from)
        
        self.volumes_sliders = {
            "Master": Slider(screen, Vector2(200, 100), Vector2(400, 20)),
            "Music": Slider(screen, Vector2(200, 160), Vector2(400, 20)),
            "SFX": Slider(screen, Vector2(200, 220), Vector2(400, 20)),
            "Voice": Slider(screen, Vector2(200, 280), Vector2(400, 20)),
        }

        self.fullscreen_btn = Button(screen, lambda: self.lambda_fullscreen(), Vector2(200, 340), Vector2(150, 50),
                                "assets/images/buttons/Option Menu/Fullscreen/Fullscreen.png",
                                "assets/images/buttons/Option Menu/Fullscreen/Fullscreen_Hovered.png",
                                "assets/images/buttons/Option Menu/Fullscreen/Fullscreen.png")

        self.menu_resolution = Dropdown(screen, Vector2(200, 400), Vector2(150, 50), [
            "assets/images/buttons/Option Menu/Resolution/800x600.png",
            "assets/images/buttons/Option Menu/Resolution/1280x720.png",
            "assets/images/buttons/Option Menu/Resolution/1920x1080.png"],
                                   "assets/images/buttons/Option Menu/Resolution/800x600.png",
                                   "assets/images/buttons/Option Menu/Resolution/800x600_Hovered.png")
        
        self.background = pygame.image.load("assets/images/backgrounds/background.jpg")
        
        self.resize_elements()


    def resize_elements(self):
        self.background = pygame.transform.scale(self.background, self.screen.get_size())

        for bar in self.volumes_sliders.values():
            bar.resize()
            
        self.fullscreen_btn.resize()
        self.menu_resolution.resize()

    def lambda_fullscreen(self):
        self.menu_resolution.is_fullscreen = not self.menu_resolution.is_fullscreen
        self.screen = pygame.display.set_mode(self.screen.get_size(), pygame.FULLSCREEN if self.menu_resolution.is_fullscreen else pygame.NOFRAME)
        self.resize_elements()
        
    def run(self):
        
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
        
                    self.menu_resolution.handle_click(event.pos)

                    self.fullscreen_btn.listen(event)
        
                if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                    for barre in self.volumes_sliders.keys():
                        if self.volumes_sliders[barre].rect.collidepoint(event.pos):
                            self.volumes_sliders[barre].save(event.pos[0], barre)
        
            for nom, barre in self.volumes_sliders.items():
                barre.draw(nom)

            self.fullscreen_btn.hover()

            self.fullscreen_btn.draw()
            self.menu_resolution.draw()
        
            pygame.display.flip()