import pygame
class Button:
    def __init__(self, screen, func, position, size, image_path, hovered_image_path, clicked_image_path):
        self.screen = screen
        self.func = func  # Function to execute on click
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


import pygame
import json

# Initialisation de pygame
pygame.init()

# Résolutions possibles
RESOLUTIONS = [(800, 600), (1280, 720), (1920, 1080)]
resolution_index = 1  # Par défaut : 1280x720
LARGEUR, HAUTEUR = RESOLUTIONS[resolution_index]

# Création de la fenêtre (commence en mode fenêtré)
ECRAN = pygame.display.set_mode((LARGEUR, HAUTEUR), pygame.RESIZABLE)
pygame.display.set_caption("Menu Options")

# Couleurs
BLANC = (255, 255, 255)
NOIR = (20, 20, 20)
BLEU = (0, 122, 255)
GRIS = (100, 100, 100)
ROUGE = (200, 50, 50)
VERT = (50, 200, 50)

# Police
police = pygame.font.Font(None, 36)

class BarreVolume:
    def __init__(self, x, y, largeur, hauteur, valeur=50):
        self.x_ratio = x / LARGEUR
        self.y_ratio = y / HAUTEUR
        self.largeur_ratio = largeur / LARGEUR
        self.hauteur_ratio = hauteur / HAUTEUR
        self.valeur = valeur
        self.redimensionner()

    def redimensionner(self):
        self.rect = pygame.Rect(
            int(self.x_ratio * LARGEUR),
            int(self.y_ratio * HAUTEUR),
            int(self.largeur_ratio * LARGEUR),
            int(self.hauteur_ratio * HAUTEUR)
        )

    def afficher(self, ecran, texte):
        pygame.draw.rect(ecran, GRIS, self.rect)
        remplissage = pygame.Rect(self.rect.x, self.rect.y, self.rect.width * (self.valeur / 100), self.rect.height)
        pygame.draw.rect(ecran, BLEU, remplissage)
        texte_surface = police.render(f"{texte}: {self.valeur}%", True, BLANC)
        ecran.blit(texte_surface, (self.rect.x, self.rect.y - 30))

    def ajuster(self, pos_x,name):

        if self.rect.x <= pos_x <= self.rect.x + self.rect.width:
            self.valeur = int(((pos_x - self.rect.x) / self.rect.width) * 100)
        with open('../../data/settings/settings.json', 'r') as file:
            data=json.load(file)
        data["audio"][name]=self.valeur
        with open('../../data/settings/settings.json', 'w') as file:
            json.dump(data, file,indent=4)
        file.close()

# Classe pour les boutons
class Bouton:
    def __init__(self, x, y, largeur, hauteur, image, hovered_image, cliked_image=None):
        self.x_ratio = x / LARGEUR
        self.y_ratio = y / HAUTEUR
        self.largeur_ratio = largeur / LARGEUR
        self.hauteur_ratio = hauteur / HAUTEUR
        self.image = pygame.image.load(image)
        self.hovered_image = pygame.image.load(hovered_image)

    def redimensionner(self):
        self.rect = pygame.Rect(
            int(self.x_ratio * LARGEUR),
            int(self.y_ratio * HAUTEUR),
            int(self.largeur_ratio * LARGEUR),
            int(self.hauteur_ratio * HAUTEUR)
        )
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
        self.hovered_image = pygame.transform.scale(self.hovered_image, (self.rect.width, self.rect.height))

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        current_image = self.hovered_image if self.rect.collidepoint(mouse_pos) else self.image
        screen.blit(current_image, self.rect.topleft)

    def est_clique(self, pos):
        return self.rect.collidepoint(pos)


# Classe pour le menu déroulant
class MenuDeroulant:
    def __init__(self, x, y, largeur, hauteur, options, image, hovered_image):
        self.x_ratio = x / LARGEUR
        self.y_ratio = y / HAUTEUR
        self.largeur_ratio = largeur / LARGEUR
        self.hauteur_ratio = hauteur / HAUTEUR
        self.option_paths = options
        self.selection = options[resolution_index]
        self.ouvert = False
        self.image = pygame.image.load(image)
        self.hovered_image = pygame.image.load(hovered_image)
        self.options = [pygame.image.load(path) for path in options]
        self.redimensionner()

    def redimensionner(self):
        self.rect = pygame.Rect(
            int(self.x_ratio * LARGEUR),
            int(self.y_ratio * HAUTEUR),
            int(self.largeur_ratio * LARGEUR),
            int(self.hauteur_ratio * HAUTEUR)
        )
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
        self.hovered_image = pygame.transform.scale(self.hovered_image, (self.rect.width, self.rect.height))
        self.options = [pygame.transform.scale(pygame.image.load(path), (self.rect.width, self.rect.height))
                        for path in self.option_paths]


    def draw(self, ecran):
        mouse_pos = pygame.mouse.get_pos()
        current_image = self.hovered_image if self.rect.collidepoint(mouse_pos) else self.image
        ecran.blit(current_image, self.rect.topleft)

        if self.ouvert:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + ((i + 1) * self.rect.height),
                    self.rect.width,
                    self.rect.height
                )
                ecran.blit(option, option_rect.topleft)

    def afficher(self, ecran):
        pygame.draw.rect(ecran, VERT, self.rect)
        texte_surface = police.render(self.selection, True, BLANC)
        texte_rect = texte_surface.get_rect(center=self.rect.center)
        ecran.blit(texte_surface, texte_rect)

        if self.ouvert:
            for i, option in enumerate(self.option_paths):
                rect_option = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width,
                                          self.rect.height)
                pygame.draw.rect(ecran, GRIS, rect_option)
                texte_surface = police.render(option, True, BLANC)
                texte_rect = texte_surface.get_rect(center=rect_option.center)
                ecran.blit(texte_surface, texte_rect)

    def gerer_clic(self, pos):
        global resolution_index, LARGEUR, HAUTEUR, ECRAN
        if self.rect.collidepoint(pos):
            self.ouvert = not self.ouvert
        elif self.ouvert:
            for i, _ in enumerate(self.options):
                rect_option = pygame.Rect(
                    self.rect.x,
                    self.rect.y + (i + 1) * self.rect.height,
                    self.rect.width,
                    self.rect.height
                )
                if rect_option.collidepoint(pos):
                    resolution_index = i
                    self.selection = self.option_paths[i]
                    LARGEUR, HAUTEUR = RESOLUTIONS[i]
                    ECRAN = pygame.display.set_mode((LARGEUR, HAUTEUR),
                                                    pygame.FULLSCREEN if plein_ecran else pygame.RESIZABLE)
                    redimensionner_elements()
                    with open('../../data/settings/settings.json', 'r') as file:
                        data = json.load(file)
                    data["graphics"]["resolution"]["width"] = RESOLUTIONS[i][0]
                    data["graphics"]["resolution"]["height"] = RESOLUTIONS[i][1]
                    with open('../../data/settings/settings.json', 'w') as file:
                        json.dump(data, file, indent=4)
                    file.close()
                    self.ouvert = False
                    print(f"Nouvelle résolution : {LARGEUR}x{HAUTEUR}")