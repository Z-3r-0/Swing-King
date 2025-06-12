import pygame
from .button import Button

def action_buttons(width, height, action_bar_pos):
    but_terrain = Button(pygame.Vector2(width * 0.06, (action_bar_pos.y - height * 0.07)),
                         pygame.Vector2(height * 0.09, height * 0.05), "Terrain", color=(31, 6, 143),
                         toggled_color=(14, 3, 66))
    but_clear = Button(pygame.Vector2(width * 0.06, action_bar_pos.y + height * 0.02),
                       pygame.Vector2(width * 0.15, height * 0.05), "Clear poly", color=(66, 220, 237))
    but_restart = Button(pygame.Vector2(width * 0.06, action_bar_pos.y + height * 0.09),
                         pygame.Vector2(width * 0.15, height * 0.05), "Restart", color=(255, 0, 0))
    but_rewind = Button(pygame.Vector2(width * 0.23, action_bar_pos.y + height * 0.02),
                        pygame.Vector2(width * 0.15, height * 0.05), "Rewind")
    but_restore = Button(pygame.Vector2(width * 0.23, action_bar_pos.y + height * 0.09),
                         pygame.Vector2(width * 0.15, height * 0.05), "Restore")

    but_grid = Button(pygame.Vector2(width * 0.62, action_bar_pos.y + height * 0.09),
                      pygame.Vector2(width * 0.15, height * 0.05), "Grid", color=(80, 80, 80),
                      toggled_color=(69, 245, 66))
    but_environment = Button(pygame.Vector2(width * 0.79, action_bar_pos.y + height * 0.02),
                         pygame.Vector2(width * 0.15, height * 0.05), "environment", color=(0, 168, 17))
    but_export = Button(pygame.Vector2(width * 0.79, action_bar_pos.y + height * 0.09),
                        pygame.Vector2(width * 0.15, height * 0.05), "Export", color=(255, 162, 0))
    but_quit = Button(pygame.Vector2(width * 0.02, height * 0.02), pygame.Vector2(width * 0.05, height * 0.05), "Quit",
                      color=(255, 0, 0))
    but_load = Button(pygame.Vector2(width * 0.88, height * 0.02), pygame.Vector2(width * 0.10, height * 0.05), "Load a level",
                      color=(0, 80, 145))

    return [but_terrain, but_clear, but_restart, but_rewind, but_restore, but_grid, but_environment, but_export, but_quit, but_load]

def camera_movement_buttons(width, height, action_bar_pos):
    but_left = Button(pygame.Vector2(width * 0.40, action_bar_pos.y + height * 0.06),
                      pygame.Vector2(width * 0.06, height * 0.04), "←", color=(80, 80, 80), font_size=20)
    but_right = Button(pygame.Vector2(width * 0.53, action_bar_pos.y + height * 0.06),
                       pygame.Vector2(width * 0.06, height * 0.04), "→", color=(80, 80, 80), font_size=20)
    but_up = Button(pygame.Vector2(width * 0.47, action_bar_pos.y + height * 0.01),
                    pygame.Vector2(width * 0.05, height * 0.04), "↑", color=(80, 80, 80), font_size=20)
    but_down = Button(pygame.Vector2(width * 0.47, action_bar_pos.y + height * 0.11),
                      pygame.Vector2(width * 0.05, height * 0.04), "↓", color=(80, 80, 80), font_size=20)

    return [but_left, but_right, but_up, but_down]

def terrain_selection_buttons(width, height, action_bar_pos):

    but_terrain_fairway = Button(pygame.Vector2(width * 0.06, (action_bar_pos.y - height * 0.125)),pygame.Vector2(height * 0.09, height * 0.05), "Fairway", color=(62, 133, 54))
    but_terrain_green = Button(pygame.Vector2(width * 0.06, (action_bar_pos.y - height * 0.18)),pygame.Vector2(height * 0.09, height * 0.05), "Green", color=(62,179,62))
    but_terrain_bunker = Button(pygame.Vector2(width * 0.06, (action_bar_pos.y - height * 0.235)),pygame.Vector2(height * 0.09, height * 0.05), "Bunker", color=(255, 197, 106))
    but_terrain_lake = Button(pygame.Vector2(width * 0.06, (action_bar_pos.y - height * 0.29)),pygame.Vector2(height * 0.09, height * 0.05), "Lake", color=(46,118,201))
    but_terrain_rocks = Button(pygame.Vector2(width * 0.06, (action_bar_pos.y - height * 0.345)),pygame.Vector2(height * 0.09, height * 0.05), "Rocks", color=(156, 151, 144)) # @Lucas ici pour la couleur des boutons
    but_terrain_dirt = Button(pygame.Vector2(width * 0.06, (action_bar_pos.y - height * 0.4)),pygame.Vector2(height * 0.09, height * 0.05), "Dirt", color=(130, 99, 54))
    but_terrain_darkgreen = Button(pygame.Vector2(width * 0.06, (action_bar_pos.y - height * 0.455)),pygame.Vector2(height * 0.09, height * 0.05), "DarkGreen", color=(38, 84, 44))
    but_terrain_darkrocks = Button(pygame.Vector2(width * 0.06, (action_bar_pos.y - height * 0.51)),pygame.Vector2(height * 0.09, height * 0.05), "DarkRocks", color=(128, 128, 128))
    but_terrain_darkdirt = Button(pygame.Vector2(width * 0.06, (action_bar_pos.y - height * 0.565)),pygame.Vector2(height * 0.09, height * 0.05), "DarkDirt", color=(87, 59, 19))

    return [but_terrain_fairway, but_terrain_green, but_terrain_bunker, but_terrain_lake, but_terrain_rocks, but_terrain_dirt, but_terrain_darkgreen, but_terrain_darkrocks, but_terrain_darkdirt]

def obstacle_type_buttons(width, height, action_bar_pos):
    but_obstacles = Button(pygame.Vector2(width * 0.62, action_bar_pos.y + height * 0.02),
                                   pygame.Vector2(width * 0.09, height * 0.05), "obstacles Natural")
    but_specials = Button(pygame.Vector2(width * 0.62, action_bar_pos.y + height * 0.02),
                                   pygame.Vector2(width * 0.09, height * 0.05), "specials")

    return [but_obstacles, but_specials]

def obstacle_switching_buttons(width, height, action_bar_pos):
    but_switch_obstacles_left = Button(pygame.Vector2(width * 0.7125, action_bar_pos.y + height * 0.02),
                                       pygame.Vector2(width * 0.0275, height * 0.05), "←")
    but_switch_obstacles_right = Button(pygame.Vector2(width * 0.7425, action_bar_pos.y + height * 0.02),
                                        pygame.Vector2(width * 0.0275, height * 0.05), "→")

    return [but_switch_obstacles_left, but_switch_obstacles_right]

def obstacle_selection_buttons(width, height, action_bar_pos):
    # For natural obstacles
    but_generate_rock1 = Button(pygame.Vector2(width * 0.62, action_bar_pos.y - height*0.07), pygame.Vector2(width * 0.07, height*0.06),"Rock 1")
    but_generate_rock2 = Button(pygame.Vector2(width * 0.62, action_bar_pos.y - height*0.14), pygame.Vector2(width * 0.07, height*0.06), "Rock 2")

    but_generate_rock3 = Button(pygame.Vector2(width * 0.62, action_bar_pos.y  - height*0.21), pygame.Vector2(width * 0.07, height*0.06), "Rock 3")
    but_generate_rock4 = Button(pygame.Vector2(width * 0.62, action_bar_pos.y  - height*0.28), pygame.Vector2(width * 0.07, height*0.06), "Rock  4")

    but_generate_rock5 = Button(pygame.Vector2(width * 0.62, action_bar_pos.y  - height*0.35), pygame.Vector2(width * 0.07, height*0.06), "Rock 5")
    but_generate_rock6 = Button(pygame.Vector2(width * 0.7, action_bar_pos.y  - height*0.07), pygame.Vector2(width * 0.07, height*0.06), "Rock 6")

    but_generate_flat_rock1 = Button(pygame.Vector2(width * 0.7, action_bar_pos.y  - height*0.14), pygame.Vector2(width * 0.07, height*0.06), "Flat Rock 1")
    but_generate_flat_rock2 = Button(pygame.Vector2(width * 0.7, action_bar_pos.y   - height*0.21), pygame.Vector2(width * 0.07, height*0.06), "Flat Rock 2")

    but_generate_big_rock1 = Button(pygame.Vector2(width * 0.7, action_bar_pos.y  - height*0.28), pygame.Vector2(width * 0.07, height*0.06), "Big Rock 1")
    but_generate_big_rock2 = Button(pygame.Vector2(width * 0.7, action_bar_pos.y   - height*0.35), pygame.Vector2(width * 0.07, height*0.06), "Big Rock 2")

    # For specials
    but_generate_starting_point = Button(pygame.Vector2(width * 0.62, action_bar_pos.y - height*0.07), pygame.Vector2(width * 0.07, height*0.06),"Start")
    but_generate_ending_point = Button(pygame.Vector2(width * 0.62, action_bar_pos.y - height*0.14), pygame.Vector2(width * 0.07, height*0.06), "End")

    but_generate_coins = Button(pygame.Vector2(width * 0.7, action_bar_pos.y  - height*0.07), pygame.Vector2(width * 0.07, height*0.06), "Coin")

    return [[but_generate_big_rock1, but_generate_big_rock2, but_generate_flat_rock1, but_generate_flat_rock2, but_generate_rock1, but_generate_rock2, but_generate_rock3, but_generate_rock4, but_generate_rock5, but_generate_rock6],
            [but_generate_starting_point, but_generate_ending_point,but_generate_coins]]
# 'rock1.png', 'rock2.png', 'rock3.png', 'rock4.png', 'rock5.png', 'rock6.png',
# 'flat_rock1.png', 'flat_rock2.png',
# 'big_rock1.png', 'big_rock2.png',

def environment_selection_buttons(width, height, action_bar_pos):
    but_size = pygame.Vector2(width * 0.07, height * 0.04)
    pgd = pygame.Vector2(width * 0.79, action_bar_pos.y)
    
    but_generate_tree1 = Button(pygame.Vector2(pgd.x, pgd.y  - height*0.05), but_size, "Tree 1")
    but_generate_tree2 = Button(pygame.Vector2(pgd.x, pgd.y  - height*0.10), but_size, "Tree 2")
    but_generate_tree3 = Button(pygame.Vector2(pgd.x, pgd.y  - height*0.15), but_size, "Tree 3")
    but_generate_tree4 = Button(pygame.Vector2(pgd.x, pgd.y  - height*0.20), but_size, "Tree 4")
    but_generate_tree5 = Button(pygame.Vector2(pgd.x, pgd.y  - height*0.25), but_size, "Tree 5")

    but_generate_big_tree1 = Button(pygame.Vector2(pgd.x, pgd.y  - height*0.30), but_size, "Big Tree 1")
    but_generate_big_tree2 = Button(pygame.Vector2(pgd.x, pgd.y  - height*0.35), but_size, "Big Tree 2")

    but_generate_tall_tree1 = Button(pygame.Vector2(pgd.x, pgd.y  - height*0.40), but_size, "Tall Tree 1")
    but_generate_tall_tree2 = Button(pygame.Vector2(pgd.x, pgd.y  - height*0.45), but_size, "Tall Tree 2")
    but_generate_tall_tree3 = Button(pygame.Vector2(pgd.x, pgd.y  - height*0.50), but_size, "Tall Tree 3")
    but_generate_tall_tree4 = Button(pygame.Vector2(pgd.x, pgd.y  - height*0.55), but_size, "Tall Tree 4")
    but_generate_tall_tree5 = Button(pygame.Vector2(pgd.x, pgd.y  - height*0.60), but_size, "Tall Tree 5")

    but_generate_big_foliage1 = Button(pygame.Vector2(pgd.x, pgd.y  - height*0.65), but_size, "Big Foliage 1")
    but_generate_big_foliage2 = Button(pygame.Vector2(pgd.x + width*0.08, pgd.y  - height*0.05), but_size, "Big Foliage 2")

    but_generate_bush1 = Button(pygame.Vector2(pgd.x + width*0.08, pgd.y  - height*0.10), but_size, "Bush 1")
    but_generate_bush2 = Button(pygame.Vector2(pgd.x + width*0.08, pgd.y  - height*0.15), but_size, "Bush 2")

    but_generate_tree_bush1 = Button(pygame.Vector2(pgd.x + width*0.08, pgd.y  - height*0.20), but_size, "Tree Bush 1")
    but_generate_tree_bush2 = Button(pygame.Vector2(pgd.x + width*0.08, pgd.y  - height*0.25), but_size, "Tree Bush 2")

    but_generate_foliage = Button(pygame.Vector2(pgd.x + width*0.08, pgd.y  - height*0.30), but_size, "Foliage")
    but_generate_crown_foliage = Button(pygame.Vector2(pgd.x + width*0.08, pgd.y  - height*0.35), but_size, "Crown Foliage")

    but_generate_falling_foliage = Button(pygame.Vector2(pgd.x + width*0.08, pgd.y  - height*0.40), but_size, "Falling Foliage")
    but_generate_leafy_vine = Button(pygame.Vector2(pgd.x + width*0.08, pgd.y  - height*0.45), but_size, "Leafy Vine 1")

    but_generate_leafy_vine2 = Button(pygame.Vector2(pgd.x + width*0.08, pgd.y  - height*0.50), but_size, "Leafy Vine 2")
    but_generate_leafy_vine3 = Button(pygame.Vector2(pgd.x + width*0.08, pgd.y  - height*0.55), but_size, "Leafy Vine 3")

    but_generate_vine = Button(pygame.Vector2(pgd.x + width*0.08, pgd.y  - height*0.60), but_size, "Vine 1")
    but_generate_vine2 = Button(pygame.Vector2(pgd.x + width*0.08, pgd.y  - height*0.65), but_size, "Vine 2")

    but_generate_vine3 = Button(pygame.Vector2(pgd.x + width*0.08, pgd.y  - height*0.70), but_size, "Vine 3")

    return [
        but_generate_big_foliage1, but_generate_big_foliage2,
        but_generate_big_tree1, but_generate_big_tree2,
        but_generate_bush1, but_generate_bush2,
        but_generate_crown_foliage,
        but_generate_falling_foliage,
        but_generate_foliage,
        but_generate_leafy_vine, but_generate_leafy_vine2, but_generate_leafy_vine3,
        but_generate_tall_tree1, but_generate_tall_tree2,but_generate_tall_tree3, but_generate_tall_tree4, but_generate_tall_tree5,
        but_generate_tree1, but_generate_tree2, but_generate_tree3, but_generate_tree4, but_generate_tree5,
        but_generate_tree_bush1, but_generate_tree_bush2,
        but_generate_vine, but_generate_vine2, but_generate_vine3
    ]
