"""
This module handles the configuration for the CacheLauncher application.
"""

import os
import pathlib
import logging
import json

LOGGER = logging.getLogger(__name__)


class ConfigHandler:
    """
    A class to handle the configuration for the CacheLauncher application.
    """

    def __init__(self):
        """
        Initialize the ConfigHandler with the path to the configuration file.
        """
        _home_path = pathlib.Path(__file__).parent.parent
        self._config_path = os.path.join(_home_path, "config.json")
        LOGGER.debug("Initialized ConfigHandler with config path: %s", self._config_path)

    @property
    def config_path(self):
        """
        Property to get the path to the configuration file.
        """
        return self._config_path

    def _config_isvalid(self, config_data: dict):
        """
        Check if the configuration data is valid.
        """
        LOGGER.debug("Validating configuration data.")
        required_keys = [("appName", str), ("version", str), ("settings", dict), ("paths", dict)]
        settings_keys = [("ui", dict), ("logLevel", str)]
        ui_keys = [("gui", bool), ("theme", str)]
        paths_keys = [("cacheDirectory", str), ("logFile", str)]

        # Check top-level keys and their types
        for key, expected_type in required_keys:
            if key not in config_data or not isinstance(config_data[key], expected_type):
                LOGGER.error(
                    "Missing or invalid type for top-level config key: %s (expected %s)",
                    key, expected_type.__name__
                )
                return False

        # Validate settings keys and their types
        settings = config_data.get("settings", {})
        for key, expected_type in settings_keys:
            if key not in settings or not isinstance(settings[key], expected_type):
                LOGGER.error(
                    "Missing or invalid type for settings key: %s (expected %s)",
                    key, expected_type.__name__
                )
                return False

        # Validate UI keys and their types
        ui = settings.get("ui", {})
        for key, expected_type in ui_keys:
            if key not in ui or not isinstance(ui[key], expected_type):
                LOGGER.error(
                    "Missing or invalid type for UI key: %s (expected %s)",
                    key, expected_type.__name__
                )
                return False

        # Validate paths keys and their types
        paths = config_data.get("paths", {})
        for key, expected_type in paths_keys:
            if key not in paths or not isinstance(paths[key], expected_type):
                LOGGER.error(
                    "Missing or invalid type for paths key: %s (expected %s)",
                    key, expected_type.__name__
                )
                return False

        LOGGER.debug("Configuration data is valid.")
        return True

    def get_config(self) -> dict:
        """
        Validate the configuration data and set the config_data attribute.
        """
        LOGGER.info("Getting configuration file.")
        if not os.path.exists(self.config_path):
            LOGGER.error("Configuration file not found: %s", self.config_path)
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding="utf8") as config_file:
            try:
                config_data = json.load(config_file)
                LOGGER.debug("Configuration file loaded successfully.")
                if not self._config_isvalid(config_data):
                    LOGGER.error("Configuration data is invalid.")
                    raise ValueError("Configuration data is invalid.")
                LOGGER.info("Configuration data returned successfully.")
                return config_data
            except json.JSONDecodeError as e:
                LOGGER.error("Error decoding JSON: %s", e)
                raise ValueError(f"Error decoding JSON: {e}") from e

    def save_config(self, config_data: dict) -> None:
        """
        Save the configuration data to the configuration file.
        """
        LOGGER.info("Saving configuration data.")
        if not self._config_isvalid(config_data):
            LOGGER.error("Cannot save invalid configuration data.")
            raise ValueError("Cannot save invalid configuration data.")

        with open(self.config_path, 'w', encoding="utf8") as config_file:
            try:
                json.dump(config_data, config_file, indent=4)
                LOGGER.info("Configuration data saved successfully.")
            except TypeError as e:
                LOGGER.error("Error saving JSON: %s", e)
                raise ValueError(f"Error saving JSON: {e}") from e
