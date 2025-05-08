# flag.py
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

        self.animation = Animation('assets/images/flag', self.position)
        self.animation_sprite_group = pygame.sprite.GroupSingle()
        self.animation_sprite_group.add(self.animation)

    def draw(self, screen: pygame.Surface, camera_offset: pygame.Vector2):
        """Draws the flag on the screen, adjusted by camera_offset."""
        self.animation.update_animation_frame()

        screen_pos_x = self.position.x - camera_offset.x
        screen_pos_y = self.position.y - camera_offset.y

        self.animation.update_screen_position(pygame.Vector2(screen_pos_x, screen_pos_y))

        self.animation_sprite_group.draw(screen)

    def get_world_rect(self) -> pygame.Rect:
        return pygame.Rect(self.animation.world_position, self.animation.image.get_size())