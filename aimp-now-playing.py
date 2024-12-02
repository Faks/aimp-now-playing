from typing import Any
import obspython as obs
import re


class AimpPlayer:
    def __init__(self):
        self.text_source_name = 'AIMP: Now Playing'

    def update_text_source(self, title):
        text_source = obs.obs_get_source_by_name(self.text_source_name)
        if text_source is not None:
            settings = obs.obs_data_create()
            obs.obs_data_set_string(settings, 'text', title)
            obs.obs_source_update(text_source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(text_source)

    def tick(self):
        file_path = "C:\/Users\/faks\Documents\/AIMP\/now_playing.txt"

        try:
            with open(file_path, "r") as file:
                get_playing_now = file.read().strip()  # Strip trailing whitespace
                self.update_text_source(get_playing_now)

        except FileNotFoundError:
            print(f"DEBUG: File at path {file_path} not found.")
        except Exception as e:
            print(f"DEBUG: An error occurred: {e}")


# Create an instance of the AimpPlayer class
aimpPlayer = AimpPlayer()


# Define the script properties for OBS
def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, 'text_source_name', 'Text Source Name', obs.OBS_TEXT_DEFAULT)

    return props


# Define the script tick function for OBS
def script_tick(seconds):
    aimpPlayer.tick()
