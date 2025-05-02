from src.utils import *
from src.scenetype import SceneType
from src.events import scene_events
from src.scenes import *

pygame.init()

# Window parameters
WIDTH, HEIGHT = 1920, 1080  # TODO - Replace by screen resolution later

screen = pygame.display.set_mode((WIDTH, HEIGHT))

scene = SceneType.MAIN_MENU
from_scene = None
args = None

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
                    args = event.dict["args"] if event.dict else None

    match scene:
        case SceneType.GAME:
            game = Game(screen, None, args[0])
            game.scene_from = from_scene
            game.running = True
            game.run()
        case SceneType.MAIN_MENU:
            main_menu = Menu(screen)
            main_menu.scene_from = from_scene
            main_menu.running = True
            main_menu.run()
        case SceneType.OPTIONS_MENU:
            option_menu = OptionMenu(screen, None)
            option_menu.scene_from = from_scene
            option_menu.running = True
            option_menu.run()
        case SceneType.LEVEL_CREATOR:
            level_creator = LevelCreator(screen, None)
            level_creator.scene_from = from_scene
            level_creator.running = True
            level_creator.run()
        case SceneType.LEVEL_SELECTOR:
            level_selector = LevelSelector(screen, SceneType.MAIN_MENU)
            level_selector.scene_from = from_scene
            level_selector.running = True
            level_selector.run()
        case SceneType.CREDITS:
            # TODO - Implement credits menu
            pygame.quit()
            exit()

    clock.tick(60)
