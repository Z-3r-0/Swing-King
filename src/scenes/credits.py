import pygame.image

from src.scene import Scene, SceneType


class Credits(Scene):
    
    def __init__(self, screen, scene_from):
        super().__init__(screen, SceneType.CREDITS, "Credits", None)
        
        self.image = pygame.image.load("assets/images/background.png").convert()
        
        
    def run(self):
        super().run()
        
        self.screen.blit(self.image, (0,0))