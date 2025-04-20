import pygame
from pygame import Vector2


class ResizableHUD:
    
    def __init__(self, screen: pygame.Surface, position: Vector2, size: Vector2, image = None, hovered_image = None):
        
        self.screen = screen
        self.position = position
        self.size = size

        self.resolution = Vector2(screen.get_size())

        self.position_ratio = Vector2(position.x / self.resolution.x, position.y / self.resolution.y)
        self.size_ratio = Vector2(size.x / self.resolution.x, size.y / self.resolution.y)

        self.rect = pygame.Rect(
            int(self.position_ratio.x * self.resolution.x),
            int(self.position_ratio.y * self.resolution.y),
            int(self.size_ratio.x * self.resolution.x),
            int(self.size_ratio.y * self.resolution.y)
        )
        
        self.image = image
        self.hovered_image = hovered_image

        self.police = pygame.font.SysFont("Arial", 20)
        
        if image:
            self.image = pygame.image.load(image).convert_alpha()
        if hovered_image:
            self.hovered_image = pygame.image.load(hovered_image).convert_alpha()
            
        self.resize()
    
    def resize(self):
        self.rect = pygame.Rect(
            int(self.position_ratio.x * self.resolution.x),
            int(self.position_ratio.y * self.resolution.y),
            int(self.size_ratio.x * self.resolution.x),
            int(self.size_ratio.y * self.resolution.y)
        )

        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height)) if self.image else None
        self.hovered_image = pygame.transform.scale(self.hovered_image, (self.rect.width, self.rect.height)) if self.hovered_image else None