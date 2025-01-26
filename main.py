# Example file showing a basic pygame "game loop"
import pygame

import src.hud.button as button



pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

test_button = button.Button(screen, lambda: print("Test"), (screen.get_width() / 2 - 100, screen.get_height() / 2 - 30), (200, 60), "assets/images/test_btn.png", scene_bg_color = pygame.Color("purple"))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    test_button.draw(screen)
    test_button.listen()

    # RENDER YOUR GAME HERE

    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()