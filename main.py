import time

import pygame

from src.hud.button import Button
from src.entities import Ball
from src.entities import Terrain
from src.entities import Obstacle

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

background = pygame.image.load("assets/images/backgrounds/background.jpg").convert()
background = pygame.transform.smoothscale(background, (screen.get_width(), screen.get_height()))

test_ball = Ball((100, 200), 4.27, 1, pygame.Color("white"), "assets/images/balls/golf_ball.png")

green = Terrain('green', pygame.Vector2(0, screen.get_height() - 50), pygame.Vector2(500, 50), 0.02, 0.3)
bunker = Terrain('bunker', pygame.Vector2(500, screen.get_height() - 50), pygame.Vector2(100, 50), 0.1, 0.1)
fairway = Terrain('fairway', pygame.Vector2(600, screen.get_height() - 50), pygame.Vector2(300, 50), 0.01, 0.5)
lake = Terrain('lake', pygame.Vector2(900, screen.get_height() - 50), pygame.Vector2(120, 30), 0.0, 0.0)

rock = Obstacle(pygame.Vector2(450, screen.get_height() - 90), pygame.Vector2(40, 60), pygame.Color("white"), "assets/images/obstacles/rock.png")

terrains = [green, fairway, bunker, lake]
obstacles = [rock]


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    dt = clock.tick(60) / 1000

    # draw the background
    screen.blit(background, (0, 0))

    for terrain in terrains:
        terrain.draw(screen)

    for obstacle in obstacles:
        obstacle.draw(screen)

    test_ball.draw_ball(screen)

    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
