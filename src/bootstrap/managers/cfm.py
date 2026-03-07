from configs import Config

from typing import Any, Dict, Optional
import logging
import json
import os

class ConfigManager:
    def __init__(self,config:object=None):
        self.configs = config
        self.config_file_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "..",
            "configs", 
            "app_config.json"
        )
    C= "C:/tmp"
    D= "D:/tmp"
    def add_config(self,config:Dict, key: str, value):
        config[key] = value
        
        
    def process_server_settings(self, settings: Dict[str, Any]) -> None:
        """Process server settings if needed."""
        # Handle case where settings is None or not a dictionary
        if not settings or not isinstance(settings, dict):
            return
        
        storage_type = settings.get("storage", "C_Drive_Temp")
        
        # Map storage type to actual storage path
        if storage_type == "C_Drive_Temp":
            settings["storage"] = self.C
        elif storage_type == "D_Drive_Temp":
            settings["storage"] = self.D
        else:
            # Default to C if unknown or if storage is None
            settings["storage"] = self.C
    
    
    def load_configs(self) -> Dict[str, Any]:
        """Load configurations from app_config.json and populate the Config singleton."""
        try:
            with open(self.config_file_path, 'r') as file:
                config_data = json.load(file)
            
            # Store configurations in the Config singleton
            if "app_info" in config_data:
                self.configs.app_info = config_data["app_info"]
            
            if "app_settings" in config_data:
                self.process_server_settings(config_data["app_settings"])
                self.configs.server_settings = config_data["app_settings"]
            
            if "user_settings" in config_data:
                self.configs.user_preferences = config_data["user_settings"]
            
            return config_data
        
        except FileNotFoundError:
            logging.error(f"Config file not found at {self.config_file_path}")
            return {}
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from {self.config_file_path}")
            return {}
    
    def get_config(self, key: str) -> Optional[Any]:
        """Get a specific configuration value by key."""
        configs = self.load_configs()
        return configs.get(key, None)
    
    def initialize(self) -> None:
        """Initialize configuration manager by loading all configurations."""
        config_data= self.load_configs()
        if config_data:
            logging.info("Configurations loaded successfully.")
        else:
            logging.warning("Failed to load configurations.")
        
