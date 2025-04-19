import pygame

from pygame import Vector2

from src.hud import Button
from src.hud.dropdown import Dropdown
from src.hud.slider import Slider

# Initialisation de pygame
pygame.init()

# Résolutions possibles
LARGEUR, HAUTEUR = 1920, 1080

# Création de la fenêtre (commence en mode fenêtré)
screen = pygame.display.set_mode((LARGEUR, HAUTEUR), pygame.RESIZABLE)
pygame.display.set_caption("Menu Options")


# Création des éléments
volumes_sliders = {
    "Master": Slider(screen, Vector2(200, 100), Vector2(400, 20)),
    "Music": Slider(screen, Vector2(200, 160), Vector2(400, 20)),
    "SFX": Slider(screen, Vector2(200, 220), Vector2(400, 20)),
    "Voice": Slider(screen, Vector2(200, 280), Vector2(400, 20)),
}

fullscreen_btn = Button(screen, lambda: lambda_fullscreen(), Vector2(200, 340), Vector2(150, 50),
                           "assets/images/buttons/Option Menu/Fullscreen/Fullscreen.png",
                           "assets/images/buttons/Option Menu/Fullscreen/Fullscreen_Hovered.png",
                           "assets/images/buttons/Option Menu/Fullscreen/Fullscreen.png")

menu_resolution = Dropdown(screen, Vector2(200, 400), Vector2(150, 50), [
    "assets/images/buttons/Option Menu/Resolution/800x600.png",
    "assets/images/buttons/Option Menu/Resolution/1280x720.png",
    "assets/images/buttons/Option Menu/Resolution/1920x1080.png"],
                                "assets/images/buttons/Option Menu/Resolution/800x600.png",
                                "assets/images/buttons/Option Menu/Resolution/800x600_Hovered.png")


background = pygame.image.load("assets/images/backgrounds/background.jpg")


def resize_elements():
    # Redimensionner le fond d'écran
    global background
    background = pygame.transform.scale(pygame.image.load("assets/images/backgrounds/background.jpg"),
                                        (LARGEUR, HAUTEUR))

    # Redimensionner les autres éléments
    for bar in volumes_sliders.values():
        bar.resize()
    fullscreen_btn.resize()
    menu_resolution.resize()
    
def lambda_fullscreen():
    global screen
    menu_resolution.is_fullscreen = not menu_resolution.is_fullscreen
    screen = pygame.display.set_mode((LARGEUR, HAUTEUR),
                                     pygame.FULLSCREEN if menu_resolution.is_fullscreen else pygame.RESIZABLE)
    resize_elements()


resize_elements()


running = True
while running:
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for barre in volumes_sliders.keys():
                if volumes_sliders[barre].rect.collidepoint(event.pos):
                    volumes_sliders[barre].save(event.pos[0], barre)

            menu_resolution.handle_click(event.pos)
            
            fullscreen_btn.listen(event)

        if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            for barre in volumes_sliders.keys():
                if volumes_sliders[barre].rect.collidepoint(event.pos):
                    volumes_sliders[barre].save(event.pos[0], barre)

    for nom, barre in volumes_sliders.items():
        barre.draw(nom)

    fullscreen_btn.hover()

    fullscreen_btn.draw()
    menu_resolution.draw()

    pygame.display.flip()

pygame.quit()