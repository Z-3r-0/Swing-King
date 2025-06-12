import json
import pygame
from pygame import Vector2

from src.entities import Terrain, Obstacle, Flag
from src.hud.level_creator_hud import polygons, obstacle, Polygon


def load_json_level(file_path):
    """
    Loads the json data from the file path specified.
    :param file_path: Path to the json file
    :return: The data under form of a list
    """
    try:
        # Use "utf-8-sig" encoding to ignore BOM
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            level = json.loads(content)
            terrain = level.get("zones", [])
            obstacles = level.get("obstacles", [])
            return terrain, obstacles
    except FileNotFoundError:
        print(f"Error : File '{file_path}' was not found.")
        return [], []
    except json.JSONDecodeError as e:
        print("JSON decoding error :", e)
        return [], []
    except Exception as e:
        print("An error occurred during level loading:", e)
        return [], []


def json_to_list(data: list, screen: pygame.Surface, layer: int, is_level_creator:bool = False) -> list:
    """
    Converts the provided data to a Terrain or Obstacle list if it respects level json structure.
    :param screen: The screen surface (used for height calculation).
    :param data: The json data representing the level part (zones or obstacles).
    :param layer: 0 for terrain (zones), 1 for obstacles.
    :return: The list of Terrain or Obstacle objects.
    """
    terrain_ids = {}
    terrain_list = []
    obstacles_ids = {}
    obstacles_list = []
    screen_height = screen.get_height()

    min_y = float('inf')

    try:
        match layer:
            case 0: # Case for terrain
                for block in data:
                    vertices = []
                    positions = block.get("vertices", [])
                    for vertice in positions:
                        vertices.append((vertice.get("x", 0), screen_height - vertice.get("y", 0)))
                        point = pygame.Vector2(vertice["x"], vertice["y"])
                        
                        if point.y < min_y:
                            min_y = point.y
                        
                    terrain_type = block.get("type", "fairway")
                    if len(vertices) >= 3:
                        if(not is_level_creator):
                            try:
                                new_terrain = Terrain(terrain_type, vertices)
                                terrain_ids[block.get("id", -1)] = new_terrain
                            except ValueError as ve:
                                 print(f"Warning: Could not create terrain ID {block.get('id', 'N/A')}: {ve}")
                            except Exception as e:
                                 print(f"Error creating terrain ID {block.get('id', 'N/A')}: {e}")
                        else:
                            try:
                                new_terrain = Polygon(terrain_type, vertices)
                                terrain_ids[block.get("id", -1)] = new_terrain
                            except ValueError as ve:
                                 print(f"Warning: Could not create terrain ID {block.get('id', 'N/A')}: {ve}")
                            except Exception as e:
                                 print(f"Error creating terrain ID {block.get('id', 'N/A')}: {e}")


                    else:
                        print(f"Warning: Terrain block ID {block.get('id', 'N/A')} has < 3 vertices. Skipping.")
                sorted_terrain_dict = dict(sorted(terrain_ids.items()))
                for value in sorted_terrain_dict.values():
                    terrain_list.append(value)
                    
                # Create a terrain of type void at 0 x position and minimum y position, as long as the level size
                vertices = [(0, screen_height - min_y), (10000, screen_height - min_y), (100000, screen_height - min_y - 30), (0, screen_height - min_y - 30)]  # 10000 is the max size of a level, +30 is arbitrary
                if not is_level_creator:
                    void = Terrain("void", vertices)
                    terrain_list.append(void)
                    
                return terrain_list

            case 1: # Case for obstacles
                for block in data:
                    if not is_level_creator and block["characteristic"] == "end":
                        position = Vector2(block["position"]["x"], screen.get_height() - block["position"]["y"] - (108-block["size"]))  # 108 is the size of the flag sprite
                        angle = block["angle"]

                        new_obstacle = Flag(position, angle)
                        obstacles_ids[block["id"]] = new_obstacle

                        continue

                    position = pygame.Vector2(block["position"]["x"], screen.get_height() - block["position"]["y"])
                    size = block["size"]
                    angle = block["angle"]
                    is_colliding = block["is_colliding"]
                    characteristic = block["characteristic"]
                    if(not is_level_creator):
                        new_obstacle = Obstacle(position=position, image_path=f"{block['type']}.png", size=size, is_colliding=is_colliding, angle=angle, nb_points=150, characteristic=characteristic)
                    else:
                        new_obstacle = obstacle.Obstacle(position=position, image_path=f"{block['type']}.png", size=size, is_colliding=is_colliding, angle=angle, nb_points=150, characteristic=characteristic)
                    obstacles_ids[block["id"]] = new_obstacle

            case _:
                print("Error: Invalid layer specified in json_to_list.")
                return []

        sorted_obstacle_dict = dict(sorted(obstacles_ids.items()))

        for value in sorted_obstacle_dict.values():
            obstacles_list.append(value)

        return obstacles_list

    except Exception as e:
        print(f"An error occurred processing layer {layer} data: {e}")
        return []
