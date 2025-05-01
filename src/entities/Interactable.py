import pygame
from enum import Enum
import math

class InteractableType(Enum):
    """Types d'objets interactifs dans le jeu."""
    COIN = 1
    FLAG = 2
    POWERUP = 3
    TELEPORT = 4
    CHECKPOINT = 5
    CUSTOM = 99

class Interactable:
    def __init__(self, position: pygame.Vector2, radius: float, interactable_type: InteractableType,
                 image_path: str = None, callback_function=None, event_id: int = None,
                 event_param=None, one_time_use: bool = False):
        """
        Initializes an interactable object.
        
        :param position: Position of the interactable object
        :param radius: Radius of the interactable object
        :param interactable_type: Type of the interactable object
        :param image_path: Path to the interactable object image
        :param callback_function:
        :param event_id:
        :param event_param: Values to pass through the event
        :param one_time_use: If True, the object can only be used once
        """
        self.position = position
        self.scale_value = 7  # Même échelle que pour la balle
        self.radius = radius
        self.type = interactable_type
        self.rect = pygame.Rect((self.position.x - self.radius * self.scale_value),
                                (self.position.y - self.radius * self.scale_value),
                                (self.radius * self.scale_value) * 2,
                                (self.radius * self.scale_value) * 2)

        # Image et masque
        self.image_path = image_path
        if self.image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.smoothscale(self.image,
                                                      (self.radius * 2 * self.scale_value,
                                                       self.radius * 2 * self.scale_value))
        else:
            # Créer une image par défaut basée sur le type
            self.image = self._create_default_image()

        # Surface pour la détection de collision
        self.surface = pygame.Surface((self.radius * 2 * self.scale_value,
                                       self.radius * 2 * self.scale_value),
                                      pygame.SRCALPHA)
        pygame.draw.circle(self.surface, (255, 255, 255),
                           (self.radius * self.scale_value, self.radius * self.scale_value),
                           self.radius * self.scale_value)
        self.mask = pygame.mask.from_surface(self.surface)

        # Callbacks et événements
        self.callback_function = callback_function
        self.event_id = event_id
        self.event_param = event_param
        self.one_time_use = one_time_use
        self.used = False

        # Animation
        self.animation_timer = 0
        self.animation_active = False
        self.ANIMATION_DURATION = 20  # frames

    def _create_default_image(self):
        """
        Creates a default image based off the interactable type.
        :return: 
        """
        size = int(self.radius * 2 * self.scale_value)
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        if self.type == InteractableType.COIN:
            color = (255, 215, 0)  # Or
            pygame.draw.circle(surface, color, (size // 2, size // 2), size // 2)
            pygame.draw.circle(surface, (0, 0, 0), (size // 2, size // 2), size // 2, 2)

        elif self.type == InteractableType.FLAG:
            # Trou de golf (pas le drapeau lui-même)
            # Cercle extérieur (bordure)
            outer_color = (40, 40, 40)  # Noir/gris foncé
            inner_color = (0, 0, 0)     # Noir pour l'intérieur du trou
            
            # TODO - CHANGE VIEW TO SIDE (currently topdown)

            # Dessiner le contour du trou
            pygame.draw.circle(surface, outer_color, (size // 2, size // 2), size // 2)

            # Dessiner l'intérieur du trou (un peu plus petit)
            inner_size = int(size * 0.8)
            pygame.draw.circle(surface, inner_color, (size // 2, size // 2), inner_size // 2)

            # Ajouter un effet d'ombre/profondeur
            shadow_size = int(size * 0.7)
            pygame.draw.circle(surface, (10, 10, 10), (size // 2, size // 2 + size // 20), shadow_size // 2)

        else:  # CUSTOM ou type non défini
            # Un cercle avec un point d'interrogation
            color = (192, 192, 192)  # Gris argenté
            pygame.draw.circle(surface, color, (size // 2, size // 2), size // 2)

            # Ajouter un "?" au centre
            if pygame.font.get_init():
                try:
                    font = pygame.font.Font(None, size // 2)
                    text = font.render("?", True, (0, 0, 0))
                    text_rect = text.get_rect(center=(size // 2, size // 2))
                    surface.blit(text, text_rect)
                except Exception:
                    # Dessiner un point d'interrogation simplifié
                    pygame.draw.arc(surface, (0, 0, 0), (size // 3, size // 4, size // 3, size // 3), 0, 3.14, 3)
                    pygame.draw.circle(surface, (0, 0, 0), (size // 2, size * 2 // 3), size // 12)

        return surface

    def draw(self, surface):
        """
        Dessine l'objet interactif sur la surface spécifiée.
        
        :param surface: Surface sur laquelle dessiner l'objet
        """
        if self.used and self.one_time_use:
            return  # Ne pas dessiner si l'objet a été utilisé et est à usage unique

        # Gérer l'animation si elle est active
        scale_factor = 1.0
        if self.animation_active:
            progress = self.animation_timer / self.ANIMATION_DURATION
            # Effet de pulsation
            scale_factor = 1.0 + 0.2 * abs(math.sin(progress * math.pi))

            self.animation_timer -= 1
            if self.animation_timer <= 0:
                self.animation_active = False

        # Appliquer l'échelle pour l'animation
        if scale_factor != 1.0:
            scaled_size = (int(self.image.get_width() * scale_factor),
                           int(self.image.get_height() * scale_factor))
            scaled_image = pygame.transform.smoothscale(self.image, scaled_size)

            # Calculer la position pour garder l'objet centré
            offset_x = (scaled_size[0] - self.image.get_width()) // 2
            offset_y = (scaled_size[1] - self.image.get_height()) // 2

            surface.blit(scaled_image,
                         (self.position.x - self.radius * self.scale_value - offset_x,
                          self.position.y - self.radius * self.scale_value - offset_y))
        else:
            surface.blit(self.image,
                         (self.position.x - self.radius * self.scale_value,
                          self.position.y - self.radius * self.scale_value))

    def check_collision(self, ball):
        """
        Vérifie s'il y a collision avec la balle et déclenche l'action correspondante.
        
        :param ball: L'objet Ball à vérifier pour collision
        :return: True si une collision a été détectée et traitée, False sinon
        """
        if self.used and self.one_time_use:
            return False

        # Vérifier la collision avec la balle
        offset = (self.rect.left - ball.rect.left, self.rect.top - ball.rect.top)
        if ball.mask.overlap(self.mask, offset):
            return self.trigger_action(ball)
        return False

    def trigger_action(self, ball):
        """
        Déclenche l'action associée à cet objet interactif.
        
        :param ball: L'objet Ball qui a déclenché l'action
        :return: True si une action a été déclenchée, False sinon
        """
        # Marquer comme utilisé si c'est un objet à usage unique
        if self.one_time_use:
            self.used = True

        # Déclencher l'animation
        self.animation_active = True
        self.animation_timer = self.ANIMATION_DURATION

        # 1. Appeler la fonction de callback si elle existe
        if self.callback_function:
            self.callback_function(ball, self)

        # 2. Poster un événement si un ID d'événement est défini
        if self.event_id:
            event = pygame.event.Event(self.event_id,
                                       {"interactable_type": self.type,
                                        "param": self.event_param,
                                        "interactable": self})
            pygame.event.post(event)

        return True

    def reset(self):
        """Réinitialise l'état de l'objet interactif (pour les objets à usage unique)."""
        self.used = False
        self.animation_active = False
        self.animation_timer = 0