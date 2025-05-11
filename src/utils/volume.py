import pygame

from src.utils import load_json_settings


def update_volume():
    pygame.mixer.Channel(0).set_volume(float(load_json_settings("data/settings/settings.json")["audio"]["SFX"] / 100 * (load_json_settings("data/settings/settings.json")["audio"]["Master"] / 100)))
    pygame.mixer.music.set_volume(float(load_json_settings("data/settings/settings.json")["audio"]["Music"] / 100 * (load_json_settings("data/settings/settings.json")["audio"]["Master"] / 100)))
