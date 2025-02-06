import time

import pygame
from pygame.examples.moveit import WIDTH

from src.hud.button import Button
from src.entities import *
from src.utils.physics_utils import *

pygame.init()
WIDTH, HEIGHT, Terrain_Real_Length = 1000, 500, 3000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
background = pygame.transform.smoothscale(background, (screen.get_width(), screen.get_height()))

# Initializing all elements of the game
Golf_Ball = Ball(pygame.Vector2(100, 200), 4.2, 0.047, pygame.Color("white"), "assets/images/balls/golf_ball.png")

green = Terrain('green', pygame.Vector2(0, screen.get_height() - 50), pygame.Vector2(500, 50), 0.02, 0.3)
bunker = Terrain('bunker', pygame.Vector2(500, screen.get_height() - 50), pygame.Vector2(100, 50), 0.1, 0.1)
fairway = Terrain('fairway', pygame.Vector2(600, screen.get_height() - 50), pygame.Vector2(300, 50), 0.01, 0.5)
lake = Terrain('lake', pygame.Vector2(900, screen.get_height() - 50), pygame.Vector2(120, 30), 0.0, 0.0)

rock = Obstacle(pygame.Vector2(450, screen.get_height() - 90), pygame.Vector2(40, 60), pygame.Color("white"), "assets/images/obstacles/rock.png")

terrains = [green, fairway, bunker, lake]
obstacles = [rock]


# initializing the camera, which will represent what we can see at the screen
# By moving to the left or right elements depending of the position of the ball
# (It is not a real camera)
camera = pygame.Rect(0, 0, WIDTH, HEIGHT)

# Initializing time for the start of the launch of the ball
Time_Start = time.time()


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

        posx = calculate_traj_x(Current_Time, 100, 30, Golf_Ball._mass) #*10 is arbitrary, else it doesn't move alot

        # Updating the position y of the ball in function of the PosX
        posy = calculate_trajectory(posx, 100, 30)

        # Update the position of the camera depending on the position of the ball and the edge of the map
        camera.x = int(posx) - WIDTH // 2
        camera.x = max(0, min(camera.x, Terrain_Real_Length - WIDTH))

        # Update the position of the ball minus the position of the camera, to always center the ball
        Golf_Ball._position = pygame.math.Vector2(posx - camera.x, HEIGHT - posy)

    # Hence we also move all objects to the left (or right) depending on where the ball is going
    for terrain in terrains:
        terrain.position = pygame.Vector2(terrain.position_constant[0]-camera.x, terrain.position_constant[1])
        terrain.draw(screen)

    for obstacle in obstacles:
        obstacle.position = pygame.Vector2(obstacle.position_constant[0]-camera.x, obstacle.position_constant[1])
        obstacle.draw(screen)

    # Displaying the golf ball on the screen
    Golf_Ball.draw_ball(screen)

    #Update whole frame
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
