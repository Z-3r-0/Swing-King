import json


def load_json_settings(file_path: str) -> dict:
    """
    Load a json settings file from a given file path
    :param file_path: The file path of the json file
    :return: The json data as a dictionary
    """

    with open(file_path) as json_file:
        return json.load(json_file)

def save_json_settings(file_path: str, data: dict):
    """²
    Save a dictionary as a json file
    :param file_path: The file path of the json file
    :param data: The dictionary to save as a json file
    """

    json_file = open(file_path, 'w')
    json.dump(data, json_file, indent=4)
    json_file.close()