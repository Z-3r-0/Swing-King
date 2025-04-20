import pygame
from src.scenetype import SceneType

scene_events = {
    SceneType.GAME: pygame.USEREVENT + SceneType.GAME.value,
    SceneType.MAIN_MENU: pygame.USEREVENT + SceneType.MAIN_MENU.value,
    SceneType.OPTIONS_MENU: pygame.USEREVENT + SceneType.OPTIONS_MENU.value,
    SceneType.CREDITS: pygame.USEREVENT + SceneType.CREDITS.value,
}

options_events = {
    "RESIZE": pygame.USEREVENT + 10,
}