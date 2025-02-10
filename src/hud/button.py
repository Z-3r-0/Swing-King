import pygame
import time

import pygame
'''''''''''
#CG1
class Button:
    def __init__(self, screen, func, position, size, image_path, hovered_image_path, clicked_image_path):
        self.screen = screen
        self.func = func  # Fonction à appeler lors du clic
        self.position = position
        self.size = size

        # Charger les images
        self.image = pygame.image.load(image_path).convert_alpha()
        self.hovered_image = pygame.image.load(hovered_image_path).convert_alpha()
        self.clicked_image = pygame.image.load(clicked_image_path).convert_alpha()

        self.image = pygame.transform.smoothscale(self.image, self.size)
        self.hovered_image = pygame.transform.smoothscale(self.hovered_image, self.size)
        self.clicked_image = pygame.transform.smoothscale(self.clicked_image, self.size)

        self.rendered_image = self.image.copy()
        self.rect = pygame.Rect(self.position, self.size)

        self.clicked = False  # ⚠️ Empêche les clics multiples
        self.hovered = False  # État du survol

    def hover(self):
        """Change l'image du bouton si la souris passe dessus"""
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.rendered_image = self.hovered_image.copy()
            self.hovered = True
        else:
            self.rendered_image = self.image.copy()
            self.hovered = False

    def listen(self, event):
        """Écoute les événements (doit être appelée dans la boucle principale)"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.rendered_image = self.clicked_image.copy()
                self.clicked = True  # Marque le bouton comme cliqué

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.clicked and self.rect.collidepoint(event.pos):
                self.func()  # 🚀 Exécute l'action
            self.clicked = False  # Réinitialise après le clic

    def draw(self):
        """Affiche le bouton sur l'écran"""
        self.screen.blit(self.rendered_image, self.position)


'''''''''




'''''''''
#Lu
class Button:
    def __init__(self, screen, func, position: pygame.Vector2, size: pygame.Vector2, image_path: str,hovered_image_path: str,clicked_image_path):
        """
        Initializes a Button instance with the given parameters.
        :param screen: pygame screen
        :param func: function to be called
        :param position: position of the button
        :param size: size of the button
        :param image_path: path to image
        """
        self.screen = screen
        self.func = func
        self.position = position
        self.size = size

        self.imagePath = image_path



        self.rect = pygame.Rect(self.position, self.size)


        self.image = pygame.image.load(image_path).convert_alpha()
        self.hovered_image = pygame.image.load(hovered_image_path).convert_alpha()
        self.clicked_image = pygame.image.load(clicked_image_path).convert_alpha()


        self.image = pygame.transform.smoothscale(self.image, self.size)
        self.hovered_image = pygame.transform.smoothscale(self.hovered_image, self.size)
        self.clicked_image = pygame.transform.smoothscale(self.clicked_image, self.size)

        self.rendered_image = self.image.copy()

        self.rect = pygame.Rect(self.position, self.size)
        self.clicked = False
        self.enabled = True
        self.debounce = False

    def hover(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.rendered_image = self.hovered_image.copy()
        else :
            self.rendered_image = self.image.copy()


    def listen(self,func):
        """
        Listens for mouse clicks on the button and triggers the button's function if clicked.
        """
        self.hover()
        self.click()
        func()

    def draw(self, surface):
        """
        Draws the button on the specified surface.
        :param surface: Surface to draw the button on.
        """

        surface.blit(self.rendered_image, self.position)

    def click3(self, func):
        """
        Triggers the button's click effect and executes the provided function.
        :param func: function to be called
        """
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.rendered_image = self.clicked_image.copy()
            func()
        else :
            self.hover()

    def click(self):

        if not self.enabled:
            return

        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                if not self.debounce:
                    self.rendered_image = self.clicked_image.copy()
                    return True

                    self.debounce = True
            else:
                self.debounce = False  # Reset debounce when the mouse button is released
        else:
            self.hover()  # Revert to hover state if not clicked
'''''''''

import pygame

class Button:
    def __init__(self, screen, func, position, size, image_path, hovered_image_path, clicked_image_path):
        self.screen = screen
        self.func = func  # Fonction à exécuter lors du clic
        self.position = position
        self.size = size

        # Charger les images
        self.image = pygame.image.load(image_path).convert_alpha()
        self.hovered_image = pygame.image.load(hovered_image_path).convert_alpha()
        self.clicked_image = pygame.image.load(clicked_image_path).convert_alpha()

        self.image = pygame.transform.smoothscale(self.image, self.size)
        self.hovered_image = pygame.transform.smoothscale(self.hovered_image, self.size)
        self.clicked_image = pygame.transform.smoothscale(self.clicked_image, self.size)

        self.rendered_image = self.image.copy()
        self.rect = pygame.Rect(self.position, self.size)

        self.clicked = False  # Empêche les clics multiples

    def hover(self):
        """Change l'image si la souris passe dessus"""
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.rendered_image = self.hovered_image.copy()
        else:
            self.rendered_image = self.image.copy()

    def listen(self, event):
        """Écoute les événements et déclenche la fonction si cliqué"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.rendered_image = self.clicked_image.copy()
                self.clicked = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.clicked and self.rect.collidepoint(event.pos):
                self.func()  # Exécute la fonction
            self.clicked = False  # Réinitialisation du clic

    def draw(self):
        """Affiche le bouton"""
        self.screen.blit(self.rendered_image, self.position)
