# animation.py
import os
import pygame


class Animation(pygame.sprite.Sprite):

    def __init__(self, source_dir: str, world_position: pygame.Vector2,
                 animation_speed: float = 0.1):
        super().__init__()

        self.sprites = []

        # Load all images from the specified directory
        for file in os.listdir(source_dir):
            if file.endswith('.png'):
                image = pygame.image.load(os.path.join(source_dir, file)).convert_alpha()
                self.sprites.append(image)

        if not self.sprites:
            # Fallback if no images are loaded, to prevent crashing
            print(f"Warning: No sprites loaded from {source_dir}. Creating a placeholder.")
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            self.image.fill((255, 0, 255, 128))
            self.sprites.append(self.image)

        self.current_sprite_index = 0.0
        self.image = self.sprites[int(self.current_sprite_index)]
        self.rect = self.image.get_rect()

        self.world_position = world_position.copy()
        self.rect.topleft = (
        int(self.world_position.x), int(self.world_position.y))  # Initial rect based on world_position

        self.animation_speed = animation_speed

    def update_animation_frame(self):
        """Advances the animation to the next frame."""
        self.current_sprite_index = (self.current_sprite_index + self.animation_speed) % len(self.sprites)
        self.image = self.sprites[int(self.current_sprite_index)]
        current_topleft = self.rect.topleft
        self.rect = self.image.get_rect()
        self.rect.topleft = current_topleft

    def update_screen_position(self, screen_position_topleft: pygame.Vector2):
        """Updates the sprite's rect.topleft for drawing at a specific screen position."""
        self.rect.topleft = (int(screen_position_topleft.x), int(screen_position_topleft.y))