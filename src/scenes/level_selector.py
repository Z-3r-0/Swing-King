import math

import pygame
from pygame import Vector2

from src.scene import Scene, SceneType
from src.hud.button import Button
from src.utils.level_export import get_level_count


class LevelSelector(Scene):

    def __init__(self, screen, scene_from: SceneType = None):

        super().__init__(screen, SceneType.LEVEL_SELECTOR, "Level Selector", scene_from)

        self.background = pygame.image.load("assets/images/backgrounds/swing_king_1.png").convert()
        self.background = pygame.transform.scale(self.background, self.screen.get_size())
        self.panel = pygame.Surface((self.screen.get_width() - 400, self.screen.get_height() - 200))
        self.panel.fill((128, 128, 128))
        self.panel.set_alpha(200)


        # Here, each files stores the completion data of a level, if there is no file for a level, it means we did not complete it
        # Thus, we can't access the following levels
        # This is why we don't look directly in the data/levels folder but rather in the stats
        self.level_count = get_level_count("data/stats") + 1  # +1 because we want to be able to play the level after the last one finished
        self.level_count = min(self.level_count, get_level_count("data/levels"))  # To make sure there are not too many buttons compared to the actual count of levels in data/levels
        
        self.max_button_per_row = 4
        self.buttons = []  # This will be a matrix so that we can easily build a grid out of the button list
        self.texts = []  # Also a matrix corresponding to the text to display on each button

        self.build_buttons()

    def reload(self):
        self.level_count = get_level_count("data/stats") + 1
        self.level_count = min(self.level_count, get_level_count("data/levels"))
        self.max_button_per_row = 4
        self.buttons = []  # This will be a matrix so that we can easily build a grid out of the button list

        self.build_buttons()

    def build_buttons(self):
        count = self.level_count
        rows = math.ceil(self.level_count / self.max_button_per_row)
    
        # Pre-compute the number of lines we need
        for i in range(rows):
            self.buttons.append([])
            self.texts.append([])
    
        # Calculate sizes
        button_width = 270
        button_height = 80
        panel_width = self.screen.get_width() - 400
        panel_height = self.screen.get_height() - 200
    
        # Calculate spacing
        horizontal_spacing = panel_width / self.max_button_per_row
        vertical_spacing = panel_height / rows
    
        for i in range(len(self.buttons)):
            for j in range(self.max_button_per_row):
                if count <= 0:
                    break
    
                # Calculate position based on indices i and j
                position = Vector2(
                    100 + horizontal_spacing / 2 + j * horizontal_spacing,  # X position
                    50 + vertical_spacing / 2 + i * vertical_spacing       # Y position
                )
    
                size = Vector2(button_width, button_height)
                button = Button(
                    self.screen,
                    lambda lvl=self.level_count - count + 1: self.switch_scene(SceneType.GAME, args={"level": lvl}),
                    position,
                    size,
                    "assets/images/buttons/blank/blank_button.png",
                    "assets/images/buttons/blank/blank_button.png",
                    "assets/images/buttons/blank/blank_button.png"
                )



                # Add text at the center of the button
                x = button.rect.x + button.rect.width / 2
                y = button.rect.y + button.rect.height / 2
                text_position = Vector2(x, y)
                label = f"Level {self.level_count - count + 1}"

                text = (text_position, label)

                self.buttons[i].append(button)
                self.texts[i].append(text)
                count -= 1

    def run(self):

        super().run()

        while self.running:
            self.screen.blit(self.background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                for row in self.buttons:
                    for button in row:
                        button.listen(event)

            self.screen.blit(self.panel, (200, 100))

            for row in self.buttons:
                for button in row:
                    button.hover()
                    button.draw()

            for row in self.texts:
                for text in row:

                    font = pygame.font.Font("assets/fonts/shrikhand-regular.ttf", 30)
                    label = text[1]
                    text_surface = font.render(label, True, (31, 128, 41))
                    text_rect = text_surface.get_rect(center=text[0])
                    self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            self.clock.tick(self.fps)
