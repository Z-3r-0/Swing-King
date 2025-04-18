from enum import Enum

class SceneType(Enum):
    """
    Enum representing the different scenes in the game.
    """
    MAIN_MENU = 1
    GAME = 2
    OPTIONS_MENU = 3
    LEVEL_SELECTOR = 4
    LEVEL_CREATOR = 5
    CREDITS = 6