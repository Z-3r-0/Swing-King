import json
import pygame

from src.entities import Terrain


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
            return level["zones"]
    except FileNotFoundError:
        print(f"Error : File '{file_path}' was not found.")
    except json.JSONDecodeError as e:
        print("JSON decoding error :", e)
    except Exception as e:
        print("An error occurred :", e)


def json_to_list(data: list, screen: pygame.Surface) -> list:
    """
    Converts the provided data to a Terrain list if it respects level json structure.
    :param screen: The screen where the terrain will be drawn
    :param data: The json data representing the level
    :return: The terrain list representing the level.
    """

    terrain_ids = {}
    terrain_list = []


    for block in data:
        vertices = []
        # Recreate a Terrain instance
        positions = block["vertices"]

        for vertice in positions:
            vertices.append((vertice["x"], screen.get_height() - vertice["y"]))

        terrain_type = block["type"]

        new_terrain = Terrain(terrain_type, vertices)

        terrain_ids[block["id"]] = new_terrain

    # To get the final list in the order we want to draw the zones (not to display one over another in a weird way)
    # The order is based off the id of each zone in the json file
    sorted_terrain_dict = dict(sorted(terrain_ids.items()))

    for value in sorted_terrain_dict.values():
        terrain_list.append(value)

    return terrain_list
