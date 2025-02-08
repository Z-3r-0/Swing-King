import sys
import pygame
pygame.init()

pygame.display.set_caption('SwingKing main menu')
screen = pygame.display.set_mode((800, 600))
background = pygame.image.load("assets/images/backgrounds/SwingKing2.jpg").convert()

clock = pygame.time.Clock()

#surface = pygame.Surface((50, 50))
#surface.fill('cadetblue')


while True :
    #let the user quit the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.blit(background, (0, 0))

    pygame.display.update()
    clock.tick(60)

