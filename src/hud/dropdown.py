import json

import pygame
from pygame import Vector2

from src.hud.colors import Color
from src.hud.resizable_hud import ResizableHUD


class Dropdown(ResizableHUD):
    def __init__(self, screen, position: Vector2, size: Vector2, options, image, hovered_image):

        self.option_paths = options
        super().__init__(screen, position, size, image, hovered_image)

        self.resolutions = [(800, 600), (1280, 720), (1920, 1080)]
        self.resolution_index = 1  # Par défaut : 1280x720

        self.is_fullscreen = False
        
        self.selection = options[self.resolution_index]
        self.open = False

        self.options = [pygame.image.load(path).convert_alpha() for path in options]
        self.resize()

    def resize(self):
        
        super().resize()
        self.options = [pygame.transform.scale(pygame.image.load(path), (self.rect.width, self.rect.height))
                        for path in self.option_paths]


    def draw(self):
        
        mouse_pos = pygame.mouse.get_pos()
        current_image = self.hovered_image if self.rect.collidepoint(mouse_pos) else self.image
        self.screen.blit(current_image, self.rect.topleft)

        if self.open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + ((i + 1) * self.rect.height),
                    self.rect.width,
                    self.rect.height
                )
                self.screen.blit(option, option_rect.topleft)

    def display(self):
        pygame.draw.rect(self.screen, Color.green.value, self.rect)
        surface_text = self.police.render(self.selection, True, Color.white.value.value)
        rect_text = surface_text.get_rect(center=self.rect.center)
        self.screen.blit(surface_text, rect_text)

        if self.open:
            for i, option in enumerate(self.option_paths):
                rect_option = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width,
                                          self.rect.height)
                pygame.draw.rect(self.screen, Color.grey.value, rect_option)
                surface_text = self.police.render(option, True, Color.white.value)
                rect_text = surface_text.get_rect(center=rect_option.center)
                self.screen.blit(surface_text, rect_text)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.open = not self.open
        elif self.open:
            for i, _ in enumerate(self.options):
                rect_option = pygame.Rect(
                    self.rect.x,
                    self.rect.y + (i + 1) * self.rect.height,
                    self.rect.width,
                    self.rect.height
                )
                if rect_option.collidepoint(pos):
                    self.resolution_index = i
                    self.selection = self.option_paths[i]
                    LARGEUR, HAUTEUR = self.resolutions[i]
                    ECRAN = pygame.display.set_mode((LARGEUR, HAUTEUR),
                                                    pygame.FULLSCREEN if self.is_fullscreen else pygame.NOFRAME)
                    
                    # resize_elements() TODO - SEND EVENT TO RESIZE
                    
                    with open('data/settings/settings.json', 'r') as file:
                        data = json.load(file)
                        
                    data["graphics"]["resolution"]["width"] = self.resolutions[i][0]
                    data["graphics"]["resolution"]["height"] = self.resolutions[i][1]
                    
                    with open('data/settings/settings.json', 'w') as file:
                        json.dump(data, file, indent=4)
                    file.close()
                    self.open = False