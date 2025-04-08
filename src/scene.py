import abc

import pygame

from src.scenetype import SceneType


class Scene:

    def __init__(self, scene_type:SceneType, name: str, screen: pygame.Surface):

        self.scene_type = scene_type
        self.name = name
        self.screen = screen

    @abc.abstractmethod
    def run(self):
        """
        Abstract method to run the scene. This method should be implemented by subclasses.
        """
        pass
