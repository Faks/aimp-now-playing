from typing import Any
import obspython as obs
import re
import os


class AimpPlayer:
    def __init__(
            self,
            text_source_name='AIMP: Now Playing',
            now_playing_file='C:/Users/faks/Documents/AIMP/now_playing.txt',
            state_file='C:/Users/faks/Documents/AIMP/state_detector.txt',
    ):
        # Validate and set the text source name
        self.text_source_name = text_source_name if re.match(r'^[\w\s:]+$', text_source_name) else 'AIMP: Now Playing'
        if not re.match(r'^[\w\s:]+$', text_source_name):
            obs.script_log(obs.LOG_WARNING, "Invalid text source name. Defaulting to 'AIMP: Now Playing'.")

        # Validate and set the now playing file path
        self.now_playing_file = self.validate_file_path(now_playing_file,
                                                        'C:/Users/faks/Documents/AIMP/now_playing.txt')

        # Validate and set the state file path
        self.state_file = self.validate_file_path(state_file, 'C:/Users/faks/Documents/AIMP/state_detector.txt')

    @staticmethod
    def validate_file_path(file_path, default_path):
        """Validate the file path and return a safe default if invalid."""
        if not os.path.isfile(file_path) or AimpPlayer.is_sensitive_path(file_path):
            obs.script_log(obs.LOG_WARNING, f"Invalid or sensitive file path. Using default: {default_path}")
            return default_path
        return file_path

    @staticmethod
    def is_sensitive_path(path):
        """Check if the path points to a sensitive system directory or file."""
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
        """Validate the text source name."""
        allowed_sources = ['AIMP: Now Playing', 'Another Trusted Source']
        if self.text_source_name not in allowed_sources:
            obs.script_log(obs.LOG_WARNING, "Text source name not trusted. Defaulting to 'AIMP: Now Playing'.")
            self.text_source_name = 'AIMP: Now Playing'

    def update_text_source(self, title):
        """Update the OBS text source with the given title."""
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

    def read_file(self, file_path):
        """Read and return the content of a file, handling errors gracefully."""
        try:
            with open(file_path, "r") as file:
                content = file.read().strip()  # Strip trailing whitespace
                if content:
                    return content
                else:
                    obs.script_log(obs.LOG_INFO, f"The file {file_path} is empty.")
                    return "No data"
        except FileNotFoundError:
            obs.script_log(obs.LOG_WARNING, f"The file {file_path} was not found.")
        except PermissionError:
            obs.script_log(obs.LOG_ERROR, f"Permission denied for file: {file_path}.")
        except IsADirectoryError:
            obs.script_log(obs.LOG_ERROR, f"Expected a file but found a directory: {file_path}.")
        except OSError:
            obs.script_log(obs.LOG_ERROR, f"An OS error occurred while accessing the file: {file_path}.")
        return "Error reading file"

    def tick(self):
        """Read the current playing song and state, and update the OBS text source."""
        now_playing = self.read_file(self.now_playing_file)
        state = self.read_file(self.state_file)

        # Combine the song title and state
        if state in ["Stopped"]:
            combined_text = ''
        else:
            combined_text = f"{now_playing}"

        self.update_text_source(combined_text)


# Create an instance of the AimpPlayer class
aimpPlayer = AimpPlayer()


# Define the script properties for OBS
def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, 'text_source_name', 'Text Source Name', obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, 'now_playing_file', 'Now Playing File Path', obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, 'state_file', 'State File Path', obs.OBS_TEXT_DEFAULT)

    return props


# Define the script tick function for OBS
def script_tick(seconds):
    aimpPlayer.tick()
