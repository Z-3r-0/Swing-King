import pygame
from src.hud import button

def fullscreen():
    global current_screen
    current_screen = fullscreen


run=True
while run:
    screen = pygame.display.set_mode((1300, 755))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False