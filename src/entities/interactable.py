from enum import Enum

from pygame import Vector2


class InteractableType(Enum):
    COIN = 1,
    FLAG = 2,


class Interactable:
    
    
    def __init__(self, type: InteractableType, position: Vector2, ):
        pass