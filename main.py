﻿from src.scenes.credits import Credits
from src.utils import *
from src.scene import SceneType
from src.scenes import *
from src.events import scene_events, options_events
from src.utils.volume import update_volume

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("assets/audio/music/SwingKing.mp3")


screen = pygame.display.set_mode(flags=pygame.SRCALPHA)
game = Game(screen, "data/levels", None)
main_menu = Menu(screen)
option_menu = OptionMenu(screen, None)
level_creator = LevelCreator(screen, None)
level_selector = LevelSelector(screen, None)
credits = Credits(screen, None)

scene = SceneType.MAIN_MENU
from_scene = None

clock = pygame.time.Clock()
pygame.mixer.Channel(0)

pygame.mixer.music.play(-1)

update_volume()

while True:
    args = None
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type in scene_events.values():
            for scene_type, evt_id in scene_events.items():
                if event.type == evt_id:
                    from_scene = scene
                    scene = scene_type
                    
                    args = event.dict.get("args", None)
                    
                    if scene == SceneType.GAME and args is not None:
                        level_number = args["level"]
                        game.load_level(level_number)

    match scene:
        case SceneType.GAME:
            game.scene_from = from_scene
            game.reset_level_state()
            game.run()
        case SceneType.MAIN_MENU:
            main_menu.scene_from = from_scene
            main_menu.run()
        case SceneType.OPTIONS_MENU:
            option_menu.scene_from = from_scene
            option_menu.run()
        case SceneType.LEVEL_CREATOR:
            level_creator.scene_from = from_scene
            level_creator.run()
        case SceneType.LEVEL_SELECTOR:
            level_selector.reload()
            level_selector.scene_from = from_scene
            level_selector.run()
        case SceneType.CREDITS:
            credits.scene_from = from_scene
            credits.run()

    clock.tick(load_json_settings("data/settings/settings.json")["graphics"]["fps_limit"])