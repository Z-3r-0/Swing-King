import pygame
import sys
import math
from src.utils.physics_utils import *
from src.entities import *

# Initialisation de Pygame
pygame.init()

# Configuration de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Swing King - Optimal Trajectory")

# Couleurs
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Paramètres de la balle
BALL_RADIUS = 20
BALL_COLOR = RED
BALL_START_X, BALL_START_Y = WIDTH // 2, HEIGHT // 2

# Variables de contrôle
dragging = False
initial_pos = (0, 0)
velocity = pygame.Vector2(0, 0)
GRAVITY = pygame.Vector2(0, 9.8)  # Gravité réaliste
FRICTION = 0.98  # Frottement réduit pour plus de dynamisme

# Dimensions de la scène
SCENE_WIDTH, SCENE_HEIGHT = 10000, 10000

# Configuration des pointillés
DOT_SPACING = 10
DOT_RADIUS = 2



def drag_and_release(start_pos, end_pos):
    """
    Calcule la force et l'angle en fonction de la distance de traction.
    Retourne un tuple (force, angle).
    """
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = math.hypot(dx, dy)
    angle = math.degrees(math.atan2(dy, dx))
    force = min(distance, 500) * 0.1  # Limite la force et ajuste la sensibilité
    return force, angle


def draw_dotted_line(surface, color, start_pos, end_pos):
    """
    Dessine une ligne en pointillés entre deux points.
    """
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = math.hypot(dx, dy)
    if distance < DOT_SPACING:
        return  # Évite de dessiner si la distance est trop petite

    steps = max(1, int(distance // DOT_SPACING))  # Au moins 1 étape
    dx_step = dx / steps
    dy_step = dy / steps

    for i in range(steps + 1):  # +1 pour inclure le dernier point
        x = int(start_pos[0] + dx_step * i)
        y = int(start_pos[1] + dy_step * i)
        pygame.draw.circle(surface, color, (x, y), DOT_RADIUS)

def run_game():
    global dragging, initial_pos, velocity

    # Initialisation de la caméra et de la scène
    camera = Camera(pygame.Vector2(0,0), WIDTH, HEIGHT)
    scene = pygame.Surface((SCENE_WIDTH, SCENE_HEIGHT))
    scene.fill(BLUE)

    # Dessiner la grille
    for i in range(0, SCENE_WIDTH, 50):
        pygame.draw.line(scene, WHITE, (i, 0), (i, SCENE_HEIGHT))
    for j in range(0, SCENE_HEIGHT, 50):
        pygame.draw.line(scene, WHITE, (0, j), (SCENE_WIDTH, j))

    # Position initiale de la balle dans la scène
    ball_scene_x, ball_scene_y = SCENE_WIDTH // 2, SCENE_HEIGHT // 2

    # Boucle principale du jeu
    clock = pygame.time.Clock()
    while True:
        dt = clock.tick(60) / 1000  # Temps écoulé depuis la dernière frame en secondes

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if math.hypot(mouse_x - BALL_START_X, mouse_y - BALL_START_Y) <= BALL_RADIUS:
                    dragging = True
                    initial_pos = event.pos
            if event.type == pygame.MOUSEBUTTONUP:
                if dragging:
                    # Calculer la force et l'angle avec la fonction drag_and_release
                    force, angle = drag_and_release(initial_pos, pygame.mouse.get_pos())
                    print(f"Force: {force}, Angle: {angle}")  # Affiche le tuple (force, angle)
                    # Appliquer la force et l'angle à la vitesse (correction des signes)
                    velocity = pygame.Vector2(-force * math.cos(math.radians(angle)), -force * math.sin(math.radians(angle)))
                    dragging = False

        # Appliquer la gravité
        velocity += GRAVITY * dt

        # Mettre à jour la position de la balle
        ball_scene_x += velocity.x * dt * 50  # Ajustement pour une animation plus lente
        ball_scene_y += velocity.y * dt * 50  # Ajustement pour une animation plus lente

        # Appliquer le frottement
        velocity *= FRICTION

        # Mettre à jour la caméra
        camera.update(ball_scene_x, ball_scene_y)
        screen.fill(WHITE)
        screen.blit(scene.subsurface(camera.camera), (0, 0))

        # Dessiner la balle
        pygame.draw.circle(screen, BALL_COLOR, (BALL_START_X, BALL_START_Y), BALL_RADIUS)

        # Dessiner la ligne de traction en pointillés
        if dragging:
            draw_dotted_line(screen, GREEN, initial_pos, pygame.mouse.get_pos())

        # Mettre à jour l'affichage
        pygame.display.flip()

if __name__ == "__main__":
    run_game()