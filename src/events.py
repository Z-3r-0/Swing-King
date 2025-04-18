import pygame
from src.scenetype import SceneType

events = {
    SceneType.GAME: pygame.USEREVENT + SceneType.GAME.value,
    SceneType.MAIN_MENU: pygame.USEREVENT + SceneType.MAIN_MENU.value,
    SceneType.OPTIONS_MENU: pygame.USEREVENT + SceneType.OPTIONS_MENU.value,
    SceneType.CREDITS: pygame.USEREVENT + SceneType.CREDITS.value,
}
