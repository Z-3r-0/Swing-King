import abc

from enum import Enum
import pygame


import src.utils.settings_loader as settings


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

from src.events import scene_events

class Scene:

    def __init__(self, screen: pygame.Surface, scene_type:SceneType, name: str, scene_from: SceneType = None):

        self.scene_type = scene_type
        self.name = name
        self.screen = screen
        self.settings = settings.load_json_settings("data/settings/settings.json")
        self.fps = self.settings["graphics"]["fps_limit"]

        self.running = False
        
        self.scene_from = scene_from
        
        self.clock = pygame.time.Clock()

    @abc.abstractmethod
    def run(self):
        """
        Abstract method to run the scene. This method should be implemented by subclasses.
        """
        pass


    def resize_hud(self):
        pass

    def switch_scene(self, scene: SceneType, args: dict = None):
        self.running = False
        
        if args:
            pygame.event.post(pygame.event.Event(scene_events[scene], {"args": args}))
        else:
            pygame.event.post(pygame.event.Event(scene_events[scene]))