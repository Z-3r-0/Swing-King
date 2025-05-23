import pygame
from src.scene import SceneType

scene_events = {
    SceneType.GAME: pygame.USEREVENT + SceneType.GAME.value,
    SceneType.MAIN_MENU: pygame.USEREVENT + SceneType.MAIN_MENU.value,
    SceneType.OPTIONS_MENU: pygame.USEREVENT + SceneType.OPTIONS_MENU.value,
    SceneType.CREDITS: pygame.USEREVENT + SceneType.CREDITS.value,
    SceneType.LEVEL_CREATOR: pygame.USEREVENT + SceneType.LEVEL_CREATOR.value,
    SceneType.LEVEL_SELECTOR: pygame.USEREVENT + SceneType.LEVEL_SELECTOR.value,
}

options_events = {
    "RESIZE": pygame.USEREVENT + 10,
    "VOLUME_UPDATE": pygame.USEREVENT + 11,
}

interact_events = {
    "COIN_COLLECTED": pygame.USEREVENT + 20,
    "FLAG_REACHED": pygame.USEREVENT + 21,
}

collision_events = {
    "HIT_RESTART_ZONE": pygame.USEREVENT + 30,
}