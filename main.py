from src.utils import *
import src.game as game


pygame.init()

# Window parameters
WIDTH, HEIGHT = 1920, 1080 # TODO - REPLACE BY SCREEN RESOLUTION LATER (OR SETTINGS FILE)
                           # LEAVING IT HERE FOR NOW FOR TESTING PURPOSES (Console easy to read for non fullscreen)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
game = game.Game(screen)

# Main game loop
while True:
    game.handle_events()
    game.draw()

    pygame.display.flip()

    game.clock.tick(game.fps)
    game.dt = 1 / game.fps