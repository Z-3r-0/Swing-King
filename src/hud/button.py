import pygame

from src.hud.resizable_hud import ResizableHUD


class Button(ResizableHUD):
    def __init__(self, screen, func, position, size, image_path, hovered_image_path, clicked_image_path):
        
        super().__init__(screen, position, size, image_path, hovered_image_path)
        
        self.screen = screen
        self.func = func  # Function to execute on click
        self.position = position
        self.size = size

        # Load images
        self.image = pygame.image.load(image_path).convert_alpha()
        self.hovered_image = pygame.image.load(hovered_image_path).convert_alpha()
        self.clicked_image = pygame.image.load(clicked_image_path).convert_alpha()

        self.image = pygame.transform.smoothscale(self.image, self.size)
        self.hovered_image = pygame.transform.smoothscale(self.hovered_image, self.size)
        self.clicked_image = pygame.transform.smoothscale(self.clicked_image, self.size)

        self.rendered_image = self.image.copy()
        self.rect = pygame.Rect(self.position, self.size)

        self.clicked = False  # Prevents multiple clicks

    def hover(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.rendered_image = self.hovered_image.copy()
        else:
            self.rendered_image = self.image.copy()

    def listen(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.rendered_image = self.clicked_image.copy()
                self.clicked = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.clicked and self.rect.collidepoint(event.pos):
                self.func()
            self.clicked = False  # Click reset

    def draw(self):
        self.screen.blit(self.rendered_image, self.position)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
        
    def resize(self):
        super().resize()
