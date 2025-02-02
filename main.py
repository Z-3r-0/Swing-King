import time

import pygame

import src.hud.button as button
import src.entities.ball as ball

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

test_button = button.Button(screen, lambda: print("Test"), (screen.get_width() / 2 - 100, screen.get_height() / 2 - 30),
                            (200, 60), "assets/images/hud/test_btn.png", scene_bg_color=pygame.Color("purple"))
test_button_1 = button.Button(screen, lambda: print("New test button !"),
                              (screen.get_width() / 2 - 100, screen.get_height() / 2 - 30), (200, 60),
                              foreground_color=pygame.Color(48, 154, 219), background_color=pygame.Color(39, 128, 184),
                              text="Test button", font_color=pygame.Color("white"),
                              scene_bg_color=pygame.Color("purple"))

test_ball = ball.Ball(screen, (100, 200), 4.27, 1, pygame.Color("white"), "assets/images/balls/golf_ball.png")

x = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    dt = clock.tick(60) / 1000

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    """test_button.draw(screen)
    test_button.listen()"""

    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
