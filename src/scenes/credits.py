import sys

import pygame.image
from pygame import Vector2

from src.hud import Button
from src.scene import Scene, SceneType


class Credits(Scene):
    
    def __init__(self, screen, scene_from):
        super().__init__(screen, SceneType.CREDITS, "Credits", None)
        
        self.background = pygame.image.load("assets/images/backgrounds/credits.png").convert()
        self.background = pygame.transform.scale(self.background, self.screen.get_size())

        button_size = Vector2(270, 80)

        pos_x = screen.get_width() / 2 - button_size.x / 2
        pos_y = screen.get_height() / 2 - button_size.y / 2
        
        self.back = Button(self.screen, lambda: self.switch_scene(self.scene_from), Vector2(pos_x, pos_y + 425), button_size,
                                       "assets/images/buttons/menus/main/back/back.png",
                                       "assets/images/buttons/menus/main/back/back_hovered.png",
                                       "assets/images/buttons/menus/main/back/back_clicked.png"
                                       )
        
    def run(self):
        super().run()
        
        while self.running:
            self.screen.blit(self.background, (0,0))
    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
    
                self.back.listen(event)
            
    
            self.back.hover()
    
            self.draw()
    
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        
        
        
    def draw(self):
        self.back.draw()