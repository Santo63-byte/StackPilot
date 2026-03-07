from custom.customaddons import CustomAddons
from core.envinspector import EnvInspector
import logging

# Define all addons in the system here. This class can be extended to include more addons in the future.
class Addons:
    def __init__(self,config):
        self._addons = {}
        self._config = config
        self.construct_addons()
        self._custom_addons = CustomAddons(config)
        self._env_inspector = EnvInspector()    
    
    def get_addons(self):
        return self._addons
    
    def construct_addons(self):
        """Construct and register all addons based on configuration."""
        settings = self._config.server_settings
        logging.info(f"Addons::: Constructing addons with settings: {settings}")
        core_addons = settings.get("core_addons", {})
        custom_addons = settings.get("custom_addons", {})
        for addon_name in core_addons:
            self._addons[addon_name] = core_addons[addon_name]
        for addon_name in custom_addons:
            self._addons[addon_name] = custom_addons[addon_name]

    
    # Define addon features as methods that utilize the registered addons
    def is_server_process_running(self, server_id: str):
        """Check if the server process is currently running."""
        return self._env_inspector.is_server_process_running(server_id)
    
    def get_git_branch_name(self, repo_path: str = None):
        """Get the current Git branch name for a given repository path."""
        return self._env_inspector.get_git_branch_name(repo_path)
