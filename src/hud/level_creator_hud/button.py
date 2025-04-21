import pygame

pygame.init()
font = pygame.font.SysFont("Arial", 20)


class Button:
    def __init__(self, position: pygame.Vector2, dimensions: pygame.Vector2, text: str, color: tuple = (69, 74, 237),
                 text_color: tuple = (255, 255, 255), font_size: int = 32, font_name: str = None,
                 toggled_color: tuple = None):
        self.rect = pygame.Rect(position.x, position.y, dimensions.x, dimensions.y)
        self.color = color
        self.basic_color = color
        self.toggled_color = toggled_color if toggled_color else color
        self.text = text
        self.text_color = text_color
        self.font = font if font else pygame.font.Font(font_name, font_size)
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        self.toggled = False

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surface, self.text_rect)

    def toggle(self):
        self.toggled = not self.toggled
        if self.toggled:
            self.color = self.toggled_color
        else:
            self.color = self.basic_color

    def contour(self, screen: pygame.Surface, color: tuple = (255, 0, 0)):
        pygame.draw.rect(screen, color, self.rect, 2)