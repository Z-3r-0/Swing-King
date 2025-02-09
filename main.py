import time

import pygame

from src.entities import *
from src.utils import *


import src.utils.level_loader as level_loader

pygame.init()
WIDTH, HEIGHT, Terrain_Max_Length, Terrain_Max_Height = 1000, 600, 10000, 2000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True
FPS = 120

background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
background = pygame.transform.smoothscale(background, (screen.get_width(), screen.get_height()))

# Initializing all elements of the game
Golf_Ball = Ball(pygame.Vector2(100, 200), 4.2, 0.047, pygame.Color("white"), "assets/images/balls/golf_ball.png")

rock = Obstacle(pygame.Vector2(450, screen.get_height() - 90), pygame.Vector2(40, 60), pygame.Color("white"),
                "assets/images/obstacles/rock.png")

obstacles = [rock]

# initializing the camera, which will represent what we can see at the screen
# By moving to the left or right elements depending on the position of the ball
# (It is not a real camera)
camera = Camera(pygame.Vector2(0, 0))

# Initializing time for the start of the launch of the ball
Time = 0

# test variables
Old_speed = 0
speed = 0



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
    if Golf_Ball.position[1] <= HEIGHT:
        # Updating the position x of the ball in function of the time since the start of the timer
        pos_x = calculate_traj_x(Time, 250, 30, Golf_Ball.mass)  # *10 is arbitrary, else it doesn't move alot

        # Updating the position y of the ball in function of the PosX
        pos_y = calculate_trajectory(pos_x, 250, 30)

        # Update the position of the camera depending on the position of the ball and the edge of the map
        camera.calculate_position(pygame.Vector2(pos_x, pos_y), WIDTH, HEIGHT, Terrain_Max_Length, Terrain_Max_Height)

        # Update the position of the ball minus the position of the camera, to always center the ball
        Golf_Ball.update_position(pygame.math.Vector2(pos_x - camera.position.x, HEIGHT - pos_y), camera.position.x)

    # Hence we also move all objects to the left (or right) depending on where the ball is going
    for terrain in lvl:
        terrain.position = pygame.Vector2(terrain.start_position[0] - camera.position.x, terrain.start_position[1])
        terrain.draw(screen)

    for obstacle in obstacles:
        obstacle.position = pygame.Vector2(obstacle.position_constant[0] - camera.position.x, obstacle.position_constant[1])
        obstacle.draw(screen)

    Golf_Ball.draw_ball(screen)

    pygame.display.flip()

    clock.tick(FPS)  # limits FPS to 60
    Time += 1 / 60

pygame.quit()
