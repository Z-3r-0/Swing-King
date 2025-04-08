from src.utils import *
import src.game as game
from src.scenetype import SceneType

# Window parameters
WIDTH, HEIGHT = 1920, 1080 # TODO - REPLACE BY SCREEN RESOLUTION LATER (OR SETTINGS FILE)
                           # LEAVING IT HERE FOR NOW FOR TESTING PURPOSES (Console easy to read for non fullscreen)

scene = SceneType.MAIN_MENU

pygame.init()

game = game.Game(pygame.Vector2(WIDTH, HEIGHT))
game.run()