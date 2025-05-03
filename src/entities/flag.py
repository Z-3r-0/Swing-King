import pygame
from pygame import Vector2

from src import Animation
from src.entities.interactable import Interactable, InteractableType


class Flag:
    """
        This class defines the flag (or end of level) object designed to register when a level has been finished.
    """

    def __init__(self, position: Vector2, angle: int = 0):
        
        self.position = position.copy()
        self.angle = angle
        self.height = 110  # 110 is the height of the flag sprite
        
        self.animation = Animation('assets/images/flag', self.position)
        self.animation_sprite = pygame.sprite.Group()
        self.animation_sprite.add(self.animation)
    
    def draw(self, screen):
        self.animation.update()
        self.animation_sprite.draw(screen)