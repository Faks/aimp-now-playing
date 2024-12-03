
from typing import Any
import obspython as obs
import re
import os


class AimpPlayer:
    def __init__(self, text_source_name='AIMP: Now Playing', file_path='C:/Users/faks/Documents/AIMP/now_playing.txt'):
        if not text_source_name or not re.match(r'^[\w\s:]+$', text_source_name):
            obs.script_log(obs.LOG_WARNING, "Invalid text source name provided. Defaulting to 'AIMP: Now Playing'.")
            self.text_source_name = 'AIMP: Now Playing'
        else:
            self.text_source_name = text_source_name

        if not os.path.isfile(file_path) or not re.match(r'^[A-Za-z0-9_\-/:\.]+$', file_path) or self.is_sensitive_path(
                file_path):
            obs.script_log(obs.LOG_WARNING,
                           "Invalid or sensitive file path provided. Defaulting to a safe default path.")
            self.file_path = 'C:/Users/faks/Documents/AIMP/now_playing.txt'
        else:
            self.file_path = file_path

    @staticmethod
    def is_sensitive_path(path):
        # Check if the path points to a sensitive system directory or file
        sensitive_paths = [
            'C:/Windows',
            'C:/Windows/System32',
            '/etc',
            '/bin',
            '/usr'
        ]

        normalized_path = os.path.normpath(path).lower()
        for sensitive in sensitive_paths:
            if normalized_path.startswith(os.path.normpath(sensitive).lower()):
                return True
        return False

    def validate_text_source_name(self):
        # Ensure text_source_name is from a trusted source or matches expected patterns
        allowed_sources = ['AIMP: Now Playing', 'Another Trusted Source']
        if self.text_source_name not in allowed_sources:
            obs.script_log(obs.LOG_WARNING, "Text source name is not trusted. Defaulting to 'AIMP: Now Playing'.")
            self.text_source_name = 'AIMP: Now Playing'

    def update_text_source(self, title):
        self.validate_text_source_name()
        text_source = obs.obs_get_source_by_name(self.text_source_name)
        if text_source is not None:
            settings = obs.obs_data_create()
            sanitized_title = re.sub(r'[<>"\'\\]', '', title)
            obs.obs_data_set_string(settings, 'text', sanitized_title)
            obs.obs_source_update(text_source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(text_source)
        else:
            obs.script_log(obs.LOG_WARNING, "Text source not found. Please check the OBS configuration.")

    def read_now_playing_file(self):
        try:
            with open(self.file_path, "r") as file:
                content = file.read().strip()  # Strip trailing whitespace
                if content:
                    return content
                else:
                    obs.script_log(obs.LOG_INFO, "The file is empty. No song is currently playing.")
                    return "No song playing"
        except FileNotFoundError:
            obs.script_log(obs.LOG_WARNING, "The specified file was not found. Please check the file path.")
        except PermissionError:
            obs.script_log(obs.LOG_ERROR,
                           "Permission denied when accessing the specified file. Please check file permissions.")
        except IsADirectoryError:
            obs.script_log(obs.LOG_ERROR, "Expected a file but found a directory. Please provide a valid file path.")
        except OSError:
            obs.script_log(obs.LOG_ERROR,
                           "An OS error occurred while accessing the file. Please check the file path and permissions.")
        return "No song playing"

    def tick(self):
        get_playing_now = self.read_now_playing_file()
        self.update_text_source(get_playing_now)


# Create an instance of the AimpPlayer class
aimpPlayer = AimpPlayer()


# Define the script properties for OBS
def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, 'text_source_name', 'Text Source Name', obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, 'file_path', 'File Path', obs.OBS_TEXT_DEFAULT)

    return props


# Define the script tick function for OBS
def script_tick(seconds):
    aimpPlayer.tick()
