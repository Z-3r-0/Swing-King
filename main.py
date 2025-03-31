import pygame
import sys
import math
from src.entities import Ball, Obstacle, Camera
from src.utils import *
import src.utils.settings_loader as settings
import src.utils.level_loader as level_loader

# Initialization of Pygame
pygame.init()

# Window parameters
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 50
BALL_START_X, BALL_START_Y = 300, 300
SCENE_WIDTH, SCENE_HEIGHT = 10000, 2000
GRAVITY = 980  # Gravitational acceleration in pixels/s²

# Game parameters
dt = 0
DOT_SPACING = 10
DOT_RADIUS = 2
FPS = settings.load_json_settings("data/settings/settings.json")["graphics"]["fps_limit"]

# Creation of the window and the clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Loading the background
background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))

# Initialization of game objects
Golf_Ball = Ball(pygame.Vector2(BALL_START_X, BALL_START_Y), 4.2, 0.047, pygame.Color("white"),
                 "assets/images/balls/golf_ball2.png")

# Initialization of obstacles
rock = Obstacle(pygame.Vector2(450, HEIGHT - 90), pygame.Vector2(40, 60), pygame.Color("white"),
                "assets/images/obstacles/rock.png")
obstacles = [rock]

# Loading the level
dungeon_level = level_loader.load_json_level("data/levels/level1.json")
lvl = level_loader.json_to_list(dungeon_level, screen)

# Variables for drag-and-release (possible only once)
dragging = False
drag_done = False
ball_in_motion = False

# Initialization of the camera
camera = Camera(pygame.Vector2(0, 0), WIDTH, HEIGHT)


def drag_and_release(start_pos, end_pos):
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = min(math.hypot(dx, dy), 500)  # Limit the force
    angle = math.degrees(math.atan2(-dy, dx))  # Natural direction from the center
    force = distance * 3.0  # Greatly increased force to propel the ball further
    return force, angle


def check_collision(ball, obstacles):
    for obstacle in obstacles:
        if obstacle.rect.collidepoint(ball.position.x, ball.position.y):
            return True
    return False


def draw_predicted_trajectory(start_pos, force, angle):
    # Calculate the initial velocity vector from the center of the ball
    initial_velocity = pygame.Vector2(
        -force * math.cos(math.radians(angle)),
        force * math.sin(math.radians(angle))
    )
    # Incorporation of friction in the prediction:
    # k is the continuous friction coefficient, such that exp(-k) ~ 0.98 over one frame.
    k = -math.log(0.98) * FPS

    # Draw only the beginning of the trajectory (for example during 0.75 seconds)
    t = 0.0
    dt_sim = 0.1  # Fewer points for a cleaner trajectory
    while t < 0.75:
        # Predicted position incorporating friction and gravity:
        pred_x = start_pos.x + (initial_velocity.x / k) * (1 - math.exp(-k * t))
        pred_y = start_pos.y + ((initial_velocity.y - GRAVITY / k) / k) * (1 - math.exp(-k * t)) + (GRAVITY * t / k)
        pygame.draw.circle(screen, pygame.Color("white"), (int(pred_x), int(pred_y)), 3)
        t += dt_sim


# Main game loop
running = True
while running:
    screen.fill(pygame.Color("black"))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Start the drag if the click is within the radius of the ball (from its center)
            if (not drag_done) and math.hypot(event.pos[0] - Golf_Ball.position.x,
                                              event.pos[1] - Golf_Ball.position.y) <= BALL_RADIUS:
                dragging = True

        if event.type == pygame.MOUSEBUTTONUP and dragging:
            if not drag_done:
                # Use the center of the ball for the calculation
                force, angle = drag_and_release(Golf_Ball.position, pygame.mouse.get_pos())
                Golf_Ball.velocity = pygame.Vector2(
                    -force * math.cos(math.radians(angle)),  # Inversion of the X axis
                    force * math.sin(math.radians(angle))
                )
                print(f"Force: {force}, Angle: {angle}")
                dragging = False
                ball_in_motion = True
                drag_done = True

    if ball_in_motion:
        # Update the position with the initial movement
        Golf_Ball.position += Golf_Ball.velocity * dt

        # Apply gravity realistically:
        Golf_Ball.velocity.y += GRAVITY * dt

        # Apply a slight friction to the entire velocity
        Golf_Ball.velocity *= 0.98

        if check_collision(Golf_Ball, obstacles) or Golf_Ball.velocity.length() < 0.1:
            ball_in_motion = False
            Golf_Ball.velocity = pygame.Vector2(0, 0)

    # Update the camera
    camera.calculate_position(Golf_Ball.position, SCENE_WIDTH, SCENE_HEIGHT)

    # Draw elements
    for terrain in lvl:
        terrain.draw(screen)
    for obstacle in obstacles:
        obstacle.draw(screen)

    Golf_Ball.draw_ball(screen)

    # Display the drag line and the beginning of the predicted trajectory
    if dragging:
        current_mouse = pygame.mouse.get_pos()
        pygame.draw.line(screen, pygame.Color("red"), Golf_Ball.position, current_mouse, 2)
        force, angle = drag_and_release(Golf_Ball.position, current_mouse)
        draw_predicted_trajectory(Golf_Ball.position, force, angle)

    pygame.display.flip()
    clock.tick(FPS)
    dt = 1 / FPS

pygame.quit()