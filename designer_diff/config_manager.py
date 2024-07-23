import yaml
import os
from designer_diff.logging_config import logger

DEFAULT_CONFIG = {
    "relevant_properties": ["Location", "Size"],
    "ignored_properties": ["TabIndex"],
    "designer_file_pattern": "Dash*.Designer.cs",
    "git_root_path": "",
}

class ConfigManager:
    def __init__(self, config_file="config.yaml"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as file:
                    loaded_config = yaml.safe_load(file)
                    logger.info(f"Configuration loaded from {self.config_file}")
                    return {**DEFAULT_CONFIG, **loaded_config}  # Merge with default config
            else:
                logger.warning(f"Configuration file {self.config_file} not found. Using default configuration.")
                return DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}. Using default configuration.")
            return DEFAULT_CONFIG.copy()

    def save_config(self):
        try:
            with open(self.config_file, 'w') as file:
                yaml.dump(self.config, file)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")

    def get(self, key, default=None):
        value = self.config.get(key, default)
        if value is None:
            logger.warning(f"Configuration key '{key}' not found. Using default value: {default}")
        return value

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
        logger.info(f"Configuration updated: {key} = {value}")

config_manager = ConfigManager()