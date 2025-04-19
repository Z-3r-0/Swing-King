import pygame
from src.utils import *
from src.scenetype import SceneType
import src.game as game_module
import src.menu as menu_module
from src.events import scene_events

# Window parameters
WIDTH, HEIGHT = 1920, 1080  # TODO - Replace by screen resolution later
scene = SceneType.MAIN_MENU

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
game = game_module.Game(screen)
main_menu = menu_module.Menu(screen)

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type in scene_events.values():
            for scene_type, evt_id in scene_events.items():
                if event.type == evt_id:
                    scene = scene_type
                    print(f"Changing scene to {scene.name}")

    match scene:
        case SceneType.GAME:
            game.run()
        case SceneType.MAIN_MENU:
            main_menu.run()
        case SceneType.OPTIONS_MENU:
            pygame.quit()
            exit()
            # TODO - Implement options menu
        case SceneType.CREDITS:
            # TODO - Implement credits menu
            pygame.quit()
            exit()

    clock.tick(60)
