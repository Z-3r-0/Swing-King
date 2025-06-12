from src.hud.level_creator_hud import *
from src.hud.level_creator_hud import Polygon
from src.utils.level_export import *


def rewind(list_polygons):
    """
    Rewinds the last action on the list of polygons.

    :param list_polygons: The list of polygons to rewind.
    :type list_polygons: list
    :return: The updated list of polygons.
    :rtype: list
    """
    polygons = list_polygons.copy()

    if list_polygons and not list_polygons[-1].points and len(list_polygons) > 1:
        polygons.pop()

    polygons[-1].remove_point()

    return polygons


def restore(list_polygons):
    """
    Restores the last removed point on the list of polygons.

    :param list_polygons: The list of polygons to restore.
    :type list_polygons: list
    :return: The updated list of polygons.
    :rtype: list
    """
    polygons = list_polygons.copy()
    polygons[-1].restore_point()

    return polygons


def clear(list_polygons, current_terrain_type):
    """
    Clears the last polygon from the list.

    :param list_polygons: The list of polygons to clear.
    :type list_polygons: list
    :return: The updated list of polygons and the current terrain type.
    :rtype: tuple
    """
    polygons = list_polygons.copy()

    if len(polygons) > 0:
        polygons.pop()
        current_terrain_type = polygons[-1].terrain_type if len(polygons) > 0 else current_terrain_type

    return polygons, current_terrain_type


def restart():
    """
    Restarts the polygon list with a default polygon.

    :return: The initial list of polygons and the current terrain type.
    :rtype: tuple
    """
    return [Polygon(terrain_type="fairway")], "fairway"


def export(list_polygons, list_obstacles):
    """
    Exports the list of polygons and obstacles to a JSON file.

    :param list_polygons: The list of polygons to export.
    :type list_polygons: list
    :param list_obstacles: The list of obstacles to export.
    :type list_obstacles: list
    :return: None
    """
    polygons = list_polygons.copy()
    obstacles = list_obstacles.copy()

    global_origin = (0, 0)
    if len(polygons[0].points) > 0:
        global_origin = polygons[0].points[0]



    data = {
        "zones": [],
        "obstacles": []
    }

    for poly in polygons:
        if (len(poly.points)) > 2:
            relative_points = [(x - global_origin[0], global_origin[1] - y) for (x, y) in poly.points]
            data["zones"].append({
                "type": poly.terrain_type,
                "vertices": relative_points
            })

    for obstacle in obstacles:
        data["obstacles"].append({
            "type": str.replace(obstacle.image_path, "assets/images/obstacles/", "")[:-4],  # Remove the .png
            "is_colliding": obstacle.is_colliding,
            "position": (obstacle.position.x - global_origin[0], global_origin[1] - obstacle.position.y),
            "size": obstacle.size,
            "angle": obstacle.angle,
            "characteristic": obstacle.characteristic
        })

    file_count = get_level_count("data/levels")

    export_level(f"data/levels/level{file_count + 1}.json", data["zones"], data["obstacles"])


def add_polygon_of_type(list_polygons, current_terrain_type, new_terrain_type):
    """
    Adds a new polygon of a specified type to the list.

    :param list_polygons: The list of polygons to add to.
    :type list_polygons: list
    :param current_terrain_type: The current terrain type.
    :type current_terrain_type: str
    :param new_terrain_type: The new terrain type to add.
    :type new_terrain_type: str
    :return: The updated list of polygons and the new terrain type.
    :rtype: tuple
    """
    if new_terrain_type == current_terrain_type:
        return list_polygons.copy(), current_terrain_type

    polygons = list_polygons.copy()

    # Create new polygon linked to the previous one
    last_poly = polygons[-1] if polygons else Polygon(terrain_type=new_terrain_type)

    new_poly = Polygon(terrain_type=new_terrain_type)

    if (len(last_poly.points)) > 2:
        new_poly.add_point(last_poly.points[-1])
        new_poly.add_point(last_poly.points[-2])  # Start with bottom point

    polygons.append(new_poly)

    return polygons, new_terrain_type


def camera_left(camera, camera_speed, camera_movement, min_width):
    """
    Moves the camera to the left.

    :param camera: The current camera position.
    :type camera: pygame.Vector2
    :param camera_speed: The speed of the camera movement.
    :type camera_speed: pygame.Vector2
    :param camera_movement: The current camera movement.
    :type camera_movement: pygame.Vector2
    :param min_width: The minimum width boundary.
    :type min_width: int
    :return: The updated camera position and movement.
    :rtype: tuple
    """
    if camera.x <= min_width:
        camera.x = min_width
    else:
        camera.x -= camera_speed.x
        camera_movement.x = -camera_speed.x

    return camera, camera_movement


def camera_right(camera, camera_speed, camera_movement, max_width, width):
    """
    Moves the camera to the right.

    :param camera: The current camera position.
    :type camera: pygame.Vector2
    :param camera_speed: The speed of the camera movement.
    :type camera_speed: pygame.Vector2
    :param camera_movement: The current camera movement.
    :type camera_movement: pygame.Vector2
    :param max_width: The maximum width boundary.
    :type max_width: int
    :param width: The width of the screen.
    :type width: int
    :return: The updated camera position and movement.
    :rtype: tuple
    """
    if camera.x >= max_width - width:
        camera.x = max_width - width
    else:
        camera.x += camera_speed.x
        camera_movement.x = camera_speed.x

    return camera, camera_movement


def camera_up(camera, camera_speed, camera_movement, min_height):
    """
    Moves the camera up.

    :param camera: The current camera position.
    :type camera: pygame.Vector2
    :param camera_speed: The speed of the camera movement.
    :type camera_speed: pygame.Vector2
    :param camera_movement: The current camera movement.
    :type camera_movement: pygame.Vector2
    :param min_height: The minimum height boundary.
    :type min_height: int
    :return: The updated camera position and movement.
    :rtype: tuple
    """
    if camera.y <= min_height:
        camera.y = min_height
    else:
        camera.y -= camera_speed.y
        camera_movement.y = -camera_speed.y

    return camera, camera_movement


def camera_down(camera, camera_speed, camera_movement, max_height, height):
    """
    Moves the camera down.

    :param camera: The current camera position.
    :type camera: pygame.Vector2
    :param camera_speed: The speed of the camera movement.
    :type camera_speed: pygame.Vector2
    :param camera_movement: The current camera movement.
    :type camera_movement: pygame.Vector2
    :param max_height: The maximum height boundary.
    :type max_height: int
    :param height: The height of the screen.
    :type height: int
    :return: The updated camera position and movement.
    :rtype: tuple
    """
    if camera.y >= max_height - height:
        camera.y = max_height - height
    else:
        camera.y += camera_speed.y
        camera_movement.y = camera_speed.y

    return camera, camera_movement


def switch_obstacles_left(obstacles_type, obstacles_types):
    """
    Switches to the previous obstacle type in the list.

    :param obstacles_type: The current obstacle type.
    :type obstacles_type: str
    :param obstacles_types: The list of all obstacle types.
    :type obstacles_types: list
    :return: The index of the previous obstacle type.
    :rtype: int
    """
    index = obstacles_types.index(obstacles_type)
    index = (index - 1) % len(obstacles_types)
    return index


def switch_obstacles_right(obstacles_type, obstacles_types):
    """
    Switches to the next obstacle type in the list.

    :param obstacles_type: The current obstacle type.
    :type obstacles_type: str
    :param obstacles_types: The list of all obstacle types.
    :type obstacles_types: list
    :return: The index of the next obstacle type.
    :rtype: int
    """
    index = obstacles_types.index(obstacles_type)
    index = (index + 1) % len(obstacles_types)
    return index

def sort_levels(levels):
    """
    Trie une liste de niveaux en séparant le préfixe 'level' des numéros et en triant les numéros.

    :param levels: Liste des noms de fichiers de niveaux.
    :type levels: list
    :return: Liste triée des noms de fichiers de niveaux.
    :rtype: list
    """
    return sorted(levels, key=lambda x: int(x.replace("level", "").replace(".json", "")))
