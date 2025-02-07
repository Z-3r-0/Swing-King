import time

import pygame

from src.entities import *
from src.utils.physics_utils import *

import src.utils.level_loader as level_loader

pygame.init()
WIDTH, HEIGHT, Terrain_Real_Length = 1000, 500, 10000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
background = pygame.transform.smoothscale(background, (screen.get_width(), screen.get_height()))

# Initializing all elements of the game
Golf_Ball = Ball(pygame.Vector2(100, 200), 4.2, 0.047, pygame.Color("white"), "assets/images/balls/golf_ball.png")

green = Terrain('green', pygame.Vector2(0, screen.get_height() - 50), pygame.Vector2(1000, 92), 5)
bunker = Terrain('bunker', pygame.Vector2(995, screen.get_height() - 92), pygame.Vector2(400, 92), 0)
fairway = Terrain('fairway', pygame.Vector2(1391, screen.get_height() - 70), pygame.Vector2(500, 100), -5)
lake = Terrain('lake', pygame.Vector2(1890, screen.get_height() - 47), pygame.Vector2(300, 50), 0)

rock = Obstacle(pygame.Vector2(450, screen.get_height() - 90), pygame.Vector2(40, 60), pygame.Color("white"),
                "assets/images/obstacles/rock.png")

terrains = [green, fairway, bunker, lake]
obstacles = [rock]

# initializing the camera, which will represent what we can see at the screen
# By moving to the left or right elements depending on the position of the ball
# (It is not a real camera)
camera = pygame.Rect(0, 0, WIDTH, HEIGHT)

# Initializing time for the start of the launch of the ball
Time_Start = time.time()

# Load test level (level1.json) data
lvl = level_loader.load_json_level("data/levels/level1.json")
lvl = level_loader.json_to_list(lvl, screen)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # draw the background
    screen.blit(background, (0, 0))

    # We update the ball while it is above the ground
    if Golf_Ball._position[1] <= HEIGHT:
        # Updating the position x of the ball in function of the time since the start of the timer
        Current_Time = time.time() - Time_Start

        posx = calculate_traj_x(Current_Time, 250, 30, Golf_Ball._mass)  #*10 is arbitrary, else it doesn't move alot

        # Updating the position y of the ball in function of the PosX
        posy = calculate_trajectory(posx, 250, 30)

        # Update the position of the camera depending on the position of the ball and the edge of the map
        camera.x = int(posx) - WIDTH // 2
        camera.x = max(0, min(camera.x, Terrain_Real_Length - WIDTH))

        # Update the position of the ball minus the position of the camera, to always center the ball
        Golf_Ball._position = pygame.math.Vector2(posx - camera.x, HEIGHT - posy)

    # Hence we also move all objects to the left (or right) depending on where the ball is going
    for terrain in lvl:
        terrain.position = pygame.Vector2(terrain.start_position[0] - camera.x, terrain.start_position[1])
        terrain.draw(screen)

    for obstacle in obstacles:
        obstacle.position = pygame.Vector2(obstacle.position_constant[0] - camera.x, obstacle.position_constant[1])
        obstacle.draw(screen)


    Golf_Ball.draw_ball(screen)

    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
