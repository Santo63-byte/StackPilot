from configs import Config
import logging
from core.addons import Addons
from typing import Any, Dict
import json

class AppManager:
    def __init__(self):
        self._config = Config()
        self._addons = None
        self._addonscfg = {}
        
    def get_app_render_attributes(self):
        """Get attributes needed for app rendering, such as terminal type and addon statuses."""
        self._addons = Addons(self._config)
        self._addonscfg = self._addons.get_addons()
        logging.info(f'SPServerManager::: Fetching app render attributes with config: {self._config.server_settings}, addons config: {self._addonscfg}')
        return {
            "app_name": self._config.app_info.get("app_name", "DevDock"),
            "version": self._config.app_info.get("version", "unknown"),
            "refresh_interval": self._config.server_settings.get("refresh_interval", 10),
            "terminal": self._config.server_settings.get("terminal", "Windows_Terminal"),
            "error_reporting": self._config.server_settings.get("error_reporting", False),
            "enable_notifications": self._config.server_settings.get("enable_notifications", False),
            "addons": {
                "git_integration": self._addonscfg.get("git_integration", {}).get("enabled", False),
                "proxy_settings": {
                   "enabled": self._addonscfg.get("proxy_settings", {}).get("enabled", False),
                   "active_environment": self._addons._custom_addons.get_current_proxy_environment() if self._addonscfg.get("proxy_settings", {}).get("enabled", False) else None,
                   "is_proxy_running": self._addons._custom_addons.is_proxy_running() if self._addonscfg.get("proxy_settings", {}).get("enabled", False) else None      
                },
                "console_display": self._addonscfg.get("console_display", {}).get("enabled", False),
                "server_detection": self._addonscfg.get("server_detection", {}).get("enabled",False),
                "port_killer": self._addonscfg.get("port_killer", {}).get("enabled", False),
            }
        }
    def get_app_settings(self):
        """Get app settings that can be modified by the user."""
        
        settings:Dict[str,Dict[str,Any]] = {
            "basic_settings": {
                "refresh_interval": self._config.server_settings.get("refresh_interval", 10),
                "error_reporting": self._config.server_settings.get("error_reporting", False),
                "enable_notifications": self._config.server_settings.get("enable_noti,fications", False),
                "terminal": self._config.server_settings.get("terminal", "Windows_Terminal")  
            },
            "advanced_settings": {}
        }
        #Currently user controlled addon settings are only proxy settings, but this can be extended in the future to include settings for other addons as well.
        addons_settings = {
            "proxy_settings": {
                "root_path": self._addons._custom_addons.get_proxy_root_path() if self._addonscfg.get("proxy_settings", {}).get("enabled", False) else None
            }
        }
        settings["advanced_settings"] = addons_settings
        return settings
        
    def update_app_settings(self, new_settings:Dict[str,Dict[str,Any]]):
        """Update app settings based on user input."""
        logging.info(f"Updating app settings with new settings: {new_settings}")
        basic_settings = new_settings.get("basic_settings", {})
        advanced_settings = new_settings.get("advanced_settings", {})
        
        # Update basic settings in config
        #updating in memory config, the changes will be written to file in write_updated_settings_to_file method which is called at the end of this method. This way we ensure that the in-memory config and the config file are always in sync after any update.
        for key, value in basic_settings.items():
            if key in self._config.server_settings:
                self._config.server_settings[key] = value
                
        self.write_updated_settings_to_file(basic_settings, advanced_settings)
        
        # Update advanced settings (currently only proxy settings)
        #since proxy settings can be configured in serverlist file it should be updated differently and not in internal config as it is not read from config but directly from proxy config file by the addons manager, so we will directly call the respective method in addons manager to update the proxy settings based on user input. This way we ensure that the changes to proxy settings are immediately reflected in the proxy config file which is the source of truth for proxy settings in our application.
        proxy_settings = advanced_settings.get("proxy_settings", {})
        if proxy_settings and self._addonscfg.get("proxy_settings", {}).get("enabled", False):
            self._addons._custom_addons.save_proxy_config(proxy_settings)
            logging.info(f"Received request to update proxy settings: {proxy_settings}")
            
    def write_updated_settings_to_file(self, basic_settings:Dict[str,Any], advanced_settings:Dict[str,Any]):
        """Write the updated settings back to the app_config.json file."""
        app_settings_file_path = self._config.context.get("app_settings_file_path", "")
        try:
            with open(app_settings_file_path, 'r') as file:
                config_data = json.load(file)
            # Update the app_settings section with the new settings
            app_settings = config_data.setdefault("app_settings", {})

            # Map basic_settings keys to their corresponding json keys
            basic_key_map = {
                "refresh_interval": "refresh_interval",
                "error_reporting": "error_reporting",
                "enable_notifications": "enable_notifications",
                "terminal": "terminal",
            }
            for settings_key, json_key in basic_key_map.items():
                if settings_key in basic_settings:
                    app_settings[json_key] = basic_settings[settings_key]

            # Map advanced_settings: proxy_settings overrides custom_addons.proxy_settings in json
            proxy_settings = advanced_settings.get("proxy_settings", {})
            if proxy_settings:
                custom_addons = app_settings.setdefault("custom_addons", {})
                existing_proxy = custom_addons.setdefault("proxy_settings", {})
                existing_enabled = existing_proxy.get("enabled")
                existing_proxy.update({k: v for k, v in proxy_settings.items() if k != "enabled"})
                if existing_enabled is not None:
                    existing_proxy["enabled"] = existing_enabled

            with open(app_settings_file_path, 'w') as file:
                json.dump(config_data, file, indent=4)
            logging.info(f"Successfully wrote updated settings to {app_settings_file_path}")
        except Exception as e:
            logging.error(f"Error writing updated settings to file: {e}")
            
    def download_server_config(self):
        """Return the path of the server list JSON file for download."""
        datasources = self._config.context.get("datasources", {})
        server_list_file_path = datasources.get("server_list")
        return server_list_file_path
        
        
    def upload_server_config(self, new_config):
        """Upload a new server configuration file provided by the user."""
        datasources = self._config.context.get("datasources", {})
        server_list_file_path = datasources.get("server_list")
        try:
            with open(server_list_file_path, 'w') as file:
                json.dump(new_config, file, indent=4)
            logging.info(f"Successfully uploaded new server config to {server_list_file_path}")
            return True
        except Exception as e:
            logging.error(f"Error uploading new server config: {e}")
            return False
