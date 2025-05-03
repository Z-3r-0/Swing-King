import json
import pygame

from src.entities import Terrain, Obstacle


def load_json_level(file_path):
    """
    Loads the json data from the file path specified.
    :param file_path: Path to the json file
    :return: The data under form of a list
    """
    try:
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


def json_to_list(data: list, screen: pygame.Surface, layer: int) -> list:
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

    try:
        match layer:
            case 0: # Case for terrain
                for block in data:
                    vertices = []
                    positions = block.get("vertices", [])
                    for vertice in positions:
                        vertices.append((vertice.get("x", 0), screen_height - vertice.get("y", 0)))
                    terrain_type = block.get("type", "dirt")
                    if len(vertices) >= 3:
                        try:
                            new_terrain = Terrain(terrain_type, vertices)
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
                return terrain_list

            case 1: # Case for obstacles
                for block in data:
                    pos_data = block.get("position", {"x": 0, "y": 0})
                    position = pygame.Vector2(pos_data.get("x", 0), screen_height - pos_data.get("y", 0))
                    size = block.get("size", 100)
                    angle = block.get("angle", 0)
                    is_colliding = block.get("is_colliding", True)
                    characteristic = block.get("characteristic", None)
                    obstacle_type = block.get("type", "default_obstacle")
                    image_path = f"assets/images/obstacles/{obstacle_type}.png"
                    try:
                        new_obstacle = Obstacle(
                            position=position,
                            image_path=image_path,
                            size=size,
                            is_colliding=is_colliding,
                            angle=angle,
                            nb_points=150,
                            characteristic=characteristic
                        )
                        obstacles_ids[block.get("id", -1)] = new_obstacle
                    except pygame.error as img_err:
                         print(f"Error loading obstacle image '{image_path}': {img_err}. Skipping obstacle ID {block.get('id', 'N/A')}.")
                    except Exception as obs_err:
                         print(f"Error creating obstacle ID {block.get('id', 'N/A')}: {obs_err}. Skipping.")
                sorted_obstacle_dict = dict(sorted(obstacles_ids.items()))
                for value in sorted_obstacle_dict.values():
                    obstacles_list.append(value)
                return obstacles_list

            case _:
                print("Error: Invalid layer specified in json_to_list.")
                return []
    except Exception as e:
        print(f"An error occurred processing layer {layer} data: {e}")
        return []