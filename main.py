import pygame
import sys
import math
from src.entities import Ball, Obstacle, Camera
from src.utils import *
import src.utils.settings_loader as settings
import src.utils.level_loader as level_loader

# Initialisation de Pygame
pygame.init()

# Paramètres de la fenêtre
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 50
BALL_START_X, BALL_START_Y = 300, 300
SCENE_WIDTH, SCENE_HEIGHT = 10000, 2000
GRAVITY = 980  # Accélération gravitationnelle en pixels/s²

# Paramètres du jeu
dt = 0
DOT_SPACING = 10
DOT_RADIUS = 2
FPS = settings.load_json_settings("data/settings/settings.json")["graphics"]["fps_limit"]

# Création de la fenêtre et de l'horloge
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Chargement du fond d'écran
background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))

# Initialisation des objets de jeu
Golf_Ball = Ball(pygame.Vector2(BALL_START_X, BALL_START_Y), 4.2, 0.047, pygame.Color("white"),
                 "assets/images/balls/golf_ball.png")

# Initialisation des obstacles
rock = Obstacle(pygame.Vector2(450, HEIGHT - 90), pygame.Vector2(40, 60), pygame.Color("white"),
                "assets/images/obstacles/rock.png")
obstacles = [rock]

# Chargement du niveau
dungeon_level = level_loader.load_json_level("data/levels/level1.json")
lvl = level_loader.json_to_list(dungeon_level, screen)

# Variables pour le drag-and-release (possible une seule fois)
dragging = False
drag_done = False
ball_in_motion = False

# Initialisation de la caméra
camera = Camera(pygame.Vector2(0, 0), WIDTH, HEIGHT)


def drag_and_release(start_pos, end_pos):
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = min(math.hypot(dx, dy), 500)  # Limite la force
    angle = math.degrees(math.atan2(-dy, dx))  # Direction naturelle depuis le centre
    force = distance * 3.0  # Force beaucoup augmentée pour propulser la balle plus loin
    return force, angle


def check_collision(ball, obstacles):
    for obstacle in obstacles:
        if obstacle.rect.collidepoint(ball.position.x, ball.position.y):
            return True
    return False


def draw_predicted_trajectory(start_pos, force, angle):
    # Calculer le vecteur vitesse initiale depuis le centre de la balle
    initial_velocity = pygame.Vector2(
        -force * math.cos(math.radians(angle)),
        force * math.sin(math.radians(angle))
    )
    # Incorporation de la friction dans la prédiction :
    # k est le coefficient de frottement continu, tel que exp(-k) ~ 0.98 sur une frame.
    k = -math.log(0.98) * FPS

    # On dessine seulement le début de la trajectoire (par exemple pendant 0.75 secondes)
    t = 0.0
    dt_sim = 0.1  # Moins de points pour une trajectoire plus épurée
    while t < 0.75:
        # Position prédite intégrant friction et gravité :
        pred_x = start_pos.x + (initial_velocity.x / k) * (1 - math.exp(-k * t))
        pred_y = start_pos.y + ((initial_velocity.y - GRAVITY / k) / k) * (1 - math.exp(-k * t)) + (GRAVITY * t / k)
        pygame.draw.circle(screen, pygame.Color("white"), (int(pred_x), int(pred_y)), 3)
        t += dt_sim


# Boucle principale du jeu
running = True
while running:
    screen.fill(pygame.Color("black"))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Démarrer le drag si le clic se fait dans le rayon de la balle (depuis son centre)
            if (not drag_done) and math.hypot(event.pos[0] - Golf_Ball.position.x,
                                              event.pos[1] - Golf_Ball.position.y) <= BALL_RADIUS:
                dragging = True

        if event.type == pygame.MOUSEBUTTONUP and dragging:
            if not drag_done:
                # Utiliser le centre de la balle pour le calcul
                force, angle = drag_and_release(Golf_Ball.position, pygame.mouse.get_pos())
                Golf_Ball.velocity = pygame.Vector2(
                    -force * math.cos(math.radians(angle)),  # Inversion de l'axe X
                    force * math.sin(math.radians(angle))
                )
                print(f"Force: {force}, Angle: {angle}")
                dragging = False
                ball_in_motion = True
                drag_done = True

    if ball_in_motion:
        # Mise à jour de la position avec le mouvement initial
        Golf_Ball.position += Golf_Ball.velocity * dt

        # Application de la gravité de manière réaliste :
        Golf_Ball.velocity.y += GRAVITY * dt

        # Application d'une friction légère sur l'ensemble de la vitesse
        Golf_Ball.velocity *= 0.98

        print(f"Position: {Golf_Ball.position}, Vitesse: {Golf_Ball.velocity}")

        if check_collision(Golf_Ball, obstacles) or Golf_Ball.velocity.length() < 0.1:
            ball_in_motion = False
            Golf_Ball.velocity = pygame.Vector2(0, 0)

    # Mise à jour de la caméra
    camera.calculate_position(Golf_Ball.position, SCENE_WIDTH, SCENE_HEIGHT)

    # Dessin des éléments
    for terrain in lvl:
        terrain.draw(screen)
    for obstacle in obstacles:
        obstacle.draw(screen)

    Golf_Ball.draw_ball(screen)

    # Affichage de la ligne de drag et du début de la trajectoire prédite
    if dragging:
        current_mouse = pygame.mouse.get_pos()
        pygame.draw.line(screen, pygame.Color("red"), Golf_Ball.position, current_mouse, 2)
        force, angle = drag_and_release(Golf_Ball.position, current_mouse)
        draw_predicted_trajectory(Golf_Ball.position, force, angle)

    pygame.display.flip()
    clock.tick(FPS)
    dt = 1 / FPS

pygame.quit()
