import json
import os

def get_level_count(folder_path):
    """
    Returns the number of level files in the specified folder.

    :param folder_path: The path to the folder containing level files.
    :type folder_path: str
    :return: The number of level files in the folder.
    :rtype: int
    """
    count = 0
    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            count += 1
    return count

def export_level(file_path, surface_vertices: list, obstacles: list):
    """
    Exports terrain data to a JSON file.

    :param file_path: The path to the file where the data will be saved.
    :type file_path: str
    :param surface_vertices: A list of dictionaries containing surface vertices data.
    :type surface_vertices: list
    :param obstacles: A list of dictionaries containing obstacle data.
    :type obstacles: list
    :return: None
    """
    count = 0
    data = {
        "zones": [],
        "obstacles": []
    }

    print("Exporting terrain data...")

    for dico in surface_vertices:
        data["zones"].append({
            "id": count,
            "type": dico["type"],
            "vertices": [{"x": dico["vertices"][i][0], "y": dico["vertices"][i][1]} for i in range(len(dico["vertices"]))],
        })
        count += 1

    count = 0

    for dico in obstacles:
        data["obstacles"].append({
            "id": count,
            "type": dico["type"],
            "is_colliding": dico["is_colliding"],
            "position": {"x": dico["position"][0], "y": dico["position"][1]},
            "size": dico["size"],
            "angle": dico["angle"],
            "characteristic": dico["characteristic"] if dico["characteristic"] else None
        })
        count += 1

    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data exported to {file_path}")