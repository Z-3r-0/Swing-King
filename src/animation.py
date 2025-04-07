import os
import pygame


class Animation(pygame.sprite.Sprite):

    def __init__(self, source_dir: str, position: pygame.Vector2, animation_speed: float = 0.1):
        super().__init__()  # Call the parent class (Sprite) constructor

        self.sprites = []

        # Load all images from the specified directory
        for file in os.listdir(source_dir):
            if file.endswith('.png'):
                image = pygame.image.load(os.path.join(source_dir, file)).convert_alpha()
                self.sprites.append(image)

        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.position = position
        self.rect.topleft = (int(position.x), int(position.y))

        self.animation_speed = animation_speed

    def update(self):
        self.current_sprite += self.animation_speed

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]