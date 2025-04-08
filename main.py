from src.utils import *
import src.game as game
from src.scenetype import SceneType

# Window parameters
WIDTH, HEIGHT = 1920, 1080 # TODO - REPLACE BY SCREEN RESOLUTION LATER (OR SETTINGS FILE)
                           # LEAVING IT HERE FOR NOW FOR TESTING PURPOSES (Console easy to read for non fullscreen)

scene = SceneType.MAIN_MENU # Default scene (arrival in the game)

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

game = game.Game(screen)
game.run()