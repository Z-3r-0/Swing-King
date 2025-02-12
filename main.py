import pygame

from src.entities import *
from src.utils import *

import src.utils.settings_loader as settings

import src.utils.level_loader as level_loader

pygame.init()
WIDTH, HEIGHT, Terrain_Max_Length, Terrain_Max_Height = 1920, 1080, 10000, 2000
FPS = settings.load_json_settings("data/settings/settings.json")["graphics"]["fps_limit"]
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
background = pygame.transform.smoothscale(background, (screen.get_width(), screen.get_height()))

# Initializing all elements of the game
Golf_Ball = Ball(pygame.Vector2(0, 50), 4.2, 0.047, pygame.Color("white"), "assets/images/balls/golf_ball.png")

rock = Obstacle(pygame.Vector2(450, screen.get_height() - 90), pygame.Vector2(40, 60), pygame.Color("white"),
                "assets/images/obstacles/rock.png")
obstacles = [rock]

# initializing the camera, which will represent what we can see at the screen
# By moving to the left or right elements depending on the position of the ball
# (It is not a real camera)
camera = Camera(pygame.Vector2(0, 0))

# Initializing time for the start of the launch of the ball
Time = 0

# define shot variables
Shot_Angle = 25
Shot_Strength = 250


# Load test level (level1.json) data
lvl = level_loader.load_json_level("data/levels/level1.json")
lvl = level_loader.json_to_list(lvl, screen)


ball_rect = pygame.Rect(Golf_Ball.position.x - Golf_Ball.rayon, Golf_Ball.position.y - Golf_Ball.rayon, Golf_Ball.position.x + Golf_Ball.rayon, Golf_Ball.position.y + Golf_Ball.rayon)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # draw the background
    screen.blit(background, (0, 0))

    # if not Golf_Ball.is_colliding :

    # Updating the position x of the ball in function of the time since the start of the timer
    pos_x = calculate_traj_x(Time, Shot_Strength, Shot_Angle, Golf_Ball.mass, Golf_Ball.start_position.x)  # *10 is arbitrary, else it doesn't move alot

    # Updating the position y of the ball in function of the PosX
    pos_y = calculate_trajectory(pos_x, Shot_Strength, Shot_Angle, Golf_Ball.start_position.y)

    # Update the position of the camera depending on the position of the ball and the edge of the map
    camera.calculate_position(pygame.Vector2(pos_x, pos_y), WIDTH, HEIGHT, Terrain_Max_Length, Terrain_Max_Height)

    # Update the position of the ball minus the position of the camera, to always center the ball
    Golf_Ball.update_position(pygame.math.Vector2(pos_x - camera.position.x, HEIGHT - pos_y), camera.position.x)
    # else:
    #     # If the ball is colliding, we restart the timer
    #     # And put the actual position of the ball as the new start position
    #     Time = 0
    #     Golf_Ball.is_colliding = False
    #     Golf_Ball.start_position = Golf_Ball.position
    #     Shot_Strength *= 0.5

    # Hence we also move all objects to the left (or right) depending on where the ball is going
    for terrain in lvl:
        terrain.position_update(camera.position)
        terrain.draw(screen)

    # pygame.draw.polygon(screen, (255, 255, 255), lvl[0].vertices)

    # Check if the ball is colliding with the terrain
    # if not Golf_Ball.is_colliding and Time > 1/6:
    #     Golf_Ball.is_colliding = Golf_Ball.check_collision(terrain.rect)
    #     if Golf_Ball.is_colliding:
    #         print(f"Collision detected: {terrain}")

    for obstacle in obstacles:
        obstacle.position = pygame.Vector2(obstacle.position_constant.x - camera.position.x, obstacle.position_constant.y)
        obstacle.draw(screen)
        # # Check if the ball is colliding with the terrain
        # if not Golf_Ball.is_colliding:
        #     Golf_Ball.is_colliding = Golf_Ball.check_collision(terrain.rect)

    Golf_Ball.draw_ball(screen)
    ball_rect = pygame.Rect(Golf_Ball.position.x - Golf_Ball.rayon, Golf_Ball.position.y - Golf_Ball.rayon,Golf_Ball.diameter, Golf_Ball.diameter)
    pygame.draw.rect(screen, (255, 0, 0), ball_rect, 1)
    pygame.display.flip()

    clock.tick(FPS)  # limits FPS to settings
    Time += 1 / FPS

pygame.quit()