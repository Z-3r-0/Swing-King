from src.utils import *
from src.scene import SceneType
import src.scenes.game as game_module
import src.scenes.menu as menu_module
import src.scenes.level_creator as level_creator_module
import src.scenes.option_menu as option_module
from src.events import scene_events

pygame.init()

# Window parameters
WIDTH, HEIGHT = 1920, 1080  # TODO - Replace by screen resolution later

screen = pygame.display.set_mode((WIDTH, HEIGHT))
game = game_module.Game(screen, "data/levels", None)
main_menu = menu_module.Menu(screen)
option_menu = option_module.OptionMenu(screen, None)
level_creator = level_creator_module.LevelCreator(screen, None)

scene = SceneType.MAIN_MENU
from_scene = None

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type in scene_events.values():
            for scene_type, evt_id in scene_events.items():
                if event.type == evt_id:
                    from_scene = scene
                    scene = scene_type

    match scene:
        case SceneType.GAME:
            game.scene_from = from_scene
            game.running = True
            game.run()
        case SceneType.MAIN_MENU:
            main_menu.scene_from = from_scene
            main_menu.running = True
            main_menu.run()
        case SceneType.OPTIONS_MENU:
            option_menu.scene_from = from_scene
            option_menu.running = True
            option_menu.run()
        case SceneType.LEVEL_CREATOR:
            level_creator.scene_from = from_scene
            level_creator.running = True
            level_creator.run()
        case SceneType.CREDITS:
            # TODO - Implement credits menu
            pygame.quit()
            exit()

    clock.tick(60)
