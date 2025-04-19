import pygame

from pygame import Vector2
from pygame.display import toggle_fullscreen

from src.hud import Button
from src.hud.dropdown import Dropdown
from src.hud.slider import Slider

# Initialisation de pygame
pygame.init()

# Résolutions possibles
LARGEUR, HAUTEUR = 1920, 1080

# Création de la fenêtre (commence en mode fenêtré)
ECRAN = pygame.display.set_mode((LARGEUR, HAUTEUR), pygame.RESIZABLE)
pygame.display.set_caption("Menu Options")


# Création des éléments
volumes_sliders = {
    "Master": Slider(ECRAN, Vector2(200, 100), Vector2(400, 20)),
    "Music": Slider(ECRAN, Vector2(200, 160), Vector2(400, 20)),
    "SFX": Slider(ECRAN, Vector2(200, 220), Vector2(400, 20)),
    "Voice": Slider(ECRAN, Vector2(200, 280), Vector2(400, 20)),
}

fullscreen_btn = Button(ECRAN, lambda: toggle_fullscreen(), Vector2(200, 340), Vector2(150, 50),
                           "../../assets/images/buttons/Option Menu/Fullscreen/Fullscreen.png",
                           "../../assets/images/buttons/Option Menu/Fullscreen/Fullscreen_Hovered.png",
                           "../../assets/images/buttons/Option Menu/Fullscreen/Fullscreen.png")

menu_resolution = Dropdown(ECRAN, Vector2(200, 400), Vector2(150, 50), [
    "../../assets/images/buttons/Option Menu/Resolution/800x600.png",
    "../../assets/images/buttons/Option Menu/Resolution/1280x720.png",
    "../../assets/images/buttons/Option Menu/Resolution/1920x1080.png"],
                                "../../assets/images/buttons/Option Menu/Resolution/800x600.png",
                                "../../assets/images/buttons/Option Menu/Resolution/800x600_Hovered.png")


background = pygame.image.load("../../assets/images/backgrounds/background.jpg")


def resize_elements():
    # Redimensionner le fond d'écran
    global background
    background = pygame.transform.scale(pygame.image.load("../../assets/images/backgrounds/background.jpg"),
                                        (LARGEUR, HAUTEUR))

    # Redimensionner les autres éléments
    for bar in volumes_sliders.values():
        bar.resize()
    fullscreen_btn.resize()
    menu_resolution.resize()


resize_elements()

# Boucle principale
running = True
while running:
    ECRAN.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for barre in volumes_sliders.keys():
                if volumes_sliders[barre].rect.collidepoint(event.pos):
                    volumes_sliders[barre].save(event.pos[0], barre)

            if fullscreen_btn.is_clicked(event.pos):
                plein_ecran = not plein_ecran
                ECRAN = pygame.display.set_mode((LARGEUR, HAUTEUR),
                                                pygame.FULLSCREEN if plein_ecran else pygame.RESIZABLE)
                resize_elements()

            menu_resolution.handle_click(event.pos)

        if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            for barre in volumes_sliders.keys():
                if volumes_sliders[barre].rect.collidepoint(event.pos):
                    volumes_sliders[barre].save(event.pos[0], barre)

    for nom, barre in volumes_sliders.items():
        barre.display(ECRAN, nom)

    fullscreen_btn.draw()
    menu_resolution.draw()

    pygame.display.flip()

pygame.quit()