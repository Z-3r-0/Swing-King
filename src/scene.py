import abc

import pygame

from src.scenetype import SceneType
import src.utils.settings_loader as settings


class Scene:

    def __init__(self, screen: pygame.Surface, scene_type:SceneType, name: str, scene_from: SceneType = None):

        self.scene_type = scene_type
        self.name = name
        self.screen = screen
        self.settings = settings.load_json_settings("data/settings/settings.json")
        self.fps = self.settings["graphics"]["fps_limit"]

        self.running = False
        
        self.scene_from = scene_from

    @abc.abstractmethod
    def run(self):
        """
        Abstract method to run the scene. This method should be implemented by subclasses.
        """
        pass


    def resize_hud(self):
        pass
    
    def switch_to_scene(self, scene: SceneType):
        pass