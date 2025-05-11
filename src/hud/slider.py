import json
import pygame
from pygame import Vector2

from src.hud.colors import Color
from src.hud.resizable_hud import ResizableHUD

class Slider(ResizableHUD):
    def __init__(self, screen, position: Vector2, size: Vector2, value=50):
        super().__init__(screen, position, size)
        self.value = value
        self.resize()

    def resize(self):
        super().resize()

    def draw(self, text):
        
        pygame.draw.rect(self.screen, Color.grey.value, self.rect)
        filling = pygame.Rect(self.rect.x, self.rect.y, self.rect.width * (self.value / 100), self.rect.height)
        
        pygame.draw.rect(self.screen, Color.blue.value, filling)
    
        if hasattr(self, 'police'):
            surface_text = self.police.render(f"{text}: {self.value}%", True, Color.cyan.value)
            bg_rect = pygame.Surface((100, 25), pygame.SRCALPHA)
            bg_rect.fill((0, 0, 0, 150))
            self.screen.blit(bg_rect, (self.rect.x, self.rect.y - 30))
            self.police.set_bold(True)
            self.screen.blit(surface_text, (self.rect.x, self.rect.y - 30))
        else:
            print("Error: self.police is not defined!")

    def save(self, pos_x, name):
        if self.rect.x <= pos_x <= self.rect.x + self.rect.width:
            self.value = int(((pos_x - self.rect.x) / self.rect.width) * 100)
        with open('data/settings/settings.json', 'r') as file:
            data = json.load(file)
        data["audio"][name] = self.value
        with open('data/settings/settings.json', 'w') as file:
            json.dump(data, file, indent=4)
        file.close()