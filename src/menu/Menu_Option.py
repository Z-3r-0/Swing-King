import pygame

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

# Classe pour les barres de volume
class BarreVolume:
    def __init__(self, x, y, largeur, hauteur, valeur=50):
        self.x_ratio = x / LARGEUR
        self.y_ratio = y / HAUTEUR
        self.largeur_ratio = largeur / LARGEUR
        self.hauteur_ratio = hauteur / HAUTEUR
        self.valeur = valeur

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

    def ajuster(self, pos_x):
        if self.rect.x <= pos_x <= self.rect.x + self.rect.width:
            self.valeur = int(((pos_x - self.rect.x) / self.rect.width) * 100)

# Classe pour les boutons
class Bouton:
    def __init__(self, x, y, largeur, hauteur, texte, image,hovered_image,cliked_image):
        self.x_ratio = x / LARGEUR
        self.y_ratio = y / HAUTEUR
        self.largeur_ratio = largeur / LARGEUR
        self.hauteur_ratio = hauteur / HAUTEUR
        self.texte = texte
        self.image = pygame.image.load(image)
        self.hovered_image = pygame.image.load(hovered_image)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        current_image = self.hovered_image if self.rect.collidepoint(mouse_pos) else self.image
        screen.blit(current_image, self.rect)

    def redimensionner(self):
        self.rect = pygame.Rect(
            int(self.x_ratio * LARGEUR),
            int(self.y_ratio * HAUTEUR),
            int(self.largeur_ratio * LARGEUR),
            int(self.hauteur_ratio * HAUTEUR)
        )

    def afficher(self, ecran):

        texte_surface = police.render(self.texte, True, BLANC)
        texte_rect = texte_surface.get_rect(center=self.rect.center)
        ecran.blit(texte_surface, texte_rect)

    def est_clique(self, pos):
        return self.rect.collidepoint(pos)

# Classe pour le menu déroulant
class MenuDeroulant:
    def __init__(self, x, y, largeur, hauteur, options):
        self.x_ratio = x / LARGEUR
        self.y_ratio = y / HAUTEUR
        self.largeur_ratio = largeur / LARGEUR
        self.hauteur_ratio = hauteur / HAUTEUR
        self.options = options
        self.selection = options[resolution_index]
        self.ouvert = False

    def redimensionner(self):
        self.rect = pygame.Rect(
            int(self.x_ratio * LARGEUR),
            int(self.y_ratio * HAUTEUR),
            int(self.largeur_ratio * LARGEUR),
            int(self.hauteur_ratio * HAUTEUR)
        )

    def afficher(self, ecran):
        pygame.draw.rect(ecran, VERT, self.rect)
        texte_surface = police.render(self.selection, True, BLANC)
        texte_rect = texte_surface.get_rect(center=self.rect.center)
        ecran.blit(texte_surface, texte_rect)

        if self.ouvert:
            for i, option in enumerate(self.options):
                rect_option = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(ecran, GRIS, rect_option)
                texte_surface = police.render(option, True, BLANC)
                texte_rect = texte_surface.get_rect(center=rect_option.center)
                ecran.blit(texte_surface, texte_rect)

    def gerer_clic(self, pos):
        global resolution_index, LARGEUR, HAUTEUR, ECRAN
        if self.rect.collidepoint(pos):
            self.ouvert = not self.ouvert
        elif self.ouvert:
            for i, option in enumerate(self.options):
                rect_option = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                if rect_option.collidepoint(pos):
                    resolution_index = i
                    self.selection = option
                    LARGEUR, HAUTEUR = RESOLUTIONS[i]
                    ECRAN = pygame.display.set_mode((LARGEUR, HAUTEUR), pygame.FULLSCREEN if plein_ecran else pygame.RESIZABLE)
                    redimensionner_elements()
                    self.ouvert = False
                    print(f"Nouvelle résolution : {LARGEUR}x{HAUTEUR}")

# Création des éléments
barres_volume = {
    "Master": BarreVolume(200, 100, 400, 20),
    "Music": BarreVolume(200, 160, 400, 20),
    "SFX": BarreVolume(200, 220, 400, 20),
    "Voice": BarreVolume(200, 280, 400, 20)
}

bouton_fullscreen = Bouton(100, 200, 200, 50, "Fullscreen",
                           "../../assets/images/buttons/Option Menu/Fullscreen/Fullscreen.png",
                           "../../assets/images/buttons/Option Menu/Fullscreen/Fullscreen_Hovered.png",
                           "../../assets/images/buttons/Option Menu/Fullscreen/Fullscreen.png")
menu_resolution = MenuDeroulant(200, 420, 200, 50, ["800x600", "1280x720", "1920x1080"])

plein_ecran = False

def redimensionner_elements():
    for barre in barres_volume.values():
        barre.redimensionner()
    bouton_fullscreen.redimensionner()
    menu_resolution.redimensionner()

redimensionner_elements()

# Boucle principale
running = True
while running:
    ECRAN.fill(NOIR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for barre in barres_volume.values():
                if barre.rect.collidepoint(event.pos):
                    barre.ajuster(event.pos[0])

            if bouton_fullscreen.est_clique(event.pos):
                plein_ecran = not plein_ecran
                ECRAN = pygame.display.set_mode((LARGEUR, HAUTEUR), pygame.FULLSCREEN if plein_ecran else pygame.RESIZABLE)
                redimensionner_elements()

            menu_resolution.gerer_clic(event.pos)

        if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            for barre in barres_volume.values():
                if barre.rect.collidepoint(event.pos):
                    barre.ajuster(event.pos[0])

    for nom, barre in barres_volume.items():
        barre.afficher(ECRAN, nom)

    bouton_fullscreen.draw(ECRAN)
    menu_resolution.afficher(ECRAN)

    pygame.display.flip()

pygame.quit()